import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, Lock, User, Eye, EyeOff, AlertCircle, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { authLogin, authRegister, authGoogle, authForgotPw, authResendVerify, getMe } from '../utils/api';
import { useAuth } from '../context/AuthContext';

const GOOGLE_CLIENT_ID = '704836746742-5ekd8ctbsffpa1mvio762u4srve43g3n.apps.googleusercontent.com';

// ── Google GSI loader ─────────────────────────────────────────────────────────
let gsiLoaded = false;
const loadGSI = () => new Promise((resolve) => {
  if (gsiLoaded || window.google) { resolve(); return; }
  const s = document.createElement('script');
  s.src = 'https://accounts.google.com/gsi/client';
  s.async = true;
  s.defer = true;
  s.onload = () => { gsiLoaded = true; resolve(); };
  document.head.appendChild(s);
});

// ── Shared input ──────────────────────────────────────────────────────────────
const Input = ({ icon: Icon, rightIcon, onRightClick, ...props }) => (
  <div className="relative">
    <div className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500">
      <Icon size={16} />
    </div>
    <input
      {...props}
      className={`w-full bg-surface border border-border-soft rounded-xl pl-10 pr-${rightIcon ? '10' : '4'} py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-neon-blue/60 focus:ring-1 focus:ring-neon-blue/30 transition-all`}
    />
    {rightIcon && (
      <button type="button" onClick={onRightClick} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300 transition-colors">
        {rightIcon}
      </button>
    )}
  </div>
);

// Google Sign-In works on localhost and any deployed HTTPS domain.
// It doesn't work on private LAN IPs (192.168.x.x, 10.x.x.x).
const isGoogleAllowed = (
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1' ||
  window.location.protocol === 'https:'
);

// ── Google button ─────────────────────────────────────────────────────────────
// Uses renderButton() — reliable on any HTTPS domain in Google Cloud Console.
// Does NOT use prompt()/One Tap, which gets suppressed after a few dismissals.
const GoogleBtn = ({ onSuccess, label = 'Continue with Google' }) => {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!isGoogleAllowed || !containerRef.current) return;
    let active = true;
    loadGSI().then(() => {
      if (!active || !window.google || !containerRef.current) return;
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: async (res) => {
          try {
            const data = await authGoogle(res.credential);
            localStorage.setItem('be_token', data.access_token);
            const user = await getMe();
            onSuccess(data.access_token, user);
          } catch (err) {
            toast.error(err.response?.data?.detail || 'Google sign-in failed');
          }
        },
      });
      window.google.accounts.id.renderButton(containerRef.current, {
        theme: 'outline',
        size: 'large',
        width: containerRef.current.offsetWidth || 360,
        text: label.toLowerCase().includes('up') ? 'signup_with' : 'signin_with',
        logo_alignment: 'left',
        shape: 'rectangular',
      });
    });
    return () => { active = false; };
  }, [onSuccess, label]);

  if (!isGoogleAllowed) {
    return (
      <p className="text-center text-xs text-gray-600 py-1">
        Google Sign-In is not available on local network access.
        Please use email &amp; password.
      </p>
    );
  }

  return <div ref={containerRef} className="w-full flex justify-center" style={{ minHeight: 44 }} />;
};

