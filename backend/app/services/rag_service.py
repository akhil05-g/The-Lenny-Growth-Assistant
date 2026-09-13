"""Hybrid RAG Retrieval Engine for Lenny's Podcast Transcripts."""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import yaml
from rank_bm25 import BM25Okapi

from backend.app.config import settings
from backend.app.schemas.chat import GroundedSource

logger = logging.getLogger("lenny_assistant.rag_service")


class TranscriptChunk:
    """Represents a chunk of podcast dialogue with source metadata."""
    def __init__(
        self,
        episode_slug: str,
        title: str,
        guest: str,
        youtube_url: str,
        video_id: str,
        speaker: str,
        timestamp: str,
        text: str,
    ):
        self.episode_slug = episode_slug
        self.title = title
        self.guest = guest
        self.youtube_url = youtube_url
        self.video_id = video_id
        self.speaker = speaker
        self.timestamp = timestamp
        self.text = text

    @property
    def full_reference(self) -> str:
        return f"{self.title} (Guest: {self.guest})"

    @property
    def timestamped_url(self) -> str:
        if not self.youtube_url or not self.timestamp:
            return self.youtube_url or ""
        try:
            cleaned = self.timestamp.replace("(", "").replace(")", "").strip()
            parts = [int(p) for p in cleaned.split(":")]
            if len(parts) == 3:
                secs = parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2:
                secs = parts[0] * 60 + parts[1]
            else:
                secs = 0
            sep = "&" if "?" in self.youtube_url else "?"
            return f"{self.youtube_url}{sep}t={secs}s"
        except Exception:
            return self.youtube_url


