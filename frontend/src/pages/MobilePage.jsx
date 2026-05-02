import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Video, Square, CheckCircle2, AlertCircle, Loader2, Upload, FlipHorizontal, Info, X } from 'lucide-react';

const fmtTime = (s) => `${String(Math.floor(s / 60)).padStart(2,'0')}:${String(s % 60).padStart(2,'0')}`;
// In production (Vercel), VITE_API_URL must point to the Oracle Cloud backend (e.g. https://1.2.3.4:8000).
// In dev, leave it unset — Vite proxy forwards /api and /auth to localhost:8000.
const API_BASE = import.meta.env.VITE_API_URL || '';
const API = (path) => `${API_BASE}${path}`;

const MEDIAPIPE_DRAWING = 'https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils@0.3.1620248257/drawing_utils.js';
const MEDIAPIPE_POSE    = 'https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/pose.js';

const loadScript = (src) => new Promise((resolve) => {
  if (document.querySelector(`script[src="${src}"]`)) { resolve(); return; }
  const s = document.createElement('script');
  s.src = src; s.crossOrigin = 'anonymous';
  s.onload = resolve; s.onerror = resolve;
  document.head.appendChild(s);
});

// Pre-fetch scripts immediately (before camera is ready) so pose AI loads faster
const preloadPoseScripts = () => {
  loadScript(MEDIAPIPE_DRAWING).catch(() => {});
  loadScript(MEDIAPIPE_POSE).catch(() => {});
};

const CONNECTIONS = [
  [11,12],[11,13],[13,15],[15,17],[15,19],[17,19],
  [12,14],[14,16],[16,18],[16,20],[18,20],
  [11,23],[12,24],[23,24],
  [23,25],[25,27],[27,29],[29,31],[27,31],
  [24,26],[26,28],[28,30],[30,32],[28,32],
  [0,1],[1,2],[2,3],[3,7],[0,4],[4,5],[5,6],[6,8],[9,10],
];

