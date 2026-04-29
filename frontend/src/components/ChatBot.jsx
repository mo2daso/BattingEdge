import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Loader2, RotateCcw, Bot } from 'lucide-react';
import api from '../utils/api';

const QUICK_QUESTIONS = [
  'How do I improve my cover drive?',
  'Tips for playing spin bowling',
  'What is a pull shot and how to play it?',
  'Best drills for batting footwork',
  'What does my grade mean on BattingEdge?',
  'How should I film for best results?',
];

const WELCOME = {
  role: 'assistant',
  content: "Hey! I'm BESSA 🏏 — BattingEdge's Smart Sports Assistant. Ask me anything about cricket techniques, batting tips, shot advice, or how to get the most out of BattingEdge. Ready to level up your game?",
};

const BessaIcon = ({ size = 22 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="10" fill="#00d4ff" />
    <circle cx="12" cy="12" r="10" stroke="#0099bb" strokeWidth="0.5"/>
    {/* cricket bat shape */}
    <path d="M8 16 L14 8 L16 10 L10 18 Z" fill="rgba(0,0,0,0.6)" />
    <circle cx="8.5" cy="15.5" r="2" fill="rgba(0,0,0,0.4)" />
    <path d="M14 8 L16 10" stroke="white" strokeWidth="1" strokeLinecap="round"/>
  </svg>
);

const TypingIndicator = () => (
  <div className="flex items-end gap-2 mb-3">
    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-neon-blue to-blue-700 flex items-center justify-center flex-shrink-0 border border-neon-blue/30">
      <span className="text-[10px] font-bold text-black">BE</span>
    </div>
    <div className="px-4 py-3 rounded-2xl rounded-bl-sm border border-border-dim" style={{ background: 'var(--surface-2)' }}>
      <div className="flex gap-1.5">
        {[0,1,2].map(i => (
          <div key={i} className="typing-dot w-1.5 h-1.5 rounded-full bg-neon-blue" />
        ))}
      </div>
    </div>
  </div>
);

const ChatBot = () => {
  const [open,     setOpen]     = useState(false);
  const [messages, setMessages] = useState([WELCOME]);
  const [input,    setInput]    = useState('');
  const [loading,  setLoading]  = useState(false);
  const bottomRef  = useRef(null);
  const inputRef   = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 200);
  }, [open]);

  const sendMessage = async (text) => {
    const msg = text || input.trim();
    if (!msg || loading) return;
    setInput('');

    const userMsg = { role: 'user', content: msg };
    const history  = [...messages, userMsg];
    setMessages(history);
    setLoading(true);

    try {
      const { data } = await api.post('/api/chat', {
        messages: history.filter(m => m.role !== 'system').slice(-10),
      });
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: "Sorry, I'm having a quick timeout 😅 Try again in a moment!" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => setMessages([WELCOME]);

  return (
    <>
      {/* Floating button */}
      <div className="fixed bottom-6 right-6 z-50">
        <AnimatePresence mode="wait">
          {!open && (
            <motion.button
              key="btn"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              onClick={() => setOpen(true)}
              className="relative w-14 h-14 rounded-full shadow-lg hover:shadow-neon hover:scale-110 transition-transform flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #00d4ff, #0066aa)' }}
              aria-label="Open BESSA cricket assistant"
            >
              <span className="ping-ring absolute inset-0 rounded-full bg-neon-blue opacity-30" />
              <span className="font-display font-black text-black text-xs">BESSA</span>
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-neon-green rounded-full border-2 border-black" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>

      {/* Chat window */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 40, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 40, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            className="fixed bottom-6 right-6 z-50 w-[360px] max-w-[calc(100vw-24px)] flex flex-col"
            style={{ height: '520px' }}
          >
            <div className="flex flex-col h-full rounded-2xl overflow-hidden shadow-2xl border border-neon-blue/20"
                 style={{ background: 'var(--surface)' }}>

              {/* Header */}
              <div className="flex items-center gap-3 px-4 py-3.5 border-b border-border-dim"
                   style={{ background: 'linear-gradient(90deg, rgba(0,212,255,0.12), var(--surface-2))' }}>
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-neon-blue to-blue-700 flex items-center justify-center flex-shrink-0 border border-neon-blue/30">
                  <span className="font-display font-black text-black text-[9px] leading-none">BESSA</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-display font-bold text-sm text-neon-blue">BESSA</p>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
                    <span className="text-[11px]" style={{ color: 'var(--text-dim)' }}>BattingEdge Sports Assistant</span>
                  </div>
                </div>
                <button onClick={reset} className="p-1.5 rounded-lg hover:bg-white/5 transition-colors" style={{ color: 'var(--text-dim)' }} title="Reset chat">
                  <RotateCcw size={14} />
                </button>
                <button onClick={() => setOpen(false)} className="p-1.5 rounded-lg hover:bg-white/5 transition-colors" style={{ color: 'var(--text-dim)' }}>
                  <X size={16} />
                </button>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-1 scroll-smooth">
                {messages.map((m, i) => (
                  <div
                    key={i}
                    className={`flex items-end gap-2 mb-3 chat-bubble-in ${m.role === 'user' ? 'flex-row-reverse' : ''}`}
                  >
                    {m.role === 'assistant' && (
                      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-neon-blue to-blue-700 flex items-center justify-center flex-shrink-0 border border-neon-blue/30">
                        <span className="text-black text-[8px] font-black">BE</span>
                      </div>
                    )}
                    <div
                      className={`max-w-[82%] px-3.5 py-2.5 text-xs leading-relaxed rounded-2xl ${
                        m.role === 'user'
                          ? 'bg-neon-blue text-black font-medium rounded-br-sm'
                          : 'border border-border-dim rounded-bl-sm'
                      }`}
                      style={m.role !== 'user' ? { color: 'var(--text)', background: 'var(--surface-2)' } : {}}
                    >
                      {m.content}
                    </div>
                  </div>
                ))}
                {loading && <TypingIndicator />}

                {/* Quick questions — only when just welcome msg */}
                {messages.length === 1 && !loading && (
                  <div className="mt-2 space-y-1.5">
                    <p className="text-[10px] uppercase tracking-wider px-1" style={{ color: 'var(--text-dim)' }}>Quick questions</p>
                    {QUICK_QUESTIONS.map((q, i) => (
                      <button
                        key={i}
                        onClick={() => sendMessage(q)}
                        className="w-full text-left px-3 py-2 rounded-xl text-xs border border-border-dim hover:border-neon-blue/40 hover:bg-neon-blue/5 transition-all"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                )}
                <div ref={bottomRef} />
              </div>

              {/* Input */}
              <div className="p-3 border-t border-border-dim">
                <form
                  onSubmit={(e) => { e.preventDefault(); sendMessage(); }}
                  className="flex items-center gap-2 px-3 py-2 rounded-xl border border-border-dim focus-within:border-neon-blue/40 transition-colors"
                  style={{ background: 'var(--surface-2)' }}
                >
                  <input
                    ref={inputRef}
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder="Ask BESSA about cricket…"
                    className="flex-1 bg-transparent text-xs outline-none"
                    style={{ color: 'var(--text)' }}
                    disabled={loading}
                  />
                  <button
                    type="submit"
                    disabled={!input.trim() || loading}
                    className="w-7 h-7 rounded-lg flex items-center justify-center transition-all disabled:opacity-30 bg-neon-blue hover:bg-[#33deff] text-black"
                  >
                    {loading ? <Loader2 size={12} className="animate-spin" /> : <Send size={12} />}
                  </button>
                </form>
                <p className="text-[10px] text-center mt-1.5" style={{ color: 'var(--text-dim)' }}>Cricket only · Powered by Groq AI</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatBot;