class RAGService:
    """Hybrid Retrieval Service with topic indexing and BM25 ranking."""

    def __init__(self, data_dir: str = settings.TRANSCRIPTS_DATA_DIR, index_dir: str = settings.INDEX_DATA_DIR):
        self.data_dir = Path(data_dir)
        self.index_dir = Path(index_dir)
        self.chunks: List[TranscriptChunk] = []
        self.bm25: Optional[BM25Okapi] = None
        self.tokenized_corpus: List[List[str]] = []
        self.topic_map: Dict[str, List[str]] = {}  # topic -> list of episode slugs
        self.guest_index: Dict[str, List[int]] = {}  # guest_name_lower -> chunk indices
        self.is_indexed = False

    def initialize(self) -> None:
        """Load and index transcripts from disk."""
        if self.is_indexed:
            return
        logger.info(f"Initializing Knowledge Base from {self.data_dir}...")
        self._load_topic_indices()
        self._load_episodes()
        self._build_bm25_index()
        self.is_indexed = True
        logger.info(f"RAG Knowledge Base initialized with {len(self.chunks)} chunks across {len(self.guest_index)} guests.")

    def _load_topic_indices(self) -> None:
        """Parse index directory markdown files."""
        if not self.index_dir.exists():
            return
        for file_path in self.index_dir.glob("*.md"):
            topic_name = file_path.stem.replace("-", " ").lower()
            try:
                content = file_path.read_text(encoding="utf-8")
                slugs = re.findall(r"episodes/([a-zA-Z0-9_\-]+)/", content)
                if slugs:
                    self.topic_map[topic_name] = slugs
            except Exception as e:
                logger.warning(f"Error reading topic index {file_path}: {e}")

    def _load_episodes(self) -> None:
        """Traverse episode directories and chunk markdown files."""
        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} does not exist.")
            return

        episode_files = list(self.data_dir.glob("**/transcript.md"))
        logger.info(f"Found {len(episode_files)} transcript markdown files.")

        for file_path in episode_files:
            slug = file_path.parent.name
            try:
                content = file_path.read_text(encoding="utf-8")
                self._process_transcript_file(slug, content)
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")

    def _process_transcript_file(self, slug: str, content: str) -> None:
        """Line-by-line streaming parser for rapid, non-backtracking dialogue chunking."""
        frontmatter = {}
        body = content

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2]
                except Exception:
                    body = content

        title = frontmatter.get("title") or slug.replace("-", " ").title()
        guest = frontmatter.get("guest") or slug.replace("-", " ").title()
        youtube_url = frontmatter.get("youtube_url") or ""
        video_id = frontmatter.get("video_id") or ""

        # Line-by-line speaker turn parsing
        current_speaker = guest
        current_timestamp = "(00:00:00)"
        current_buffer: List[str] = []

        turn_header_re = re.compile(r"^([A-Za-z0-9\s\.\'\-]+)?\s*(\(\d{1,2}:\d{2}(?::\d{2})?\))\s*:\s*(.*)$")

        # Low-signal phrases to exclude from retrieval (intros, sponsor reads, transition banter)
        noise_phrases = [
            "today my guest is",
            "brought to you by",
            "welcome to lenny's podcast",
            "thank you to our sponsor",
            "see you next week",
        ]

        for line in body.split("\n"):
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            match = turn_header_re.match(line_str)
            if match:
                # Flush existing buffer
                if current_buffer:
                    chunk_text = " ".join(current_buffer).strip()
                    text_lower = chunk_text.lower()
                    is_noise = any(p in text_lower for p in noise_phrases)
                    # Require at least 40 words for substantive operator insight
                    if len(chunk_text.split()) >= 40 and not is_noise:
                        self._add_chunk(
                            slug=slug,
                            title=title,
                            guest=guest,
                            youtube_url=youtube_url,
                            video_id=video_id,
                            speaker=current_speaker,
                            timestamp=current_timestamp,
                            text=chunk_text[:1400],
                        )
                    current_buffer = []

                spk_name = match.group(1)
                if spk_name and spk_name.strip():
                    current_speaker = spk_name.strip()
                current_timestamp = match.group(2).strip()
                remaining = match.group(3)
                if remaining and remaining.strip():
                    current_buffer.append(remaining.strip())
            else:
                current_buffer.append(line_str)

        # Flush trailing buffer
        if current_buffer:
            chunk_text = " ".join(current_buffer).strip()
            text_lower = chunk_text.lower()
            is_noise = any(p in text_lower for p in noise_phrases)
            if len(chunk_text.split()) >= 40 and not is_noise:
                self._add_chunk(
                    slug=slug,
                    title=title,
                    guest=guest,
                    youtube_url=youtube_url,
                    video_id=video_id,
                    speaker=current_speaker,
                    timestamp=current_timestamp,
                    text=chunk_text[:1400],
                )


    def _add_chunk(
        self,
        slug: str,
        title: str,
        guest: str,
        youtube_url: str,
        video_id: str,
        speaker: str,
        timestamp: str,
        text: str,
    ) -> None:
        chunk = TranscriptChunk(
            episode_slug=slug,
            title=title,
            guest=guest,
            youtube_url=youtube_url,
            video_id=video_id,
            speaker=speaker,
            timestamp=timestamp,
            text=text,
        )
        idx = len(self.chunks)
        self.chunks.append(chunk)

        guest_key = guest.lower()
        if guest_key not in self.guest_index:
            self.guest_index[guest_key] = []
        self.guest_index[guest_key].append(idx)

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\w+", text) if len(w) > 2]

    def _build_bm25_index(self) -> None:
        """Construct Okapi BM25 index over all chunks."""
        self.tokenized_corpus = []
        for c in self.chunks:
            tokens = self._tokenize(f"{c.guest} {c.title} {c.speaker} {c.text}")
            self.tokenized_corpus.append(tokens)

        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(
        self,
        query: str,
        top_k: int = 5,
        guest_filter: Optional[str] = None,
    ) -> List[GroundedSource]:
        """Search knowledge base with hybrid scoring and metadata enrichment."""
        if not self.is_indexed:
            self.initialize()

        if not self.chunks or not self.bm25:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # 1. BM25 Lexical Scores
        doc_scores = self.bm25.get_scores(query_tokens)

        query_lower = query.lower()
        matched_guests = [g for g in self.guest_index.keys() if g in query_lower]
        matched_topic_slugs = []
        for topic, slugs in self.topic_map.items():
            if any(t in query_lower for t in topic.split()):
                matched_topic_slugs.extend(slugs)

        # Identify guest terms vs content query terms
        guest_terms = set()
        for g in matched_guests:
            guest_terms.update(self._tokenize(g))
        if guest_filter:
            guest_terms.update(self._tokenize(guest_filter))


        content_tokens = [t for t in query_tokens if t not in guest_terms]
        
        # Domain expansion for common strategic themes (e.g. founder mode, leadership, roadmaps)
        expanded_content_tokens = list(content_tokens)
        query_text_lower = query.lower()
        if "founder" in query_text_lower or "mode" in query_text_lower:
            expanded_content_tokens.extend(["details", "micromanagement", "decision", "cpo", "roadmap", "founder"])
        if "leadership" in query_text_lower or "management" in query_text_lower:
            expanded_content_tokens.extend(["leaders", "expert", "culture", "organization", "clarity"])

        expanded_token_set = set(expanded_content_tokens)
        query_token_set = set(query_tokens)

        scored_candidates: List[Tuple[float, int]] = []
        for idx, score in enumerate(doc_scores):
            chunk = self.chunks[idx]

            if guest_filter and guest_filter.lower() not in chunk.guest.lower():
                continue

            # Check query token overlap ratio against full query
            chunk_tokens = set(self.tokenized_corpus[idx])
            overlap = len(query_token_set.intersection(chunk_tokens))
            overlap_ratio = overlap / len(query_token_set)

            # Strict relevance filter: prevent incidental 1-word matches on multi-word out-of-domain queries
            if len(query_tokens) >= 3 and overlap_ratio < 0.35 and score < 25.0:
                continue

            # Content relevance: how well does the chunk's body text match the topical terms?
            body_tokens = set(self._tokenize(chunk.text))
            content_match_count = len(expanded_token_set.intersection(body_tokens))

            # Penalty for chunks with zero content/topic match (pure chatter)
            if content_tokens and content_match_count == 0:
                continue

            boost = 1.0
            # Topical match boost based on body text density of relevant concepts
            if content_match_count > 0:
                boost += min(content_match_count * 0.8, 4.0)

            if any(g in chunk.guest.lower() for g in matched_guests):
                boost += 1.5

            if chunk.episode_slug in matched_topic_slugs:
                boost += 1.5

            # Favor longer, substantive paragraphs over short fragments
            word_count = len(chunk.text.split())
            if word_count >= 80:
                boost += 0.5

            final_score = float(score) * boost
            if final_score >= 12.0:
                scored_candidates.append((final_score, idx))

        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        results: List[GroundedSource] = []
        seen_chunks = set()

        for score, idx in scored_candidates:
            chunk = self.chunks[idx]
            # Avoid near-duplicate turns from the same timestamp
            chunk_key = (chunk.episode_slug, chunk.timestamp)
            if chunk_key in seen_chunks:
                continue
            seen_chunks.add(chunk_key)

            results.append(
                GroundedSource(
                    episode_title=chunk.title,
                    guest=chunk.guest,
                    quote=chunk.text,
                    youtube_url=chunk.timestamped_url,
                    timestamp=chunk.timestamp,
                    relevance_score=round(score, 3),
                )
            )
            if len(results) >= top_k:
                break

        return results



# Global RAGService singleton
rag_service = RAGService()
