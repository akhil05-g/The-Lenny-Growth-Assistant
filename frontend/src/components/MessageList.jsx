import React from 'react';
import { Sparkles, User, ExternalLink, Play, Layers, ChevronDown, ChevronUp, FileText } from 'lucide-react';

function parseArtifactFromMessage(msg) {
  let content = msg.content || '';
  let artifact = msg.artifact || null;

  if (content.includes(':::artifact')) {
    const artMatch = content.match(/:::artifact\s+title=["'](.*?)["'](?:\s+type=["'](markdown|html)["'])?\s*\n?([\s\S]*?)(?:\n?:::|$)/i);
    if (artMatch) {
      if (!artifact) {
        artifact = {
          title: artMatch[1].trim(),
          type: (artMatch[2] || 'html').toLowerCase(),
          content: artMatch[3].trim(),
        };
      }
      content = content.replace(artMatch[0], '').trim();
      if (!content) {
        content = `Here is the interactive ${artifact.title} generated from Lenny's podcast frameworks:`;
      }
    }
  }
  return { content, artifact };
}

export default function MessageList({ messages, isStreaming, currentStreamTokens, currentStreamSources, onOpenArtifact }) {
  const [expandedSources, setExpandedSources] = React.useState({});

  const toggleSourceExpand = (msgId, sourceIdx) => {
    const key = `${msgId}-${sourceIdx}`;
    setExpandedSources((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const streamingParsed = parseArtifactFromMessage({ content: currentStreamTokens });

  return (
    <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3.5 max-w-3xl w-full mx-auto">
      {messages.map((msg) => {
        const { content: displayContent, artifact: displayArtifact } = parseArtifactFromMessage(msg);

        return (
          <div
            key={msg.id}
            className={`flex gap-2.5 animate-in fade-in slide-in-from-bottom-2 duration-300 ${
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-rose-500 to-pink-500 flex-shrink-0 flex items-center justify-center text-white shadow-sm mt-0.5">
                <Sparkles className="w-3.5 h-3.5" />
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl p-3.5 ${
                msg.role === 'user'
                  ? 'bg-slate-900 text-white rounded-br-sm shadow-md'
                  : 'glass-card text-slate-800 rounded-tl-sm shadow-[0_4px_20px_rgba(0,0,0,0.03)]'
              }`}
            >
              {/* Attached Transcript Badge */}
              {msg.attachedFileName && (
                <div className="text-[11px] text-rose-300 font-medium flex items-center gap-1.5 mb-1.5 pb-1.5 border-b border-slate-700/60">
                  <FileText className="w-3.5 h-3.5 text-rose-400" />
                  <span>Loaded Transcript: {msg.attachedFileName}</span>
                </div>
              )}

              {/* Message Body */}
              <div className="text-sm leading-relaxed whitespace-pre-wrap font-normal">
                {displayContent}
              </div>

              {/* Artifact Pill if message contains an artifact */}
              {displayArtifact && (
                <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                    <span className="p-1.5 rounded-lg bg-rose-50 text-rose-600">
                      <Layers className="w-3.5 h-3.5" />
                    </span>
                    <span>{displayArtifact.title || 'Interactive Artifact'}</span>
                  </div>
                  <button
                    onClick={() => onOpenArtifact(displayArtifact)}
                    className="text-xs bg-rose-500 hover:bg-rose-600 text-white px-3 py-1 rounded-full font-medium transition-colors shadow-sm"
                  >
                    Open Preview
                  </button>
                </div>
              )}

              {/* Grounded Citations Section */}
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-4 pt-3 border-t border-slate-100/80">
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <span>Verified Podcast Citations</span>
                    <span className="bg-rose-100 text-rose-700 text-[10px] font-bold px-1.5 py-0.2 rounded-full">
                      {msg.sources.length}
                    </span>
                  </div>

                  <div className="space-y-1.5">
                    {msg.sources.map((s, idx) => {
                      const isExpanded = expandedSources[`${msg.id}-${idx}`];
                      return (
                        <div
                          key={idx}
                          className="bg-white/90 border border-slate-100 rounded-xl p-2 text-xs transition-all"
                        >
                          <div
                            className="flex items-center justify-between cursor-pointer"
                            onClick={() => toggleSourceExpand(msg.id, idx)}
                          >
                            <div className="flex items-center gap-2 font-medium text-slate-800 truncate pr-2">
                              <span className="w-1.5 h-1.5 rounded-full bg-rose-500 flex-shrink-0" />
                              <span className="font-semibold">{s.guest}</span>
                              <span className="text-slate-400 truncate text-[11px]">"{s.episode_title}"</span>
                            </div>
                            <div className="flex items-center gap-1 text-slate-400 flex-shrink-0 text-[11px]">
                              <span className="bg-slate-50 px-1.5 py-0.5 rounded text-slate-600 font-mono">
                                {s.timestamp || '(00:00:00)'}
                              </span>
                              {s.youtube_url && (
                                <a
                                  href={s.youtube_url}
                                  target="_blank"
                                  rel="noreferrer"
                                  onClick={(e) => e.stopPropagation()}
                                  className="text-rose-500 hover:text-rose-700 p-0.5"
                                  title="Listen on YouTube at exact timestamp"
                                >
                                  <Play className="w-3 h-3 fill-rose-500" />
                                </a>
                              )}
                              {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                            </div>
                          </div>

                          {isExpanded && (
                            <div className="mt-2 pt-2 border-t border-slate-50 text-slate-600 text-[11px] leading-relaxed italic bg-slate-50/50 p-2 rounded-lg">
                              "{s.quote}"
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-slate-200 flex-shrink-0 flex items-center justify-center text-slate-600 mt-0.5">
                <User className="w-3.5 h-3.5" />
              </div>
            )}
          </div>
        );
      })}

      {/* Real-time Streaming Turn */}
      {isStreaming && (
        <div className="flex gap-2.5 animate-in fade-in duration-200 justify-start">
          <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-rose-500 to-pink-500 flex-shrink-0 flex items-center justify-center text-white shadow-sm mt-0.5 animate-pulse">
            <Sparkles className="w-3.5 h-3.5" />
          </div>

          <div className="max-w-[85%] glass-card text-slate-800 rounded-2xl rounded-tl-sm p-3.5 shadow-[0_4px_20px_rgba(0,0,0,0.03)]">
            {/* Streaming Sources if arrived first */}
            {currentStreamSources && currentStreamSources.length > 0 && (
              <div className="mb-3 pb-2 border-b border-slate-100 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs font-semibold text-slate-700">
                  Found {currentStreamSources.length} verified transcript excerpts
                </span>
              </div>
            )}

            <div className="text-sm leading-relaxed whitespace-pre-wrap font-normal">
              {streamingParsed.content || (
                <span className="text-slate-400 italic flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-rose-400 rounded-full animate-bounce" />
                  <span className="w-1.5 h-1.5 bg-rose-400 rounded-full animate-bounce [animation-delay:0.2s]" />
                  <span className="w-1.5 h-1.5 bg-rose-400 rounded-full animate-bounce [animation-delay:0.4s]" />
                  Synthesizing grounded answer from Lenny's podcast...
                </span>
              )}
            </div>

            {/* If streaming artifact parsed, show interactive open button */}
            {streamingParsed.artifact && (
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
                  <span className="p-1.5 rounded-lg bg-rose-50 text-rose-600">
                    <Layers className="w-3.5 h-3.5" />
                  </span>
                  <span>{streamingParsed.artifact.title || 'Interactive Artifact'}</span>
                </div>
                <button
                  onClick={() => onOpenArtifact(streamingParsed.artifact)}
                  className="text-xs bg-rose-500 hover:bg-rose-600 text-white px-3 py-1 rounded-full font-medium transition-colors shadow-sm"
                >
                  Open Preview
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
