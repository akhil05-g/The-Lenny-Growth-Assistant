import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import HeroOrb from './components/HeroOrb';
import ChatInput from './components/ChatInput';
import MessageList from './components/MessageList';
import ArtifactViewer from './components/ArtifactViewer';
import ModelSelector from './components/ModelSelector';
import SettingsModal from './components/SettingsModal';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [activeArtifact, setActiveArtifact] = useState(null);
  const [activeModel, setActiveModel] = useState('ollama');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamTokens, setCurrentStreamTokens] = useState('');
  const [currentStreamSources, setCurrentStreamSources] = useState([]);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');

  // Load initial sessions
  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const res = await fetch('/api/sessions');
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (e) {
      console.warn('Failed to load sessions:', e);
    }
  };

  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setActiveArtifact(null);
    setCurrentStreamTokens('');
    setCurrentStreamSources([]);
  };

  const handleSelectSession = async (sessionId) => {
    try {
      setActiveSessionId(sessionId);
      const res = await fetch(`/api/sessions/${sessionId}`);
      if (res.ok) {
        const data = await res.json();
        setMessages(data.messages || []);
        if (data.artifacts && data.artifacts.length > 0) {
          setActiveArtifact(data.artifacts[0]);
        } else {
          setActiveArtifact(null);
        }
      }
    } catch (e) {
      console.error('Failed to load session details:', e);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    try {
      await fetch(`/api/sessions/${sessionId}`, { method: 'DELETE' });
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      if (activeSessionId === sessionId) {
        handleNewChat();
      }
    } catch (e) {
      console.error('Failed to delete session:', e);
    }
  };

  const handleSendMessage = async (userText, attachedFileName = null) => {
    if (!userText.trim() || isStreaming) return;

    // Display text in user bubble: show clean question if attached file was prepended
    let displayContent = userText;
    if (attachedFileName && userText.includes('---')) {
      const parts = userText.split('---');
      displayContent = parts[parts.length - 1].replace('Question:', '').trim();
    }

    // Optimistically add user message
    const tempUserMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: displayContent,
      attachedFileName: attachedFileName,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsStreaming(true);
    setCurrentStreamTokens('');
    setCurrentStreamSources([]);

    try {
      const isShip30 = userText.toLowerCase().includes('ship 30') || userText.toLowerCase().includes('ship30') || userText.toLowerCase().includes('essay');
      const streamEndpoint = isShip30 ? '/api/skills/ship30/stream' : '/api/chat/stream';
      const payload = isShip30
        ? { topic: userText }
        : { message: userText, session_id: activeSessionId };

      const response = await fetch(streamEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let accumulatedText = '';
      let incomingSources = [];
      let incomingArtifact = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        let currentEvent = 'message';
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.replace('event: ', '').trim();
          } else if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (dataStr === '[DONE]') continue;

            try {
              const parsed = JSON.parse(dataStr);
              if (currentEvent === 'sources') {
                incomingSources = parsed;
                setCurrentStreamSources(parsed);
              } else if (currentEvent === 'token') {
                accumulatedText += parsed.token || '';
                setCurrentStreamTokens(accumulatedText);
              } else if (currentEvent === 'artifact') {
                incomingArtifact = parsed;
                setActiveArtifact(parsed);
              } else if (currentEvent === 'done') {
                if (parsed.session_id && !activeSessionId) {
                  setActiveSessionId(parsed.session_id);
                }
                if (parsed.clean_content) {
                  accumulatedText = parsed.clean_content;
                }
                fetchSessions();
              }
            } catch (err) {
              // Plain string token fallback
              if (currentEvent === 'token') {
                accumulatedText += dataStr;
                setCurrentStreamTokens(accumulatedText);
              }
            }
          }
        }
      }

      // Client-side fallback: If text contains raw :::artifact blocks, extract it
      if (!incomingArtifact && accumulatedText.includes(':::artifact')) {
        const artMatch = accumulatedText.match(/:::artifact\s+title=["'](.*?)["'](?:\s+type=["'](markdown|html)["'])?\s*\n?([\s\S]*?)(?:\n?:::|$)/i);
        if (artMatch) {
          const title = artMatch[1].trim();
          const type = (artMatch[2] || 'html').toLowerCase();
          const content = artMatch[3].trim();
          incomingArtifact = { title, type, content };
          setActiveArtifact(incomingArtifact);
          accumulatedText = accumulatedText.replace(artMatch[0], '').trim() || `Here is the interactive ${title} generated from Lenny's podcast frameworks:`;
        }
      }

      // Finalize assistant turn into permanent state
      const finalAssistantMsg = {
        id: `asst-${Date.now()}`,
        role: 'assistant',
        content: accumulatedText,
        sources: incomingSources,
        artifact: incomingArtifact,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, finalAssistantMsg]);
    } catch (e) {
      console.error('Streaming turn error:', e);
      // Fallback message
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: 'assistant',
          content: 'Sorry, there was an issue processing your request. Please check if the backend service is online.',
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsStreaming(false);
      setCurrentStreamTokens('');
      setCurrentStreamSources([]);
    }
  };

  return (
    <div className="w-screen h-screen app-mesh-bg flex items-center justify-center p-4 overflow-hidden select-none">
      {/* Outer Glass Container — fitted to viewport like the Dribbble reference */}
      <div className="w-full h-full max-w-[1200px] max-h-[800px] glass-card rounded-3xl flex overflow-hidden relative shadow-[0_16px_48px_rgba(0,0,0,0.06)] border border-white/90">
        
        {/* Left Navigation Dock Rail */}
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onNewChat={handleNewChat}
          onDeleteSession={handleDeleteSession}
          onOpenSettings={() => setSettingsOpen(true)}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />

        {/* Central Chat & Interaction Canvas */}
        <main className="flex-1 flex flex-col h-full relative overflow-hidden">
          
          {/* Top Header Bar */}
          <header className="w-full px-6 py-3 flex items-center justify-between z-10 flex-shrink-0">
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm tracking-tight text-slate-900">
                The Lenny Growth Assistant
              </span>
              <span className="text-[9px] font-bold text-slate-500 bg-white/80 border border-slate-200/80 px-2 py-0.5 rounded-full shadow-2xs">
                303 Episodes Grounded
              </span>
            </div>

            {/* Right Side: Model Selector */}
            <ModelSelector
              activeModel={activeModel}
              onSelectModel={(id) => setActiveModel(id)}
            />
          </header>

          {/* Main Body: Hero when empty, MessageList when active */}
          <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
            {messages.length === 0 ? (
              <HeroOrb />
            ) : (
              <MessageList
                messages={messages}
                isStreaming={isStreaming}
                currentStreamTokens={currentStreamTokens}
                currentStreamSources={currentStreamSources}
                onOpenArtifact={(art) => setActiveArtifact(art)}
              />
            )}
          </div>

          {/* Floating Input Bar at Bottom */}
          <div className="w-full flex-shrink-0 z-10">
            <ChatInput
              onSendMessage={handleSendMessage}
              isStreaming={isStreaming}
            />
          </div>
        </main>

        {/* Right-Hand Sliding Artifact Viewer */}
        {activeArtifact && (
          <ArtifactViewer
            artifact={activeArtifact}
            onClose={() => setActiveArtifact(null)}
          />
        )}
      </div>

      {/* System Diagnostics & Observability Modal */}
      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        activeModel={activeModel}
        onSelectModel={(id) => setActiveModel(id)}
      />
    </div>
  );
}
