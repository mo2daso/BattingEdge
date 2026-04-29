import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Lock, Eye, EyeOff, CheckCircle2, XCircle } from 'lucide-react';
import { authResetPw } from '../utils/api';

const ResetPasswordPage = () => {
  const [params]   = useSearchParams();
  const navigate   = useNavigate();
  const token      = params.get('token');

  const [pw, setPw]         = useState('');
  const [pw2, setPw2]       = useState('');
  const [show, setShow]     = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('form'); // form | success | error
  const [msg, setMsg]       = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (pw.length < 8) { setMsg('Password must be at least 8 characters.'); return; }
    if (pw !== pw2)    { setMsg('Passwords do not match.'); return; }
    setLoading(true); setMsg('');
    try {
      await authResetPw(token, pw);
      setStatus('success');
    } catch (err) {
      setMsg(err.response?.data?.detail || 'Reset failed. The link may have expired.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-jet-black flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <span className="text-2xl font-display font-black text-white">Batting<span className="text-neon-blue">Edge</span></span>
        </div>

        <div className="p-8 rounded-2xl bg-surface-2 border border-border-dim">
          {status === 'success' ? (
            <div className="text-center">
              <div className="w-16 h-16 rounded-full bg-neon-green/10 border-2 border-neon-green/30 flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 size={32} className="text-neon-green" />
              </div>
              <h2 className="text-xl font-display font-bold text-white mb-2">Password Reset!</h2>
              <p className="text-gray-400 text-sm mb-6">Your password has been updated. You can now sign in.</p>
              <button
                onClick={() => navigate('/')}
                className="w-full py-3 rounded-xl bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon"
              >
                Go to Homepage
              </button>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center">
                  <Lock size={18} className="text-neon-blue" />
                </div>
                <div>
                  <h2 className="font-display font-bold text-white">Reset Password</h2>
                  <p className="text-gray-500 text-xs">Enter your new password below</p>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative">
                  <Lock size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type={show ? 'text' : 'password'}
                    placeholder="New password (min 8 chars)"
                    value={pw} onChange={e => setPw(e.target.value)}
                    required
                    className="w-full bg-surface border border-border-soft rounded-xl pl-10 pr-10 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-neon-blue/60 transition-all"
                  />
                  <button type="button" onClick={() => setShow(s => !s)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300">
                    {show ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>

                <div className="relative">
                  <Lock size={15} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type={show ? 'text' : 'password'}
                    placeholder="Confirm new password"
                    value={pw2} onChange={e => setPw2(e.target.value)}
                    required
                    className="w-full bg-surface border border-border-soft rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-neon-blue/60 transition-all"
                  />
                </div>

                {msg && (
                  <div className="flex items-center gap-2 text-red-400 text-sm">
                    <XCircle size={14} /> {msg}
                  </div>
                )}

                <button
                  type="submit" disabled={loading}
                  className="w-full py-3 rounded-xl bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon disabled:opacity-50"
                >
                  {loading ? 'Updating…' : 'Reset Password'}
                </button>
              </form>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default ResetPasswordPage;
