import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft, Download, CheckCircle2, XCircle,
  ChevronDown, ChevronUp, FileText,
  Dumbbell, Target, Footprints, Repeat,
  Lightbulb, MessageSquare,
} from 'lucide-react';
import Navbar from '../components/Navbar';
import { getResult, getPdfUrl, getOverlayUrl, saveToHistory, fetchHistoryFromBackend } from '../utils/api';
import { useAuth } from '../context/AuthContext';

// ── Grade & level helpers ─────────────────────────────────────────────────────

const gradeColor = (g = '') => {
  if (['A+','A'].includes(g))  return { text: '#00ff88', bg: 'rgba(0,255,136,0.1)', border: 'rgba(0,255,136,0.25)' };
  if (['B+','B'].includes(g))  return { text: '#00d4ff', bg: 'rgba(0,212,255,0.1)', border: 'rgba(0,212,255,0.25)' };
  if (['C+','C'].includes(g))  return { text: '#f59e0b', bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.25)' };
  return { text: '#ef4444', bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.25)' };
};

const levelColor = (l = '') => {
  const lo = l.toLowerCase();
  if (lo.includes('elite'))        return 'text-neon-green';
  if (lo.includes('advanced'))     return 'text-neon-blue';
  if (lo.includes('intermediate')) return 'text-yellow-400';
  return 'text-orange-400';
};

const drillIcon = (name = '') => {
  const n = name.toLowerCase();
  if (n.includes('foot') || n.includes('balance')) return <Footprints size={18} className="text-orange-400" />;
  if (n.includes('target') || n.includes('zone'))  return <Target     size={18} className="text-red-400" />;
  if (n.includes('repeat') || n.includes('rep'))   return <Repeat     size={18} className="text-blue-400" />;
  return <Dumbbell size={18} className="text-neon-blue" />;
};

const SHOT_LABELS = {
  cover_drive: 'Cover Drive',
  cut_shot:    'Cut Shot',
  defense:     'Defense',
  pull_shot:   'Pull Shot',
  sweep_shot:  'Sweep Shot',
};

// ── Animated score counter ────────────────────────────────────────────────────

const AnimatedScore = ({ target }) => {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let start = 0;
    const step = Math.ceil(target / 40);
    const interval = setInterval(() => {
      start = Math.min(start + step, target);
      setDisplay(start);
      if (start >= target) clearInterval(interval);
    }, 30);
    return () => clearInterval(interval);
  }, [target]);
  return <>{display}</>;
};


// ── Shot facts ────────────────────────────────────────────────────────────────

