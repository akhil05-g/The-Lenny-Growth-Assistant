import React, { useState } from 'react';
import { Sparkles, MessageSquare, Settings, Plus, Trash2, Clock } from 'lucide-react';

export default function Sidebar({ 
  sessions, 
  activeSessionId, 
  onSelectSession, 
  onNewChat, 
  onDeleteSession,
  onOpenSettings,
  activeTab,
  setActiveTab
}) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <aside className="relative flex items-center z-20 flex-shrink-0">
      {/* Slim vertical dock rail — compact to match Dribbble reference */}
      <div className="w-[52px] h-[85%] bg-white/90 backdrop-blur-2xl rounded-full border border-white/80 shadow-[0_8px_24px_rgba(0,0,0,0.04)] flex flex-col items-center justify-between py-4 my-auto ml-3">
        {/* Top Logo */}
        <button 
          onClick={onNewChat}
          className="w-9 h-9 rounded-full bg-gradient-to-tr from-rose-100 to-teal-50 border border-white flex items-center justify-center shadow-sm hover:scale-105 transition-transform"
          title="New Conversation"
        >
          <span className="font-bold text-sm bg-gradient-to-r from-rose-500 to-pink-600 bg-clip-text text-transparent">
            L
          </span>
        </button>

        {/* Middle Navigation Icons */}
        <div className="flex flex-col items-center gap-3">
          <button
            onClick={() => {
              setActiveTab('chat');
              setDrawerOpen(false);
            }}
            className={`w-9 h-9 rounded-full flex items-center justify-center transition-all ${
              activeTab === 'chat' && !drawerOpen
                ? 'bg-rose-50 text-rose-600 shadow-[0_2px_8px_rgba(244,63,94,0.15)] ring-2 ring-rose-200'
                : 'text-slate-400 hover:text-slate-700 hover:bg-slate-50'
            }`}
            title="Assistant Chat"
          >
            <Sparkles className="w-4 h-4" />
          </button>

          <button
            onClick={() => setDrawerOpen(!drawerOpen)}
            className={`relative w-9 h-9 rounded-full flex items-center justify-center transition-all ${
              drawerOpen
                ? 'bg-rose-50 text-rose-600 shadow-[0_2px_8px_rgba(244,63,94,0.15)] ring-2 ring-rose-200'
                : 'text-slate-400 hover:text-slate-700 hover:bg-slate-50'
            }`}
            title="Chat History"
          >
            <MessageSquare className="w-4 h-4" />
            {sessions.length > 0 && (
              <span className="absolute top-0.5 right-0.5 w-1.5 h-1.5 bg-rose-500 rounded-full" />
            )}
          </button>

          <button
            onClick={onOpenSettings}
            className="w-9 h-9 rounded-full flex items-center justify-center text-slate-400 hover:text-slate-700 hover:bg-slate-50 transition-all"
            title="System Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>

        {/* Bottom Action */}
        <button
          onClick={onNewChat}
          className="w-8 h-8 rounded-full flex items-center justify-center text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-all"
          title="New Chat Session"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>

      {/* Slide-out Session History Drawer */}
      {drawerOpen && (
        <div className="absolute left-[68px] top-4 bottom-4 w-64 bg-white/95 backdrop-blur-2xl rounded-2xl border border-white/90 shadow-[0_16px_36px_rgba(0,0,0,0.08)] p-3 flex flex-col z-30 animate-in fade-in slide-in-from-left-4 duration-200">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <h3 className="font-semibold text-xs text-slate-800 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-rose-500" />
              Past Conversations
            </h3>
            <button
              onClick={() => {
                onNewChat();
                setDrawerOpen(false);
              }}
              className="text-[10px] bg-rose-50 text-rose-600 px-2 py-0.5 rounded-full font-medium hover:bg-rose-100 transition-colors flex items-center gap-1"
            >
              <Plus className="w-3 h-3" /> New
            </button>
          </div>

          <div className="flex-1 overflow-y-auto mt-2 space-y-1 pr-1">
            {sessions.length === 0 ? (
              <div className="text-center py-8 text-[11px] text-slate-400">
                No past sessions yet. Start asking questions!
              </div>
            ) : (
              sessions.map((s) => (
                <div
                  key={s.id}
                  onClick={() => {
                    onSelectSession(s.id);
                    setDrawerOpen(false);
                  }}
                  className={`group flex items-center justify-between p-2 rounded-xl cursor-pointer text-[11px] transition-all ${
                    s.id === activeSessionId
                      ? 'bg-rose-50 text-rose-700 font-medium'
                      : 'hover:bg-slate-50 text-slate-600'
                  }`}
                >
                  <span className="truncate pr-2">{s.title || 'Untitled Session'}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteSession(s.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-600 p-0.5 rounded-lg hover:bg-white transition-opacity"
                    title="Delete session"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </aside>
  );
}
