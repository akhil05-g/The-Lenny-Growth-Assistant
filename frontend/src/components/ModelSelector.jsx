import React, { useState, useEffect } from 'react';
import { Cpu, ChevronDown, Check, Zap, Sparkles } from 'lucide-react';

export default function ModelSelector({ activeModel, onSelectModel }) {
  const [open, setOpen] = useState(false);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/models');
      if (res.ok) {
        const data = await res.json();
        setModels(data);
      }
    } catch (e) {
      console.warn('Failed to fetch model telemetry:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (modelId) => {
    try {
      const res = await fetch('/api/models/switch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: modelId }),
      });
      if (res.ok) {
        onSelectModel(modelId);
      }
    } catch (e) {
      console.error('Failed to switch model:', e);
    } finally {
      setOpen(false);
    }
  };

  const currentDisplayName = () => {
    if (activeModel === 'ollama') return 'Ollama (Llama 3.2)';
    if (activeModel === 'claude' || activeModel === 'anthropic') return 'Claude Sonnet 4.6';
    if (activeModel === 'openai') return 'OpenAI (GPT-4o)';
    if (activeModel === 'resilient_local') return 'Resilient Local (Failsafe)';
    return activeModel || 'Ollama (Local)';
  };

  return (
    <div className="relative">
      {/* Pill button matching the "+ Connect Wallet" style in top-right of the screenshot */}
      <button
        onClick={() => setOpen(!open)}
        className="glass-pill flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold text-slate-800 transition-all active:scale-95"
      >
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        <span className="text-slate-500 font-normal">+</span>
        <span>{currentDisplayName()}</span>
        <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 mt-2 w-72 bg-white/95 backdrop-blur-2xl rounded-2xl border border-white/90 shadow-[0_20px_40px_rgba(0,0,0,0.12)] p-2 z-50 animate-in fade-in zoom-in-95 duration-150">
            <div className="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100">
              Active LLM Inference Engine
            </div>

            <div className="space-y-1 mt-1">
              {[
                { id: 'ollama', name: 'Ollama (Llama 3.2:latest)', tag: 'Local GPU/CPU • Free', icon: Cpu },
                { id: 'anthropic', name: 'Claude (claude-sonnet-4-6)', tag: 'Anthropic SDK • Cloud', icon: Sparkles },
                { id: 'openai', name: 'OpenAI (gpt-4o)', tag: 'Cloud API', icon: Zap },
                { id: 'resilient_local', name: 'Resilient Local Fallback', tag: 'Deterministic • Always On', icon: Cpu },
              ].map((m) => {
                const Icon = m.icon;
                const isSelected = activeModel === m.id || (m.id === 'anthropic' && activeModel === 'claude');
                return (
                  <button
                    key={m.id}
                    onClick={() => handleSelect(m.id)}
                    className={`w-full flex items-center justify-between p-2.5 rounded-xl text-left transition-all ${
                      isSelected ? 'bg-rose-50/80 text-rose-700 font-medium' : 'hover:bg-slate-50 text-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <div className={`p-1.5 rounded-lg ${isSelected ? 'bg-rose-100 text-rose-600' : 'bg-slate-100 text-slate-500'}`}>
                        <Icon className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <div className="text-xs font-semibold leading-tight">{m.name}</div>
                        <div className="text-[10px] text-slate-400">{m.tag}</div>
                      </div>
                    </div>
                    {isSelected && <Check className="w-4 h-4 text-rose-600" />}
                  </button>
                );
              })}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