const SHOT_FACTS = {
  cover_drive: {
    emoji: '🏏', tagline: 'The King of Elegant Shots',
    keyPoints: ['Step front foot towards the ball', 'Keep head still — eyes level at contact', 'Drive through the line, don\'t slog', 'Full follow-through, bat finishing high', 'Weight fully on front foot at impact'],
    players: [
      { name: 'Babar Azam',      note: 'Textbook cover drive — best in modern cricket' },
      { name: 'Mohammad Yousuf', note: 'Mastered off-side play with exceptional timing' },
      { name: 'Zaheer Abbas',    note: '"Asian Bradman" — built his career on the cover drive' },
    ],
    tip:  'Drive through the line with a straight bat. Let the ball come to you — don\'t chase it.',
    fact: 'Neville Cardus called the cover drive "the champagne of strokes." The most aesthetically pleasing shot in cricket.',
    beginnerNote: 'Step your front foot towards the ball, keep your head still, and swing the bat through like a pendulum.',
  },
  cut_shot: {
    emoji: '⚡', tagline: 'The Punisher of Short Balls',
    keyPoints: ['Pick up the short ball early from the bowler\'s hand', 'Back foot steps back and across towards off stump', 'Stay tall — don\'t crouch or lean back too far', 'Play late — let the ball arrive alongside you', 'Punch it, don\'t slog — control over power'],
    players: [
      { name: 'Younis Khan',     note: '10,000 Test runs — cut shot was a primary weapon' },
      { name: 'Inzamam-ul-Haq', note: 'Deceptive footwork made his cut shot devastating' },
      { name: 'Saeed Anwar',    note: 'Elegant cut through point was his signature' },
    ],
    tip:  'Watch the ball early, stay tall, and play late. The cut is all about patience — wait for the short, wide ball.',
    fact: 'Playing the cut on a good length is one of the most common ways to get caught in the slip cordon.',
    beginnerNote: 'When the ball bounces short and wide, step back and punch it towards point — like a horizontal tennis backhand.',
  },
  defense: {
    emoji: '🛡️', tagline: 'The Foundation of Every Great Innings',
    keyPoints: ['Move front foot towards the ball\'s line', 'Head directly over the front knee', 'Bat face angled downward to kill the ball', 'Soft hands — present the bat, don\'t push', 'Eyes stay on the ball through contact'],
    players: [
      { name: 'Younis Khan',     note: '10,099 Test runs built on an impenetrable defence' },
      { name: 'Hanif Mohammad',  note: 'Batted 970 mins for 337 — the art of patience' },
      { name: 'Mohammad Yousuf', note: 'Near-perfect technique through cover and mid-on' },
    ],
    tip:  'Head over the ball. Soft hands — don\'t push at it. The bat face should angle down, not square.',
    fact: 'Hanif Mohammad\'s 337 against West Indies (1958) took 16 hours 10 minutes — the longest innings in Test history at the time.',
    beginnerNote: 'Lean forward, head over the ball, and let it die at your feet. Don\'t push — just present the bat.',
  },
  pull_shot: {
    emoji: '💥', tagline: 'The Dominator of Short-Pitch Bowling',
    keyPoints: ['Pick up the short ball early from the bowler\'s hand', 'Get inside the ball\'s line', 'Rock back on the back foot, pivot on it', 'Roll wrists through impact to keep it down', 'Head steady — eyes track ball all the way'],
    players: [
      { name: 'Javed Miandad', note: 'His 1986 Sharjah last-ball six is cricket\'s most iconic pull' },
      { name: 'Babar Azam',    note: 'Rolls wrists to keep the pull shot safe and powerful' },
      { name: 'Imran Khan',    note: 'Aggressive puller who unnerved even the fastest bowlers' },
    ],
    tip:  'Get inside the line. Pivot on the back foot, stay balanced. Roll your wrists to keep the ball down.',
    fact: 'Javed Miandad\'s last-ball six off Chetan Sharma in Sharjah 1986 is considered the greatest finish in ODI history.',
    beginnerNote: 'Step back, swing across like a baseball hit, and roll your wrists over so the ball stays low.',
  },
  sweep_shot: {
    emoji: '🌀', tagline: 'The Spin Killer',
    keyPoints: ['Get to the pitch with the front foot', 'Front knee comes down low', 'Head stays over the front knee', 'Horizontal bat swings low to high', 'Eyes on ball until contact'],
    players: [
      { name: 'Mohammad Hafeez', note: 'Aggressive sweeper — neutralised top spinners worldwide' },
      { name: 'Shoaib Malik',    note: 'Used the sweep to dominate sub-continental pitches' },
      { name: 'Azhar Ali',       note: 'Patient sweeper who converted dot balls into boundaries' },
    ],
    tip:  'Get to the pitch of the ball. Open your hips early, keep your front knee down, and swing through the line.',
    fact: 'The sweep became a signature weapon for Pakistani batters against spin on subcontinental tracks.',
    beginnerNote: 'Kneel on your front knee and swat the ball around towards fine leg — like sweeping a floor.',
  },
};

