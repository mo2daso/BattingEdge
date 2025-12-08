import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  ArrowLeft, Download, CheckCircle2, XCircle, 
  ChevronRight, AlertTriangle, ChevronDown, ChevronUp,
  Activity
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';
import Navbar from '../components/Navbar';

const API_BASE = 'http://localhost:8000/api';

const ResultPage = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let interval;
    let attempts = 0;
    const maxAttempts = 30; 

    const fetchData = async () => {
      try {
        const res = await axios.get(`${API_BASE}/result/${videoId}`);
        if (res.data.status === 'completed') {
          setData(res.data);
          setLoading(false);
          clearInterval(interval);
          toast.success("Analysis Complete!");
        } else if (res.data.status === 'failed') {
          setError(res.data.error_message);
          setLoading(false);
          clearInterval(interval);
        }
        attempts++;
        if (attempts >= maxAttempts) {
          setError("Request timed out.");
          setLoading(false);
          clearInterval(interval);
        }
      } catch (err) { console.error(err); }
    };
    fetchData();
    interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, [videoId]);

  if (loading) return <LoadingScreen />;
  if (error) return <ErrorScreen error={error} navigate={navigate} />;

  const formAnalysis = typeof data.form_checks === 'string' ? JSON.parse(data.form_checks) : data.form_checks;
  const probabilities = typeof data.all_probabilities === 'string' ? JSON.parse(data.all_probabilities) : data.all_probabilities;
  const score = data.form_score || 0;
  const checks = formAnalysis.checks || [];
  const improvements = formAnalysis.key_improvements || [];
  const summary = formAnalysis.summary || "Analysis complete.";

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-[#0a0e1a] text-gray-900 dark:text-white font-sans transition-colors duration-300 pb-20">
      <Navbar />
      
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Header Actions */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
          <button onClick={() => navigate('/')} className="flex items-center gap-2 text-gray-500 hover:text-cricket-green transition-colors font-medium">
            <ArrowLeft className="w-5 h-5" /> Back
          </button>
          <div className="flex gap-3">
             <a href={`${API_BASE}/report/${videoId}/pdf`} target="_blank" rel="noreferrer" className="flex items-center gap-2 px-5 py-2.5 bg-white dark:bg-[#1a2133] hover:bg-gray-100 dark:hover:bg-[#252d42] text-gray-800 dark:text-gray-200 rounded-xl font-bold transition-all border border-gray-200 dark:border-white/5 shadow-sm">
                <Download size={18} /> Coaching Report
              </a>
             <button onClick={() => navigate('/')} className="px-5 py-2.5 bg-cricket-green text-black rounded-xl font-bold hover:bg-[#00e25b] transition-all shadow-[0_0_20px_rgba(0,200,81,0.2)]">
                New Analysis
              </button>
          </div>
        </div>

        <div className="grid lg:grid-cols-12 gap-8">
          {/* LEFT: Video & AI */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            <div className="relative group rounded-2xl overflow-hidden border border-gray-200 dark:border-white/10 bg-black shadow-2xl aspect-video">
              <video src={`${API_BASE}/video/${videoId}/overlay`} className="w-full h-full object-contain" controls autoPlay loop playsInline />
            </div>
            
            {/* AI Confidence */}
            <div className="bg-white dark:bg-[#111625] rounded-xl p-6 border border-gray-200 dark:border-white/5 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-gray-500 uppercase tracking-widest flex gap-2"><Activity size={16}/> AI Confidence</h3>
              </div>
              <div className="grid grid-cols-2 gap-4">
                {Object.entries(probabilities || {}).sort(([,a], [,b]) => b - a).map(([shot, prob]) => (
                  <div key={shot} className={`p-3 rounded-lg border ${shot === data.shot_type ? 'bg-cricket-green/10 border-cricket-green/30' : 'bg-gray-50 dark:bg-[#0a0e1a] border-gray-200 dark:border-white/5'}`}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className={`uppercase font-bold ${shot === data.shot_type ? 'text-cricket-green' : 'text-gray-500'}`}>{shot}</span>
                      <span className="font-mono text-gray-900 dark:text-white">{prob.toFixed(1)}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
                      <motion.div initial={{ width: 0 }} animate={{ width: `${prob}%` }} className={`h-full ${shot === data.shot_type ? 'bg-cricket-green' : 'bg-gray-400'}`} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT: Coaching Dashboard */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            {/* Score */}
            <div className="bg-white dark:bg-[#111625] rounded-2xl p-6 border border-gray-200 dark:border-white/5 shadow-sm">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <p className="text-xs font-bold text-gray-500 uppercase tracking-widest">Technique Grade</p>
                  <h2 className="text-5xl font-black mt-2 text-gray-900 dark:text-white">{score}</h2>
                </div>
                <div className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold border-4 ${score >= 80 ? 'border-green-500 text-green-500' : score >= 60 ? 'border-yellow-500 text-yellow-500' : 'border-red-500 text-red-500'}`}>
                  {score >= 80 ? 'A' : score >= 60 ? 'B' : 'C'}
                </div>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-[#0a0e1a] rounded-xl border border-gray-200 dark:border-white/5">
                <p className="text-sm text-gray-600 dark:text-gray-300 italic border-l-2 border-cricket-green pl-3">"{summary}"</p>
              </div>
            </div>

            {/* Improvements */}
            {improvements.length > 0 && (
              <div className="bg-red-50 dark:bg-red-500/5 border border-red-200 dark:border-red-500/20 rounded-2xl p-5 shadow-sm">
                <h3 className="text-red-600 dark:text-red-400 font-bold text-sm uppercase tracking-wide mb-3 flex items-center gap-2"><AlertTriangle size={16} /> Key Adjustments</h3>
                <ul className="space-y-3">
                  {improvements.map((imp, i) => (
                    <li key={i} className="flex gap-3 text-sm text-gray-700 dark:text-gray-300 bg-white dark:bg-red-500/5 p-2 rounded-lg border border-red-100 dark:border-transparent">
                      <span className="text-red-500 font-bold">•</span> {imp}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Checklist */}
            <div className="bg-white dark:bg-[#111625] rounded-2xl border border-gray-200 dark:border-white/5 shadow-sm overflow-hidden flex-grow">
              <div className="p-4 border-b border-gray-200 dark:border-white/5 bg-gray-50 dark:bg-[#151b2d]">
                <h3 className="font-bold text-gray-700 dark:text-gray-200">Form Breakdown</h3>
              </div>
              <div className="divide-y divide-gray-100 dark:divide-white/5 max-h-[500px] overflow-y-auto custom-scrollbar">
                {checks.map((check, i) => <CheckItem key={i} check={check} />)}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

const CheckItem = ({ check }) => {
  const [isOpen, setIsOpen] = useState(false);
  const isError = check.is_error;

  return (
    <div className="group transition-colors hover:bg-gray-50 dark:hover:bg-white/5">
      <button onClick={() => setIsOpen(!isOpen)} className="w-full p-4 flex items-center justify-between text-left">
        <div className="flex items-center gap-3">
          {isError ? <XCircle className="w-5 h-5 text-red-500 shrink-0" /> : <CheckCircle2 className="w-5 h-5 text-cricket-green shrink-0" />}
          <div>
            <p className="font-semibold text-sm text-gray-800 dark:text-gray-200">{check.name}</p>
            {/* Friendly Status Badge instead of numbers */}
            <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${isError ? 'bg-red-100 text-red-600 dark:bg-red-500/20 dark:text-red-400' : 'bg-green-100 text-green-600 dark:bg-green-500/20 dark:text-green-400'}`}>
              {isError ? "Needs Work" : "Perfect"}
            </span>
          </div>
        </div>
        <div className={`p-1 rounded-full transition-colors ${isOpen ? 'bg-gray-200 dark:bg-white/10' : ''}`}>
           {isOpen ? <ChevronUp size={16} className="text-gray-500" /> : <ChevronDown size={16} className="text-gray-400" />}
        </div>
      </button>
      
      <AnimatePresence>
        {isOpen && (
          <motion.div initial={{ height: 0 }} animate={{ height: 'auto' }} exit={{ height: 0 }} className="overflow-hidden bg-gray-50 dark:bg-[#0a0e1a]/50">
            <div className="p-4 pt-0 pl-12 text-sm pb-4 text-gray-600 dark:text-gray-400">
              <p className="font-medium text-gray-900 dark:text-gray-200 mb-1">Coach's Note:</p>
              <p className="mb-2">{check.advice}</p>
              {/* Technical data hidden in dropdown for curious users */}
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-white/10 text-xs font-mono opacity-70">
                Data: {check.value} (Target: {check.ideal || "N/A"})
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const LoadingScreen = () => (
  <div className="min-h-screen bg-[#0a0e1a] flex flex-col items-center justify-center">
    <div className="w-16 h-16 border-4 border-gray-800 rounded-full mb-4 relative">
        <div className="absolute inset-0 border-4 border-cricket-green border-t-transparent rounded-full animate-spin"></div>
    </div>
    <h2 className="text-xl font-bold text-white">Analyzing...</h2>
  </div>
);

const ErrorScreen = ({ error, navigate }) => (
  <div className="min-h-screen bg-[#0a0e1a] flex flex-col items-center justify-center p-4">
    <AlertTriangle className="w-12 h-12 text-red-500 mb-4" />
    <h2 className="text-xl font-bold text-white mb-2">Analysis Failed</h2>
    <p className="text-gray-400 mb-6">{error}</p>
    <button onClick={() => navigate('/')} className="px-6 py-2 bg-white text-black font-bold rounded-lg hover:bg-gray-200">Try Again</button>
  </div>
);

export default ResultPage;