import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Upload, Camera, FileVideo, X, AlertCircle, Info,
  CheckCircle2, Loader2, Zap, Smartphone, RefreshCw, Scissors
} from 'lucide-react';
import QRCode from 'react-qr-code';
import toast from 'react-hot-toast';
import Navbar from '../components/Navbar';
import CameraModal from '../components/CameraModal';
import { uploadVideo, triggerAnalysis, getResult, saveToHistory } from '../utils/api';
import { useAuth } from '../context/AuthContext';

// ── Progress Steps ─────────────────────────────────────────────────────────────
const STEPS = [
  { label: 'Uploading',         icon: Upload,       range: [0, 10]  },
  { label: 'Extracting Pose',   icon: Zap,          range: [10, 60] },
  { label: 'AI Classification', icon: Loader2,      range: [60, 85] },
  { label: 'Generating Report', icon: FileVideo,    range: [85, 100]},
];

const getStep = (progress) => {
  if (progress < 10)  return 0;
  if (progress < 60)  return 1;
  if (progress < 85)  return 2;
  if (progress < 100) return 3;
  return 4;
};

const ProgressStepper = ({ progress, status }) => {
  const activeStep = getStep(progress);
  return (
    <div className="w-full max-w-lg mx-auto">
      {/* Bar */}
      <div className="h-1.5 bg-white/5 rounded-full overflow-hidden mb-8">
        <motion.div
          className="h-full progress-bar rounded-full"
          animate={{ width: `${Math.max(2, progress)}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>

      {/* Steps */}
      <div className="grid grid-cols-4 gap-2">
        {STEPS.map((s, i) => {
          const done    = i < activeStep;
          const active  = i === activeStep;
          const pending = i > activeStep;
          return (
            <div key={s.label} className="flex flex-col items-center gap-2 text-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all ${
                done   ? 'bg-neon-green border-neon-green text-black' :
                active ? 'bg-neon-blue/10 border-neon-blue text-neon-blue' :
                         'bg-white/3 border-white/10 text-gray-600'
              }`}>
                {done
                  ? <CheckCircle2 size={18} />
                  : <s.icon size={16} className={active ? 'animate-pulse' : ''} />
                }
              </div>
              <span className={`text-[10px] font-medium leading-tight ${
                done ? 'text-neon-green' : active ? 'text-white' : 'text-gray-600'
              }`}>
                {s.label}
              </span>
            </div>
          );
        })}
      </div>

      <div className="mt-6 text-center">
        <p className="text-2xl font-display font-bold text-white">{Math.round(progress)}%</p>
        <p className="text-sm text-gray-500 mt-1">
          {status === 'processing' ? STEPS[Math.min(activeStep, 3)].label + '…' : status}
        </p>
      </div>
    </div>
  );
};

// ──────────────────────────────────────────────────────────────────────────────