// ── Main Modal ────────────────────────────────────────────────────────────────
const AuthModal = ({ isOpen, onClose, defaultTab = 'login' }) => {
  const { login } = useAuth();
  const [tab, setTab]           = useState(defaultTab);
  const [flow, setFlow]         = useState('main'); // main | forgot | verify_sent | reset_sent
  const [showPw, setShowPw]     = useState(false);
  const [loading, setLoading]   = useState(false);

  // form fields
  const [name, setName]         = useState('');
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');

  useEffect(() => {
    if (isOpen) { setTab(defaultTab); setFlow('main'); setError(''); }
  }, [isOpen, defaultTab]);

  const reset = () => { setName(''); setEmail(''); setPassword(''); setError(''); };

  const handleSuccess = (token, user) => {
    login(token, user);
    toast.success(`Welcome${user.full_name ? ', ' + user.full_name.split(' ')[0] : ''}!`);
    onClose();
    reset();
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const data = await authLogin({ email, password });
      localStorage.setItem('be_token', data.access_token);
      const user = await getMe();
      handleSuccess(data.access_token, user);
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed';
      if (err.response?.status === 403) {
        setError('Email not verified. Check your inbox.');
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (password.length < 8) { setError('Password must be at least 8 characters'); return; }
    setError(''); setLoading(true);
    try {
      const data = await authRegister({ email, password, full_name: name });
      localStorage.setItem('be_token', data.access_token);
      const user = await getMe();
      handleSuccess(data.access_token, user);
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleForgot = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      await authForgotPw(email);
      setFlow('reset_sent');
    } catch {
      setFlow('reset_sent'); // always show sent for security
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    try {
      await authResendVerify(email);
      toast.success('Verification email resent!');
    } catch {
      toast.error('Failed to resend. Try again.');
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      >
        {/* Backdrop */}
        <motion.div
          className="absolute inset-0 bg-black/70 backdrop-blur-sm"
          onClick={onClose}
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="relative w-full max-w-md glass-strong rounded-2xl overflow-hidden shadow-[0_24px_80px_rgba(0,0,0,0.7)] border border-border-soft"
        >
          {/* Header accent */}
          <div className="h-1 w-full bg-gradient-to-r from-neon-blue via-neon-green to-neon-blue bg-[length:200%] animate-gradient" />

          <div className="p-6 sm:p-8">
            {/* Close */}
            <button onClick={onClose} className="absolute top-5 right-5 p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all">
              <X size={18} />
            </button>

            {/* ── Verify Sent ── */}
            {flow === 'verify_sent' && (
              <div className="text-center py-4">
                <div className="w-16 h-16 rounded-full bg-neon-green/10 border border-neon-green/20 flex items-center justify-center mx-auto mb-4">
                  <CheckCircle2 size={32} className="text-neon-green" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Check your inbox</h2>
                <p className="text-gray-400 text-sm mb-6">We sent a verification link to <span className="text-white font-medium">{email}</span>. Click it to activate your account.</p>
                <button onClick={handleResend} className="text-neon-blue text-sm hover:underline">Didn't get it? Resend</button>
                <button onClick={() => { setTab('login'); setFlow('main'); }} className="block w-full mt-4 text-sm text-gray-500 hover:text-white transition-colors">Back to Sign In</button>
              </div>
            )}

            {/* ── Reset Sent ── */}
            {flow === 'reset_sent' && (
              <div className="text-center py-4">
                <div className="w-16 h-16 rounded-full bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center mx-auto mb-4">
                  <Mail size={32} className="text-neon-blue" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Reset link sent</h2>
                <p className="text-gray-400 text-sm mb-6">If an account exists for <span className="text-white font-medium">{email}</span>, you'll receive a reset link shortly.</p>
                <button onClick={() => { setTab('login'); setFlow('main'); }} className="text-neon-blue text-sm hover:underline">Back to Sign In</button>
              </div>
            )}

            {/* ── Forgot Password ── */}
            {flow === 'forgot' && (
              <>
                <h2 className="text-2xl font-bold text-white mb-1">Reset Password</h2>
                <p className="text-gray-500 text-sm mb-6">Enter your email and we'll send a reset link.</p>
                <form onSubmit={handleForgot} className="space-y-4">
                  <Input icon={Mail} type="email" placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)} required />
                  {error && <p className="text-red-400 text-sm flex items-center gap-2"><AlertCircle size={14}/>{error}</p>}
                  <button type="submit" disabled={loading} className="w-full py-3 rounded-xl bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all disabled:opacity-60">
                    {loading ? 'Sending…' : 'Send Reset Link'}
                  </button>
                  <button type="button" onClick={() => setFlow('main')} className="w-full text-sm text-gray-500 hover:text-white transition-colors">Back to Sign In</button>
                </form>
              </>
            )}

            {/* ── Main login/register ── */}
            {flow === 'main' && (
              <>
                {/* Tabs */}
                <div className="flex gap-1 bg-surface rounded-xl p-1 mb-6">
                  {['login', 'register'].map(t => (
                    <button
                      key={t}
                      onClick={() => { setTab(t); setError(''); }}
                      className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
                        tab === t ? 'bg-surface-2 text-white shadow-sm' : 'text-gray-500 hover:text-gray-300'
                      }`}
                    >
                      {t === 'login' ? 'Sign In' : 'Sign Up'}
                    </button>
                  ))}
                </div>

                {/* ── LOGIN ── */}
                {tab === 'login' && (
                  <form onSubmit={handleLogin} className="space-y-4">
                    <Input icon={Mail} type="email" placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)} required autoFocus />
                    <Input
                      icon={Lock} type={showPw ? 'text' : 'password'} placeholder="Password"
                      value={password} onChange={e => setPassword(e.target.value)} required
                      rightIcon={showPw ? <EyeOff size={15}/> : <Eye size={15}/>}
                      onRightClick={() => setShowPw(s => !s)}
                    />
                    {error && <p className="text-red-400 text-sm flex items-center gap-2"><AlertCircle size={14}/>{error}</p>}
                    <button type="submit" disabled={loading} className="w-full py-3 rounded-xl bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon disabled:opacity-60">
                      {loading ? 'Signing in…' : 'Sign In'}
                    </button>
                    <button type="button" onClick={() => setFlow('forgot')} className="block w-full text-center text-xs text-gray-500 hover:text-neon-blue transition-colors mt-1">
                      Forgot password?
                    </button>
                    <div className="relative flex items-center gap-3 py-1">
                      <div className="flex-1 h-px bg-border-dim" />
                      <span className="text-xs text-gray-600">or</span>
                      <div className="flex-1 h-px bg-border-dim" />
                    </div>
                    <GoogleBtn onSuccess={handleSuccess} label="Sign in with Google" />
                  </form>
                )}

                {/* ── REGISTER ── */}
                {tab === 'register' && (
                  <form onSubmit={handleRegister} className="space-y-4">
                    <Input icon={User} type="text" placeholder="Full name" value={name} onChange={e => setName(e.target.value)} required autoFocus />
                    <Input icon={Mail} type="email" placeholder="Email address" value={email} onChange={e => setEmail(e.target.value)} required />
                    <Input
                      icon={Lock} type={showPw ? 'text' : 'password'} placeholder="Password (min 8 chars)"
                      value={password} onChange={e => setPassword(e.target.value)} required
                      rightIcon={showPw ? <EyeOff size={15}/> : <Eye size={15}/>}
                      onRightClick={() => setShowPw(s => !s)}
                    />
                    {error && <p className="text-red-400 text-sm flex items-center gap-2"><AlertCircle size={14}/>{error}</p>}
                    <button type="submit" disabled={loading} className="w-full py-3 rounded-xl bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon disabled:opacity-60">
                      {loading ? 'Creating account…' : 'Create Account'}
                    </button>
                    <div className="relative flex items-center gap-3 py-1">
                      <div className="flex-1 h-px bg-border-dim" />
                      <span className="text-xs text-gray-600">or</span>
                      <div className="flex-1 h-px bg-border-dim" />
                    </div>
                    <GoogleBtn onSuccess={handleSuccess} label="Sign up with Google" />
                    <p className="text-xs text-gray-600 text-center">By signing up you agree to our Terms of Service.</p>
                  </form>
                )}
              </>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default AuthModal;
