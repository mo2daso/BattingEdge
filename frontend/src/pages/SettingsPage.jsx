import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Settings, Sun,
  CheckCircle2, User, Lock, HelpCircle, Mail,
  Eye, EyeOff, ChevronDown, AlertCircle,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import api, { authUpdatePw, authUpdateEmail } from '../utils/api';
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
    <div className="flex items-center gap-3 px-5 py-4 border-b border-border-dim">
      <Icon size={17} className="text-neon-blue" />
      <h2 className="font-display font-bold text-sm" style={{ color: 'var(--text)' }}>{title}</h2>
    </div>
    <div className="p-4 sm:p-6">{children}</div>
  </motion.div>
);

// Small password input with show/hide toggle
const PwInput = ({ placeholder, value, onChange, show, onToggle, onKeyDown }) => (
  <div className="relative">
    <input
      type={show ? 'text' : 'password'}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      onKeyDown={onKeyDown}
      className="w-full px-4 py-2.5 pr-10 rounded-xl text-sm border border-border-dim focus:border-neon-blue/50 outline-none transition-colors"
      style={{ background: 'var(--surface-2)', color: 'var(--text)' }}
    />
    <button
      type="button"
      onClick={onToggle}
      className="absolute right-3 top-1/2 -translate-y-1/2 transition-colors hover:text-white"
      style={{ color: 'var(--text-muted)' }}
    >
      {show ? <EyeOff size={14} /> : <Eye size={14} />}
    </button>
  </div>
);

// ── Main ──────────────────────────────────────────────────────────────────────

