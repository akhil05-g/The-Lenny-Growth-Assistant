import React, { useState } from 'react';
import { X, Copy, Check, Eye, Code, ExternalLink, ShieldCheck } from 'lucide-react';

export default function ArtifactViewer({ artifact, onClose }) {
  const [viewMode, setViewMode] = useState('preview'); // 'preview' | 'code'
  const [copied, setCopied] = useState(false);

  if (!artifact) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-[380px] lg:w-[440px] h-full bg-white/95 backdrop-blur-2xl border-l border-white/80 shadow-[-10px_0_30px_rgba(0,0,0,0.04)] flex flex-col z-30 animate-in slide-in-from-right-8 duration-300 flex-shrink-0">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-sm text-slate-800 truncate max-w-[240px]">
              {artifact.title || 'Interactive Artifact'}
            </h3>
            <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-rose-50 text-rose-600 border border-rose-100">
              {artifact.type || 'html'}
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-emerald-500" />
            Isolated Sandboxed Execution
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-1.5">
          {/* Preview / Code Toggle */}
          <div className="flex items-center bg-slate-100 p-1 rounded-xl text-xs font-medium">
            <button
              onClick={() => setViewMode('preview')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg transition-all ${
                viewMode === 'preview' ? 'bg-white shadow-sm text-slate-800 font-semibold' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <Eye className="w-3 h-3" />
              <span>Preview</span>
            </button>
            <button
              onClick={() => setViewMode('code')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg transition-all ${
                viewMode === 'code' ? 'bg-white shadow-sm text-slate-800 font-semibold' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              <Code className="w-3 h-3" />
              <span>Code</span>
            </button>
          </div>

          <button
            onClick={handleCopy}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
            title="Copy Source Code"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <Copy className="w-4 h-4" />}
          </button>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors"
            title="Close Viewer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden p-4">
        {viewMode === 'preview' ? (
          <div className="w-full h-full rounded-2xl overflow-hidden border border-slate-100 bg-white shadow-inner">
            {artifact.type === 'html' ? (
              <iframe
                title={artifact.title}
                srcDoc={`<!DOCTYPE html><html><head><meta charset="utf-8"><style>body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;}</style></head><body>${artifact.content}</body></html>`}
                sandbox="allow-scripts"
                className="w-full h-full border-0"
              />
            ) : (
              <div className="p-4 text-sm text-slate-700 whitespace-pre-wrap overflow-y-auto h-full font-mono text-xs">
                {artifact.content}
              </div>
            )}
          </div>
        ) : (
          <div className="w-full h-full rounded-2xl bg-slate-900 text-slate-200 p-4 overflow-auto font-mono text-xs leading-relaxed shadow-inner">
            <pre className="whitespace-pre-wrap">{artifact.content}</pre>
          </div>
        )}
      </div>
    </div>
  );
}
