import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, Star, Zap, Shield, Target, BookOpen, ArrowLeft } from 'lucide-react';
import Navbar from '../components/Navbar';
import { Link, useNavigate } from 'react-router-dom';

const SHOTS = [
  {
    key:     'cover_drive',
    name:    'Cover Drive',
    emoji:   '🏏',
    tagline: 'The King of Elegant Shots',
    difficulty: 'Intermediate',
    style:   'Attacking',
    color:   '#00d4ff',
    bg:      'rgba(0,212,255,0.08)',
    border:  'rgba(0,212,255,0.25)',
    imageCaption: 'Side-on view showing full extension through the off-side',
    description: `The cover drive is widely regarded as the most beautiful shot in cricket. It is played to a full-length delivery on or outside off stump, driving the ball through the covers with a straight bat and full follow-through. The shot requires excellent footwork, balance, and timing.`,
    keyPoints: [
      'Move front foot down the pitch towards the ball',
      'Keep head still and eyes level at point of contact',
      'Drive through the line — don\'t try to hit too hard',
      'Full follow-through with bat finishing high',
      'Weight transfers fully onto the front foot',
    ],
    commonMistakes: [
      { mistake: 'Chasing wide deliveries', fix: 'Only play when the ball is in the driving zone — not too wide' },
      { mistake: 'Hitting across the line', fix: 'Keep bat straight through the ball, pointing at mid-off after' },
      { mistake: 'Falling away to leg side', fix: 'Keep head over the front foot, eyes on the ball' },
      { mistake: 'Hard hands', fix: 'Soft, relaxed grip at contact to improve timing and reduce edges' },
    ],
    drills: [
      { name: 'Throw-down cover drives', desc: 'Partner throws full deliveries on off stump from 10m, hit 20 in a row focusing on head position and follow-through.' },
      { name: 'Cone target drill', desc: 'Place a cone in the cover region and try to hit it. Develops shot placement and precision.' },
      { name: 'Mirror footwork drill', desc: 'Practice stepping forward (no ball) in front of a mirror, checking your foot lands aligned with the ball\'s line.' },
    ],
    legend: 'Babar Azam',
    legendNote: 'Babar\'s cover drive is considered the most technically perfect in modern cricket — watch how his head stays still and his weight flows through.',
    funFact: 'Neville Cardus, the legendary cricket writer, called the cover drive "the champagne of strokes." It remains the most aesthetically pleasing shot in cricket history.',
    mccStandard: 'Front foot should land close to the pitch of the ball. Bat face angled slightly downward at impact to keep ball along ground.',
    players: ['Babar Azam (Pakistan)', 'Zaheer Abbas (Pakistan)', 'Mohammad Yousuf (Pakistan)', 'Virat Kohli (India)', 'Kumar Sangakkara (Sri Lanka)'],
  },
  {
    key:     'cut_shot',
    name:    'Cut Shot',
    emoji:   '⚡',
    tagline: 'The Punisher of Short Balls',
    difficulty: 'Advanced',
    style:   'Attacking',
    color:   '#f59e0b',
    bg:      'rgba(245,158,11,0.08)',
    border:  'rgba(245,158,11,0.25)',
    imageCaption: 'Late-cut position — weight on back foot, bat swinging horizontally',
    description: `The cut shot is played to a short-pitched delivery outside off stump, cutting the ball through the point/gully region. It requires sharp eyes to judge the length early, a quick back-foot movement, and a decisive horizontal bat swing. Timing is everything — playing too early or too hard results in edges.`,
    keyPoints: [
      'Pick up short ball early — watch the bowler\'s hand',
      'Back foot steps back and across towards off stump',
      'Stay tall — don\'t crouch or lean back too far',
      'Play late — let the ball come close to the body',
      'Punch the ball, don\'t slog it — control is key',
    ],
    commonMistakes: [
      { mistake: 'Playing on a good length', fix: 'The cut only works on genuinely short, wide balls. Let good-length balls go.' },
      { mistake: 'Playing too early', fix: 'Be patient — cut as the ball arrives alongside you, not in front.' },
      { mistake: 'Squeezing eyes shut', fix: 'Keep eyes open through the shot for better contact.' },
      { mistake: 'Too high a backlift', fix: 'Keep the backlift compact for the cut — this is a punching, not a swinging shot.' },
    ],
    drills: [
      { name: 'Bobbing ball cut', desc: 'Suspend a ball on a string at chest height, practice back-foot movement and horizontal bat.' },
      { name: 'Short ball reactions', desc: 'Partner throws short balls from 8m, you react and cut — focus on "see ball, move back" decision.' },
      { name: 'Stationary weight transfer', desc: 'Without a ball, practice stepping back-and-across quickly, holding the final position for balance check.' },
    ],
    legend: 'Younis Khan',
    legendNote: 'Younis Khan built 10,099 Test runs partly through a devastating cut shot. Watch how he waits and punches through point.',
    funFact: 'The cut shot requires the ball to pitch on or outside off stump and to be short. Playing it on a good length is one of the most common ways to get caught at slip or gully.',
    mccStandard: 'Back foot should be inside the crease. Head must stay level. Ball contact should be alongside or slightly behind the front hip.',
    players: ['Younis Khan (Pakistan)', 'Inzamam-ul-Haq (Pakistan)', 'Saeed Anwar (Pakistan)', 'Ricky Ponting (Australia)', 'Marnus Labuschagne (Australia)'],
  },
  {
    key:     'defense',
    name:    'Defensive Shot',
    emoji:   '🛡️',
    tagline: 'The Foundation of Every Great Innings',
    difficulty: 'Beginner',
    style:   'Defensive',
    color:   '#00ff88',
    bg:      'rgba(0,255,136,0.08)',
    border:  'rgba(0,255,136,0.25)',
    imageCaption: 'Forward defense — head over ball, angled bat face, soft hands',
    description: `The defensive shot is the most fundamental technique in batting. It neutralises good-length deliveries, giving the batsman time to assess conditions. A proper forward defense requires excellent footwork, head position, and soft hands to prevent the ball carrying to a fielder.`,
    keyPoints: [
      'Move front foot towards the ball\'s line and length',
      'Head stays directly over the front knee',
      'Bat face angled downward (closing the face) to kill the ball',
      'Soft hands — don\'t push, just present the bat',
      'Eyes stay fixed on the ball through contact',
    ],
    commonMistakes: [
      { mistake: 'Hard hands pushing the ball', fix: 'Relax the grip at the point of contact — the ball should die at your feet.' },
      { mistake: 'Playing away from the body', fix: 'Keep the bat close to your pad — there should be no gap between bat and pad.' },
      { mistake: 'Reaching for the ball', fix: 'Move your feet first, so the ball comes to you.' },
      { mistake: 'Looking up too early', fix: 'Keep your head down through contact — "watch it onto the bat."' },
    ],
    drills: [
      { name: 'Front foot defense with target', desc: 'Place a towel at your feet. Play forward defense, aiming to drop the ball on the towel every time.' },
      { name: 'Backward defense drill', desc: 'Partner throws short balls, you play backward defense — focus on keeping ball dead under the bat.' },
      { name: 'Gap elimination', desc: 'Hold a piece of paper between bat and front pad — perfect defense means the paper doesn\'t fall.' },
    ],
    legend: 'Hanif Mohammad',
    legendNote: 'Hanif Mohammad batted for 970 minutes in a Test innings (337 runs). His flawless defense and patience remain the gold standard of Test batting.',
    funFact: 'Hanif Mohammad\'s 337 against West Indies in 1958 took 16 hours 10 minutes — the longest innings in Test history at the time. Patience built on perfect defense.',
    mccStandard: 'Front foot lands beside the pitch of the ball. Bat face at 30-45° downward angle at impact. Head must be over the knee, not behind it.',
    players: ['Younis Khan (Pakistan)', 'Hanif Mohammad (Pakistan)', 'Mohammad Yousuf (Pakistan)', 'Steve Smith (Australia)', 'Joe Root (England)'],
  },
  {
    key:     'pull_shot',
    name:    'Pull Shot',
    emoji:   '💥',
    tagline: 'The Dominator of Short-Pitch Bowling',
    difficulty: 'Advanced',
    style:   'Attacking',
    color:   '#ef4444',
    bg:      'rgba(239,68,68,0.08)',
    border:  'rgba(239,68,68,0.25)',
    imageCaption: 'Pull shot — pivoting on back foot, rolling wrists through impact',
    description: `The pull shot is played to a short-pitched delivery on or around leg stump, pulling the ball through the square leg/mid-wicket region. It is one of the most powerful shots in cricket but also one of the riskiest — requiring sharp reflexes, correct judgment of ball height, and wrist control to keep the ball down.`,
    keyPoints: [
      'Pick up the short ball early from the bowler\'s hand',
      'Get inside the ball\'s line — don\'t let it hit you',
      'Rock back on the back foot, pivot on it',
      'Roll the wrists through the shot to keep ball down',
      'Head stays steady — eyes track the ball all the way',
    ],
    commonMistakes: [
      { mistake: 'Playing across the line at a high ball', fix: 'If the ball is above shoulder height, duck under it or play the hook shot — don\'t pull.' },
      { mistake: 'Not rolling the wrists', fix: 'Wrist roll at contact keeps the ball down — flat wrists mean the ball goes in the air.' },
      { mistake: 'Losing balance', fix: 'Stay low and pivot smoothly — don\'t fall away to leg side.' },
      { mistake: 'Playing too soon', fix: 'Wait for the ball to drop into the right zone before committing.' },
    ],
    drills: [
      { name: 'Kneel-and-pull drill', desc: 'Kneel on one knee, partner throws short balls. Forces correct wrist and arm position with no footwork variable.' },
      { name: 'Short-ball batting practice', desc: 'Face short bowling in nets, focusing only on the pull shot. Choose length carefully.' },
      { name: 'Wrist-roll shadow batting', desc: 'Shadow pull shots, consciously rolling wrists through contact. 50 reps morning and evening.' },
    ],
    legend: 'Javed Miandad',
    legendNote: 'Javed Miandad\'s last-ball six off Chetan Sharma in Sharjah 1986 is iconic. His pull/hook game was built on reflexes, courage, and perfect wrist control.',
    funFact: 'Miandad\'s 1986 Sharjah last-ball six is often called the greatest finish in ODI history — a pulled shot to win the match off the very last delivery.',
    mccStandard: 'Ball must be genuinely short (bouncing between hip and chest height). Back foot pivot complete before contact. Wrists must close (roll over) through the shot.',
    players: ['Javed Miandad (Pakistan)', 'Babar Azam (Pakistan)', 'Imran Khan (Pakistan)', 'Viv Richards (West Indies)', 'David Warner (Australia)'],
  },
  {
    key:     'sweep_shot',
    name:    'Sweep Shot',
    emoji:   '🌀',
    tagline: 'The Spin Killer',
    difficulty: 'Intermediate',
    style:   'Attacking',
    color:   '#8b5cf6',
    bg:      'rgba(139,92,246,0.08)',
    border:  'rgba(139,92,246,0.25)',
    imageCaption: 'Sweep shot — front knee down, bat swinging horizontally through square leg',
    description: `The sweep shot is primarily played against spin bowling, using a horizontal bat to sweep the ball around the leg side. It is a key weapon for batsmen on sub-continental pitches where spin dominates. The shot requires commitment, correct foot position, and a well-timed horizontal bat swing.`,
    keyPoints: [
      'Get to the pitch of the ball with the front foot',
      'Front knee comes down, back knee nearly touches ground',
      'Head stays forward and over the front knee',
      'Horizontal bat swings through the line from low to high',
      'Eyes watch the ball until the moment of contact',
    ],
    commonMistakes: [
      { mistake: 'Playing the sweep to the wrong ball', fix: 'Only sweep when you can reach the pitch — a ball that skids through will hit pad or bat too high.' },
      { mistake: 'Not getting down low enough', fix: 'Front knee should almost touch the ground — this gives the horizontal swing room.' },
      { mistake: 'Closing the face too early', fix: 'Commit to the sweep — half-hearted sweeps lead to top edges.' },
      { mistake: 'Losing sight of the ball', fix: 'Watch it all the way onto the bat — don\'t turn the head away.' },
    ],
    drills: [
      { name: 'Static sweep practice', desc: 'Kneel in the sweep position, partner feeds balls at knee height — practice controlled contact 30 times.' },
      { name: 'Spin lane drill', desc: 'Face a spin bowler in nets, committing to sweep every ball on the stumps. Builds confidence and muscle memory.' },
      { name: 'Reverse sweep variation', desc: 'After mastering the conventional sweep, practice the reverse sweep to make you harder to bowl to.' },
    ],
    legend: 'Mohammad Hafeez',
    legendNote: 'Hafeez used the sweep shot as a primary weapon against world-class spinners — his ability to neutralise quality spin with the sweep made him invaluable in sub-continental conditions.',
    funFact: 'The sweep shot was popularised in modern cricket by England\'s players against Pakistan and Indian spinners. It is now the default weapon for batsmen facing quality spin on turning pitches.',
    mccStandard: 'Front foot must be at or past the line of the ball. Bat face should be angled slightly downward at contact to keep ball along ground. Head must not move after commitment.',
    players: ['Mohammad Hafeez (Pakistan)', 'Shoaib Malik (Pakistan)', 'Azhar Ali (Pakistan)', 'Graeme Swann (England)', 'AB de Villiers (South Africa)'],
  },
];

