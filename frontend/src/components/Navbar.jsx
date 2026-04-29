import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap, X, Menu, User, LogOut, LayoutDashboard,
  ChevronDown, Settings, Sun, Moon, HelpCircle,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const NAV_LINKS = [
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'FAQs',          href: '/faq' },
];

const AVATAR_COLORS = [
  ['#00d4ff','#0099bb'],
  ['#00ff88','#00bb66'],
  ['#f59e0b','#d97706'],
  ['#8b5cf6','#7c3aed'],
  ['#ef4444','#dc2626'],
  ['#06b6d4','#0891b2'],
];
const AVATARS = ['🏏', '🪃', '🏆', '🎯', '⚡', '💫', '🛡️', '🌟'];

const UserAvatar = ({ size = 7 }) => {
  const avatarIdx = parseInt(localStorage.getItem('be_avatar') || '0');
  const colorIdx  = parseInt(localStorage.getItem('be_avatar_color') || '0');
  const [c1, c2]  = AVATAR_COLORS[colorIdx] || AVATAR_COLORS[0];
  const emoji     = AVATARS[avatarIdx] || '🏏';
  return (
    <div
      className={`w-${size} h-${size} rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0`}
      style={{ background: `linear-gradient(135deg, ${c1}, ${c2})` }}
    >
      {emoji}
    </div>
  );
};

