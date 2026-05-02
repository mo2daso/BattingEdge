import React, { useRef, useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, useInView, animate } from 'framer-motion';
import {
  Zap, ArrowRight, Upload, BrainCircuit, FileText,
  Scan, BarChart3, Layers, ShieldCheck, Activity,
  ChevronDown, Users, Star, TrendingUp,
} from 'lucide-react';
import Navbar from '../components/Navbar';

/* ── Scroll-triggered fade-up ─────────────────────────────────────────────── */
const FadeUp = ({ children, delay = 0, className = '' }) => {
  const ref   = useRef(null);
  const inView = useInView(ref, { once: true, margin: '-80px' });
  return (
    <motion.div ref={ref}
      initial={{ opacity: 0, y: 32 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.65, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

/* ── Animated counter ─────────────────────────────────────────────────────── */
const Counter = ({ to, suffix = '', prefix = '' }) => {
  const [val, setVal] = useState(0);
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });
  useEffect(() => {
    if (!inView) return;
    const ctrl = animate(0, to, {
      duration: 2,
      ease: 'easeOut',
      onUpdate: (v) => setVal(Math.round(v)),
    });
    return ctrl.stop;
  }, [inView, to]);
  return <span ref={ref}>{prefix}{val.toLocaleString()}{suffix}</span>;
};

/* ── Data ─────────────────────────────────────────────────────────────────── */
const SHOTS = [
  { name: 'Cover Drive',  icon: '🏏', color: 'neon-blue',  desc: 'The signature front-foot attacking shot. Elbow angle, bat swing plane, weight transfer.' },
  { name: 'Cut Shot',     icon: '⚡', color: 'neon-green', desc: 'Short ball dispatched through point. Head stability, hip rotation, bat speed.' },
  { name: 'Defense',      icon: '🛡️', color: 'neon-blue',  desc: 'The foundation of batting. Vertical bat, soft hands, stride depth against ECB standard.' },
  { name: 'Pull Shot',    icon: '🔥', color: 'neon-green', desc: 'Aggressive short-ball play. Shoulder alignment, body pivot, follow-through arc.' },
  { name: 'Sweep Shot',   icon: '💫', color: 'neon-blue',  desc: 'Front-foot sweep. Head position, front knee angle, bat contact zone.' },
];

const STANDARDS = [
  { shot: 'Cover Drive', metric: 'Elbow Angle',      standard: '90–130°',          icon: '📐' },
  { shot: 'Defense',     metric: 'Bat Angle',         standard: '0–15° vertical',   icon: '🏏' },
  { shot: 'Pull Shot',   metric: 'Hip Rotation',      standard: '> 45°',            icon: '🔄' },
  { shot: 'Cut Shot',    metric: 'Head Stability',    standard: '< 10° drift',      icon: '👁️' },
  { shot: 'Sweep Shot',  metric: 'Front Knee Bend',   standard: '130–160°',         icon: '🦵' },
];

const FEATURES = [
  { icon: Scan,         title: 'MediaPipe Skeleton',    desc: '33 body landmarks tracked at 30fps — stance, swing, and follow-through measured with precision.',  color: 'text-neon-blue' },
  { icon: BrainCircuit, title: 'V9.5 Stacking Ensemble',desc: 'BiLSTM + XGBoost + Random Forest meta-model achieves 94.71% validation accuracy.',                color: 'text-neon-green' },
  { icon: BarChart3,    title: 'Biomechanics Metrics',  desc: 'Elbow angles, head drift, knee extension, and hip rotation quantified against professional norms.',color: 'text-neon-blue' },
  { icon: Layers,       title: 'ECB/MCC Standards',     desc: 'Your technique benchmarked against England Cricket Board Level 3 coaching guidelines.',            color: 'text-neon-green' },
];

const PROBLEMS = [
  { num: '130M+', label: 'Pakistanis who follow cricket',   icon: '🏏' },
  { num: 'PKR 5,000+', label: 'Cost of a single coaching session', icon: '💸' },
  { num: '< 1%',   label: 'Of youngsters reach certified coaches', icon: '📉' },
  { num: '0',      label: 'Cost with BattingEdge',          icon: '✅' },
];

/* ──────────────────────────────────────────────────────────────────────────── */

const LandingPage = ({ onOpenAuth }) => {
  const location = useLocation();

  useEffect(() => {
    const hash = location.state?.scrollTo;
    if (!hash) return;
    // Small delay lets the page render before scrolling
    const t = setTimeout(() => {
      document.querySelector(hash)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 120);
    return () => clearTimeout(t);
  }, [location.state]);

  return (
    <div className="min-h-screen bg-jet-black text-white">
      <Navbar onOpenAuth={onOpenAuth} />

      {/* ═══ HERO ════════════════════════════════════════════════════════════ */}
      <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-4 pt-24 pb-20 hero-grid overflow-hidden">

        {/* Background glows */}
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-neon-blue/6 rounded-full blur-[130px] pointer-events-none" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-neon-green/4 rounded-full blur-[100px] pointer-events-none" />

        {/* Badge */}
        <motion.div initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.1 }}
          className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm font-medium text-gray-300 mb-8"
        >
          <span className="text-base">🇵🇰</span>
          Pakistan's First Free AI Batting Coach
          <span className="w-px h-4 bg-white/20" />
          <span className="text-neon-green text-xs font-bold">100% FREE</span>
        </motion.div>

        {/* Headline */}
        <motion.h1 initial={{ opacity:0, y:28 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.2, duration:0.7, ease:[0.22,1,0.36,1] }}
          className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-display font-extrabold tracking-tight leading-[1.05] max-w-5xl mb-5"
        >
          Train Like a Pro.<br />
          <span className="gradient-text text-glow">Coach Yourself.</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p initial={{ opacity:0, y:24 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.3 }}
          className="text-lg sm:text-xl text-gray-400 max-w-2xl mb-10 leading-relaxed"
        >
          Upload your batting video. Get instant biomechanical feedback — the same quality a
          <span className="text-white font-medium"> certified ECB Level 3 coach</span> would give.
          No fees. No appointments. Just results.
        </motion.p>

        {/* CTAs */}
        <motion.div initial={{ opacity:0, y:24 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.4 }}
          className="flex flex-col sm:flex-row items-center gap-4 mb-14"
        >
          <Link to="/analyze"
            className="flex items-center gap-2.5 px-8 py-4 rounded-full bg-neon-blue text-black font-bold text-base hover:bg-[#33deff] transition-all shadow-neon hover:shadow-neon-strong hover:-translate-y-0.5"
          >
            <Zap size={18} /> Analyze Your Shot — Free
          </Link>
          <a href="#problem" onClick={e => { e.preventDefault(); document.querySelector('#problem')?.scrollIntoView({ behavior:'smooth' }); }}
            className="flex items-center gap-2 px-6 py-4 rounded-full border border-border-soft text-white font-medium text-base hover:border-white/30 hover:bg-white/5 transition-all"
          >
            Why BattingEdge? <ArrowRight size={16} />
          </a>
        </motion.div>

        {/* Trust stats */}
        <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ delay:0.55 }}
          className="flex flex-wrap justify-center gap-8 text-sm text-gray-500"
        >
          {[
            { icon: Activity,    label: '94.71% Accuracy' },
            { icon: ShieldCheck, label: 'ECB & MCC Standards' },
            { icon: Zap,         label: 'Results in 30 Seconds' },
            { icon: Star,        label: 'Free Forever' },
          ].map(({ icon: Icon, label }) => (
            <div key={label} className="flex items-center gap-2">
              <Icon size={15} className="text-neon-blue" />
              {label}
            </div>
          ))}
        </motion.div>

        {/* Scroll cue */}
        <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ delay:1.2 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 text-gray-600"
        >
          <span className="text-xs tracking-widest uppercase">Scroll</span>
          <ChevronDown size={16} className="animate-bounce" />
        </motion.div>
      </section>

      {/* ═══ THE PROBLEM ═════════════════════════════════════════════════════ */}
      <section id="problem" className="py-24 lg:py-32 px-4 bg-surface relative overflow-hidden">
        <div className="absolute inset-0 hero-grid opacity-30 pointer-events-none" />
        <div className="max-w-6xl mx-auto relative z-10">
          <FadeUp className="text-center mb-16">
            <span className="text-xs font-semibold tracking-widest uppercase text-neon-green mb-3 block">The Reality</span>
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-white mb-4">
              Great Cricket Talent.<br />
              <span className="text-gray-500">No Access to Great Coaching.</span>
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Pakistan produces world-class cricketers — Babar Azam, Shaheen Afridi, Wasim Akram.
              But for every star, thousands of talented youngsters never get professional feedback
              because certified coaching is simply out of reach.
            </p>
          </FadeUp>

          {/* Problem stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
            {PROBLEMS.map(({ num, label, icon }, i) => (
              <FadeUp key={label} delay={i * 0.08}>
                <div className="p-6 rounded-2xl bg-surface-2 border border-border-dim text-center card-hover">
                  <div className="text-3xl mb-3">{icon}</div>
                  <div className="text-3xl font-display font-black text-white mb-2">{num}</div>
                  <p className="text-gray-500 text-sm leading-snug">{label}</p>
                </div>
              </FadeUp>
            ))}
          </div>

          {/* Solution callout */}
          <FadeUp>
            <div className="relative p-8 lg:p-12 rounded-3xl overflow-hidden"
              style={{ background: 'linear-gradient(135deg, rgba(0,212,255,0.06), rgba(0,255,136,0.04))', border: '1px solid rgba(0,212,255,0.15)' }}
            >
              <div className="absolute top-0 right-0 w-64 h-64 bg-neon-blue/5 rounded-full blur-[60px] pointer-events-none" />
              <div className="relative z-10 flex flex-col lg:flex-row items-center gap-8">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-2xl">🏏</span>
                    <span className="text-neon-green font-bold text-sm uppercase tracking-widest">BattingEdge Solves This</span>
                  </div>
                  <h3 className="text-3xl font-display font-bold text-white mb-4">
                    Professional-Grade Analysis.<br />Zero Cost. Instant Results.
                  </h3>
                  <p className="text-gray-400 leading-relaxed mb-6">
                    We built BattingEdge specifically for Pakistani cricketers. Whether you're in Karachi,
                    Lahore, Peshawar, or a small town — if you have a phone and can record a video,
                    you get the same feedback as a PCB-certified coaching session.
                  </p>
                  <ul className="space-y-2 text-sm text-gray-300">
                    {['No coaching fees — completely free forever', 'Works on any phone or laptop', 'Results based on ECB & MCC standards', 'Download a professional PDF coaching report'].map(t => (
                      <li key={t} className="flex items-center gap-2">
                        <span className="text-neon-green">✓</span> {t}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="flex-shrink-0">
                  <Link to="/analyze"
                    className="flex items-center gap-2.5 px-8 py-4 rounded-full bg-neon-green text-black font-bold text-base hover:bg-[#33ffaa] transition-all shadow-neon-green hover:-translate-y-0.5"
                  >
                    <Zap size={18} /> Start Free Analysis
                  </Link>
                </div>
              </div>
            </div>
          </FadeUp>
        </div>
      </section>

      {/* ═══ HOW IT WORKS ════════════════════════════════════════════════════ */}
      <section id="how-it-works" className="py-24 lg:py-32 px-4">
        <div className="max-w-6xl mx-auto">
          <FadeUp className="text-center mb-16">
            <span className="text-xs font-semibold tracking-widest uppercase text-neon-blue mb-3 block">Simple Process</span>
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-white mb-4">Three Steps to Better Batting</h2>
            <p className="text-gray-400 max-w-xl mx-auto">No equipment needed. Just your phone and a batting video.</p>
          </FadeUp>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { step:'01', icon:Upload,       title:'Upload or Record',      desc:'Drop your batting video or record live with your camera. Supports MP4, MOV, AVI. Max 100MB.', color:'neon-blue' },
              { step:'02', icon:BrainCircuit, title:'AI Analyses Technique', desc:'V9.5 Stacking Ensemble extracts 107 biomechanical features across 50 frames — classifies your shot with 94.71% accuracy.', color:'neon-green' },
              { step:'03', icon:FileText,     title:'Get Your Report',       desc:'Receive scores, ECB standards comparison, personalised drills, coach feedback, and a downloadable PDF report.', color:'neon-blue' },
            ].map(({ step, icon: Icon, title, desc, color }, i) => (
              <FadeUp key={step} delay={i * 0.12}>
                <div className="relative p-8 rounded-2xl bg-surface-2 border border-border-dim card-hover group h-full">
                  <div className={`absolute top-5 right-6 text-7xl font-display font-black text-${color}/5 select-none leading-none`}>{step}</div>
                  <div className={`w-13 h-13 w-14 h-14 rounded-2xl bg-${color}/10 border border-${color}/20 flex items-center justify-center mb-5 text-${color} group-hover:scale-110 transition-transform`}>
                    <Icon size={26} />
                  </div>
                  <h3 className="text-xl font-display font-bold text-white mb-3">{title}</h3>
                  <p className="text-gray-500 text-sm leading-relaxed">{desc}</p>
                </div>
              </FadeUp>
            ))}
          </div>

          <FadeUp delay={0.4} className="text-center mt-10">
            <Link to="/analyze" className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon">
              Start Your Analysis <ArrowRight size={15} />
            </Link>
          </FadeUp>
        </div>
      </section>

      {/* ═══ SHOT LIBRARY ════════════════════════════════════════════════════ */}
      <section id="shots" className="py-24 lg:py-32 px-4 bg-surface">
        <div className="max-w-6xl mx-auto">
          <FadeUp className="text-center mb-14">
            <span className="text-xs font-semibold tracking-widest uppercase text-neon-green mb-3 block">Shot Library</span>
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-white mb-4">5 Shots. 107 Features. One AI.</h2>
            <p className="text-gray-400 max-w-xl mx-auto">Each shot has its own biomechanical ruleset derived from ECB Level 3 coaching manuals.</p>
          </FadeUp>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {SHOTS.map((s, i) => (
              <FadeUp key={s.name} delay={i * 0.08}>
                <div className={`p-6 rounded-2xl bg-surface-2 border border-border-dim card-hover group hover:border-${s.color}/20 h-full`}>
                  <div className="flex items-center gap-4 mb-4">
                    <span className="text-4xl">{s.icon}</span>
                    <div>
                      <h3 className="font-display font-bold text-white">{s.name}</h3>
                      <span className={`text-xs font-semibold text-${s.color} opacity-70`}>AI Analysed</span>
                    </div>
                  </div>
                  <p className="text-gray-500 text-sm leading-relaxed">{s.desc}</p>
                </div>
              </FadeUp>
            ))}

            {/* CTA card */}
            <FadeUp delay={0.45}>
              <Link to="/analyze" className="flex flex-col items-center justify-center p-6 rounded-2xl border-2 border-dashed border-neon-blue/20 hover:border-neon-blue/40 hover:bg-neon-blue/3 transition-all group h-full min-h-[160px]">
                <Zap size={32} className="text-neon-blue mb-3 group-hover:scale-110 transition-transform" />
                <span className="font-bold text-white text-sm mb-1">Analyze Your Shot</span>
                <span className="text-gray-500 text-xs text-center">Upload a video to see which shot the AI classifies</span>
              </Link>
            </FadeUp>
          </div>
        </div>
      </section>

      {/* ═══ TECHNOLOGY ══════════════════════════════════════════════════════ */}
      <section id="tech" className="py-24 lg:py-32 px-4">
        <div className="max-w-6xl mx-auto">
          <FadeUp className="text-center mb-14">
            <span className="text-xs font-semibold tracking-widest uppercase text-neon-blue mb-3 block">Under the Hood</span>
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-white mb-4">Enterprise AI for Every Cricketer</h2>
            <p className="text-gray-400 max-w-xl mx-auto">Built on the same computer vision research used in professional sports analytics.</p>
          </FadeUp>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 mb-14">
            {FEATURES.map((f, i) => (
              <FadeUp key={f.title} delay={i * 0.1}>
                <div className="p-6 rounded-2xl bg-surface-2 border border-border-dim card-hover group h-full">
                  <div className={`w-12 h-12 rounded-xl bg-white/5 border border-border-dim flex items-center justify-center ${f.color} mb-5 group-hover:scale-110 transition-transform`}>
                    <f.icon size={22} />
                  </div>
                  <h3 className="font-display font-bold text-white mb-2 text-sm">{f.title}</h3>
                  <p className="text-gray-500 text-xs leading-relaxed">{f.desc}</p>
                </div>
              </FadeUp>
            ))}
          </div>

          {/* Accuracy bars */}
          <FadeUp>
            <div className="p-8 rounded-2xl bg-surface-2 border border-border-dim">
              <h3 className="font-display font-bold text-white text-lg mb-6 text-center">Model Accuracy Comparison</h3>
              <div className="space-y-4 max-w-lg mx-auto">
                {[
                  { name:'Stacking Ensemble V9.5', acc:94.71, bold:true,  bar:'bg-gradient-to-r from-neon-blue to-neon-green' },
                  { name:'BiLSTM',                 acc:91.80, bold:false, bar:'bg-neon-blue' },
                  { name:'BiGRU',                  acc:91.80, bold:false, bar:'bg-neon-blue' },
                  { name:'Random Forest',           acc:89.42, bold:false, bar:'bg-neon-green' },
                  { name:'XGBoost',                acc:87.30, bold:false, bar:'bg-neon-green' },
                ].map(({ name, acc, bold, bar }) => (
                  <div key={name} className="flex items-center gap-3">
                    <span className={`text-sm w-44 text-right flex-shrink-0 ${bold ? 'text-white font-bold' : 'text-gray-400'}`}>{name}</span>
                    <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width:0 }} whileInView={{ width:`${acc}%` }}
                        viewport={{ once:true }} transition={{ duration:1.2, delay:0.2, ease:'easeOut' }}
                        className={`h-full rounded-full ${bar}`}
                      />
                    </div>
                    <span className={`text-sm w-14 flex-shrink-0 ${bold ? 'text-white font-bold' : 'text-gray-500'}`}>{acc}%</span>
                  </div>
                ))}
              </div>
            </div>
          </FadeUp>
        </div>
      </section>

      {/* ═══ ECB / MCC STANDARDS ═════════════════════════════════════════════ */}
      <section id="standards" className="py-24 lg:py-32 px-4 bg-surface">
        <div className="max-w-5xl mx-auto">
          <FadeUp className="text-center mb-14">
            <span className="text-xs font-semibold tracking-widest uppercase text-neon-green mb-3 block">World-Class Benchmarks</span>
            <h2 className="text-4xl lg:text-5xl font-display font-bold text-white mb-4">Benchmarked Against ECB & MCC Standards</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Every analysis cross-references your biomechanics against England Cricket Board Level 3
              coaching manuals and MCC Laws of Cricket technical guidelines — the global gold standard.
            </p>
          </FadeUp>

          <FadeUp>
            <div className="rounded-2xl overflow-hidden border border-border-dim">
              <div className="grid grid-cols-4 bg-surface-2 border-b border-border-dim px-6 py-4">
                {['Shot Type','Metric','ECB Standard','Visual'].map(h => (
                  <span key={h} className="text-xs font-bold text-gray-500 uppercase tracking-wider">{h}</span>
                ))}
              </div>
              {STANDARDS.map((s, i) => (
                <div key={i} className={`grid grid-cols-4 px-6 py-4 items-center border-b border-border-dim last:border-0 ${i % 2 === 0 ? 'bg-jet-black' : 'bg-surface'} hover:bg-surface-2 transition-colors`}>
                  <span className="font-medium text-white text-sm">{s.shot}</span>
                  <span className="text-gray-400 text-sm">{s.metric}</span>
                  <span className="text-neon-blue font-mono text-sm font-semibold">{s.standard}</span>
                  <span className="text-2xl">{s.icon}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-600 mt-4 text-center">Full ECB/MCC standards breakdown included in every PDF coaching report.</p>
          </FadeUp>
        </div>
      </section>

      {/* ═══ TESTIMONIAL / IMPACT ═══════════════════════════════════════════ */}
      <section className="py-24 px-4">
        <div className="max-w-5xl mx-auto">
          <FadeUp>
            <div className="grid md:grid-cols-3 gap-6 text-center">
              {[
                { value:94.71, suffix:'%', label:'Model Accuracy',        color:'text-neon-blue',  desc:'Stacking Ensemble V9.5' },
                { value:107,   suffix:'',  label:'Biomechanical Features', color:'text-neon-green', desc:'Extracted per video' },
                { value:30,    suffix:'s', label:'Average Analysis Time',  color:'text-neon-blue',  desc:'From upload to results' },
              ].map(({ value, suffix, label, color, desc }) => (
                <div key={label} className="p-8 rounded-2xl bg-surface-2 border border-border-dim">
                  <p className={`text-5xl font-display font-black mb-2 ${color}`}>
                    <Counter to={value} suffix={suffix} />
                  </p>
                  <p className="font-bold text-white text-lg mb-1">{label}</p>
                  <p className="text-gray-500 text-sm">{desc}</p>
                </div>
              ))}
            </div>
          </FadeUp>
        </div>
      </section>

      {/* ═══ CTA ══════════════════════════════════════════════════════════════ */}
      <section className="py-24 lg:py-32 px-4 bg-surface relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-[700px] h-[400px] bg-neon-blue/5 rounded-full blur-[100px]" />
        </div>
        <div className="max-w-3xl mx-auto text-center relative z-10">
          <FadeUp>
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-neon-green/10 border border-neon-green/20 text-neon-green text-xs font-semibold uppercase tracking-widest mb-8">
              <span className="w-1.5 h-1.5 rounded-full bg-neon-green animate-pulse" />
              100% Free · No Sign-up Required
            </div>
            <h2 className="text-4xl lg:text-6xl font-display font-extrabold text-white mb-5 leading-tight">
              Your Journey to Better<br />
              <span className="gradient-text">Batting Starts Now</span>
            </h2>
            <p className="text-gray-400 text-lg mb-10 max-w-xl mx-auto">
              Join Pakistani cricketers getting professional-grade biomechanical coaching — for free, instantly, on any device.
            </p>
            <Link to="/analyze"
              className="inline-flex items-center gap-3 px-10 py-5 rounded-full bg-neon-blue text-black font-bold text-lg hover:bg-[#33deff] transition-all shadow-neon hover:shadow-neon-strong hover:-translate-y-1 duration-200"
            >
              <Zap size={20} /> Analyze Your First Shot Free
            </Link>
          </FadeUp>
        </div>
      </section>

      {/* ═══ FOOTER ══════════════════════════════════════════════════════════ */}
      <footer className="bg-jet-black border-t border-border-dim py-10 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <img src="/be_logo.png" alt="Logo" className="w-8 h-8 rounded-xl opacity-80" />
              <div>
                <span className="font-display font-bold text-white">Batting<span className="text-neon-blue">Edge</span> AI</span>
                <p className="text-gray-600 text-xs mt-0.5">Pakistan's First Free AI Batting Coach</p>
              </div>
            </div>
            <div className="flex items-center gap-8 text-sm text-gray-500 flex-wrap justify-center">
              {[['#problem','Why BattingEdge'],['#how-it-works','How It Works'],['#shots','Shot Library']].map(([href, label]) => (
                <a key={href} href={href}
                  onClick={e => { e.preventDefault(); document.querySelector(href)?.scrollIntoView({ behavior:'smooth' }); }}
                  className="hover:text-white transition-colors"
                >{label}</a>
              ))}
              <Link to="/faq" className="hover:text-white transition-colors">FAQs</Link>
              <Link to="/analyze" className="hover:text-white transition-colors">Analyze</Link>
            </div>
            <div className="text-xs text-gray-600 text-center md:text-right">
              <p>Final Year Project · Bahria University Karachi · 2025</p>
              <p className="mt-0.5">© 2026 BattingEdge. All rights reserved.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