const SettingsPage = ({ onOpenAuth }) => {
  const { theme, toggleTheme }  = useTheme();
  const { user, logout, refetch } = useAuth();

  // ── Avatar state ──────────────────────────────────────────────────────────
  const [avatarPick, setAvatarPick] = useState(() => parseInt(localStorage.getItem('be_avatar') || '0'));
  const [colorPick,  setColorPick]  = useState(() => parseInt(localStorage.getItem('be_avatar_color') || '0'));

  // ── Change Password state ─────────────────────────────────────────────────
  const [pwOpen,    setPwOpen]    = useState(false);
  const [curPw,     setCurPw]     = useState('');
  const [newPw,     setNewPw]     = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [showCurPw, setShowCurPw] = useState(false);
  const [showNewPw, setShowNewPw] = useState(false);
  const [pwLoading, setPwLoading] = useState(false);

  // ── Change Email state ────────────────────────────────────────────────────
  const [emailOpen,    setEmailOpen]    = useState(false);
  const [newEmailVal,  setNewEmailVal]  = useState('');
  const [emailPw,      setEmailPw]      = useState('');
  const [showEmailPw,  setShowEmailPw]  = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const saveAvatar = (idx, colorIdx) => {
    localStorage.setItem('be_avatar', String(idx));
    localStorage.setItem('be_avatar_color', String(colorIdx ?? colorPick));
    setAvatarPick(idx);
    if (colorIdx !== undefined) setColorPick(colorIdx);
    toast.success('Avatar saved!');
  };

  const closePwForm  = () => { setPwOpen(false);    setCurPw(''); setNewPw(''); setConfirmPw(''); };
  const closeEmailForm = () => { setEmailOpen(false); setNewEmailVal(''); setEmailPw(''); };

  const handleChangePw = async () => {
    if (!curPw)           { toast.error('Enter your current password'); return; }
    if (newPw.length < 8) { toast.error('New password must be at least 8 characters'); return; }
    if (newPw !== confirmPw) { toast.error('New passwords do not match'); return; }
    setPwLoading(true);
    try {
      await authUpdatePw(curPw, newPw);
      toast.success('Password updated!');
      closePwForm();
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to update password');
    } finally {
      setPwLoading(false);
    }
  };

  const handleChangeEmail = async () => {
    if (!newEmailVal || !newEmailVal.includes('@')) { toast.error('Enter a valid email address'); return; }
    if (newEmailVal.toLowerCase() === user?.email?.toLowerCase()) { toast.error('That is already your current email'); return; }
    if (!emailPw) { toast.error('Enter your current password to confirm'); return; }
    setEmailLoading(true);
    try {
      await authUpdateEmail(newEmailVal, emailPw);
      toast.success('Email updated! Check your new inbox for a verification link.');
      closeEmailForm();
      refetch(); // refresh user object in context
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to update email');
    } finally {
      setEmailLoading(false);
    }
  };

  // Submit on Enter key
  const onPwKey    = (e) => { if (e.key === 'Enter') handleChangePw(); };
  const onEmailKey = (e) => { if (e.key === 'Enter') handleChangeEmail(); };

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen pb-20" style={{ background: 'var(--bg)' }}>
      <Navbar onOpenAuth={onOpenAuth} />

      <main className="max-w-3xl mx-auto px-4 pt-24 sm:pt-28">

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

          {/* ── Account & Security ────────────────────────────────────── */}
          {user && (
            <SectionCard icon={Lock} title="Account & Security" delay={0.2}>
              <div className="space-y-3">

                {/* Current email + verified badge */}
                <div className="flex items-center justify-between p-3 rounded-xl border border-border-dim"
                     style={{ background: 'var(--surface-3)' }}>
                  <div>
                    <p className="text-sm font-medium" style={{ color: 'var(--text)' }}>Email</p>
                    <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{user.email}</p>
                  </div>
                  {user.is_verified
                    ? <CheckCircle2 size={16} className="text-neon-green" />
                    : <span className="text-xs text-yellow-400 border border-yellow-400/30 bg-yellow-400/10 px-2 py-0.5 rounded-full">Unverified</span>
                  }
                </div>

                {/* ── Change Password accordion ──────────────────────── */}
                <div className="rounded-xl border border-border-dim overflow-hidden"
                     style={{ background: 'var(--surface-3)' }}>
                  <button
                    onClick={() => { setPwOpen(v => !v); setEmailOpen(false); }}
                    className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium transition-colors hover:bg-white/5"
                    style={{ color: 'var(--text)' }}
                  >
                    <span className="flex items-center gap-2">
                      <Lock size={14} className="text-neon-blue" /> Change Password
                    </span>
                    <ChevronDown
                      size={14}
                      className={`transition-transform duration-200 ${pwOpen ? 'rotate-180' : ''}`}
                      style={{ color: 'var(--text-muted)' }}
                    />
                  </button>

                  <AnimatePresence initial={false}>
                    {pwOpen && (
                      <motion.div
                        key="pw-form"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2, ease: 'easeInOut' }}
                        style={{ overflow: 'hidden' }}
                      >
                        <div className="px-4 pb-4 pt-4 space-y-3 border-t border-border-dim">
                          <PwInput
                            placeholder="Current password"
                            value={curPw}
                            onChange={e => setCurPw(e.target.value)}
                            show={showCurPw}
                            onToggle={() => setShowCurPw(v => !v)}
                            onKeyDown={onPwKey}
                          />
                          <PwInput
                            placeholder="New password (8+ characters)"
                            value={newPw}
                            onChange={e => setNewPw(e.target.value)}
                            show={showNewPw}
                            onToggle={() => setShowNewPw(v => !v)}
                            onKeyDown={onPwKey}
                          />
                          <input
                            type="password"
                            placeholder="Confirm new password"
                            value={confirmPw}
                            onChange={e => setConfirmPw(e.target.value)}
                            onKeyDown={onPwKey}
                            className="w-full px-4 py-2.5 rounded-xl text-sm border border-border-dim focus:border-neon-blue/50 outline-none transition-colors"
                            style={{ background: 'var(--surface-2)', color: 'var(--text)' }}
                          />
                          {newPw && confirmPw && newPw !== confirmPw && (
                            <p className="text-xs text-red-400 flex items-center gap-1.5">
                              <AlertCircle size={11} /> Passwords do not match
                            </p>
                          )}
                          <div className="flex gap-2 pt-1">
                            <button
                              onClick={handleChangePw}
                              disabled={pwLoading}
                              className="flex-1 py-2.5 rounded-xl bg-neon-blue text-black text-sm font-bold hover:bg-[#33deff] disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                            >
                              {pwLoading && <span className="w-3.5 h-3.5 border-2 border-black/30 border-t-black rounded-full animate-spin" />}
                              {pwLoading ? 'Saving…' : 'Save Password'}
                            </button>
                            <button
                              onClick={closePwForm}
                              className="px-4 py-2.5 rounded-xl text-sm border border-border-dim hover:border-white/20 transition-colors"
                              style={{ color: 'var(--text-muted)' }}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* ── Change Email accordion ─────────────────────────── */}
                <div className="rounded-xl border border-border-dim overflow-hidden"
                     style={{ background: 'var(--surface-3)' }}>
                  <button
                    onClick={() => { setEmailOpen(v => !v); setPwOpen(false); }}
                    className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium transition-colors hover:bg-white/5"
                    style={{ color: 'var(--text)' }}
                  >
                    <span className="flex items-center gap-2">
                      <Mail size={14} className="text-neon-blue" /> Change Email
                    </span>
                    <ChevronDown
                      size={14}
                      className={`transition-transform duration-200 ${emailOpen ? 'rotate-180' : ''}`}
                      style={{ color: 'var(--text-muted)' }}
                    />
                  </button>

                  <AnimatePresence initial={false}>
                    {emailOpen && (
                      <motion.div
                        key="email-form"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2, ease: 'easeInOut' }}
                        style={{ overflow: 'hidden' }}
                      >
                        <div className="px-4 pb-4 pt-4 space-y-3 border-t border-border-dim">
                          <input
                            type="email"
                            placeholder="New email address"
                            value={newEmailVal}
                            onChange={e => setNewEmailVal(e.target.value)}
                            onKeyDown={onEmailKey}
                            className="w-full px-4 py-2.5 rounded-xl text-sm border border-border-dim focus:border-neon-blue/50 outline-none transition-colors"
                            style={{ background: 'var(--surface-2)', color: 'var(--text)' }}
                          />
                          <PwInput
                            placeholder="Confirm with your current password"
                            value={emailPw}
                            onChange={e => setEmailPw(e.target.value)}
                            show={showEmailPw}
                            onToggle={() => setShowEmailPw(v => !v)}
                            onKeyDown={onEmailKey}
                          />
                          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                            A verification link will be sent to the new address.
                          </p>
                          <div className="flex gap-2 pt-1">
                            <button
                              onClick={handleChangeEmail}
                              disabled={emailLoading}
                              className="flex-1 py-2.5 rounded-xl bg-neon-blue text-black text-sm font-bold hover:bg-[#33deff] disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                            >
                              {emailLoading && <span className="w-3.5 h-3.5 border-2 border-black/30 border-t-black rounded-full animate-spin" />}
                              {emailLoading ? 'Saving…' : 'Update Email'}
                            </button>
                            <button
                              onClick={closeEmailForm}
                              className="px-4 py-2.5 rounded-xl text-sm border border-border-dim hover:border-white/20 transition-colors"
                              style={{ color: 'var(--text-muted)' }}
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

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
