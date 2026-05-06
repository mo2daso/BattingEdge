import React, { useMemo, useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard, Zap, FileText, BarChart3, Clock, Trophy,
  TrendingUp, ExternalLink, Target, ChevronDown, ChevronUp,
  Star, AlertCircle, CheckCircle2, RefreshCw,
} from 'lucide-react';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { getHistory, fetchHistoryFromBackend, getPdfUrl } from '../utils/api';

// ── Shot metadata ──────────────────────────────────────────────────────────────
const SHOT_META = {
  cover_drive: {
    icon: '🏏', label: 'Cover Drive',
    tip: 'Move your front foot towards the ball — don\'t wait for it to come to you. Drive through with soft hands and a full follow-through. Keep your head still throughout.',
    drills: ['Front-foot drive against throw-downs (30 reps)', 'Cone placement drill in cover region', 'Mirror drill — check head stays still'],
  },
  cut_shot: {
    icon: '⚡', label: 'Cut Shot',
    tip: 'Stay tall and play late. Back-foot should step back-and-across. Let the ball come alongside you before cutting — rushing the cut is the #1 mistake.',
    drills: ['Bobbing ball cut practice (20 reps)', 'React-and-cut drill with short throws', 'Static weight transfer reps for balance'],
  },
  defense: {
    icon: '🛡️', label: 'Defense',
    tip: 'Soft hands are everything. Drop the ball dead at your feet — don\'t push at it. Head over the front knee, bat face angled down at 30–45°.',
    drills: ['Towel target defense drill', 'Paper-between-bat-and-pad drill', 'Backward defense short ball session'],
  },
  pull_shot: {
    icon: '💥', label: 'Pull Shot',
    tip: 'Get inside the line. Roll your wrists through the shot to keep the ball down. Flat wrists = top edge and possible wicket.',
    drills: ['Kneeling pull drill (wrist control)', 'Short-ball nets session', 'Shadow wrist-roll reps — 50 morning/evening'],
  },
  sweep_shot: {
    icon: '🌀', label: 'Sweep Shot',
    tip: 'Commit fully — half-committed sweeps produce top edges. Front knee nearly on the ground, head forward over front knee. Eyes on the ball until contact.',
    drills: ['Static sweep position feeding drill', 'Spin lane commitment drill', 'Reverse sweep variation practice'],
  },
};

const normalize = (s = '') => s.toLowerCase().replace(/\s+/g, '_');
const GRADE_ORDER = ['A+','A','B+','B','C+','C','D','F'];

const gradeColor = (g = '') => {
  if (['A+','A'].includes(g))   return 'text-neon-green border-neon-green/30 bg-neon-green/10';
  if (['B+','B'].includes(g))   return 'text-neon-blue  border-neon-blue/30  bg-neon-blue/10';
  if (['C+','C'].includes(g))   return 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10';
  return 'text-red-400 border-red-400/30 bg-red-400/10';
};

const shotIcon = (s = '') => SHOT_META[normalize(s)]?.icon || '🏏';

const fmtDate = (iso) => {
  try { return new Date(iso).toLocaleDateString('en-GB', { day:'numeric', month:'short', year:'numeric' }); }
  catch { return iso; }
};

// ── Sub-components ─────────────────────────────────────────────────────────────

const StatCard = ({ icon: Icon, label, value, color = 'text-neon-blue', sub }) => (
  <div className="p-5 rounded-2xl border border-border-dim flex flex-col justify-between h-full card-hover"
       style={{ background: 'var(--surface-2)' }}>
    <div className={`w-11 h-11 rounded-xl border border-border-dim flex items-center justify-center flex-shrink-0 ${color}`}
         style={{ background: 'var(--surface-3)' }}>
      <Icon size={19} />
    </div>
    <div>
      <p className="text-2xl font-display font-bold" style={{ color: 'var(--text)' }}>{value}</p>
      <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>{label}</p>
      {sub && <p className="text-xs mt-0.5" style={{ color: 'var(--text-dim)' }}>{sub}</p>}
    </div>
  </div>
);