const ShotFacts = ({ shot }) => {
  const key  = shot?.toLowerCase().replace(/ /g, '_');
  const data = SHOT_FACTS[key];
  if (!data) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
      className="p-5 rounded-2xl border border-border-dim space-y-4"
      style={{ background: 'var(--surface-2)' }}
    >
      <div className="flex items-center gap-3">
        <span className="text-2xl">{data.emoji}</span>
        <div>
          <h4 className="font-display font-bold text-sm" style={{ color: 'var(--text)' }}>{data.tagline}</h4>
          <p className="text-xs" style={{ color: 'var(--text-dim)' }}>Players to study</p>
        </div>
      </div>

      {/* Beginner-friendly note */}
      <div className="p-3 rounded-xl border border-neon-blue/15" style={{ background: 'rgba(0,212,255,0.05)' }}>
        <div className="flex items-start gap-2">
          <Lightbulb size={13} className="text-neon-blue flex-shrink-0 mt-0.5" />
          <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>
            <span className="text-neon-blue font-semibold">Simply put: </span>
            {data.beginnerNote}
          </p>
        </div>
      </div>

      {/* Players */}
      <div className="space-y-2">
        {data.players.map((p, i) => (
          <div key={i} className="flex items-start gap-2.5">
            <div className="w-6 h-6 rounded-full bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-neon-blue text-[10px] font-bold">{i + 1}</span>
            </div>
            <div>
              <span className="text-xs font-semibold" style={{ color: 'var(--text)' }}>{p.name}</span>
              <p className="text-[11px] leading-relaxed" style={{ color: 'var(--text-dim)' }}>{p.note}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Coach tip */}
      <div className="p-3 rounded-xl border border-neon-green/15" style={{ background: 'rgba(0,255,136,0.04)' }}>
        <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>
          <span className="text-neon-green font-semibold">Coach Tip: </span>{data.tip}
        </p>
      </div>

      {/* Fun fact */}
      <div className="p-3 rounded-xl border border-border-dim" style={{ background: 'var(--surface-3)' }}>
        <p className="text-[11px] leading-relaxed italic" style={{ color: 'var(--text-dim)' }}>
          <span className="font-semibold not-italic" style={{ color: 'var(--text-muted)' }}>Did you know? </span>
          {data.fact}
        </p>
      </div>
    </motion.div>
  );
};

// ── Check item (biomechanics) ─────────────────────────────────────────────────

const CheckItem = ({ check }) => {
  const [open, setOpen] = useState(false);
  const good = !check.is_error;
  return (
    <div className="rounded-xl overflow-hidden transition-colors hover:bg-white/2">
      <button onClick={() => setOpen(o => !o)} className="w-full flex items-center justify-between p-3.5 text-left">
        <div className="flex items-center gap-3">
          {good
            ? <CheckCircle2 size={17} className="text-neon-green flex-shrink-0" />
            : <XCircle      size={17} className="text-red-400 flex-shrink-0" />
          }
          <span className="text-sm font-medium" style={{ color: 'var(--text)' }}>{check.name}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${good ? 'text-neon-green bg-neon-green/10' : 'text-red-400 bg-red-400/10'}`}>
            {check.status}
          </span>
          {open ? <ChevronUp size={14} style={{ color: 'var(--text-dim)' }} /> : <ChevronDown size={14} style={{ color: 'var(--text-dim)' }} />}
        </div>
      </button>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height:0 }} animate={{ height:'auto' }} exit={{ height:0 }} className="overflow-hidden">
            <div className="pb-4 px-4 pl-11 space-y-1.5 text-xs" style={{ color: 'var(--text-muted)' }}>
              <div className="flex items-center justify-between">
                <span style={{ color: 'var(--text-dim)' }}>Measured</span>
                <span className="font-mono font-semibold" style={{ color: 'var(--text)' }}>{check.value}</span>
              </div>
              <div className="flex items-center justify-between">
                <span style={{ color: 'var(--text-dim)' }}>Target Range</span>
                <span className="font-mono text-neon-blue">{check.ideal_range}</span>
              </div>
              <p className="mt-2 leading-relaxed border-t border-border-dim pt-2 italic"
                 style={{ color: 'var(--text-muted)' }}>"{check.advice}"</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ── Beginner-friendly summary ─────────────────────────────────────────────────

const GRADE_MESSAGE = {
  'A+': 'Outstanding! You\'re performing at elite level. Your technique is close to professional standards.',
  'A':  'Excellent work! This is advanced-level batting. A few small tweaks and you\'re elite.',
  'B+': 'Really good shot! You\'ve got the core technique. Focus on the improvements below to get to A grade.',
  'B':  'Good batting! You\'re above average. Keep working on the drill recommendations.',
  'C+': 'Decent attempt. The fundamentals are there — you need more practice on the specific points below.',
  'C':  'Keep going! Cricket takes time. Focus on one improvement at a time, not everything at once.',
  'D':  'Don\'t give up — everyone starts here. Work through the drills below slowly and consistently.',
  'F':  'This might be a new shot for you, or the video angle made it hard to assess. Try again with better conditions.',
};

// ── Main component ────────────────────────────────────────────────────────────

const ResultPage = ({ onOpenAuth }) => {
  const { videoId }  = useParams();
  const navigate     = useNavigate();
  const { user }     = useAuth();
  const pollRef      = useRef(null);
  const savedRef     = useRef(false);

  const [data,          setData]         = useState(null);
  const [loading,       setLoading]      = useState(true);
  const [error,         setError]        = useState(null);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [isPortrait,    setIsPortrait]   = useState(false);
  const [gradeVisible,  setGradeVisible] = useState(false);
  const videoPlayerRef = useRef(null);

  const handleVideoMetadata = () => {
    const v = videoPlayerRef.current;
    if (v) setIsPortrait(v.videoHeight > v.videoWidth);
  };

  const applySpeed = (s) => {
    setPlaybackSpeed(s);
    if (videoPlayerRef.current) videoPlayerRef.current.playbackRate = s;
  };

  useEffect(() => {
    window.scrollTo(0, 0);
    savedRef.current = false;
    let failCount = 0;

    const fetchData = async () => {
      try {
        const res = await getResult(videoId);
        if (res.status === 'completed') {
          setData(res);
          setLoading(false);
          clearInterval(pollRef.current);
          setTimeout(() => setGradeVisible(true), 500);
          if (!savedRef.current) {
            savedRef.current = true;
            const fa = (typeof res.result?.form_analysis === 'string'
              ? JSON.parse(res.result.form_analysis)
              : res.result?.form_analysis) || {};
            // Save to backend (if logged in) + localStorage cache
            await saveToHistory(videoId, res.result?.prediction, fa.overall_score, fa.grade, user?.id || null);
            // Mark free analysis as used for guests
            if (!user) localStorage.setItem('be_free_used', '1');
          }
        } else if (res.status === 'failed') {
          setError(res.error || 'Analysis failed');
          setLoading(false);
          clearInterval(pollRef.current);
        }
        failCount = 0;
      } catch {
        failCount++;
        if (failCount > 15) {
          setError('Connection lost');
          setLoading(false);
          clearInterval(pollRef.current);
        }
      }
    };

    fetchData();
    pollRef.current = setInterval(fetchData, 2000);
    return () => clearInterval(pollRef.current);
  }, [videoId]);

  if (loading) return <LoadingScreen />;
  if (error)   return <ErrorScreen error={error} onBack={() => navigate('/')} />;

  const result = data.result || {};
  const fa     = (typeof result.form_analysis === 'string'
    ? JSON.parse(result.form_analysis)
    : result.form_analysis) || {};

  const shot        = result.prediction      || data.shot_type   || '—';
  const score       = fa.overall_score       ?? data.form_score  ?? 0;
  const grade       = fa.grade               ?? '—';
  const level       = fa.performance_level   ?? '—';
  const checks      = fa.checks              ?? [];
  const drills      = fa.recommended_drills  ?? [];
  const summary     = fa.summary             ?? '';
  const strengths   = fa.strengths           ?? [];
  const improvements = fa.key_improvements   ?? [];
  const gc       = gradeColor(grade);
  const gradeMsg = GRADE_MESSAGE[grade] || '';

  return (
    <div className="min-h-screen pb-20" style={{ background: 'var(--bg)' }}>
      <Navbar onOpenAuth={onOpenAuth} />

      <main className="max-w-7xl mx-auto px-4 pt-24 sm:pt-28">


        {/* Top bar */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <button onClick={() => navigate('/analyze')}
            className="flex items-center gap-2 text-sm transition-colors hover:text-neon-blue"
            style={{ color: 'var(--text-muted)' }}>
            <ArrowLeft size={16} /> Back to Analysis
          </button>
          <a href={getPdfUrl(videoId)} target="_blank" rel="noreferrer"
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-border-dim hover:border-neon-blue/40 transition-all text-sm font-medium"
            style={{ background: 'var(--surface-2)', color: 'var(--text)' }}>
            <Download size={15} /> Download Full PDF Report
          </a>
        </div>

        {/* ── Shot header card ─────────────────────────────────────── */}
        <motion.div
          initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }}
          className="p-6 sm:p-8 rounded-2xl border border-border-dim mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6"
          style={{ background: 'var(--surface-2)' }}
        >
          <div className="flex-1">
            <p className="text-xs font-semibold uppercase tracking-widest mb-1" style={{ color: 'var(--text-dim)' }}>Shot Detected</p>
            <h1 className="text-3xl sm:text-4xl font-display font-extrabold mb-1" style={{ color: 'var(--text)' }}>{shot}</h1>

            {/* Beginner grade message */}
            {gradeMsg && (
              <p className="text-sm mt-3 leading-relaxed max-w-sm"
                 style={{ color: 'var(--text-muted)' }}>
                {gradeMsg}
              </p>
            )}
          </div>

          <div className="flex items-center gap-4 sm:gap-6 flex-wrap sm:flex-nowrap">
            {/* Animated Score */}
            <div className="text-center">
              <p className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--text-dim)' }}>Score</p>
              <p className="text-4xl sm:text-5xl font-display font-black" style={{ color: 'var(--text)' }}>
                <AnimatedScore target={score} />
              </p>
              <p className="text-xs mt-0.5" style={{ color: 'var(--text-dim)' }}>/100</p>
            </div>

            {/* Animated Grade */}
            <div className="text-center">
              <p className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--text-dim)' }}>Grade</p>
              <AnimatePresence>
                {gradeVisible && (
                  <motion.div
                    key="grade"
                    className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl flex items-center justify-center border-2 text-xl sm:text-2xl font-display font-black grade-reveal"
                    style={{ color: gc.text, background: gc.bg, borderColor: gc.border }}
                  >
                    {grade}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Level */}
            <div className="text-center hidden sm:block">
              <p className="text-xs uppercase tracking-wider mb-1" style={{ color: 'var(--text-dim)' }}>Level</p>
              <p className={`font-display font-bold text-xl ${levelColor(level)}`}>{level}</p>
            </div>
          </div>
        </motion.div>

        {/* ── Main grid ─────────────────────────────────────────────── */}
        <div className="grid lg:grid-cols-2 gap-6">

          {/* LEFT — Video + coaching */}
          <div className="space-y-6">

            {/* Video player */}
            <motion.div
              initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.1 }}
              className="space-y-2"
            >
              <div className={`bg-black rounded-2xl overflow-hidden border border-border-dim shadow-card flex items-center justify-center ${
                isPortrait ? 'max-h-[72vh]' : 'aspect-video'
              }`}>
                <video
                  ref={videoPlayerRef}
                  src={getOverlayUrl(videoId)}
                  controls autoPlay loop
                  onLoadedMetadata={handleVideoMetadata}
                  className={isPortrait ? 'max-h-[72vh] w-auto rounded-2xl' : 'w-full h-full object-contain'}
                />
              </div>
              {/* Playback controls */}
              <div className="flex items-center gap-2 px-1">
                <span className="text-xs font-medium" style={{ color: 'var(--text-dim)' }}>Speed:</span>
                {[0.25, 0.5, 0.75, 1].map(s => (
                  <button
                    key={s}
                    onClick={() => applySpeed(s)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all ${
                      playbackSpeed === s
                        ? 'bg-neon-blue text-black'
                        : 'border border-border-dim hover:border-border-soft'
                    }`}
                    style={playbackSpeed !== s ? { background: 'var(--surface-3)', color: 'var(--text-muted)' } : {}}
                  >
                    {s}×
                  </button>
                ))}
                <span className="ml-auto text-[10px]" style={{ color: 'var(--text-dim)' }}>Slow-motion for detail</span>
              </div>
            </motion.div>

            {/* What this means (beginner-friendly coach section) */}
            <motion.div
              initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.12 }}
              className="p-5 rounded-2xl border border-neon-blue/15 space-y-3"
              style={{ background: 'rgba(0,212,255,0.04)' }}
            >
              <div className="flex items-center gap-2">
                <MessageSquare size={15} className="text-neon-blue" />
                <h3 className="font-display font-bold text-sm text-neon-blue">What Does This Mean?</h3>
              </div>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>
                {summary
                  ? `"${summary}"`
                  : 'Your shot has been analysed against MCC and ECB coaching standards. The checks below show each aspect of your technique — green means you nailed it, red means there\'s room to improve.'}
              </p>
              {(strengths.length > 0 || improvements.length > 0) && (
                <div className="grid sm:grid-cols-2 gap-3 pt-1">
                  <div>
                    <p className="text-xs font-bold text-neon-green mb-1.5 flex items-center gap-1.5">
                      <CheckCircle2 size={12} /> What you did well
                    </p>
                    {strengths.map((s,i) => (
                      <p key={i} className="text-xs leading-relaxed mb-1" style={{ color: 'var(--text-muted)' }}>✦ {s}</p>
                    ))}
                  </div>
                  <div>
                    <p className="text-xs font-bold text-neon-blue mb-1.5 flex items-center gap-1.5">
                      <TrendingUpIcon size={12} /> What to work on
                    </p>
                    {improvements.map((s,i) => (
                      <p key={i} className="text-xs leading-relaxed mb-1" style={{ color: 'var(--text-muted)' }}>→ {s}</p>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>

            {/* Key Points to Master */}
            {(() => {
              const shotKey = shot?.toLowerCase().replace(/ /g, '_');
              const kp = SHOT_FACTS[shotKey]?.keyPoints;
              if (!kp?.length) return null;
              return (
                <motion.div
                  initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.18 }}
                  className="p-5 rounded-2xl border border-border-dim space-y-3"
                  style={{ background: 'var(--surface-2)' }}
                >
                  <div className="flex items-center gap-2">
                    <Lightbulb size={15} className="text-yellow-400" />
                    <h3 className="font-display font-bold text-sm" style={{ color: 'var(--text)' }}>Key Points to Master</h3>
                  </div>
                  <div className="space-y-2">
                    {kp.map((point, i) => (
                      <div key={i} className="flex items-start gap-3">
                        <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 text-[11px] font-bold"
                             style={{ background: 'rgba(245,158,11,0.12)', border: '1px solid rgba(245,158,11,0.25)', color: '#f59e0b' }}>
                          {i + 1}
                        </div>
                        <p className="text-sm leading-relaxed pt-0.5" style={{ color: 'var(--text-muted)' }}>{point}</p>
                      </div>
                    ))}
                  </div>
                </motion.div>
              );
            })()}

          </div>

          {/* RIGHT — Analysis panel */}
          <div className="space-y-5">

            {/* Biomechanics */}
            <motion.div
              initial={{ opacity:0, x:20 }} animate={{ opacity:1, x:0 }} transition={{ delay:0.15 }}
              className="rounded-2xl border border-border-dim overflow-hidden"
              style={{ background: 'var(--surface-2)' }}
            >
              <div className="px-5 py-4 border-b border-border-dim">
                <h3 className="font-display font-bold text-sm" style={{ color: 'var(--text)' }}>
                  Technique Breakdown
                </h3>
                <p className="text-xs mt-0.5" style={{ color: 'var(--text-dim)' }}>
                  Click any item to see what was measured and the ideal range
                </p>
              </div>
              <div className="p-3 space-y-0.5">
                {checks.length ? checks.map((c,i) => <CheckItem key={i} check={c} />) : (
                  <p className="text-xs p-4" style={{ color: 'var(--text-dim)' }}>No technique checks available.</p>
                )}
              </div>
            </motion.div>

            {/* Drills */}
            <motion.div
              initial={{ opacity:0, x:20 }} animate={{ opacity:1, x:0 }} transition={{ delay:0.2 }}
              className="rounded-2xl border border-border-dim overflow-hidden"
              style={{ background: 'var(--surface-2)' }}
            >
              <div className="px-5 py-4 border-b border-border-dim flex items-center gap-2">
                <Dumbbell size={15} className="text-neon-blue" />
                <h3 className="font-display font-bold text-sm" style={{ color: 'var(--text)' }}>Your Practice Drills</h3>
              </div>
              <div className="p-4 space-y-3">
                {drills.length ? drills.map((d,i) => (
                  <div key={i} className="flex gap-4 p-4 rounded-xl border border-border-dim hover:border-border-soft transition-colors"
                       style={{ background: 'var(--surface-3)' }}>
                    <div className="mt-0.5 flex-shrink-0">{drillIcon(d.name)}</div>
                    <div>
                      <h4 className="font-bold text-sm mb-1" style={{ color: 'var(--text)' }}>{d.name}</h4>
                      <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>{d.description}</p>
                    </div>
                  </div>
                )) : (
                  <p className="text-sm italic p-2" style={{ color: 'var(--text-dim)' }}>
                    No specific drills needed — keep it up!
                  </p>
                )}
              </div>
            </motion.div>

            {/* Shot facts — players, tips, fun fact (below technical content) */}
            <ShotFacts shot={shot} />

          </div>
        </div>

        {/* PDF Banner */}
        <motion.div
          initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.3 }}
          className="mt-8 p-6 rounded-2xl border border-neon-blue/15 flex flex-col sm:flex-row items-center justify-between gap-4"
          style={{ background: 'linear-gradient(135deg, rgba(0,212,255,0.05) 0%, rgba(0,255,136,0.05) 100%)' }}
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center flex-shrink-0">
              <FileText size={22} className="text-neon-blue" />
            </div>
            <div>
              <h4 className="font-display font-bold" style={{ color: 'var(--text)' }}>Full PDF Report Available</h4>
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                Includes ECB/MCC standards table, biomechanics, personalised drills, and coaching notes.
              </p>
            </div>
          </div>
          <a href={getPdfUrl(videoId)} target="_blank" rel="noreferrer"
            className="flex-shrink-0 flex items-center gap-2 px-6 py-3 rounded-xl bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon">
            <Download size={15} /> Download Report
          </a>
        </motion.div>

        {/* Guest sign-up CTA — shown after first free analysis */}
        {!user && (
          <motion.div
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
            className="mt-6 p-6 rounded-2xl border border-neon-green/20 flex flex-col sm:flex-row items-center justify-between gap-4"
            style={{ background: 'linear-gradient(135deg, rgba(0,255,136,0.06) 0%, rgba(0,212,255,0.06) 100%)' }}
          >
            <div>
              <h4 className="font-display font-bold text-base" style={{ color: 'var(--text)' }}>
                You've used your free analysis
              </h4>
              <p className="text-sm mt-1" style={{ color: 'var(--text-muted)' }}>
                Sign up free to get unlimited analyses, save your history, and track your progress over time.
              </p>
            </div>
            <div className="flex gap-3 flex-shrink-0">
              <button
                onClick={() => onOpenAuth('login')}
                className="px-5 py-2.5 rounded-xl border border-border-soft text-sm font-semibold hover:border-neon-blue/40 transition-all"
                style={{ color: 'var(--text)' }}
              >
                Sign In
              </button>
              <button
                onClick={() => onOpenAuth('register')}
                className="px-5 py-2.5 rounded-xl bg-neon-green text-black font-bold text-sm hover:opacity-90 transition-all"
              >
                Sign Up Free
              </button>
            </div>
          </motion.div>
        )}
      </main>
    </div>
  );
};