const AnalyzePage = ({ onOpenAuth }) => {
  const navigate  = useNavigate();
  const { user }  = useAuth();
  const fileRef   = useRef(null);
  const pollRef   = useRef(null);

  const [tab,          setTab]          = useState('upload');
  const [file,         setFile]         = useState(null);
  const [isDragging,   setIsDragging]   = useState(false);
  const [stage,        setStage]        = useState('idle');
  const [uploadPct,    setUploadPct]    = useState(0);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisStatus,   setAnalysisStatus]   = useState('');
  const [errMsg,       setErrMsg]       = useState('');
  const [camOpen,      setCamOpen]      = useState(false);
  const [serverInfo,   setServerInfo]   = useState(null);
  const [qrLoading,    setQrLoading]    = useState(false);
  const [qrWaiting,    setQrWaiting]    = useState(false);
  const qrPollRef     = useRef(null);

  // ── Video trim state ──────────────────────────────────────────────────────────
  const [videoDuration, setVideoDuration] = useState(0);
  const [trimStart,     setTrimStart]     = useState(0);
  const [trimEnd,       setTrimEnd]       = useState(0);
  const [videoUrl,      setVideoUrl]      = useState(null);
  const [isTrimming,    setIsTrimming]    = useState(false);
  const trimVideoRef = useRef(null);

  // Fetch server LAN info when phone tab is opened; reset when leaving tab
  useEffect(() => {
    if (tab !== 'phone') {
      clearInterval(qrPollRef.current);
      setQrWaiting(false);
      return;
    }
    if (serverInfo) return;
    setQrLoading(true);
    fetch('/api/server-info')
      .then(r => r.json())
      .then(d => { setServerInfo(d); setQrLoading(false); })
      .catch(() => { setServerInfo({ lan_ip: window.location.hostname, api_port: 8000, frontend_port: 5173 }); setQrLoading(false); });
  }, [tab]);

  // Poll for new mobile result using baseline-ID comparison (timezone-proof).
  // We snapshot whatever is already completed when the QR appears, then only
  // navigate when a DIFFERENT (newer) video_id shows up.
  useEffect(() => {
    if (tab !== 'phone' || !serverInfo || qrLoading) return;

    let active = true;
    let baselineId = null;

    const startPolling = () => {
      clearInterval(qrPollRef.current);
      setQrWaiting(true);
      qrPollRef.current = setInterval(async () => {
        try {
          const res  = await fetch('/api/latest-result?after=1970-01-01T00:00:00');
          const data = await res.json();
          if (active && data.video_id && data.video_id !== baselineId) {
            clearInterval(qrPollRef.current);
            setQrWaiting(false);
            navigate(`/result/${data.video_id}`);
          }
        } catch { /* ignore transient network errors */ }
      }, 3000);
    };

    // Snapshot current latest so we ignore it going forward
    fetch('/api/latest-result?after=1970-01-01T00:00:00')
      .then(r => r.json())
      .then(d => { baselineId = d.video_id || null; if (active) startPolling(); })
      .catch(() => { if (active) startPolling(); });

    return () => { active = false; clearInterval(qrPollRef.current); setQrWaiting(false); };
  }, [tab, serverInfo, qrLoading]);

  // ── File handling ───────────────────────────────────────────────────────────
  const acceptFile = (f) => {
    if (!f) return;
    if (f.size > 150 * 1024 * 1024) { toast.error('File too large. Max 150MB.'); return; }
    setFile(f);
    setStage('idle');
    setErrMsg('');
    // Load video to get duration for trim sliders
    const url = URL.createObjectURL(f);
    setVideoUrl(url);
    const vid = document.createElement('video');
    vid.src = url;
    vid.onloadedmetadata = () => {
      const dur = Math.floor(vid.duration);
      setVideoDuration(dur);
      setTrimStart(0);
      setTrimEnd(dur);
    };
  };

  // Client-side video trim using captureStream + MediaRecorder
  const trimVideoBlob = (sourceFile, startSec, endSec) => new Promise((resolve, reject) => {
    const url = URL.createObjectURL(sourceFile);
    const vid = document.createElement('video');
    vid.src = url; vid.muted = true; vid.preload = 'auto';
    vid.onloadedmetadata = () => {
      vid.currentTime = startSec;
      vid.onseeked = () => {
        const duration = endSec - startSec;
        const mimeType = ['video/webm;codecs=vp8','video/webm'].find(t => MediaRecorder.isTypeSupported(t)) || 'video/webm';
        let stream;
        try { stream = vid.captureStream(); } catch { resolve(sourceFile); URL.revokeObjectURL(url); return; }
        const recorder = new MediaRecorder(stream, { mimeType });
        const chunks = [];
        recorder.ondataavailable = e => { if (e.data?.size > 0) chunks.push(e.data); };
        recorder.onstop = () => { URL.revokeObjectURL(url); resolve(new Blob(chunks, { type: mimeType })); };
        recorder.start(100);
        vid.play().catch(() => {});
        setTimeout(() => { recorder.stop(); vid.pause(); }, duration * 1000 + 200);
      };
    };
    vid.onerror = () => { URL.revokeObjectURL(url); reject(new Error('Cannot read video')); };
  });

  const handleDrop = (e) => {
    e.preventDefault(); setIsDragging(false);
    acceptFile(e.dataTransfer.files?.[0]);
  };

  const handleCameraVideo = (f) => { setTab('upload'); acceptFile(f); };

  // ── Poll result ─────────────────────────────────────────────────────────────
  const startPolling = useCallback((videoId) => {
    let failCount = 0;
    pollRef.current = setInterval(async () => {
      try {
        const res = await getResult(videoId);
        if (res.status === 'completed') {
          clearInterval(pollRef.current);
          setAnalysisProgress(100);
          // only save to history when logged in (ResultPage handles this too, avoiding double-save)
          if (user?.id) {
            const fa = res.result?.form_analysis || {};
            saveToHistory(videoId, res.result?.prediction, fa.overall_score, fa.grade, user.id);
          }
          setTimeout(() => navigate(`/result/${videoId}`), 600);
        } else if (res.status === 'failed') {
          clearInterval(pollRef.current);
          setStage('error');
          setErrMsg(res.error || 'Analysis failed. Please try again.');
        } else {
          // still processing
          const p = res.progress ?? 0;
          setAnalysisProgress(p);
          setAnalysisStatus(res.status || 'processing');
          failCount = 0;
        }
      } catch {
        failCount++;
        if (failCount > 10) {
          clearInterval(pollRef.current);
          setStage('error');
          setErrMsg('Lost connection to server. Please retry.');
        }
      }
    }, 2000);
  }, [navigate]);

  // ── Main analyze flow (with optional trim) ──────────────────────────────────
  const handleAnalyze = async () => {
    if (!file) return;
    setErrMsg('');
    try {
      let uploadFile = file;
      // Trim if user selected a subset of the video
      const needsTrim = videoDuration > 0 && (trimStart > 0 || trimEnd < videoDuration);
      if (needsTrim) {
        setIsTrimming(true);
        try {
          const trimmed = await trimVideoBlob(file, trimStart, trimEnd);
          uploadFile = new File([trimmed], file.name, { type: trimmed.type });
        } catch { /* fall back to full video */ }
        setIsTrimming(false);
      }
      setStage('uploading');
      setUploadPct(0);
      const { video_id } = await uploadVideo(uploadFile, setUploadPct);
      setStage('analyzing');
      setAnalysisProgress(5);
      await triggerAnalysis(video_id);
      startPolling(video_id);
    } catch (err) {
      clearInterval(pollRef.current);
      setIsTrimming(false);
      setStage('error');
      setErrMsg(err.response?.data?.detail || err.message || 'Something went wrong');
    }
  };

  const reset = () => {
    clearInterval(pollRef.current);
    clearInterval(qrPollRef.current);
    setFile(null); setStage('idle'); setUploadPct(0);
    setAnalysisProgress(0); setErrMsg('');
    if (videoUrl) { URL.revokeObjectURL(videoUrl); setVideoUrl(null); }
    setVideoDuration(0); setTrimStart(0); setTrimEnd(0);
    setServerInfo(null);
  };

  const isProcessing = stage === 'uploading' || stage === 'analyzing';
  const freeUsed = !user && localStorage.getItem('be_free_used') === '1';

  if (freeUsed) {
    return (
      <div className="min-h-screen bg-jet-black text-white">
        <Navbar onOpenAuth={onOpenAuth} />
        <main className="max-w-lg mx-auto px-4 pt-40 pb-20 text-center">
          <div className="w-20 h-20 rounded-2xl bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center mx-auto mb-6">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <h2 className="text-3xl font-display font-extrabold text-white mb-3">Free Analysis Used</h2>
          <p className="text-gray-400 mb-8">
            You've already used your free analysis. Sign up for free to get unlimited analyses,
            save your history, and track your progress.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => onOpenAuth('register')}
              className="px-8 py-3 rounded-xl bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon"
            >
              Sign Up Free
            </button>
            <button
              onClick={() => onOpenAuth('login')}
              className="px-8 py-3 rounded-xl border border-border-soft text-sm font-semibold hover:border-neon-blue/40 transition-all text-white"
            >
              Sign In
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-jet-black text-white">
      <Navbar onOpenAuth={onOpenAuth} />
      <CameraModal isOpen={camOpen} onClose={() => setCamOpen(false)} onVideoReady={handleCameraVideo} />

      <main className="max-w-3xl mx-auto px-4 pt-28 pb-20">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-neon-blue/10 border border-neon-blue/20 text-neon-blue text-xs font-semibold tracking-widest uppercase mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-neon-blue animate-pulse" />
            AI Analysis Engine
          </div>
          <h1 className="text-4xl lg:text-5xl font-display font-extrabold text-white mb-3">
            Analyze Your Shot
          </h1>
          <p className="text-gray-400">Upload a video or record with your camera. Results in under 30 seconds.</p>
        </div>

        {/* ── ANALYZING / UPLOADING STATE ── */}
        <AnimatePresence mode="wait">
          {isProcessing && (
            <motion.div
              key="processing"
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
              className="p-10 rounded-3xl bg-surface-2 border border-border-dim text-center"
            >
              {stage === 'uploading' ? (
                <>
                  <div className="w-16 h-16 rounded-2xl bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center mx-auto mb-6">
                    <Upload size={28} className="text-neon-blue animate-pulse" />
                  </div>
                  <h3 className="text-2xl font-display font-bold text-white mb-2">Uploading Video…</h3>
                  <p className="text-gray-500 text-sm mb-8">{file?.name}</p>
                  <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full progress-bar rounded-full"
                      animate={{ width: `${uploadPct}%` }}
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                  <p className="text-neon-blue font-bold text-lg mt-4">{uploadPct}%</p>
                </>
              ) : (
                <>
                  <h3 className="text-2xl font-display font-bold text-white mb-2 mt-2">Analyzing Your Technique…</h3>
                  <p className="text-gray-500 text-sm mb-10">Comparing against ECB & MCC standards</p>
                  <ProgressStepper progress={analysisProgress} status={analysisStatus} />
                </>
              )}
            </motion.div>
          )}

          {!isProcessing && (
            <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {/* Tabs */}
              <div className="flex gap-1 bg-surface rounded-2xl p-1.5 mb-6">
                {[
                  { id: 'upload', label: 'Upload Video', icon: Upload },
                  { id: 'camera', label: 'Use Camera',   icon: Camera },
                  { id: 'phone',  label: 'Use Phone',    icon: Smartphone },
                ].map(({ id, label, icon: Icon }) => (
                  <button
                    key={id}
                    onClick={() => setTab(id)}
                    className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold transition-all ${
                      tab === id ? 'bg-surface-2 text-white shadow-sm' : 'text-gray-500 hover:text-gray-300'
                    }`}
                  >
                    <Icon size={15} /> {label}
                  </button>
                ))}
              </div>

              {/* ── CAMERA TAB ── */}
              {tab === 'camera' && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-10 rounded-3xl bg-surface-2 border border-border-dim text-center"
                >
                  <div className="w-20 h-20 rounded-2xl bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center mx-auto mb-6">
                    <Camera size={36} className="text-neon-blue" />
                  </div>
                  <h3 className="text-2xl font-display font-bold text-white mb-2">Record Your Shot</h3>
                  <p className="text-gray-400 text-sm max-w-sm mx-auto mb-4">
                    Record up to 60 seconds. Real-time AI pose skeleton shows your biomechanics live.
                  </p>
                  <div className="flex items-start gap-2 bg-red-500/5 border border-red-500/15 rounded-xl p-4 text-left max-w-sm mx-auto mb-3">
                    <AlertCircle size={14} className="text-red-400 mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-red-200/80 leading-relaxed">
                      <strong className="text-white">Only 1 person</strong> must be in frame. Multiple people will confuse the AI.
                    </p>
                  </div>
                  <div className="flex items-start gap-2 bg-neon-blue/5 border border-neon-blue/10 rounded-xl p-4 text-left max-w-sm mx-auto mb-8">
                    <Info size={15} className="text-neon-blue mt-0.5 flex-shrink-0" />
                    <p className="text-xs text-blue-200/80 leading-relaxed">
                      Stand <strong className="text-white">side-on</strong> (bowler's view), full body head to toe, good lighting. Clear video = accurate analysis.
                    </p>
                  </div>
                  <button
                    onClick={() => setCamOpen(true)}
                    className="flex items-center gap-2 mx-auto px-7 py-3.5 rounded-full bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon"
                  >
                    <Camera size={16} /> Open Camera
                  </button>
                </motion.div>
              )}

              {/* ── PHONE / QR TAB ── */}
              {tab === 'phone' && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-8 rounded-3xl bg-surface-2 border border-border-dim text-center"
                >
                  <div className="w-16 h-16 rounded-2xl bg-neon-green/10 border border-neon-green/20 flex items-center justify-center mx-auto mb-5">
                    <Smartphone size={30} className="text-neon-green" />
                  </div>
                  <h3 className="text-2xl font-display font-bold text-white mb-2">Record from Your Phone</h3>
                  <p className="text-gray-400 text-sm max-w-sm mx-auto mb-6">
                    Scan the QR code with your phone. It opens a recording page — record your shot, and the video is sent straight to the AI for analysis.
                  </p>

                  {qrLoading ? (
                    <div className="flex flex-col items-center gap-3 py-8">
                      <Loader2 size={28} className="text-neon-blue animate-spin" />
                      <p className="text-gray-500 text-sm">Getting network info…</p>
                    </div>
                  ) : serverInfo ? (
                    <>
                      <div className="inline-block p-4 bg-white rounded-2xl mb-4 shadow-[0_0_40px_rgba(0,212,255,0.15)]">
                        <QRCode
                          value={`https://${serverInfo.lan_ip}:${serverInfo.frontend_port}/mobile`}
                          size={180}
                          bgColor="#ffffff"
                          fgColor="#0a0a0f"
                          level="M"
                        />
                      </div>
                      <p className="text-xs text-gray-500 mb-1">Scan with your phone camera</p>
                      <p className="text-[10px] font-mono text-gray-600 mb-4">
                        {`https://${serverInfo.lan_ip}:${serverInfo.frontend_port}/mobile`}
                      </p>

                      {/* Waiting indicator */}
                      {qrWaiting && (
                        <div className="flex items-center justify-center gap-2 mb-4 py-2 px-4 rounded-full bg-neon-blue/10 border border-neon-blue/20 mx-auto w-fit">
                          <Loader2 size={12} className="text-neon-blue animate-spin" />
                          <span className="text-neon-blue text-xs font-semibold">Waiting for mobile analysis…</span>
                        </div>
                      )}

                      <div className="flex items-start gap-2 bg-amber-500/5 border border-amber-500/15 rounded-xl p-4 text-left max-w-sm mx-auto mb-3">
                        <Info size={14} className="text-amber-400 mt-0.5 flex-shrink-0" />
                        <p className="text-xs text-amber-200/70 leading-relaxed">
                          Phone and laptop must be on the <strong className="text-white">same WiFi</strong>. When your phone finishes analyzing, this page will automatically show the result.
                        </p>
                      </div>
                      <div className="flex items-start gap-2 bg-red-500/5 border border-red-500/15 rounded-xl p-4 text-left max-w-sm mx-auto">
                        <AlertCircle size={14} className="text-red-400 mt-0.5 flex-shrink-0" />
                        <p className="text-xs text-red-200/70 leading-relaxed">
                          <strong className="text-red-300">Wrong angle = Wrong prediction.</strong> Record <strong className="text-white">side-on</strong> (bowler's view), full body head to toe. Front or back-on angles give inaccurate results.
                        </p>
                      </div>
                      <button
                        onClick={() => { setServerInfo(null); }}
                        className="mt-4 flex items-center gap-1.5 mx-auto text-xs text-gray-600 hover:text-gray-400 transition-colors"
                      >
                        <RefreshCw size={11} /> Refresh QR
                      </button>
                    </>
                  ) : null}
                </motion.div>
              )}

              {/* ── UPLOAD TAB ── */}
              {tab === 'upload' && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  {/* Drop zone */}
                  <div
                    className={`relative rounded-3xl border-2 border-dashed transition-all duration-200 ${
                      isDragging ? 'border-neon-blue bg-neon-blue/5 scale-[1.01]' : 'border-border-soft hover:border-white/20 bg-surface-2'
                    }`}
                    onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                    onDragLeave={() => setIsDragging(false)}
                    onDrop={handleDrop}
                  >
                    <div className="p-10 flex flex-col items-center justify-center min-h-[320px] text-center">
                      <AnimatePresence mode="wait">
                        {!file ? (
                          <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center">
                            <div
                              onClick={() => fileRef.current?.click()}
                              className="w-20 h-20 rounded-2xl bg-white/5 border border-border-soft flex items-center justify-center cursor-pointer hover:bg-white/8 hover:border-white/20 transition-all group mb-6"
                            >
                              <Upload size={32} className="text-gray-500 group-hover:text-neon-blue transition-colors" />
                            </div>
                            <h3 className="text-xl font-display font-bold text-white mb-2">Drop your video here</h3>
                            <p className="text-gray-500 text-sm max-w-xs mb-4">MP4, MOV, AVI, WebM — up to 150MB.</p>

                            <div className="flex items-start gap-2 bg-red-500/5 border border-red-500/15 rounded-xl p-4 text-left max-w-xs mb-3">
                              <AlertCircle size={14} className="text-red-400 mt-0.5 flex-shrink-0" />
                              <p className="text-xs text-red-200/80 leading-relaxed">
                                <strong className="text-white">Only 1 person</strong> must be in the video. Multiple people will confuse the AI and give wrong results.
                              </p>
                            </div>
                            <div className="flex items-start gap-2 bg-neon-blue/5 border border-neon-blue/10 rounded-xl p-4 text-left max-w-xs mb-7">
                              <Info size={14} className="text-neon-blue mt-0.5 flex-shrink-0" />
                              <p className="text-xs text-blue-200/70 leading-relaxed">
                                <strong className="text-white">Best accuracy:</strong> Record <u>side-on</u> (bowler's view), full body visible head to toe, clear lighting.
                              </p>
                            </div>

                            <button
                              onClick={() => fileRef.current?.click()}
                              className="px-6 py-3 rounded-xl bg-white text-black font-bold text-sm hover:bg-gray-200 transition-colors"
                            >
                              Browse File
                            </button>
                          </motion.div>
                        ) : (
                          <motion.div key="selected" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="w-full">
                            {/* File info row */}
                            <div className="flex items-center gap-3 bg-white/5 border border-border-soft rounded-2xl p-4 mb-5">
                              <div className="w-10 h-10 rounded-xl bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center flex-shrink-0">
                                <FileVideo size={18} className="text-neon-blue" />
                              </div>
                              <div className="flex-1 overflow-hidden text-left">
                                <p className="text-white font-medium text-sm truncate">{file.name}</p>
                                <p className="text-gray-500 text-xs mt-0.5">{(file.size / 1024 / 1024).toFixed(1)} MB {videoDuration > 0 && `· ${videoDuration}s`}</p>
                              </div>
                              <button onClick={reset} className="p-1.5 rounded-full hover:bg-white/10 text-gray-500 hover:text-white transition-all flex-shrink-0">
                                <X size={16} />
                              </button>
                            </div>

                            {/* Video preview */}
                            {videoUrl && (
                              <div className="mb-5 rounded-2xl overflow-hidden border border-border-dim bg-black">
                                <video
                                  ref={trimVideoRef}
                                  src={videoUrl}
                                  className="w-full max-h-52 object-contain"
                                  muted
                                  playsInline
                                  onTimeUpdate={() => {
                                    if (trimVideoRef.current && trimVideoRef.current.currentTime >= trimEnd) {
                                      trimVideoRef.current.pause();
                                    }
                                  }}
                                />
                              </div>
                            )}

                            {/* Trim sliders — only if video is longer than 5s */}
                            {videoDuration > 5 && (
                              <div className="mb-5 p-4 rounded-2xl border border-border-dim space-y-4" style={{ background: 'var(--surface-2)' }}>
                                <div className="flex items-center gap-2 mb-1">
                                  <Scissors size={13} className="text-neon-blue" />
                                  <span className="text-sm font-semibold text-white">Trim Clip</span>
                                  <span className="ml-auto text-xs font-mono text-neon-green">
                                    {trimStart}s → {trimEnd}s &nbsp;({trimEnd - trimStart}s selected)
                                  </span>
                                </div>
                                <div>
                                  <div className="flex justify-between text-[11px] mb-1" style={{ color: 'var(--text-dim)' }}>
                                    <span>Start</span><span>{trimStart}s</span>
                                  </div>
                                  <input
                                    type="range" min={0} max={videoDuration - 1} value={trimStart}
                                    onChange={e => {
                                      const v = Math.min(Number(e.target.value), trimEnd - 1);
                                      setTrimStart(v);
                                      if (trimVideoRef.current) trimVideoRef.current.currentTime = v;
                                    }}
                                    className="w-full accent-neon-blue"
                                  />
                                </div>
                                <div>
                                  <div className="flex justify-between text-[11px] mb-1" style={{ color: 'var(--text-dim)' }}>
                                    <span>End</span><span>{trimEnd}s</span>
                                  </div>
                                  <input
                                    type="range" min={1} max={videoDuration} value={trimEnd}
                                    onChange={e => {
                                      const v = Math.max(Number(e.target.value), trimStart + 1);
                                      setTrimEnd(v);
                                      if (trimVideoRef.current) trimVideoRef.current.currentTime = trimStart;
                                    }}
                                    className="w-full accent-neon-blue"
                                  />
                                </div>
                                <button
                                  onClick={() => {
                                    if (trimVideoRef.current) {
                                      trimVideoRef.current.currentTime = trimStart;
                                      trimVideoRef.current.play();
                                    }
                                  }}
                                  className="text-xs text-neon-blue hover:underline"
                                >
                                  ▶ Preview selection
                                </button>
                              </div>
                            )}

                            <button
                              onClick={handleAnalyze}
                              disabled={isTrimming}
                              className="w-full py-4 rounded-2xl bg-neon-blue text-black font-bold text-lg hover:bg-[#33deff] transition-all shadow-neon hover:shadow-neon-strong disabled:opacity-60"
                            >
                              {isTrimming ? 'Trimming clip…' : 'Start Analysis'}
                            </button>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                    <input ref={fileRef} type="file" accept="video/*" className="hidden" onChange={e => e.target.files?.[0] && acceptFile(e.target.files[0])} />
                  </div>
                </motion.div>
              )}

              {/* Error */}
              {stage === 'error' && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm"
                >
                  <AlertCircle size={18} className="flex-shrink-0" />
                  <span>{errMsg}</span>
                  <button onClick={reset} className="ml-auto underline text-xs hover:text-red-300">Reset</button>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default AnalyzePage;