const Navbar = ({ onOpenAuth }) => {
  const { user, logout }       = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location  = useLocation();
  const navigate  = useNavigate();
  const [scrolled,     setScrolled]     = useState(false);
  const [mobileOpen,   setMobileOpen]   = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => { setMobileOpen(false); }, [location.pathname]);

  const scrollTo = (href) => {
    setMobileOpen(false);
    if (href.startsWith('/')) { navigate(href); return; }
    if (location.pathname !== '/') {
      navigate('/' + href);
    } else {
      document.querySelector(href)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleLogout = () => { logout(); setUserMenuOpen(false); navigate('/'); };

  return (
    <>
      <nav className={`fixed w-full z-50 top-0 transition-all duration-300 ${scrolled ? 'glass-strong shadow-card' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-18 py-4">

            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group flex-shrink-0">
              <div className="relative w-9 h-9 rounded-xl overflow-hidden border border-white/10 group-hover:border-neon-blue/50 transition-all duration-300">
                <img src="/be_logo.png" alt="BattingEdge" className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-neon-blue/20 blur-md opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <span className="font-display font-bold text-xl tracking-tight" style={{ color: 'var(--text)' }}>
                Batting<span className="text-neon-blue text-glow">Edge</span>
              </span>
            </Link>

            {/* Right side — links + controls grouped together */}
            <div className="hidden md:flex items-center gap-2">

              {/* Nav links */}
              {NAV_LINKS.map(({ label, href }) => (
                <button
                  key={href}
                  onClick={() => scrollTo(href)}
                  className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium transition-colors hover:text-neon-blue"
                  style={{ color: 'var(--text-muted)' }}
                >
                  {label === 'FAQs' && <HelpCircle size={13} />}
                  {label}
                </button>
              ))}

              <div className="w-px h-5 mx-1" style={{ background: 'var(--border-dim)' }} />

              {/* Theme toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg transition-all hover:bg-white/5 border border-transparent hover:border-border-dim"
                title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
                style={{ color: 'var(--text-muted)' }}
              >
                {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              </button>

              {user ? (
                /* User avatar dropdown */
                <div className="relative">
                  <button
                    onClick={() => setUserMenuOpen(o => !o)}
                    className="flex items-center gap-2 px-3 py-2 rounded-xl border border-border-dim hover:border-neon-blue/30 transition-all"
                    style={{ background: 'var(--surface-2)' }}
                  >
                    <UserAvatar size={7} />
                    <ChevronDown size={14} style={{ color: 'var(--text-dim)' }} className={`transition-transform ${userMenuOpen ? 'rotate-180' : ''}`} />
                  </button>

                  <AnimatePresence>
                    {userMenuOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: 8, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 8, scale: 0.95 }}
                        transition={{ duration: 0.15 }}
                        className="absolute right-0 mt-2 w-52 glass-strong rounded-xl overflow-hidden shadow-card"
                      >
                        {/* User info header */}
                        <div className="px-4 py-3 border-b border-border-dim">
                          <div className="flex items-center gap-3">
                            <UserAvatar size={8} />
                            <div className="min-w-0">
                              <p className="text-sm font-semibold truncate" style={{ color: 'var(--text)' }}>{user.full_name}</p>
                              <p className="text-xs truncate" style={{ color: 'var(--text-muted)' }}>{user.email}</p>
                            </div>
                          </div>
                        </div>

                        <Link
                          to="/dashboard"
                          onClick={() => setUserMenuOpen(false)}
                          className="flex items-center gap-3 px-4 py-3 text-sm transition-colors hover:bg-white/5"
                          style={{ color: 'var(--text-muted)' }}
                        >
                          <LayoutDashboard size={14} /> Dashboard
                        </Link>
                        <Link
                          to="/settings"
                          onClick={() => setUserMenuOpen(false)}
                          className="flex items-center gap-3 px-4 py-3 text-sm transition-colors hover:bg-white/5"
                          style={{ color: 'var(--text-muted)' }}
                        >
                          <Settings size={14} /> Settings
                        </Link>

                        <div className="border-t border-border-dim">
                          <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-3 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                          >
                            <LogOut size={14} /> Sign Out
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                <button
                  onClick={() => onOpenAuth?.('login')}
                  className="flex items-center gap-1.5 px-4 py-2 text-sm font-medium transition-colors hover:text-white"
                  style={{ color: 'var(--text-muted)' }}
                >
                  <User size={15} /> Sign In
                </button>
              )}

              <Link
                to="/analyze"
                className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon hover:shadow-neon-strong"
              >
                <Zap size={14} /> Analyze Now
              </Link>
            </div>

            {/* Mobile: theme + hamburger */}
            <div className="md:hidden flex items-center gap-2">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg transition-colors"
                style={{ color: 'var(--text-muted)' }}
              >
                {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
              </button>
              <button
                onClick={() => setMobileOpen(o => !o)}
                className="p-2 rounded-lg transition-colors"
                style={{ color: 'var(--text-muted)' }}
              >
                {mobileOpen ? <X size={22} /> : <Menu size={22} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        <AnimatePresence>
          {mobileOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden glass-strong border-t border-border-dim overflow-hidden"
            >
              <div className="px-4 py-4 space-y-1">
                {/* Nav links always shown on mobile */}
                {NAV_LINKS.map(({ label, href }) => (
                  <button
                    key={href}
                    onClick={() => scrollTo(href)}
                    className="w-full text-left px-4 py-3 text-sm font-medium hover:bg-white/5 rounded-xl transition-all"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    {label}
                  </button>
                ))}

                <div className="border-t border-border-dim pt-2 mt-1">
                  {user ? (
                    <>
                      <div className="flex items-center gap-3 px-4 py-3">
                        <UserAvatar size={9} />
                        <div>
                          <p className="text-sm font-semibold" style={{ color: 'var(--text)' }}>{user.full_name}</p>
                          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{user.email}</p>
                        </div>
                      </div>
                      <Link to="/dashboard" onClick={() => setMobileOpen(false)}
                            className="flex items-center gap-2 px-4 py-3 text-sm hover:bg-white/5 rounded-xl transition-all"
                            style={{ color: 'var(--text-muted)' }}>
                        <LayoutDashboard size={15} /> Dashboard
                      </Link>
                      <Link to="/settings" onClick={() => setMobileOpen(false)}
                            className="flex items-center gap-2 px-4 py-3 text-sm hover:bg-white/5 rounded-xl transition-all"
                            style={{ color: 'var(--text-muted)' }}>
                        <Settings size={15} /> Settings
                      </Link>
                      <button onClick={handleLogout}
                              className="w-full flex items-center gap-2 px-4 py-3 text-sm text-red-400 hover:bg-red-500/10 rounded-xl transition-all">
                        <LogOut size={15} /> Sign Out
                      </button>
                    </>
                  ) : (
                    <button onClick={() => { onOpenAuth?.('login'); setMobileOpen(false); }}
                            className="w-full flex items-center gap-2 px-4 py-3 text-sm hover:bg-white/5 rounded-xl transition-all"
                            style={{ color: 'var(--text-muted)' }}>
                      <User size={15} /> Sign In
                    </button>
                  )}
                </div>

                <Link
                  to="/analyze"
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center justify-center gap-2 w-full py-3 rounded-full bg-neon-blue text-black font-bold text-sm mt-2"
                >
                  <Zap size={14} /> Analyze Now
                </Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* Close user menu on outside click */}
      {userMenuOpen && (
        <div className="fixed inset-0 z-40" onClick={() => setUserMenuOpen(false)} />
      )}
    </>
  );
};

export default Navbar;
