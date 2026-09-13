"""Agent Orchestration Service coordinating RAG, Skills, Memory, and Persistence."""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import async_session_factory
from backend.app.models.session import SessionModel
from backend.app.models.message import MessageModel
from backend.app.schemas.chat import (
    ChatMessageResponse,
    GroundedSource,
    ArtifactSummary,
)
from backend.app.services.rag_service import rag_service
from backend.app.services.llm_provider import llm_manager
from backend.app.services.ship30_skill import (
    SHIP30_SYSTEM_PROMPT,
    build_ship30_prompt,
)
from backend.app.services.artifact_service import artifact_service

logger = logging.getLogger("lenny_assistant.agent_service")

GENERAL_GROUNDING_SYSTEM_PROMPT = """You are "The Lenny Growth Assistant", an authoritative, friendly AI assistant built for product managers, growth executives, and founders.

CORE BEHAVIOR & GUIDELINES:
1. CONVERSATIONAL COURTESY: When the user greets you, says hello, or asks how you are doing, respond warmly and conversationally as "The Lenny Growth Assistant". Introduce your role—synthesizing tactical wisdom from over 300 in-depth episodes of Lenny's Podcast on product management, growth loops, metrics, and leadership—and invite them to ask their question. Do NOT refuse greetings or claim lack of transcripts for polite conversational banter.
2. STRICT GROUNDING ON TOPICAL QUESTIONS: When answering questions about product management, business strategy, growth frameworks, or specific guests, ground your answers in the provided transcripts. Clearly credit the guest by name and quote their core insight.
3. CITATION DISCIPLINE: Quote the guest accurately (e.g. "Brian Chesky shared on Lenny's Podcast...", "Elena Verna highlighted that...").
4. NO PLACEHOLDERS: NEVER output placeholder tokens like "(Episode X, Timestamp Y)", "(Episode #, Time)", or "[Link]". Use the EXACT episode title and timestamp provided in the GROUNDED PODCAST TRANSCRIPTS section. If you do not have the exact timestamp, simply state the guest's name and their insight without placeholder parentheses.
5. OUT OF DOMAIN REFUSAL: Only refuse if the user asks about completely unrelated, non-business topics (such as cooking recipes, pop music, astrology). In that case, politely state that your knowledge base is focused on product management, growth, and company building from Lenny's podcast.
6. ARTIFACT GENERATION: When the user asks for a document, checklist, matrix, or interactive mini-webpage, format it inside a structured artifact block:
   :::artifact title="Descriptive Title" type="markdown" (or type="html")
   [artifact content here]
   :::
"""


def is_conversational_turn(text: str) -> bool:
    """Check if the turn is a greeting or general conversational banter rather than a search query."""
    t = text.strip().lower()
    t_clean = re.sub(r"[^\w\s]", "", t).strip()
    greetings = {
        "hi", "hello", "hey", "hola", "sup", "yo", "good morning", "good evening",
        "good afternoon", "whats up", "what's up", "howdy", "greetings"
    }
    if t_clean in greetings:
        return True

    conversational_patterns = [
        r"^(hi|hello|hey|greetings|howdy)\b",
        r"what('?s|\s+are)\s+(you|u)\s+doing",
        r"how\s+(are\s+|r\s+)?(you|u)(\s+doing)?",
        r"who\s+are\s+(you|u)",
        r"what\s+can\s+(you|u)\s+do",
        r"how('?s|\s+is)\s+it\s+going",
        r"tell\s+me\s+about\s+yourself",
        r"what\s+is\s+this",
        r"^help(\s+me)?$",
    ]
    return any(re.search(p, t) for p in conversational_patterns)