// User avatar (matches Navbar avatar)
const AVATAR_COLORS = [
  ['#00d4ff','#0099bb'], ['#00ff88','#00bb66'], ['#f59e0b','#d97706'],
  ['#8b5cf6','#7c3aed'], ['#ef4444','#dc2626'], ['#06b6d4','#0891b2'],
];
const AVATARS = ['🏏', '🪃', '🏆', '🎯', '⚡', '💫', '🛡️', '🌟'];

const UserAvatar = ({ size = 12 }) => {
  const avatarIdx = parseInt(localStorage.getItem('be_avatar') || '0');
  const colorIdx  = parseInt(localStorage.getItem('be_avatar_color') || '0');
  const [c1, c2]  = AVATAR_COLORS[colorIdx] || AVATAR_COLORS[0];
  const emoji     = AVATARS[avatarIdx] || '🏏';
  return (
    <div className={`w-${size} h-${size} rounded-full flex items-center justify-center text-xl font-bold flex-shrink-0 shadow-lg`}
         style={{ background: `linear-gradient(135deg, ${c1}, ${c2})` }}>
      {emoji}
    </div>
  );
};

// Shot strength bar
const ShotStrengthBar = ({ shotKey, stats, index }) => {
  const meta  = SHOT_META[shotKey] || { icon: '🏏', label: shotKey };
  const avg   = stats.avg;
  const grade = stats.bestGrade;
  const pct   = Math.min(100, avg);
  const isWeak = avg < 70;
  const color = avg >= 80 ? '#00ff88' : avg >= 60 ? '#00d4ff' : avg >= 40 ? '#f59e0b' : '#ef4444';

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.07 }}
      className={`flex items-center gap-4 p-4 rounded-xl border transition-colors ${
        isWeak ? 'border-yellow-500/30' : 'border-border-dim hover:border-border-soft'
      }`}
      style={{ background: isWeak ? 'rgba(245,158,11,0.04)' : 'var(--surface-3)' }}
    >
      <span className="text-2xl flex-shrink-0">{meta.icon}</span>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1.5">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold" style={{ color: 'var(--text)' }}>{meta.label}</span>
            {isWeak && (
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
                Needs work
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold" style={{ color }}>{avg}/100</span>
            {grade && (
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${gradeColor(grade)}`}>
                {grade}
              </span>
            )}
          </div>
        </div>
        <div className="conf-bar-track">
          <motion.div
            className="conf-bar-fill strength-bar"
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 1, delay: index * 0.1, ease: 'easeOut' }}
            style={{ background: `linear-gradient(90deg, ${color}, ${color}99)`, boxShadow: `0 0 8px ${color}66` }}
          />
        </div>
        <p className="text-[10px] mt-1.5 leading-relaxed" style={{ color: 'var(--text-dim)' }}>
          {stats.count} {stats.count === 1 ? 'analysis' : 'analyses'} · Best: {grade || '—'} · Avg: {avg}/100
          {isWeak && <span className="text-yellow-400 ml-1">· Work on this shot</span>}
        </p>
      </div>
    </motion.div>
  );
};

// Drill card for a weak shot
const DrillCard = ({ shotKey, avg }) => {
  const [open, setOpen] = useState(false);
  const meta = SHOT_META[shotKey];
  if (!meta) return null;

  return (
    <div className="rounded-xl border border-yellow-500/20 overflow-hidden" style={{ background: 'var(--surface-3)' }}>
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-3.5 text-left"
      >
        <div className="flex items-center gap-3">
          <span className="text-lg">{meta.icon}</span>
          <div>
            <p className="text-sm font-semibold" style={{ color: 'var(--text)' }}>{meta.label}</p>
            <p className="text-xs text-yellow-400">Avg: {avg}/100 — below 70, needs improvement</p>
          </div>
        </div>
        {open ? <ChevronUp size={15} className="text-yellow-400 flex-shrink-0" />
               : <ChevronDown size={15} style={{ color: 'var(--text-dim)' }} className="flex-shrink-0" />}
      </button>

      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} className="overflow-hidden">
            <div className="px-4 pb-4 border-t border-yellow-500/20 pt-3 space-y-3">
              <div className="p-3 rounded-xl bg-neon-blue/5 border border-neon-blue/15">
                <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>
                  <span className="text-neon-blue font-semibold">Coach Tip: </span>{meta.tip}
                </p>
              </div>
              <div>
                <p className="text-xs font-bold mb-2 uppercase tracking-wider" style={{ color: 'var(--text-dim)' }}>
                  Recommended Drills
                </p>
                {meta.drills.map((d, i) => (
                  <div key={i} className="flex items-start gap-2.5 mb-2">
                    <div className="w-5 h-5 rounded-md bg-neon-green/10 border border-neon-green/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-neon-green text-[9px] font-bold">{i+1}</span>
                    </div>
                    <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>{d}</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ── Main ───────────────────────────────────────────────────────────────────────

const DashboardPage = ({ onOpenAuth }) => {
  const { user }  = useAuth();
  const [history, setHistory] = useState(() => getHistory(user?.id));
  const [historyLoading, setHistoryLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('history');

  // Fetch fresh history from backend when logged in
  const refreshHistory = useCallback(async () => {
    if (!user?.id) return;
    setHistoryLoading(true);
    try {
      const fresh = await fetchHistoryFromBackend(user.id);
      setHistory(fresh);
    } finally {
      setHistoryLoading(false);
    }
  }, [user?.id]);

  useEffect(() => {
    if (user?.id) {
      refreshHistory();
    } else {
      setHistory(getHistory(null));
    }
  }, [user?.id, refreshHistory]);

  // ── Aggregated stats ─────────────────────────────────────────────────────
  const avgScore = useMemo(() => {
    if (!history.length) return 0;
    return Math.round(history.reduce((a, h) => a + (h.score || 0), 0) / history.length);
  }, [history]);

  const bestGrade = useMemo(() => {
    for (const g of GRADE_ORDER) if (history.some(h => h.grade === g)) return g;
    return '—';
  }, [history]);

  const shotStats = useMemo(() => {
    const map = {};
    history.forEach(h => {
      const k = normalize(h.shotType || '');
      if (!k) return;
      if (!map[k]) map[k] = { count: 0, totalScore: 0, grades: [] };
      map[k].count++;
      map[k].totalScore += h.score || 0;
      if (h.grade) map[k].grades.push(h.grade);
    });
    return Object.fromEntries(
      Object.entries(map).map(([k, v]) => [
        k,
        {
          count:     v.count,
          avg:       Math.round(v.totalScore / v.count),
          bestGrade: v.grades.sort((a,b) => GRADE_ORDER.indexOf(a) - GRADE_ORDER.indexOf(b))[0] || null,
        },
      ])
    );
  }, [history]);

  const weakShots = useMemo(() =>
    Object.entries(shotStats)
      .filter(([, s]) => s.avg < 70)
      .sort((a,b) => a[1].avg - b[1].avg)
      .slice(0, 5),
    [shotStats]
  );

  const dailyTip = useMemo(() => {
    if (weakShots.length > 0) {
      const weakKey = weakShots[0][0];
      const meta = SHOT_META[weakKey];
      if (meta) return { icon: meta.icon, msg: meta.tip };
    }
    const tips = [
      { icon: '🏏', msg: 'Work on your cover drive footwork today. Move to the ball — don\'t wait for it.' },
      { icon: '⚡', msg: 'Stay tall on the cut shot. Back foot back-and-across, play it late.' },
      { icon: '🛡️', msg: 'Practice forward defense: soft hands, head over knee, bat face angled down.' },
      { icon: '💥', msg: 'Pull shot tip: roll your wrists through the shot. Flat wrists = top edge.' },
      { icon: '🌀', msg: 'On the sweep: get your front knee down and commit — half-sweeps produce edges.' },
    ];
    return tips[new Date().getDay() % tips.length];
  }, [weakShots]);

  const TABS = [
    { key: 'history',   label: 'Recent Analyses',  icon: Clock },
    { key: 'strengths', label: 'Shot Tracker',      icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen pb-20 overflow-x-hidden" style={{ background: 'var(--bg)' }}>
      <Navbar onOpenAuth={onOpenAuth} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 sm:pt-28">

        {/* Header with avatar */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center gap-3 sm:gap-4 mb-3">
            {user && <UserAvatar size={14} />}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-3 mb-1">
                <div className="w-8 h-8 rounded-xl bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center">
                  <LayoutDashboard size={15} className="text-neon-blue" />
                </div>
                <span className="text-xs font-semibold tracking-widest uppercase text-neon-blue">My Dashboard</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-display font-extrabold truncate" style={{ color: 'var(--text)' }}>
                {user ? `Welcome back, ${user.full_name?.split(' ')[0]}` : 'Your Analysis Hub'}
              </h1>
              {user && <p className="text-sm mt-0.5" style={{ color: 'var(--text-muted)' }}>{user.email}</p>}
            </div>
          </div>
          {user && (
            <button
              onClick={refreshHistory}
              disabled={historyLoading}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-border-dim hover:border-neon-blue/30 transition-all"
              style={{ color: 'var(--text-dim)', background: 'var(--surface-2)' }}
            >
              <RefreshCw size={11} className={historyLoading ? 'animate-spin' : ''} />
              {historyLoading ? 'Refreshing…' : 'Refresh History'}
            </button>
          )}
        </motion.div>

        {/* Daily tip */}
        {history.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}
            className="mb-6 p-4 rounded-2xl border border-neon-blue/20 bg-neon-blue/5 flex items-start gap-3"
          >
            <span className="text-2xl flex-shrink-0">{dailyTip.icon}</span>
            <div>
              <p className="text-xs font-bold text-neon-blue uppercase tracking-wider mb-0.5">
                {weakShots.length > 0 ? 'Focus Area Coach Tip' : "Today's Coach Tip"}
              </p>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>{dailyTip.msg}</p>
            </div>
          </motion.div>
        )}

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          <StatCard icon={BarChart3}   label="Total Analyses"  value={history.length || '0'}             color="text-neon-blue" />
          <StatCard icon={TrendingUp}  label="Average Score"   value={history.length ? `${avgScore}/100` : '—'} color="text-neon-green" />
          <StatCard icon={Trophy}      label="Best Grade"       value={bestGrade}                          color="text-yellow-400" />
          <StatCard icon={Clock}       label="Last Analysis"    value={history[0] ? fmtDate(history[0].date) : '—'} color="text-gray-400"
                    sub={history[0]?.shotType || undefined} />
        </motion.div>

        {/* Quick actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="flex flex-wrap items-center gap-3 mb-8"
        >
          <Link to="/analyze"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon">
            <Zap size={14} /> New Analysis
          </Link>
        </motion.div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 p-1 rounded-xl border border-border-dim w-full sm:w-fit"
             style={{ background: 'var(--surface-2)' }}>
          {TABS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex flex-1 sm:flex-none items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all min-h-[44px] ${
                activeTab === key
                  ? 'bg-neon-blue text-black shadow-sm'
                  : 'hover:bg-white/5'
              }`}
              style={activeTab !== key ? { color: 'var(--text-muted)' } : {}}
            >
              <Icon size={13} />
              <span className="hidden sm:inline">{label}</span>
            </button>
          ))}
        </div>

        {/* ── History Tab ───────────────────────────────────────────── */}
        <AnimatePresence mode="wait">
          {activeTab === 'history' && (
            <motion.div key="history" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {history.length === 0 ? (
                <div className="p-16 rounded-2xl border border-border-dim text-center"
                     style={{ background: 'var(--surface-2)' }}>
                  <div className="text-5xl mb-4">🏏</div>
                  <h3 className="font-display font-bold text-lg mb-2" style={{ color: 'var(--text)' }}>No analyses yet</h3>
                  <p className="text-sm mb-6" style={{ color: 'var(--text-muted)' }}>Upload your first batting video to see results here.</p>
                  <Link to="/analyze"
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon">
                    <Zap size={14} /> Analyze Now
                  </Link>
                </div>
              ) : (
                <div className="rounded-2xl border border-border-dim overflow-hidden"
                     style={{ background: 'var(--surface-2)' }}>
                  {/* Desktop header — hidden on mobile */}
                  <div className="hidden sm:grid grid-cols-5 px-6 py-4 border-b border-border-dim text-xs font-bold uppercase tracking-wider"
                       style={{ background: 'var(--surface-3)', color: 'var(--text-dim)' }}>
                    <span className="col-span-2">Shot</span>
                    <span>Score</span>
                    <span>Grade</span>
                    <span>Actions</span>
                  </div>

                  {history.map((h, i) => (
                    <motion.div
                      key={h.videoId}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.04 }}
                    >
                      {/* Mobile card */}
                      <div className="sm:hidden flex items-center gap-3 px-4 py-3.5 border-b border-border-dim last:border-0">
                        <span className="text-xl flex-shrink-0">{shotIcon(h.shotType)}</span>
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-sm truncate" style={{ color: 'var(--text)' }}>{h.shotType || 'Unknown'}</p>
                          <p className="text-xs mt-0.5" style={{ color: 'var(--text-dim)' }}>
                            {fmtDate(h.date)} · {h.score ?? '—'}/100
                          </p>
                        </div>
                        <span className={`inline-flex flex-shrink-0 px-2 py-0.5 rounded-lg border text-xs font-bold ${gradeColor(h.grade)}`}>
                          {h.grade || '—'}
                        </span>
                        <div className="flex items-center gap-1.5 flex-shrink-0">
                          <Link to={`/result/${h.videoId}`}
                            className="flex items-center gap-1 px-2.5 py-2 rounded-lg border border-border-dim text-xs transition-all hover:border-border-soft min-h-[36px]"
                            style={{ color: 'var(--text-muted)' }}>
                            <ExternalLink size={10} /> View
                          </Link>
                          <a href={getPdfUrl(h.videoId)} target="_blank" rel="noreferrer"
                            className="flex items-center gap-1 px-2.5 py-2 rounded-lg bg-neon-blue/10 hover:bg-neon-blue/20 border border-neon-blue/20 text-xs text-neon-blue transition-all min-h-[36px]">
                            <FileText size={10} /> PDF
                          </a>
                        </div>
                      </div>
                      {/* Desktop row */}
                      <div className="hidden sm:grid grid-cols-5 px-6 py-4 items-center border-b border-border-dim last:border-0 hover:bg-white/2 transition-colors">
                        <div className="col-span-2 flex items-center gap-3">
                          <span className="text-2xl">{shotIcon(h.shotType)}</span>
                          <div>
                            <p className="font-semibold text-sm" style={{ color: 'var(--text)' }}>{h.shotType || 'Unknown'}</p>
                            <p className="text-xs mt-0.5" style={{ color: 'var(--text-dim)' }}>{fmtDate(h.date)}</p>
                          </div>
                        </div>
                        <span className="font-display font-bold text-lg" style={{ color: 'var(--text)' }}>
                          {h.score ?? '—'}<span className="text-sm font-normal" style={{ color: 'var(--text-dim)' }}>/100</span>
                        </span>
                        <span className={`inline-flex w-fit px-2.5 py-1 rounded-lg border text-xs font-bold ${gradeColor(h.grade)}`}>
                          {h.grade || '—'}
                        </span>
                        <div className="flex items-center gap-2">
                          <Link to={`/result/${h.videoId}`}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border-dim text-xs transition-all hover:border-border-soft"
                            style={{ color: 'var(--text-muted)' }}>
                            <ExternalLink size={11} /> View
                          </Link>
                          <a href={getPdfUrl(h.videoId)} target="_blank" rel="noreferrer"
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-neon-blue/10 hover:bg-neon-blue/20 border border-neon-blue/20 text-xs text-neon-blue transition-all">
                            <FileText size={11} /> PDF
                          </a>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}

              {history.length > 0 && (
                <p className="text-xs text-center mt-4" style={{ color: 'var(--text-dim)' }}>
                  {user
                    ? <>History saved to your account · {history.length} {history.length === 1 ? 'analysis' : 'analyses'} total</>
                    : <><span>{history.length} analyses on this device</span> · <button onClick={() => onOpenAuth?.('register')} className="text-neon-blue hover:underline">Sign in</button> to save permanently</>
                  }
                </p>
              )}
            </motion.div>
          )}

          {/* ── Shot Tracker Tab ─────────────────────────────────────── */}
          {activeTab === 'strengths' && (
            <motion.div key="strengths" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {Object.keys(shotStats).length === 0 ? (
                <div className="p-12 rounded-2xl border border-border-dim text-center" style={{ background: 'var(--surface-2)' }}>
                  <BarChart3 size={40} className="text-neon-blue mx-auto mb-4 opacity-40" />
                  <h3 className="font-bold text-lg mb-2" style={{ color: 'var(--text)' }}>No data yet</h3>
                  <p className="text-sm mb-5" style={{ color: 'var(--text-muted)' }}>
                    Complete analyses to see your shot strength breakdown here.
                  </p>
                  <Link to="/analyze"
                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all">
                    <Zap size={13} /> Analyze a Video
                  </Link>
                </div>
              ) : (
                <div className="space-y-4">

                  {/* All shot scores */}
                  <div className="p-5 rounded-2xl border border-border-dim" style={{ background: 'var(--surface-2)' }}>
                    <h3 className="font-display font-bold mb-1" style={{ color: 'var(--text)' }}>Shot Tracker</h3>
                    <p className="text-xs mb-4" style={{ color: 'var(--text-muted)' }}>
                      Average score per shot type. Shots below 70 are flagged for improvement.
                    </p>
                    <div className="space-y-3">
                      {Object.entries(shotStats)
                        .sort((a,b) => b[1].avg - a[1].avg)
                        .map(([key, stats], i) => (
                          <ShotStrengthBar key={key} shotKey={key} stats={stats} index={i} />
                        ))
                      }
                    </div>
                  </div>

                  {/* Strong shots */}
                  {Object.entries(shotStats).some(([,s]) => s.avg >= 70) && (
                    <div className="p-5 rounded-2xl border border-neon-green/20 bg-neon-green/5">
                      <h4 className="font-bold text-sm text-neon-green flex items-center gap-2 mb-3">
                        <Star size={14} /> Strong Shots (70+)
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(shotStats)
                          .filter(([,s]) => s.avg >= 70)
                          .map(([k, s]) => (
                            <span key={k} className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-neon-green/20 bg-neon-green/10 text-xs font-semibold text-neon-green">
                              {SHOT_META[k]?.icon} {SHOT_META[k]?.label} — {s.avg}/100
                            </span>
                          ))
                        }
                      </div>
                    </div>
                  )}

                  {/* Weak shots — drills */}
                  {weakShots.length > 0 && (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <AlertCircle size={15} className="text-yellow-400" />
                        <h4 className="font-bold text-sm text-yellow-400">Focus Areas — Recommended Drills</h4>
                      </div>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                        These shots are averaging below 70. Click each to see personalised drill recommendations.
                      </p>
                      {weakShots.map(([key, stats]) => (
                        <DrillCard key={key} shotKey={key} avg={stats.avg} />
                      ))}
                    </div>
                  )}

                  {weakShots.length === 0 && (
                    <div className="p-8 rounded-2xl border border-neon-green/20 bg-neon-green/5 text-center">
                      <CheckCircle2 size={32} className="text-neon-green mx-auto mb-3" />
                      <h3 className="font-bold text-base text-neon-green mb-1">All shots above 70!</h3>
                      <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                        Great form across the board. Keep pushing for A grades.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default DashboardPage;
