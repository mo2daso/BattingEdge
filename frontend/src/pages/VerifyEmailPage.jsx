import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import api from '../utils/api';

const VerifyEmailPage = () => {
  const [params]   = useSearchParams();
  const navigate   = useNavigate();
  const token      = params.get('token');
  const [status, setStatus] = useState('loading'); // loading | success | error
  const [msg, setMsg]       = useState('');

  useEffect(() => {
    if (!token) { setStatus('error'); setMsg('No verification token found in the link.'); return; }
    api.get(`/auth/verify-email?token=${encodeURIComponent(token)}`)
      .then(r => {
        setStatus('success');
        setMsg(r.data?.message || 'Email verified! You can now log in.');
      })
      .catch(err => {
        setStatus('error');
        setMsg(err.response?.data?.detail || 'Verification link is invalid or has expired.');
      });
  }, [token]);

  return (
    <div className="min-h-screen bg-jet-black flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md text-center"
      >
        {/* Logo */}
        <div className="mb-8">
          <span className="text-2xl font-display font-black text-white">Batting<span className="text-neon-blue">Edge</span></span>
        </div>

        <div className="p-8 rounded-2xl bg-surface-2 border border-border-dim">
          {status === 'loading' && (
            <>
              <Loader2 size={48} className="text-neon-blue animate-spin mx-auto mb-4" />
              <h2 className="text-xl font-display font-bold text-white mb-2">Verifying your email…</h2>
              <p className="text-gray-500 text-sm">Please wait a moment.</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="w-16 h-16 rounded-full bg-neon-green/10 border-2 border-neon-green/30 flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 size={32} className="text-neon-green" />
              </div>
              <h2 className="text-xl font-display font-bold text-white mb-2">Email Verified!</h2>
              <p className="text-gray-400 text-sm mb-6">{msg}</p>
              <button
                onClick={() => navigate('/')}
                className="w-full py-3 rounded-xl bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon"
              >
                Go to Homepage & Sign In
              </button>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-16 h-16 rounded-full bg-red-500/10 border-2 border-red-500/30 flex items-center justify-center mx-auto mb-4">
                <XCircle size={32} className="text-red-400" />
              </div>
              <h2 className="text-xl font-display font-bold text-white mb-2">Verification Failed</h2>
              <p className="text-gray-400 text-sm mb-6">{msg}</p>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/')}
                  className="w-full py-3 rounded-xl bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all"
                >
                  Back to Homepage
                </button>
                <p className="text-gray-600 text-xs">
                  If the link expired, sign in and request a new verification email.
                </p>
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
};

export default VerifyEmailPage;
