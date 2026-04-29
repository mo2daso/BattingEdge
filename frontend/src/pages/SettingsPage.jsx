import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings, Sun, Moon, Bell,
  CheckCircle2, User, Lock, LogOut, HelpCircle, Mail,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import toast from 'react-hot-toast';

// ── Avatar options ────────────────────────────────────────────────────────────
const AVATAR_COLORS = [
  ['#00d4ff','#0099bb'],
  ['#00ff88','#00bb66'],
  ['#f59e0b','#d97706'],
  ['#8b5cf6','#7c3aed'],
  ['#ef4444','#dc2626'],
  ['#06b6d4','#0891b2'],
];

const AVATARS = ['🏏', '🪃', '🏆', '🎯', '⚡', '💫', '🛡️', '🌟'];

// ── Helpers ───────────────────────────────────────────────────────────────────
const SectionCard = ({ icon: Icon, title, children, delay = 0 }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}
    className="rounded-2xl border border-border-dim overflow-hidden"
    style={{ background: 'var(--surface-2)' }}
  >
    <div className="flex items-center gap-3 px-6 py-4 border-b border-border-dim">
      <Icon size={17} className="text-neon-blue" />
      <h2 className="font-display font-bold text-sm" style={{ color: 'var(--text)' }}>{title}</h2>
    </div>
    <div className="p-6">{children}</div>
  </motion.div>
);

// ── Main ──────────────────────────────────────────────────────────────────────

