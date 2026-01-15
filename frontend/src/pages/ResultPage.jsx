import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  ArrowLeft, Download, CheckCircle2, XCircle, 
  ChevronDown, ChevronUp, Activity, FileText,
  Dumbbell, Target, Footprints, Repeat
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Navbar from '../components/Navbar';

const API_BASE = 'http://localhost:8000/api';

const ResultPage = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    window.scrollTo(0, 0);
    let interval;
    let attempts = 0;

    const fetchData = async () => {
      try {
        const res = await axios.get(`${API_BASE}/result/${videoId}`);
        if (res.data.status === 'completed') {
          setData(res.data);
          setLoading(false);
          clearInterval(interval);
        } else if (res.data.status === 'failed') {
          setError(res.data.error_message);
          setLoading(false);
          clearInterval(interval);
        } else if (attempts > 30) {
          setError("Analysis timed out");
          setLoading(false);
          clearInterval(interval);
        }
        attempts++;
      } catch (err) {
        console.error(err);
      }
    };
    
    fetchData();
    interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, [videoId]);

  if (loading) return <LoadingScreen />;
  if (error) return <ErrorScreen error={error} navigate={navigate} />;

  // Parse Data safely
  const formAnalysis = typeof data.form_checks === 'string' ? JSON.parse(data.form_checks) : data.form_checks || {};
  const score = data.form_score || formAnalysis.overall_score || 0;
  // Use 'level' from new python logic, fallback to grade if needed
  const level = formAnalysis.level || formAnalysis.performance_level || "Developing";
  
  return (
    <div className="min-h-screen bg-jet-black text-white pb-20">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-4 pt-28">
        {/* Top Actions */}
        <div className="flex justify-between items-center mb-8">
          <button onClick={() => navigate('/')} className="flex items-center gap-2 text-gray-400 hover:text-neon-blue transition-colors">
            <ArrowLeft size={20} /> Back to Upload
          </button>
          <a 
            href={`${API_BASE}/report/${videoId}/pdf`} 
            target="_blank" 
            rel="noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-surface border border-white/10 rounded-lg hover:border-neon-blue/50 transition-colors text-sm font-medium"
          >
            <FileText size={16} /> Download PDF
          </a>
        </div>

        <div className="grid lg:grid-cols-12 gap-8">
          
          {/* LEFT COLUMN: Video & Score */}
          <div className="lg:col-span-8 space-y-6">
            {/* Video Player */}
            <div className="aspect-video bg-black rounded-2xl overflow-hidden border border-white/10 shadow-2xl relative group">
              <video 
                src={`${API_BASE}/video/${videoId}/overlay`} 
                controls 
                autoPlay 
                loop 
                className="w-full h-full object-contain"
              />
            </div>

            {/* Stats Bar */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard label="Shot Type" value={data.shot_type?.toUpperCase()} highlight />
              <StatCard label="Confidence" value={`${data.confidence?.toFixed(1)}%`} />
              <StatCard label="Technique Score" value={`${score}/100`} />
              <StatCard label="Skill Level" value={level} color={getLevelColor(level)} />
            </div>
          </div>

          {/* RIGHT COLUMN: Analysis & Drills */}
          <div className="lg:col-span-4 space-y-6">
            <CoachFeedback summary={formAnalysis.summary} />
            <Breakdown checks={formAnalysis.checks || []} />
            <DrillsSection drills={formAnalysis.recommended_drills || []} />
          </div>

        </div>
      </main>
    </div>
  );
};

// --- Sub Components ---

const StatCard = ({ label, value, highlight, color }) => (
  <div className="bg-surface border border-white/10 rounded-xl p-4">
    <p className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</p>
    <p className={`text-xl font-bold truncate ${highlight ? 'text-neon-blue' : color ? color : 'text-white'}`}>
      {value}
    </p>
  </div>
);

const CoachFeedback = ({ summary }) => (
  <div className="bg-surface-highlight border border-white/10 rounded-2xl p-6">
    <h3 className="text-neon-blue font-bold mb-3 flex items-center gap-2">
      <Activity size={18} /> Coach's Assessment
    </h3>
    <p className="text-gray-300 text-sm leading-relaxed">
      "{summary}"
    </p>
  </div>
);

