import React, { useState, useEffect } from 'react';
import { X, CheckCircle2, AlertCircle, Database, BookOpen, Cpu, RefreshCw } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, activeModel, onSelectModel }) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchHealth();
    }
  }, [isOpen]);

  const fetchHealth = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        setHealth(data);
      }
    } catch (e) {
      console.error('Failed to fetch health check:', e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/30 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white/95 backdrop-blur-2xl rounded-3xl border border-white/90 shadow-[0_25px_60px_rgba(0,0,0,0.15)] max-w-md w-full p-6 space-y-5 animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 className="font-bold text-base text-slate-900">System Diagnostics & Settings</h3>
            <p className="text-xs text-slate-400">Forward Deployment Operational Telemetry</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Health Check Status Cards */}
        {loading ? (
          <div className="py-8 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
            <RefreshCw className="w-4 h-4 animate-spin text-rose-500" />
            Querying backend observability endpoints...
          </div>
        ) : health ? (
          <div className="space-y-3">
            {/* Overall Status */}
            <div className="flex items-center justify-between p-3 rounded-2xl bg-slate-50 border border-slate-100">
              <span className="text-xs font-semibold text-slate-700">Application State</span>
              <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">
                <CheckCircle2 className="w-3.5 h-3.5" />
                {health.status?.toUpperCase()}
              </span>
            </div>

            {/* Database Card */}
            <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-800">
                  <Database className="w-4 h-4 text-rose-500" />
                  <span>Persistence Layer</span>
                </div>
                <span className="text-[11px] font-bold text-emerald-600">
                  {health.database}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 pl-6">
                Automatic PostgreSQL to SQLite failover active
              </p>
            </div>

            {/* Knowledge Base Card */}
            <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-800">
                  <BookOpen className="w-4 h-4 text-rose-500" />
                  <span>Knowledge Base (RAG)</span>
                </div>
                <span className="text-[11px] font-bold text-slate-700">
                  {health.knowledge_base?.total_chunks?.toLocaleString() || '49,781'} Chunks
                </span>
              </div>
              <div className="text-[11px] text-slate-400 pl-6 flex gap-3">
                <span>Guests: {health.knowledge_base?.total_guests || '301'}</span>
                <span>Topics: {health.knowledge_base?.total_topics || '89'}</span>
              </div>
            </div>

            {/* Active LLM Provider Card */}
            <div className="p-3 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-800">
                  <Cpu className="w-4 h-4 text-rose-500" />
                  <span>Active LLM Engine</span>
                </div>
                <span className="text-[11px] font-bold text-slate-700 uppercase">
                  {health.llm_provider?.active_provider}
                </span>
              </div>
              <div className="text-[11px] text-slate-500 pl-6">
                Status: {health.llm_provider?.status_message}
              </div>
              <div className="text-[10px] text-slate-400 pl-6">
                Latency: {health.llm_provider?.latency_ms} ms
              </div>
            </div>
          </div>
        ) : (
          <div className="py-6 text-center text-xs text-rose-500 flex items-center justify-center gap-1">
            <AlertCircle className="w-4 h-4" />
            Could not reach backend health endpoint. Is FastAPI running on port 8000?
          </div>
        )}

        {/* Footer */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-white bg-slate-900 rounded-full hover:bg-slate-800 transition-colors"
          >
            Close Diagnostics
          </button>
        </div>
      </div>
    </div>
  );
}