const DifficultyBadge = ({ level }) => {
  const color = level === 'Beginner' ? '#00ff88' : level === 'Intermediate' ? '#f59e0b' : '#ef4444';
  const bg    = level === 'Beginner' ? 'rgba(0,255,136,0.1)' : level === 'Intermediate' ? 'rgba(245,158,11,0.1)' : 'rgba(239,68,68,0.1)';
  return (
    <span className="text-[10px] font-bold px-2.5 py-1 rounded-full border" style={{ color, background: bg, borderColor: color + '40' }}>
      {level}
    </span>
  );
};

const ShotCard = ({ shot }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="rounded-2xl border overflow-hidden card-hover"
      style={{ background: 'var(--surface-2)', borderColor: shot.border }}
    >
      {/* Shot header */}
      <div className="p-6" style={{ background: shot.bg }}>
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-4">
            <span className="text-5xl">{shot.emoji}</span>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <DifficultyBadge level={shot.difficulty} />
                <span className="text-[10px] font-medium px-2 py-0.5 rounded-full border"
                      style={{ color: 'var(--text-dim)', borderColor: 'var(--border)', background: 'var(--surface-3)' }}>
                  {shot.style}
                </span>
              </div>
              <h2 className="text-2xl font-display font-extrabold" style={{ color: 'var(--text)' }}>{shot.name}</h2>
              <p className="text-sm mt-0.5" style={{ color: shot.color }}>{shot.tagline}</p>
            </div>
          </div>
          <Link
            to="/analyze"
            className="flex-shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-full text-black text-xs font-bold hover:opacity-90 transition-opacity"
            style={{ background: shot.color }}
          >
            <Zap size={12} /> Analyze
          </Link>
        </div>

        <p className="text-sm mt-4 leading-relaxed" style={{ color: 'var(--text-muted)' }}>{shot.description}</p>
      </div>

      {/* Key technique points */}
      <div className="px-6 py-4 border-b border-border-dim">
        <h3 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--text-dim)' }}>Key Technique Points</h3>
        <div className="space-y-2">
          {shot.keyPoints.map((pt, i) => (
            <div key={i} className="flex items-start gap-2.5">
              <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 text-[10px] font-bold"
                   style={{ background: shot.bg, color: shot.color, border: `1px solid ${shot.border}` }}>
                {i + 1}
              </div>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-muted)' }}>{pt}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Legend + fun fact (always visible) */}
      <div className="px-6 py-4 grid sm:grid-cols-2 gap-4 border-b border-border-dim">
        <div className="p-4 rounded-xl" style={{ background: 'var(--surface-3)', border: `1px solid ${shot.border}` }}>
          <div className="flex items-center gap-2 mb-2">
            <Star size={13} style={{ color: shot.color }} />
            <span className="text-xs font-bold" style={{ color: shot.color }}>Study: {shot.legend}</span>
          </div>
          <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>{shot.legendNote}</p>
        </div>
        <div className="p-4 rounded-xl border border-border-dim" style={{ background: 'var(--surface-3)' }}>
          <div className="flex items-center gap-2 mb-2">
            <BookOpen size={13} className="text-neon-green" />
            <span className="text-xs font-bold text-neon-green">Did You Know?</span>
          </div>
          <p className="text-xs leading-relaxed italic" style={{ color: 'var(--text-muted)' }}>{shot.funFact}</p>
        </div>
      </div>

      {/* Expand/collapse for drills + mistakes */}
      <button
        onClick={() => setExpanded(e => !e)}
        className="w-full flex items-center justify-between px-6 py-3.5 text-sm font-medium transition-colors hover:bg-white/3"
        style={{ color: 'var(--text-muted)' }}
      >
        <span>{expanded ? 'Hide' : 'Show'} Drills, Mistakes & MCC Standards</span>
        {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-6 space-y-5">

              {/* Common Mistakes */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--text-dim)' }}>
                  Common Mistakes & Fixes
                </h4>
                <div className="space-y-2.5">
                  {shot.commonMistakes.map((m, i) => (
                    <div key={i} className="grid sm:grid-cols-2 gap-2">
                      <div className="p-3 rounded-xl border border-red-500/20 bg-red-500/5">
                        <p className="text-xs font-semibold text-red-400 mb-1">❌ {m.mistake}</p>
                      </div>
                      <div className="p-3 rounded-xl border border-neon-green/20 bg-neon-green/5">
                        <p className="text-xs font-semibold text-neon-green mb-1">✓ Fix: {m.fix}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Drills */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--text-dim)' }}>
                  Practice Drills
                </h4>
                <div className="space-y-3">
                  {shot.drills.map((d, i) => (
                    <div key={i} className="flex gap-3 p-3 rounded-xl border border-border-dim"
                         style={{ background: 'var(--surface-3)' }}>
                      <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 text-xs font-bold"
                           style={{ background: shot.bg, color: shot.color, border: `1px solid ${shot.border}` }}>
                        {i + 1}
                      </div>
                      <div>
                        <p className="text-sm font-semibold" style={{ color: 'var(--text)' }}>{d.name}</p>
                        <p className="text-xs mt-0.5 leading-relaxed" style={{ color: 'var(--text-muted)' }}>{d.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* MCC Standard */}
              <div className="p-4 rounded-xl" style={{ background: shot.bg, border: `1px solid ${shot.border}` }}>
                <p className="text-xs font-bold mb-1" style={{ color: shot.color }}>
                  📋 MCC / ECB Technical Standard
                </p>
                <p className="text-xs leading-relaxed" style={{ color: 'var(--text-muted)' }}>{shot.mccStandard}</p>
              </div>

              {/* Players to study */}
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider mb-2" style={{ color: 'var(--text-dim)' }}>
                  Players to Study
                </h4>
                <div className="flex flex-wrap gap-2">
                  {shot.players.map((p, i) => (
                    <span key={i} className="text-xs px-3 py-1.5 rounded-full border border-border-dim"
                          style={{ background: 'var(--surface-3)', color: 'var(--text-muted)' }}>
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const ShotLibraryPage = ({ onOpenAuth }) => {
  const navigate = useNavigate();
  return (
  <div className="min-h-screen pb-20" style={{ background: 'var(--bg)' }}>
    <Navbar onOpenAuth={onOpenAuth} />

    <main className="max-w-4xl mx-auto px-4 pt-28">

      {/* Back button */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-sm mb-6 transition-colors hover:text-neon-blue"
        style={{ color: 'var(--text-muted)' }}
      >
        <ArrowLeft size={15} /> Back
      </button>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-10 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-neon-blue/20 bg-neon-blue/5 text-neon-blue text-xs font-semibold uppercase tracking-widest mb-4">
          <Target size={12} /> Shot Library
        </div>
        <h1 className="text-4xl font-display font-extrabold mb-3" style={{ color: 'var(--text)' }}>
          Master the 5 Core Shots
        </h1>
        <p className="text-sm max-w-xl mx-auto leading-relaxed" style={{ color: 'var(--text-muted)' }}>
          Deep-dive coaching guides for every shot BattingEdge analyses — built on MCC Laws and ECB coaching standards.
          Techniques used by Pakistan's greatest batsmen.
        </p>
      </motion.div>

      <div className="space-y-6">
        {SHOTS.map(shot => <ShotCard key={shot.key} shot={shot} />)}
      </div>

      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }}
        className="mt-12 p-8 rounded-2xl text-center border border-neon-blue/20 bg-neon-blue/5"
      >
        <p className="text-3xl mb-3">🏏</p>
        <h3 className="font-display font-bold text-lg mb-2" style={{ color: 'var(--text)' }}>
          Ready to test your technique?
        </h3>
        <p className="text-sm mb-5" style={{ color: 'var(--text-muted)' }}>
          Upload a video and get AI-powered analysis with your grade, score, and personalised coaching.
        </p>
        <Link
          to="/analyze"
          className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon"
        >
          <Zap size={14} /> Analyze My Batting
        </Link>
      </motion.div>
    </main>
  </div>
  );
};

export default ShotLibraryPage;