const Breakdown = ({ checks }) => (
  <div className="bg-surface border border-white/10 rounded-2xl overflow-hidden flex flex-col max-h-[400px]">
    <div className="p-4 border-b border-white/10 bg-white/5">
      <h3 className="font-bold">Biomechanical Breakdown</h3>
    </div>
    <div className="overflow-y-auto p-2 space-y-1 custom-scrollbar">
      {checks.map((check, i) => (
        <CheckItem key={i} check={check} />
      ))}
    </div>
  </div>
);

const DrillsSection = ({ drills }) => (
  <div className="bg-surface border border-white/10 rounded-2xl overflow-hidden">
    <div className="p-4 border-b border-white/10 bg-white/5 flex items-center gap-2">
      <Dumbbell className="text-neon-blue" size={18} />
      <h3 className="font-bold">Recommended Drills</h3>
    </div>
    <div className="p-4 space-y-3">
      {drills.length > 0 ? drills.map((drill, i) => (
        <div key={i} className="flex gap-4 p-3 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
          <div className="mt-1">
            {getDrillIcon(drill.name)}
          </div>
          <div>
            <h4 className="text-sm font-bold text-white mb-1">{drill.name}</h4>
            <p className="text-xs text-gray-400 leading-relaxed">{drill.description}</p>
          </div>
        </div>
      )) : (
         <p className="text-sm text-gray-500 italic">No specific drills needed.</p>
      )}
    </div>
  </div>
);

const CheckItem = ({ check }) => {
  const [open, setOpen] = useState(false);
  const isGood = !check.is_error;

  return (
    <div className="rounded-lg overflow-hidden transition-colors hover:bg-white/5">
      <button 
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-3 text-left"
      >
        <div className="flex items-center gap-3">
          {isGood ? <CheckCircle2 size={18} className="text-green-500"/> : <XCircle size={18} className="text-red-500"/>}
          <span className="text-sm font-medium">{check.name}</span>
        </div>
        {open ? <ChevronUp size={16} className="text-gray-500"/> : <ChevronDown size={16} className="text-gray-500"/>}
      </button>
      <AnimatePresence>
        {open && (
          <motion.div 
            initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }}
            className="overflow-hidden bg-black/20"
          >
            <div className="p-3 pl-10 text-xs text-gray-400 space-y-1">
              <p><span className="text-gray-500">Measured:</span> {check.value}</p>
              <p><span className="text-gray-500">Target:</span> {check.ideal_range}</p>
              <p className="mt-2 text-white italic">"{check.advice}"</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// --- Helpers ---

const getDrillIcon = (name) => {
    const n = name.toLowerCase();
    if (n.includes('foot') || n.includes('step') || n.includes('balance')) 
        return <Footprints size={20} className="text-orange-400" />;
    if (n.includes('target') || n.includes('zone') || n.includes('line')) 
        return <Target size={20} className="text-red-400" />;
    if (n.includes('reps') || n.includes('drill')) 
        return <Repeat size={20} className="text-blue-400" />;
    return <Dumbbell size={20} className="text-neon-blue" />;
};

const getLevelColor = (level) => {
  const l = level.toLowerCase();
  if (l.includes('elite')) return 'text-purple-400';
  if (l.includes('advanced')) return 'text-green-400';
  if (l.includes('intermediate')) return 'text-blue-400';
  if (l.includes('developing')) return 'text-orange-400';
  return 'text-gray-400';
};

const LoadingScreen = () => (
  <div className="min-h-screen bg-jet-black flex flex-col items-center justify-center text-center p-4">
    <div className="w-16 h-16 border-4 border-white/10 border-t-neon-blue rounded-full animate-spin mb-6"></div>
    <h2 className="text-2xl font-bold text-white mb-2">Analyzing Shot Mechanics...</h2>
    <p className="text-gray-500">Comparing against ECB & MCC standards.</p>
  </div>
);

const ErrorScreen = ({ error, navigate }) => (
  <div className="min-h-screen bg-jet-black flex flex-col items-center justify-center text-center p-4">
    <XCircle className="w-16 h-16 text-red-500 mb-4" />
    <h2 className="text-2xl font-bold text-white mb-2">Analysis Failed</h2>
    <p className="text-gray-500 mb-6">{error}</p>
    <button onClick={() => navigate('/')} className="px-6 py-3 bg-white text-black rounded-lg font-bold">Try Again</button>
  </div>
);

export default ResultPage;