import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HelpCircle, ChevronDown, ChevronUp, ArrowLeft, Search } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';

const FAQS = [
  // Getting Started
  {
    category: 'Getting Started',
    q: 'What is BattingEdge?',
    a: 'BattingEdge is an AI-powered cricket batting analysis system. You upload a batting video, and our V9.5 Stacking Ensemble model (94.71% accuracy) identifies your shot type and scores your technique against MCC and ECB coaching standards. You get a grade, score, biomechanical breakdown, and personalised drill recommendations.',
  },
  {
    category: 'Getting Started',
    q: 'Do I need to create an account?',
    a: 'No — you can analyse videos as a guest. Creating a free account lets you save your history permanently across all your devices (guests only save history on their current browser). An account also unlocks email tips and a full dashboard.',
  },
  {
    category: 'Getting Started',
    q: 'What video formats does BattingEdge support?',
    a: 'We support MP4, AVI, MOV, MKV, WebM, WMV, MPEG, 3GP, FLV, and M4V. For best results use MP4 at 720p or higher.',
  },
  {
    category: 'Getting Started',
    q: 'Is BattingEdge free?',
    a: 'Yes — BattingEdge is completely free to use. There are no paid tiers, subscription fees, or hidden charges.',
  },

  // Analysis & Accuracy
  {
    category: 'Analysis & Accuracy',
    q: 'How accurate is the shot detection?',
    a: 'Our V9.5 Stacking Ensemble model achieves 94.71% accuracy across 5 shot types (Cover Drive, Cut Shot, Defense, Pull Shot, Sweep Shot), tested on real cricket footage from multiple players and angles.',
  },
  {
    category: 'Analysis & Accuracy',
    q: 'What angle should I film from?',
    a: 'Film from a side-on (90°) angle at waist-to-shoulder height, 3–5 metres from the batsman. Make sure the full body is in frame from head to feet. Front-on or angled views significantly reduce accuracy. Avoid zooming in too close.',
  },
  {
    category: 'Analysis & Accuracy',
    q: 'My shot was misclassified — why?',
    a: 'Common causes: (1) Wrong camera angle — not side-on, (2) Partial body in frame — feet or head cut off, (3) Incomplete shot execution — stopped mid-swing, (4) Low lighting — poor contrast on pose keypoints. Re-record from a direct side-on angle in good light with full body visible.',
  },
  {
    category: 'Analysis & Accuracy',
    q: 'Which 5 shots can BattingEdge analyse?',
    a: 'Cover Drive, Cut Shot, Defensive Shot, Pull Shot, and Sweep Shot. These are the 5 most technically important batting shots in cricket, covering front-foot, back-foot, attacking, and defensive technique.',
  },
  {
    category: 'Analysis & Accuracy',
    q: 'What does the confidence percentage mean?',
    a: 'Confidence shows how certain the AI model is about the shot classification. Above 75% is high confidence. Below 50% usually means the camera angle wasn\'t ideal or the shot was incomplete. You can see the confidence breakdown for all 5 shot types on the result page.',
  },

  // Grades & Scores
  {
    category: 'Grades & Scores',
    q: 'How does the grade work?',
    a: 'A+ (90–100): Elite form — near professional standard. A (80–89): Advanced. B+/B (65–79): Good solid technique. C+/C (50–64): Developing — fundamentals present. D (below 50): Needs improvement. F: Could not assess properly. Grades are based on MCC/ECB biomechanical standards for each shot.',
  },
  {
    category: 'Grades & Scores',
    q: 'What is the overall score based on?',
    a: 'The score (0–100) is calculated from biomechanical checks: head position, foot placement, bat angle, body rotation, weight transfer, and follow-through — all compared against MCC Laws and ECB coaching standards for the specific shot type.',
  },
  {
    category: 'Grades & Scores',
    q: 'What does the technique breakdown show?',
    a: 'Each technique check tests a specific biomechanical aspect of your shot — like "Knee Angle" or "Bat Face Angle at Contact". Green tick = within the ideal range. Red cross = outside ideal range. Click any check to see your exact measured value vs. the target range.',
  },

  // Dashboard & History
  {
    category: 'Dashboard & History',
    q: 'Will my history be saved when I log out and back in?',
    a: 'Yes — if you are signed in, your analysis history is saved to our database and persists across all your sessions and devices. Guest users have localStorage-only history, which clears if you clear your browser data.',
  },
  {
    category: 'Dashboard & History',
    q: 'What is the Shot Tracker?',
    a: 'The Shot Tracker on your dashboard shows your average score for each shot type across all your analyses. Shots averaging below 70 are flagged with personalised drill recommendations to help you improve.',
  },
  {
    category: 'Dashboard & History',
    q: 'What are the Today\'s Coach Tip and Focus Area tip?',
    a: 'If you have any shots averaging below 70, the dashboard shows a personalised tip for your weakest shot. Otherwise, it shows a daily batting tip that rotates based on the day of the week.',
  },

  // Mobile & Camera
  {
    category: 'Mobile & Camera',
    q: 'Can I use BattingEdge on my phone?',
    a: 'Yes — BattingEdge works on any modern mobile browser. You can upload pre-recorded videos or use the in-app camera to record and analyse directly. On the Analyze page, tap "Record with Camera" to use your phone camera.',
  },
  {
    category: 'Mobile & Camera',
    q: 'How do I switch between front and back camera?',
    a: 'In the camera recording modal, use the "Flip" button to switch between front and back camera. For batting analysis the back (environment) camera usually gives better results since the phone is typically placed on a stand.',
  },
  {
    category: 'Mobile & Camera',
    q: 'The camera says "cannot access front camera" — what do I do?',
    a: 'Some devices do not allow front camera access from browsers for security reasons. Tap the "Use Back Camera" option that appears in the error state. If neither camera works, check that you\'ve granted camera permissions to your browser in your phone settings.',
  },

  // Reports & PDF
  {
    category: 'Reports & PDF',
    q: 'What does the PDF report include?',
    a: 'The PDF includes: shot type + confidence, overall grade + score, full biomechanical analysis with ECB/MCC reference ranges, personalised drills, coaching tips, common mistakes for your shot, and a player improvement guide. It\'s suitable for sharing with your cricket coach.',
  },
  {
    category: 'Reports & PDF',
    q: 'Are my videos stored on the server?',
    a: 'Videos are uploaded for analysis only. The overlay video (with pose keypoints drawn on top) is generated and available to view and download. We do not share your videos with third parties.',
  },

  // AI Assistant (BESSA)
  {
    category: 'AI Assistant',
    q: 'What is BESSA?',
    a: 'BESSA (Batting Edge Smart Sports Assistant) is the AI cricket chatbot built into BattingEdge. You can ask BESSA anything about batting techniques, cricket rules, shot tips, player history, or how BattingEdge works. BESSA is powered by Groq AI and only answers cricket-related questions.',
  },
  {
    category: 'AI Assistant',
    q: 'How does the BESSA chatbot work?',
    a: 'BESSA uses the Groq AI API (llama-3.1-8b-instant model) with a strict cricket-only system prompt. It cannot answer questions unrelated to cricket or BattingEdge. All conversations are session-based and not stored on our server.',
  },

  // Email & Subscription
  {
    category: 'Email & Subscription',
    q: 'How do I subscribe to cricket tips emails?',
    a: 'Go to Settings → Cricket Tips Email Subscription. Enter your email and name and click Subscribe. You\'ll receive AI-generated batting tips, drills, and cricket facts.',
  },
  {
    category: 'Email & Subscription',
    q: 'How do I cancel email subscriptions?',
    a: 'Go to Settings → Cricket Tips Email Subscription and click "Unsubscribe". You can re-subscribe at any time.',
  },
];