// ── Inline icon (avoid importing TrendingUp twice) ────────────────────────────

const TrendingUpIcon = ({ size, className }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
       strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
    <polyline points="17 6 23 6 23 12" />
  </svg>
);

// ── Cricket-themed loading screen ─────────────────────────────────────────────

const CricketBall = () => (
  <svg width="60" height="60" viewBox="0 0 60 60" className="cricket-ball-bounce">
    <circle cx="30" cy="30" r="28" fill="#dc2626" />
    <path d="M18 13 Q30 27 42 13" stroke="#fff" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
    <path d="M18 47 Q30 33 42 47" stroke="#fff" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
    <path d="M12 22 Q27 30 12 38" stroke="#fff" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
    <path d="M48 22 Q33 30 48 38" stroke="#fff" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
  </svg>
);

const LoadingScreen = () => {
  const [dots, setDots] = useState('');
  const [stage, setStage] = useState(0);
  const STAGES = [
    'Extracting pose keypoints…',
    'Computing biomechanical angles…',
    'Running stacking ensemble…',
    'Generating your coaching report…',
  ];
  useEffect(() => {
    const d = setInterval(() => setDots(p => p.length >= 3 ? '' : p + '.'), 400);
    const s = setInterval(() => setStage(p => (p + 1) % STAGES.length), 2200);
    return () => { clearInterval(d); clearInterval(s); };
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center p-4"
         style={{ background: 'var(--bg)' }}>
      <div className="mb-8 flex flex-col items-center">
        <CricketBall />
        {/* Shadow */}
        <div className="cricket-ball-shadow w-12 h-3 rounded-full bg-black/30 mt-2" />
      </div>

      <h2 className="text-2xl font-display font-bold mb-2" style={{ color: 'var(--text)' }}>
        Analysing Your Shot{dots}
      </h2>
      <AnimatePresence mode="wait">
        <motion.p
          key={stage}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -5 }}
          className="text-sm mb-6"
          style={{ color: 'var(--text-muted)' }}
        >
          {STAGES[stage]}
        </motion.p>
      </AnimatePresence>

      {/* Loading bar */}
      <div className="w-48 h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--border)' }}>
        <motion.div
          className="h-full rounded-full"
          style={{ background: 'linear-gradient(90deg, #00d4ff, #00ff88)' }}
          animate={{ width: ['0%', '85%'] }}
          transition={{ duration: 8, ease: 'easeInOut' }}
        />
      </div>

      <p className="text-xs mt-4" style={{ color: 'var(--text-dim)' }}>
        Comparing against ECB & MCC standards · V9.5 Ensemble (94.71% accuracy)
      </p>
    </div>
  );
};

const ErrorScreen = ({ error, onBack }) => (
  <div className="min-h-screen flex flex-col items-center justify-center text-center p-4"
       style={{ background: 'var(--bg)' }}>
    <XCircle size={48} className="text-red-400 mb-4" />
    <h2 className="text-2xl font-display font-bold mb-2" style={{ color: 'var(--text)' }}>Analysis Failed</h2>
    <p className="text-sm mb-6 max-w-sm" style={{ color: 'var(--text-muted)' }}>{error}</p>
    <button onClick={onBack}
      className="px-6 py-3 bg-neon-blue text-black rounded-xl font-bold text-sm hover:bg-[#33deff] transition-all">
      Try Again
    </button>
  </div>
);

export default ResultPage;