class AgentService:
    """Coordinates conversational multi-turn RAG, agent tools, and message persistence."""

    @classmethod
    async def process_user_turn(
        cls,
        session_id: str,
        user_message: str,
        db: AsyncSession,
        skill: Optional[str] = "general",
        model_override: Optional[str] = None,
    ) -> ChatMessageResponse:
        """Execute a complete agent turn with grounding, tool execution, and persistence."""

        # 1. Verify and retrieve session
        session_query = await db.execute(select(SessionModel).where(SessionModel.id == session_id))
        session_obj = session_query.scalar_one_or_none()
        if not session_obj:
            session_obj = SessionModel(id=session_id, title=user_message[:40] + ("..." if len(user_message) > 40 else ""))
            db.add(session_obj)
            await db.flush()

        if session_obj.title == "New Conversation":
            session_obj.title = user_message[:40] + ("..." if len(user_message) > 40 else "")

        # 2. Persist User Message
        user_record = MessageModel(
            session_id=session_id,
            role="user",
            content=user_message,
            sources=[],
        )
        db.add(user_record)
        await db.flush()

        # 3. Load historical messages for context (last 6 turns)
        history_query = await db.execute(
            select(MessageModel)
            .where(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.asc())
        )
        all_messages = history_query.scalars().all()
        history_context: List[Dict[str, str]] = []
        for msg in all_messages[-6:]:
            history_context.append({"role": msg.role, "content": msg.content})

        # 4. Check conversational banter & RAG Retrieval
        is_conv = is_conversational_turn(user_message)
        retrieved_sources: List[GroundedSource] = []
        if not is_conv:
            retrieved_sources = rag_service.search(
                query=user_message,
                top_k=5,
            )

        # Detect intent from message text or explicit skill parameter
        msg_lower = user_message.lower()
        wants_ship30 = skill == "ship30" or "ship 30" in msg_lower or "ship30" in msg_lower or "essay" in msg_lower
        wants_artifact = skill == "artifact" or "artifact" in msg_lower or "checklist" in msg_lower or "html" in msg_lower

        # 5. Build System & Context Prompt
        if wants_ship30:
            system_prompt = SHIP30_SYSTEM_PROMPT
            prompt_content = build_ship30_prompt(user_message, retrieved_sources)
            messages_for_llm = [{"role": "user", "content": prompt_content}]
        elif is_conv:
            system_prompt = (
                f"{GENERAL_GROUNDING_SYSTEM_PROMPT}\n\n"
                "CONVERSATIONAL TURN: The user is greeting you or chatting conversationally. "
                "Respond warmly, naturally, and helpfully as 'The Lenny Growth Assistant'. "
                "Introduce your capabilities (300+ episodes of Lenny's Podcast transcripts, product management, growth, Ship 30 essays, artifacts) "
                "and invite them to ask their question."
            )
            messages_for_llm = history_context
        else:
            if retrieved_sources:
                context_str = "GROUNDED PODCAST TRANSCRIPTS:\n"
                for idx, s in enumerate(retrieved_sources, 1):
                    context_str += (
                        f"\n--- [Source {idx}] ---\n"
                        f"Guest: {s.guest}\n"
                        f"Episode: {s.episode_title}\n"
                        f"Timestamp: {s.timestamp}\n"
                        f"Transcript Excerpt: {s.quote}\n"
                    )
            else:
                context_str = (
                    "NO_RELEVANT_TRANSCRIPTS_FOUND.\n"
                    "If the user is asking a broad question about product management, career growth, startups, or metrics, "
                    "answer helpfully based on standard industry product principles while noting that exact quotes were not found. "
                    "Only if the question is completely out-of-domain (e.g., cooking, politics, pop music), "
                    "politely state that your knowledge is focused on product management and growth from Lenny's podcast."
                )

            system_prompt = f"{GENERAL_GROUNDING_SYSTEM_PROMPT}\n\n{context_str}"
            if wants_artifact:
                system_prompt += (
                    "\n\nUSER REQUESTS AN ARTIFACT: Generate an interactive, highly formatted document or HTML/CSS widget "
                    "wrapped in :::artifact title=\"...\" type=\"html\" ... ::: blocks."
                )
            messages_for_llm = history_context

        # 6. Generate response through LLM Provider Layer
        raw_output, provider_used, latency = await llm_manager.generate_with_fallback(
            messages=messages_for_llm,
            system_prompt=system_prompt,
            temperature=0.2,
        )

        # 7. Extract Artifacts if present
        clean_text, artifact_data = artifact_service.extract_artifact(raw_output)
        persisted_artifact: Optional[ArtifactSummary] = None

        if artifact_data:
            persisted_artifact = await artifact_service.create_and_persist_artifact(
                session_id=session_id,
                artifact_data=artifact_data,
                db=db,
            )

        # 8. Persist Assistant Message
        sources_payload = [s.model_dump() for s in retrieved_sources] if retrieved_sources else []
        assistant_record = MessageModel(
            session_id=session_id,
            role="assistant",
            content=clean_text,
            sources=sources_payload,
            artifact_id=persisted_artifact.id if persisted_artifact else None,
        )
        db.add(assistant_record)
        session_obj.updated_at = datetime.now(timezone.utc)
        session_obj.model_used = provider_used
        await db.commit()
        await db.refresh(assistant_record)

        return ChatMessageResponse(
            id=assistant_record.id,
            session_id=session_id,
            role="assistant",
            content=assistant_record.content,
            sources=retrieved_sources,
            artifact=persisted_artifact,
            model_used=provider_used,
            created_at=assistant_record.created_at,
        )

    @classmethod
    async def process_user_turn_stream(
        cls,
        session_id: str,
        user_message: str,
        skill: Optional[str] = "general",
        model_override: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ):
        """Execute a streaming agent turn yielding SSE events for sources, progressive tokens, and artifacts.
        
        Manages its own database session to guarantee validity throughout the async generator lifecycle.
        """
        async with async_session_factory() as session_db:
            try:
                # 1. Verify and retrieve session
                session_query = await session_db.execute(select(SessionModel).where(SessionModel.id == session_id))
                session_obj = session_query.scalar_one_or_none()
                if not session_obj:
                    session_obj = SessionModel(
                        id=session_id,
                        title=user_message[:40] + ("..." if len(user_message) > 40 else ""),
                    )
                    session_db.add(session_obj)
                    await session_db.commit()
                    await session_db.refresh(session_obj)

                if session_obj.title == "New Conversation":
                    session_obj.title = user_message[:40] + ("..." if len(user_message) > 40 else "")

                # 2. Persist User Message
                user_record = MessageModel(
                    session_id=session_id,
                    role="user",
                    content=user_message,
                    sources=[],
                )
                session_db.add(user_record)
                await session_db.commit()

                # 3. History
                history_query = await session_db.execute(
                    select(MessageModel)
                    .where(MessageModel.session_id == session_id)
                    .order_by(MessageModel.created_at.asc())
                )
                all_messages = history_query.scalars().all()
                history_context: List[Dict[str, str]] = []
                for msg in all_messages[-6:]:
                    history_context.append({"role": msg.role, "content": msg.content})

                # 4. Conversational Check & RAG Retrieval
                is_conv = is_conversational_turn(user_message)
                retrieved_sources: List[GroundedSource] = []
                if not is_conv:
                    retrieved_sources = rag_service.search(
                        query=user_message,
                        top_k=5,
                    )

                msg_lower = user_message.lower()
                wants_ship30 = skill == "ship30" or "ship 30" in msg_lower or "ship30" in msg_lower or "essay" in msg_lower
                wants_artifact = skill == "artifact" or "artifact" in msg_lower or "checklist" in msg_lower or "html" in msg_lower

                if wants_ship30:
                    system_prompt = SHIP30_SYSTEM_PROMPT
                    prompt_content = build_ship30_prompt(user_message, retrieved_sources)
                    messages_for_llm = [{"role": "user", "content": prompt_content}]
                elif is_conv:
                    system_prompt = (
                        f"{GENERAL_GROUNDING_SYSTEM_PROMPT}\n\n"
                        "CONVERSATIONAL TURN: The user is greeting you or chatting conversationally. "
                        "Respond warmly, naturally, and helpfully as 'The Lenny Growth Assistant'. "
                        "Introduce your capabilities (300+ episodes of Lenny's Podcast transcripts, product management, growth, Ship 30 essays, artifacts) "
                        "and invite them to ask their question."
                    )
                    messages_for_llm = history_context
                else:
                    if retrieved_sources:
                        context_str = "GROUNDED PODCAST TRANSCRIPTS:\n"
                        for idx, s in enumerate(retrieved_sources, 1):
                            context_str += (
                                f"\n--- [Source {idx}] ---\n"
                                f"Guest: {s.guest}\n"
                                f"Episode: {s.episode_title}\n"
                                f"Timestamp: {s.timestamp}\n"
                                f"Transcript Excerpt: {s.quote}\n"
                            )
                    else:
                        context_str = (
                            "NO_RELEVANT_TRANSCRIPTS_FOUND.\n"
                            "If the user is asking a broad question about product management, career growth, startups, or metrics, "
                            "answer helpfully based on standard industry product principles while noting that exact quotes were not found. "
                            "Only if the question is completely out-of-domain (e.g., cooking, politics, pop music), "
                            "politely state that your knowledge is focused on product management and growth from Lenny's podcast."
                        )

                    system_prompt = f"{GENERAL_GROUNDING_SYSTEM_PROMPT}\n\n{context_str}"
                    if wants_artifact:
                        system_prompt += (
                            "\n\nUSER REQUESTS AN ARTIFACT: Generate an interactive, highly formatted document or HTML/CSS widget "
                            "wrapped in :::artifact title=\"...\" type=\"html\" ... ::: blocks."
                        )
                    messages_for_llm = history_context

                # 5. Immediately send sources event so frontend shows grounded sources while streaming
                sources_payload = [s.model_dump() for s in retrieved_sources] if retrieved_sources else []
                yield f"event: sources\ndata: {json.dumps(sources_payload)}\n\n"

                # 6. Stream progressive LLM tokens
                full_tokens = []
                async for token in llm_manager.generate_stream_with_fallback(
                    messages=messages_for_llm,
                    system_prompt=system_prompt,
                    temperature=0.2,
                ):
                    full_tokens.append(token)
                    yield f"event: token\ndata: {json.dumps({'token': token})}\n\n"

                # 7. Extract Artifacts if generated
                raw_output = "".join(full_tokens)
                clean_text, artifact_data = artifact_service.extract_artifact(raw_output)
                persisted_artifact: Optional[ArtifactSummary] = None

                if artifact_data:
                    persisted_artifact = await artifact_service.create_and_persist_artifact(
                        session_id=session_id,
                        artifact_data=artifact_data,
                        db=session_db,
                    )
                    yield f"event: artifact\ndata: {json.dumps(persisted_artifact.model_dump())}\n\n"

                # 8. Persist assistant turn to DB
                assistant_record = MessageModel(
                    session_id=session_id,
                    role="assistant",
                    content=clean_text,
                    sources=sources_payload,
                    artifact_id=persisted_artifact.id if persisted_artifact else None,
                )
                session_db.add(assistant_record)
                session_obj.updated_at = datetime.now(timezone.utc)
                await session_db.commit()

                yield f"event: done\ndata: {json.dumps({'session_id': session_id, 'message_id': assistant_record.id, 'clean_content': clean_text})}\n\n"

            except Exception as e:
                logger.error(f"Error in streaming turn: {e}", exc_info=True)
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


agent_service = AgentService()