const MobilePage = () => {
  const videoRef    = useRef(null);
  const canvasRef   = useRef(null);
  const streamRef   = useRef(null);
  const recorderRef = useRef(null);
  const chunksRef   = useRef([]);
  const poseRef     = useRef(null);
  const rafRef      = useRef(null);
  const detectedRef = useRef(0);
  const totalRef    = useRef(0);

  const [stage, setStage]       = useState('init'); // init|loading|ready|recording|recorded|uploading|done|error
  const [timer, setTimer]       = useState(0);
  const [poseOk, setPoseOk]     = useState(false);
  const [poseLoading, setPoseLoading] = useState(false);
  const [facingMode, setFacingMode]   = useState('environment');
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [validation, setValidation]   = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errMsg, setErrMsg]     = useState('');
  const [bannerDismissed, setBannerDismissed] = useState(false);

  const initCamera = useCallback(async (facing = facingMode) => {
    setStage('loading');
    setErrMsg('');
    // Stop existing stream and give hardware a moment to release (needed on iOS)
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
      await new Promise(r => setTimeout(r, 200));
    }
    cancelAnimationFrame(rafRef.current);
    try { poseRef.current?.close(); } catch { /* ignore */ }
    poseRef.current = null; setPoseOk(false);

    // Try constraints from preferred → most permissive
    // NOTE: { exact: facingMode } intentionally removed — it causes OverconstrainedError
    // on many Android Chrome / iOS Safari versions, breaking the front camera fallback chain.
    const constraintOptions = [
      { video: { facingMode: facing, width: { ideal: 640 }, height: { ideal: 480 } }, audio: false },
      { video: { facingMode: facing }, audio: false },
      { video: true, audio: false }, // last resort: any camera (avoids hard failure on devices with single camera)
    ];

    let stream = null;
    let lastErr = null;
    for (const constraints of constraintOptions) {
      try {
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        break;
      } catch (err) {
        lastErr = err;
        if (err.name === 'NotAllowedError') break; // permission denied — no point retrying
      }
    }

    if (!stream) {
      setErrMsg(lastErr?.name === 'NotAllowedError'
        ? 'Camera permission denied. Please allow camera access in your browser settings.'
        : `Cannot access ${facing === 'user' ? 'front' : 'back'} camera: ${lastErr?.message || 'Unknown error'}`);
      setStage('error');
      return;
    }

    streamRef.current = stream;
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
    }
    setStage('ready');
    setPoseLoading(true);
    loadPoseModel();
  }, [facingMode]);

  // Kick off script downloads immediately — they'll be cached by the time camera is ready
  useEffect(() => { preloadPoseScripts(); }, []);

  useEffect(() => { initCamera(); return () => cleanup(); }, []);

  const flipCamera = async () => {
    const next = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(next);
    await initCamera(next);
  };

  const loadPoseModel = async () => {
    try {
      await loadScript(MEDIAPIPE_DRAWING);
      await loadScript(MEDIAPIPE_POSE);
      if (!window.Pose) { setPoseLoading(false); return; }
      const pose = new window.Pose({
        locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/${f}`,
      });
      // modelComplexity 0 = fastest, good enough for mobile
      pose.setOptions({ modelComplexity: 0, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 });
      pose.onResults(drawPose);
      await pose.initialize();
      poseRef.current = pose;
      setPoseOk(true);
      setPoseLoading(false);
      runDetection();
    } catch { setPoseLoading(false); }
  };

  const runDetection = () => {
    const detect = async () => {
      if (!poseRef.current || !videoRef.current || videoRef.current.readyState < 2) {
        rafRef.current = requestAnimationFrame(detect); return;
      }
      try { await poseRef.current.send({ image: videoRef.current }); } catch { /* ignore */ }
      rafRef.current = requestAnimationFrame(detect);
    };
    rafRef.current = requestAnimationFrame(detect);
  };

  const drawPose = (results) => {
    const canvas = canvasRef.current;
    const video  = videoRef.current;
    if (!canvas || !video) return;
    const w = video.videoWidth || 640;
    const h = video.videoHeight || 480;
    canvas.width = w; canvas.height = h;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, w, h);
    const lm = results.poseLandmarks;

    if (recorderRef.current?.state === 'recording') {
      totalRef.current += 1;
      if (lm && lm.length > 0) detectedRef.current += 1;
    }

    if (!lm || lm.length === 0) return;
    ctx.strokeStyle = 'rgba(0,212,255,0.9)'; ctx.lineWidth = 2.5; ctx.lineCap = 'round';
    CONNECTIONS.forEach(([a, b]) => {
      const pa = lm[a], pb = lm[b];
      if (!pa || !pb || (pa.visibility ?? 1) < 0.25 || (pb.visibility ?? 1) < 0.25) return;
      ctx.beginPath(); ctx.moveTo(pa.x * w, pa.y * h); ctx.lineTo(pb.x * w, pb.y * h); ctx.stroke();
    });
    lm.forEach((pt) => {
      if (!pt || (pt.visibility ?? 1) < 0.25) return;
      ctx.beginPath(); ctx.arc(pt.x * w, pt.y * h, 4, 0, 2 * Math.PI);
      ctx.fillStyle = '#00ff88'; ctx.strokeStyle = 'rgba(0,0,0,0.5)'; ctx.lineWidth = 1;
      ctx.fill(); ctx.stroke();
    });
  };

  const startRecording = () => {
    chunksRef.current = []; detectedRef.current = 0; totalRef.current = 0;
    const mimeType = ['video/webm;codecs=vp8','video/webm','video/mp4']
      .find(t => MediaRecorder.isTypeSupported(t)) || 'video/webm';
    const recorder = new MediaRecorder(streamRef.current, { mimeType });
    recorder.ondataavailable = (e) => { if (e.data?.size > 0) chunksRef.current.push(e.data); };
    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: mimeType });
      setRecordedBlob(blob);
      const rate = totalRef.current > 0 ? detectedRef.current / totalRef.current : null;
      if (!poseOk || rate === null) {
        setValidation({ ok: true, msg: null });
      } else if (rate >= 0.6) {
        setValidation({ ok: true, msg: `Pose detected in ${Math.round(rate * 100)}% of frames — great quality!` });
      } else if (rate >= 0.3) {
        setValidation({ ok: true, msg: `Detected in ${Math.round(rate * 100)}% of frames. Keep full body in frame for best results.` });
      } else {
        setValidation({ ok: false, msg: `Only ${Math.round(rate * 100)}% pose detection. Ensure full body is visible side-on in good lighting.` });
      }
      setStage('recorded');
    };
    recorder.start(100);
    recorderRef.current = recorder;
    setTimer(0); setStage('recording');
  };

  const stopRecording = () => recorderRef.current?.stop();

  useEffect(() => {
    if (stage !== 'recording') return;
    const iv = setInterval(() => setTimer(t => {
      if (t >= 59) { stopRecording(); return 0; }
      return t + 1;
    }), 1000);
    return () => clearInterval(iv);
  }, [stage]);

  const uploadAndAnalyze = async () => {
    if (!recordedBlob) return;
    setStage('uploading'); setUploadProgress(10);
    try {
      const ext   = recordedBlob.type.includes('mp4') ? '.mp4' : '.webm';
      const fd    = new FormData();
      fd.append('file', new File([recordedBlob], `mobile_shot${ext}`, { type: recordedBlob.type }));

      const uploadRes = await fetch(API('/api/upload'), { method: 'POST', body: fd });
      if (!uploadRes.ok) {
        const err = await uploadRes.json().catch(() => ({}));
        throw new Error(err.detail || `Upload failed (${uploadRes.status})`);
      }
      const { video_id: videoId } = await uploadRes.json();
      setUploadProgress(35);

      await fetch(API(`/api/analyze/${videoId}`), { method: 'POST' });
      setUploadProgress(50);

      let attempts = 0;
      const poll = async () => {
        attempts++;
        if (attempts > 120) { setErrMsg('Analysis timed out. Please try again.'); setStage('error'); return; }
        const res  = await fetch(API(`/api/result/${videoId}`));
        const data = await res.json();
        if (data.status === 'completed') {
          setUploadProgress(100);
          setStage('done');
        } else if (data.status === 'failed') {
          setErrMsg(data.error || 'Analysis failed. Please try again.');
          setStage('error');
        } else {
          setUploadProgress(50 + Math.round((data.progress ?? 0) * 0.5));
          setTimeout(poll, 2500);
        }
      };
      setTimeout(poll, 2500);
    } catch (err) {
      setErrMsg(err.message || 'Upload failed. Check WiFi and that the backend is running.');
      setStage('error');
    }
  };

  const retake = () => { setRecordedBlob(null); setValidation(null); setStage('ready'); };

  const cleanup = () => {
    cancelAnimationFrame(rafRef.current);
    streamRef.current?.getTracks().forEach(t => t.stop());
    try { poseRef.current?.close(); } catch { /* ignore */ }
    poseRef.current = null;
  };

  const isMirrored = facingMode === 'user'; // mirror front camera only

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white flex flex-col select-none" style={{ fontFamily: 'Inter, sans-serif' }}>

      {/* ── Header / Logo ── */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-[#0d0d15]">
        <div className="flex items-center gap-2.5">
          {/* Branded logo */}
          <div className="w-9 h-9 rounded-xl overflow-hidden"
               style={{ border: '1px solid rgba(0,212,255,0.3)' }}>
            <img src="/be_logo.png" alt="BattingEdge" className="w-full h-full object-cover" />
          </div>
          <div>
            <p className="font-extrabold text-white text-sm tracking-tight"
               style={{ background: 'linear-gradient(90deg,#00d4ff,#00ff88)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              BattingEdge
            </p>
            <p className="text-[10px] text-gray-500 -mt-0.5">AI Cricket Analysis · Mobile</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {poseLoading && !poseOk && (
            <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-white/5 border border-white/10">
              <Loader2 size={9} className="text-gray-400 animate-spin" />
              <span className="text-[9px] text-gray-500">Loading AI…</span>
            </div>
          )}
          {poseOk && (
            <div className="flex items-center gap-1 px-2 py-0.5 rounded-full"
                 style={{ background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)' }}>
              <span className="w-1.5 h-1.5 rounded-full bg-[#00d4ff] animate-pulse" />
              <span className="text-[9px] font-semibold text-[#00d4ff]">POSE AI ON</span>
            </div>
          )}
          {/* Camera flip button */}
          {(stage === 'ready' || stage === 'recording') && (
            <button
              onClick={flipCamera}
              className="p-2 rounded-xl text-gray-400 hover:text-white transition-colors"
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}
              title="Flip camera"
            >
              <FlipHorizontal size={16} />
            </button>
          )}
        </div>
      </div>

      {/* ── Tip banners (dismissible) ── */}
      {(stage === 'ready' || stage === 'loading') && !bannerDismissed && (
        <div className="relative border-b border-amber-500/15 bg-amber-500/5">
          <button
            onClick={() => setBannerDismissed(true)}
            className="absolute top-1 right-1 p-3 rounded-full text-gray-400 active:text-white transition-colors"
            style={{ background: 'transparent', minWidth: 44, minHeight: 44, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
          >
            <X size={14} />
          </button>
          <div className="flex items-start gap-2 px-4 pt-2.5 pb-1.5 pr-8">
            <Info size={13} className="text-amber-400 mt-0.5 flex-shrink-0" />
            <p className="text-[11px] text-amber-200/70 leading-relaxed">
              <strong className="text-white">For best results:</strong> Stand <strong className="text-white">side-on</strong>, full body head to toe, good lighting. Use <strong className="text-white">back camera</strong>.
            </p>
          </div>
          <div className="flex items-start gap-2 px-4 pb-2.5 pr-8">
            <AlertCircle size={12} className="text-red-400 mt-0.5 flex-shrink-0" />
            <p className="text-[11px] text-red-200/70 leading-relaxed">
              <strong className="text-red-300">Wrong angle = Wrong result.</strong> Record from the <strong className="text-white">side</strong> only.
            </p>
          </div>
        </div>
      )}

      {/* ── Camera area ── */}
      <div className="relative bg-black" style={{ flex: '1 1 0', minHeight: 0, aspectRatio: '3/4', maxHeight: '62vh' }}>

        {/* Loading */}
        {stage === 'loading' && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 z-10">
            <Loader2 size={28} className="text-[#00d4ff] animate-spin" />
            <p className="text-gray-400 text-sm">Starting camera…</p>
          </div>
        )}

        {/* Error */}
        {stage === 'error' && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 p-6 text-center z-10">
            <AlertCircle size={36} className="text-red-400" />
            <p className="text-white text-sm font-medium leading-relaxed">{errMsg}</p>
          </div>
        )}

        {/* Done */}
        {stage === 'done' && (
          <div className="absolute inset-0 bg-[#0a0a0f] flex flex-col items-center justify-center gap-4 p-6 text-center z-10">
            <div className="w-16 h-16 rounded-full flex items-center justify-center"
                 style={{ background: 'rgba(0,255,136,0.1)', border: '2px solid rgba(0,255,136,0.3)' }}>
              <CheckCircle2 size={30} className="text-[#00ff88]" />
            </div>
            <p className="text-white font-bold text-lg">Shot Uploaded!</p>
            <p className="text-gray-400 text-sm max-w-xs leading-relaxed">
              Analysis is running. Open <strong className="text-white">BattingEdge on your laptop or desktop</strong> to see your full result, grade, and coaching tips.
            </p>
            <div className="px-4 py-3 rounded-xl text-xs text-[#00d4ff] font-mono"
                 style={{ background: 'rgba(0,212,255,0.08)', border: '1px solid rgba(0,212,255,0.2)' }}>
              Results are only shown on the web app
            </div>
          </div>
        )}

        {/* Uploading */}
        {stage === 'uploading' && (
          <div className="absolute inset-0 bg-[#0a0a0f]/90 flex flex-col items-center justify-center gap-4 px-8 z-10">
            <Loader2 size={28} className="text-[#00d4ff] animate-spin" />
            <p className="text-white text-sm font-medium">Uploading & Analyzing…</p>
            <div className="w-full rounded-full overflow-hidden h-2" style={{ background: 'rgba(255,255,255,0.08)' }}>
              <motion.div
                className="h-full rounded-full"
                style={{ background: 'linear-gradient(90deg,#00d4ff,#00ff88)' }}
                animate={{ width: `${uploadProgress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            <p className="text-gray-500 text-xs">{uploadProgress}% — this may take 30–60 seconds</p>
          </div>
        )}

        {/* Video feed */}
        <video
          ref={videoRef} muted playsInline
          className="absolute inset-0 w-full h-full object-cover"
          style={{
            opacity: ['loading','error','done','uploading'].includes(stage) ? 0 : 1,
            transform: isMirrored ? 'scaleX(-1)' : 'none',
          }}
        />
        {/* Pose canvas */}
        <canvas
          ref={canvasRef}
          className="absolute inset-0 w-full h-full object-cover pointer-events-none"
          style={{
            opacity: ['loading','error','done','uploading'].includes(stage) ? 0 : 1,
            transform: isMirrored ? 'scaleX(-1)' : 'none',
          }}
        />

        {/* Recording badge */}
        {stage === 'recording' && (
          <div className="absolute top-3 left-3 z-20 flex items-center gap-1.5 px-2.5 py-1 rounded-full"
               style={{ background: 'rgba(239,68,68,0.9)', backdropFilter: 'blur(4px)' }}>
            <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
            <span className="text-white text-xs font-bold">REC {fmtTime(timer)}</span>
          </div>
        )}

        {/* Recorded overlay */}
        {stage === 'recorded' && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 px-6 text-center z-10"
               style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)' }}>
            {validation?.ok === false ? (
              <>
                <AlertCircle size={28} className="text-red-400" />
                <p className="text-white font-bold text-sm">Poor Video Quality</p>
                <p className="text-gray-300 text-xs max-w-xs">{validation.msg}</p>
              </>
            ) : (
              <>
                <CheckCircle2 size={28} className="text-[#00ff88]" />
                <p className="text-white font-bold text-sm">
                  {validation?.ok ? 'Good Video Quality' : 'Recording Complete'}
                </p>
                {validation?.msg && (
                  <p className="text-[#00ff88] text-[10px] max-w-xs">{validation.msg}</p>
                )}
              </>
            )}
          </div>
        )}

        {/* Body guide frame */}
        {(stage === 'ready' || stage === 'recording') && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="w-[38%] h-[85%] rounded-2xl" style={{ border: '2px dashed rgba(255,255,255,0.1)' }} />
          </div>
        )}
      </div>

      {/* ── Controls ── */}
      <div className="px-4 py-4 flex flex-col gap-3"
           style={{ background: '#0d0d15', borderTop: '1px solid rgba(255,255,255,0.08)' }}>

        {stage === 'ready' && (
          <button onClick={startRecording}
            className="w-full py-4 rounded-full font-bold text-sm flex items-center justify-center gap-2"
            style={{ background: '#ef4444', color: '#fff' }}>
            <Video size={16} /> Start Recording
          </button>
        )}

        {stage === 'recording' && (
          <>
            <p className="text-gray-500 text-xs text-center">{60 - timer}s remaining — auto-stops at 1:00</p>
            <button onClick={stopRecording}
              className="w-full py-4 rounded-full font-bold text-sm flex items-center justify-center gap-2"
              style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff' }}>
              <Square size={14} fill="white" /> Stop Recording
            </button>
          </>
        )}

        {stage === 'recorded' && (
          <>
            <button onClick={uploadAndAnalyze}
              className="w-full py-4 rounded-full font-bold text-sm flex items-center justify-center gap-2"
              style={{ background: '#00d4ff', color: '#000' }}>
              <Upload size={16} /> Send for Analysis
            </button>
            <button onClick={retake}
              className="w-full py-3 rounded-full font-medium text-sm text-gray-400"
              style={{ border: '1px solid rgba(255,255,255,0.12)' }}>
              Retake
            </button>
          </>
        )}

        {stage === 'error' && (
          <button onClick={() => initCamera()}
            className="w-full py-4 rounded-full font-bold text-sm"
            style={{ background: '#00d4ff', color: '#000' }}>
            Try Again
          </button>
        )}
      </div>
    </div>
  );
};

export default MobilePage;
