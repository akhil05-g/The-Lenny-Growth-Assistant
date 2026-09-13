import React, { useState, useRef } from 'react';
import { Paperclip, Lightbulb, Mic, Send, X, FileText } from 'lucide-react';

export default function ChatInput({ onSendMessage, isStreaming }) {
  const [input, setInput] = useState('');
  const [deepThink, setDeepThink] = useState(true);
  const [attachedTranscript, setAttachedTranscript] = useState(null);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleAttachClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result;
      setAttachedTranscript({
        name: file.name,
        size: `${(file.size / 1024).toFixed(1)} KB`,
        content: content,
      });
    };
    reader.readAsText(file);
  };

  const handleRemoveAttachment = () => {
    setAttachedTranscript(null);
  };

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;

    let fullMessage = trimmed;
    if (attachedTranscript) {
      fullMessage = `[Attached Transcript File: ${attachedTranscript.name}]\n${attachedTranscript.content}\n\n---\nQuestion: ${trimmed}`;
    }

    onSendMessage(fullMessage, attachedTranscript ? attachedTranscript.name : null);
    setInput('');
    setAttachedTranscript(null);
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-4 pb-3">
      {/* Hidden file input for loading transcripts */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.md,.json,.csv"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Floating Rainbow Bordered Input Box */}
      <div className="rainbow-input-container transition-all focus-within:shadow-[0_12px_28px_-6px_rgba(244,63,94,0.18)]">
        <div className="rainbow-input-inner p-2.5 flex flex-col justify-between min-h-[82px]">
          {/* Loaded transcript file indicator badge */}
          {attachedTranscript && (
            <div className="mb-1.5 flex items-center justify-between bg-rose-50/90 border border-rose-200/80 rounded-xl px-2.5 py-1 text-xs">
              <div className="flex items-center gap-1.5 text-rose-700 font-medium truncate pr-2">
                <FileText className="w-3.5 h-3.5 flex-shrink-0 text-rose-500" />
                <span className="truncate">{attachedTranscript.name}</span>
                <span className="text-[10px] text-rose-400 font-normal">({attachedTranscript.size})</span>
              </div>
              <button
                type="button"
                onClick={handleRemoveAttachment}
                className="text-rose-400 hover:text-rose-600 p-0.5 rounded-lg hover:bg-rose-100/60 transition-colors"
                title="Remove transcript file"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          )}

          {/* Textarea */}
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={attachedTranscript ? "Ask any question about this loaded file..." : "Ask anything about product strategy, growth loops, or Lenny's guests..."}
            disabled={isStreaming}
            className="w-full bg-transparent border-0 resize-none outline-none text-xs md:text-sm text-slate-800 placeholder-slate-400 focus:ring-0 leading-relaxed px-1"
          />

          {/* Bottom Action Bar matching screenshot */}
          <div className="flex items-center justify-between pt-1.5 border-t border-slate-100/60 mt-1">
            {/* Left Action Pills */}
            <div className="flex items-center gap-2">
              <button 
                type="button"
                onClick={handleAttachClick}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium transition-colors ${
                  attachedTranscript 
                    ? 'bg-rose-100 text-rose-700 border border-rose-200' 
                    : 'bg-slate-100/80 text-slate-600 hover:bg-slate-200/70'
                }`}
                title="Load Transcript File (.txt, .md, .json)"
              >
                <Paperclip className="w-3 h-3 text-slate-500" />
                <span>{attachedTranscript ? 'Loaded' : 'Attach'}</span>
              </button>

              <button
                type="button"
                onClick={() => setDeepThink(!deepThink)}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium transition-all ${
                  deepThink
                    ? 'bg-rose-50 text-rose-600 border border-rose-200'
                    : 'bg-slate-100/80 text-slate-600 hover:bg-slate-200/70'
                }`}
                title="Strict Transcript Grounding & RAG Retrieval"
              >
                <Lightbulb className="w-3 h-3" />
                <span>Deep Think</span>
              </button>
            </div>

            {/* Right Action Pills */}
            <div className="flex items-center gap-2">
              <button 
                type="button"
                className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium text-slate-600 bg-slate-100/80 hover:bg-slate-200/70 transition-colors"
                title="Voice Input (Speech-to-Text)"
              >
                <Mic className="w-3 h-3 text-slate-500" />
                <span>Voice</span>
              </button>

              <button
                type="button"
                onClick={handleSubmit}
                disabled={!input.trim() || isStreaming}
                className={`flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-semibold text-white transition-all shadow-sm ${
                  !input.trim() || isStreaming
                    ? 'bg-slate-300 cursor-not-allowed opacity-60'
                    : 'bg-gradient-to-r from-rose-500 via-pink-500 to-rose-600 hover:opacity-95 hover:shadow-[0_4px_12px_rgba(244,63,94,0.35)] active:scale-95'
                }`}
              >
                <Send className="w-3 h-3" />
                <span>Send</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