const CATEGORIES = [...new Set(FAQS.map(f => f.category))];

const FAQItem = ({ faq, index }) => {
  const [open, setOpen] = useState(false);
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03 }}
      className="rounded-xl border border-border-dim overflow-hidden"
      style={{ background: 'var(--surface-3)' }}
    >
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-4 text-left hover:bg-white/3 transition-colors"
      >
        <span className="font-medium text-sm pr-4" style={{ color: 'var(--text)' }}>{faq.q}</span>
        {open
          ? <ChevronUp size={15} className="text-neon-blue flex-shrink-0" />
          : <ChevronDown size={15} style={{ color: 'var(--text-dim)' }} className="flex-shrink-0" />
        }
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <p className="px-4 pb-4 text-sm leading-relaxed border-t border-border-dim pt-3"
               style={{ color: 'var(--text-muted)' }}>
              {faq.a}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const FAQPage = ({ onOpenAuth }) => {
  const navigate = useNavigate();
  const [activeCategory, setActiveCategory] = useState('All');
  const [search, setSearch] = useState('');

  const filtered = FAQS.filter(f => {
    const matchCat  = activeCategory === 'All' || f.category === activeCategory;
    const matchSearch = !search || f.q.toLowerCase().includes(search.toLowerCase()) || f.a.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  return (
    <div className="min-h-screen pb-20" style={{ background: 'var(--bg)' }}>
      <Navbar onOpenAuth={onOpenAuth} />

      <main className="max-w-3xl mx-auto px-4 pt-28">

        {/* Back */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-sm mb-6 transition-colors hover:text-neon-blue"
          style={{ color: 'var(--text-muted)' }}
        >
          <ArrowLeft size={15} /> Back
        </button>

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-neon-blue/20 bg-neon-blue/5 text-neon-blue text-xs font-semibold uppercase tracking-widest mb-4">
            <HelpCircle size={12} /> FAQ
          </div>
          <h1 className="text-4xl font-display font-extrabold mb-3" style={{ color: 'var(--text)' }}>
            Frequently Asked Questions
          </h1>
          <p className="text-sm max-w-xl mx-auto leading-relaxed" style={{ color: 'var(--text-muted)' }}>
            Everything you need to know about BattingEdge — from getting started to advanced tips.
          </p>
        </motion.div>

        {/* Search */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="mb-5">
          <div className="flex items-center gap-2 px-4 py-3 rounded-xl border border-border-dim focus-within:border-neon-blue/40 transition-colors"
               style={{ background: 'var(--surface-2)' }}>
            <Search size={15} style={{ color: 'var(--text-dim)' }} />
            <input
              type="text"
              placeholder="Search questions…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="flex-1 bg-transparent text-sm outline-none"
              style={{ color: 'var(--text)' }}
            />
          </div>
        </motion.div>

        {/* Category filter */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.08 }}
                    className="flex flex-wrap gap-2 mb-8">
          {['All', ...CATEGORIES].map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                activeCategory === cat
                  ? 'bg-neon-blue text-black'
                  : 'border border-border-dim hover:border-neon-blue/40'
              }`}
              style={activeCategory !== cat ? { color: 'var(--text-muted)' } : {}}
            >
              {cat}
            </button>
          ))}
        </motion.div>

        {/* Results count */}
        {search && (
          <p className="text-xs mb-4" style={{ color: 'var(--text-dim)' }}>
            {filtered.length} result{filtered.length !== 1 ? 's' : ''} for "{search}"
          </p>
        )}

        {/* FAQ items grouped by category */}
        {activeCategory === 'All' && !search ? (
          CATEGORIES.map(cat => {
            const items = FAQS.filter(f => f.category === cat);
            return (
              <div key={cat} className="mb-8">
                <h2 className="text-xs font-bold uppercase tracking-widest mb-3 px-1" style={{ color: 'var(--text-dim)' }}>
                  {cat}
                </h2>
                <div className="space-y-2">
                  {items.map((faq, i) => <FAQItem key={i} faq={faq} index={i} />)}
                </div>
              </div>
            );
          })
        ) : (
          <div className="space-y-2">
            {filtered.length > 0
              ? filtered.map((faq, i) => <FAQItem key={i} faq={faq} index={i} />)
              : (
                <div className="text-center py-12">
                  <p className="text-lg mb-2" style={{ color: 'var(--text)' }}>No results found</p>
                  <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                    Try different search terms or ask BESSA the cricket assistant!
                  </p>
                </div>
              )
            }
          </div>
        )}

        {/* Still need help */}
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
          className="mt-12 p-8 rounded-2xl text-center border border-neon-blue/20 bg-neon-blue/5"
        >
          <p className="text-3xl mb-3">🏏</p>
          <h3 className="font-display font-bold text-lg mb-2" style={{ color: 'var(--text)' }}>
            Still have questions?
          </h3>
          <p className="text-sm mb-5" style={{ color: 'var(--text-muted)' }}>
            Ask BESSA — our AI cricket assistant. Click the BESSA button in the bottom-right corner.
          </p>
          <Link
            to="/analyze"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon"
          >
            Start Analysing
          </Link>
        </motion.div>
      </main>
    </div>
  );
};

export default FAQPage;