const SettingsPage = ({ onOpenAuth }) => {
  const { theme, toggleTheme }  = useTheme();
  const { user, logout }        = useAuth();

  const [subEmail,   setSubEmail]   = useState(user?.email || '');
  const [subName,    setSubName]    = useState(user?.full_name || '');
  const [subLoading, setSubLoading] = useState(false);
  const [subDone,    setSubDone]    = useState(false);
  const [avatarPick, setAvatarPick] = useState(() => parseInt(localStorage.getItem('be_avatar') || '0'));
  const [colorPick,  setColorPick]  = useState(() => parseInt(localStorage.getItem('be_avatar_color') || '0'));

  const saveAvatar = (idx, colorIdx) => {
    localStorage.setItem('be_avatar', String(idx));
    localStorage.setItem('be_avatar_color', String(colorIdx ?? colorPick));
    setAvatarPick(idx);
    if (colorIdx !== undefined) setColorPick(colorIdx);
    toast.success('Avatar saved!');
  };

  const handleSubscribe = async () => {
    if (!subEmail || !subEmail.includes('@')) { toast.error('Enter a valid email'); return; }
    setSubLoading(true);
    try {
      await api.post('/api/subscribe', { email: subEmail, name: subName || 'Cricket Fan' });
      setSubDone(true);
      toast.success('Subscribed to cricket tips!');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Subscription failed');
    } finally {
      setSubLoading(false);
    }
  };

  const handleUnsubscribe = async () => {
    if (!subEmail) return;
    try {
      await api.delete('/api/unsubscribe', { data: { email: subEmail } });
      setSubDone(false);
      toast.success('Unsubscribed successfully');
    } catch {
      toast.error('Could not unsubscribe');
    }
  };

  return (
    <div className="min-h-screen pb-20" style={{ background: 'var(--bg)' }}>
      <Navbar onOpenAuth={onOpenAuth} />

      <main className="max-w-3xl mx-auto px-4 pt-28">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-9 h-9 rounded-xl bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center">
              <Settings size={17} className="text-neon-blue" />
            </div>
            <span className="text-xs font-semibold uppercase tracking-widest text-neon-blue">Settings</span>
          </div>
          <h1 className="text-3xl font-display font-extrabold" style={{ color: 'var(--text)' }}>
            Preferences
          </h1>
          <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
            Customise your BattingEdge experience.
          </p>
        </motion.div>

        <div className="space-y-5">

          {/* ── Appearance ─────────────────────────────────────────────── */}
          <SectionCard icon={Sun} title="Appearance" delay={0.05}>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-sm" style={{ color: 'var(--text)' }}>
                  {theme === 'dark' ? 'Dark Mode' : 'Light Mode'}
                </p>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                  {theme === 'dark' ? 'Switch to a clean light theme' : 'Switch to the dark theme'}
                </p>
              </div>
              <button
                onClick={toggleTheme}
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  theme === 'light' ? 'bg-neon-blue' : 'bg-surface-3 border border-border-soft'
                }`}
              >
                <span className={`absolute top-0.5 w-5 h-5 rounded-full shadow transition-all flex items-center justify-center text-[10px]
                  ${theme === 'light' ? 'left-6 bg-white' : 'left-0.5 bg-surface-2'}`}>
                  {theme === 'light' ? '☀️' : '🌙'}
                </span>
              </button>
            </div>
          </SectionCard>

          {/* ── Profile Picture ──────────────────────────────────────────── */}
          <SectionCard icon={User} title="Profile Picture" delay={0.1}>
            <p className="text-xs mb-4" style={{ color: 'var(--text-muted)' }}>
              Choose your avatar — it appears on your dashboard and in the navigation menu.
            </p>

            <div className="flex flex-wrap gap-3 mb-4">
              {AVATARS.map((emoji, i) => (
                <button
                  key={i}
                  onClick={() => saveAvatar(i)}
                  className={`w-11 h-11 rounded-xl text-xl transition-all hover:scale-110 border-2 ${
                    avatarPick === i ? 'border-neon-blue scale-110' : 'border-border-dim'
                  }`}
                  style={{ background: 'var(--surface-3)' }}
                >
                  {emoji}
                </button>
              ))}
            </div>

            <p className="text-xs mb-2" style={{ color: 'var(--text-muted)' }}>Accent colour</p>
            <div className="flex gap-2 mb-4">
              {AVATAR_COLORS.map(([c1, c2], i) => (
                <button
                  key={i}
                  onClick={() => { setColorPick(i); localStorage.setItem('be_avatar_color', String(i)); toast.success('Colour saved!'); }}
                  className={`w-8 h-8 rounded-full border-2 transition-all hover:scale-110 ${colorPick === i ? 'border-white scale-110' : 'border-transparent'}`}
                  style={{ background: `linear-gradient(135deg, ${c1}, ${c2})` }}
                />
              ))}
            </div>

            {/* Preview */}
            <div className="flex items-center gap-3">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold shadow-lg"
                style={{ background: `linear-gradient(135deg, ${AVATAR_COLORS[colorPick][0]}, ${AVATAR_COLORS[colorPick][1]})` }}
              >
                {AVATARS[avatarPick]}
              </div>
              <div>
                <p className="font-semibold text-sm" style={{ color: 'var(--text)' }}>
                  {user?.full_name || 'Your Name'}
                </p>
                <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{user?.email || 'Sign in to save profile'}</p>
              </div>
            </div>
          </SectionCard>

          {/* ── Email Subscription ────────────────────────────────────── */}
          <SectionCard icon={Mail} title="Cricket Tips Email Subscription" delay={0.15}>
            <p className="text-xs mb-4" style={{ color: 'var(--text-muted)' }}>
              Get AI-generated batting tips, drills, and cricket facts straight to your inbox.
              Powered by Groq AI. Unsubscribe any time.
            </p>

            {subDone ? (
              <div className="flex items-center gap-3 p-4 rounded-xl bg-neon-green/5 border border-neon-green/20">
                <CheckCircle2 size={18} className="text-neon-green flex-shrink-0" />
                <div>
                  <p className="text-sm font-semibold text-neon-green">You're subscribed!</p>
                  <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>
                    Cricket tips will arrive in your inbox.
                  </p>
                </div>
                <button onClick={handleUnsubscribe} className="ml-auto text-xs text-red-400 hover:underline">
                  Unsubscribe
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <input
                  type="email"
                  placeholder="Your email"
                  value={subEmail}
                  onChange={e => setSubEmail(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl text-sm border border-border-dim focus:border-neon-blue/50 outline-none transition-colors"
                  style={{ background: 'var(--surface-3)', color: 'var(--text)' }}
                />
                <input
                  type="text"
                  placeholder="Your name (optional)"
                  value={subName}
                  onChange={e => setSubName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl text-sm border border-border-dim focus:border-neon-blue/50 outline-none transition-colors"
                  style={{ background: 'var(--surface-3)', color: 'var(--text)' }}
                />
                <button
                  onClick={handleSubscribe}
                  disabled={subLoading}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all disabled:opacity-50"
                >
                  {subLoading ? <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : <Bell size={14} />}
                  Subscribe to Cricket Tips
                </button>
              </div>
            )}
          </SectionCard>

          {/* ── Account & Security ────────────────────────────────────── */}
          {user && (
            <SectionCard icon={Lock} title="Account & Security" delay={0.2}>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 rounded-xl border border-border-dim"
                     style={{ background: 'var(--surface-3)' }}>
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text)' }}>Email Verified</p>
                    <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{user.email}</p>
                  </div>
                  {user.is_verified
                    ? <CheckCircle2 size={16} className="text-neon-green" />
                    : <span className="text-xs text-yellow-400 border border-yellow-400/30 bg-yellow-400/10 px-2 py-0.5 rounded-full">Unverified</span>
                  }
                </div>
                <button
                  onClick={() => onOpenAuth?.('login')}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-xl border border-border-dim hover:border-neon-blue/30 text-sm transition-colors"
                  style={{ color: 'var(--text-muted)', background: 'var(--surface-3)' }}
                >
                  <Lock size={15} className="text-neon-blue" /> Change Password
                </button>
              </div>
            </SectionCard>
          )}

          {/* ── FAQ link ────────────────────────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
            className="p-5 rounded-2xl border border-border-dim flex items-center justify-between"
            style={{ background: 'var(--surface-2)' }}
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center">
                <HelpCircle size={17} className="text-neon-blue" />
              </div>
              <div>
                <p className="font-semibold text-sm" style={{ color: 'var(--text)' }}>Frequently Asked Questions</p>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>Answers to common questions about BattingEdge</p>
              </div>
            </div>
            <Link
              to="/faq"
              className="flex-shrink-0 px-4 py-2 rounded-full bg-neon-blue text-black text-xs font-bold hover:bg-[#33deff] transition-all"
            >
              View FAQs
            </Link>
          </motion.div>

          {/* ── About ────────────────────────────────────────────────── */}
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
            className="text-center py-6"
          >
            <div className="flex items-center justify-center gap-2 mb-2 opacity-60">
              <span className="text-lg">🏏</span>
              <span className="font-display font-bold text-sm" style={{ color: 'var(--text)' }}>BattingEdge AI</span>
            </div>
            <p className="text-xs" style={{ color: 'var(--text-dim)' }}>
              v9.5 · 94.71% accuracy · Stacking Ensemble (BiLSTM + XGBoost + RF)
            </p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-dim)' }}>
              Final Year Project · Bahria University Karachi · 2025
            </p>
          </motion.div>
        </div>
      </main>
    </div>
  );
};

export default SettingsPage;
