import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Camera, Square, Video, AlertCircle, Loader2, CheckCircle2, FlipHorizontal } from 'lucide-react';

const MEDIAPIPE_DRAWING = 'https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils@0.3.1620248257/drawing_utils.js';
const MEDIAPIPE_POSE    = 'https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/pose.js';

const loadScript = (src) => new Promise((resolve) => {
  if (document.querySelector(`script[src="${src}"]`)) { resolve(); return; }
  const s = document.createElement('script');
  s.src = src; s.crossOrigin = 'anonymous';
  s.onload = resolve; s.onerror = resolve;
  document.head.appendChild(s);
});

const fmtTime = (s) => `${String(Math.floor(s / 60)).padStart(2,'0')}:${String(s % 60).padStart(2,'0')}`;

const CONNECTIONS = [
  [11,12],[11,13],[13,15],[15,17],[15,19],[17,19],
  [12,14],[14,16],[16,18],[16,20],[18,20],
  [11,23],[12,24],[23,24],
  [23,25],[25,27],[27,29],[29,31],[27,31],
  [24,26],[26,28],[28,30],[30,32],[28,32],
  [0,1],[1,2],[2,3],[3,7],[0,4],[4,5],[5,6],[6,8],[9,10],
];

const CameraModal = ({ isOpen, onClose, onVideoReady }) => {
  const videoRef     = useRef(null);
  const canvasRef    = useRef(null);
  const streamRef    = useRef(null);
  const recorderRef  = useRef(null);
  const chunksRef    = useRef([]);
  const poseRef      = useRef(null);
  const rafRef       = useRef(null);

  const [stage,       setStage]       = useState('init');
  const [timer,       setTimer]       = useState(0);
  const [poseOk,      setPoseOk]      = useState(false);
  const [poseLoading, setPoseLoading] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [errMsg,      setErrMsg]      = useState('');
  const [validation,  setValidation]  = useState(null);
  const [facingMode,  setFacingMode]  = useState('environment'); // 'environment'=back, 'user'=front
  const [canSwitchCamera, setCanSwitchCamera] = useState(false);
  const detectedFrames = useRef(0);
  const totalFrames    = useRef(0);

  // ── Camera init ───────────────────────────────────────────────────────────
  const initCamera = useCallback(async (facing = facingMode) => {
    setStage('loading');
    setErrMsg('');

    // Stop any existing stream
    streamRef.current?.getTracks().forEach(t => t.stop());

    const constraints = [
      { video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: facing }, audio: false },
      { video: { facingMode: facing }, audio: false },
      { video: true, audio: false }, // last resort — no facingMode constraint
    ];

    let stream = null;
    let lastErr = null;

    for (const c of constraints) {
      try {
        stream = await navigator.mediaDevices.getUserMedia(c);
        break;
      } catch (err) {
        lastErr = err;
      }
    }

    if (!stream) {
      const isPermissionErr = lastErr?.name === 'NotAllowedError';
      const isFrontErr      = facing === 'user';

      if (isPermissionErr) {
        setErrMsg('Camera permission denied. Please allow camera access in your browser settings.');
      } else if (isFrontErr) {
        setErrMsg('Front camera is not available on this device.');
      } else {
        setErrMsg('Could not access camera. Please check your device.');
      }
      setStage('error');
      return;
    }

    streamRef.current = stream;
    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
    }
    setStage('ready');

    // Check if device has multiple cameras
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoCams = devices.filter(d => d.kind === 'videoinput');
      setCanSwitchCamera(videoCams.length > 1);
    } catch { /* ignore */ }

    setPoseLoading(true);
    loadPose();
  }, [facingMode]);

  useEffect(() => {
    if (isOpen) initCamera('environment');
    return () => cleanup();
  }, [isOpen]);

  // ── Camera flip ───────────────────────────────────────────────────────────
  const flipCamera = async () => {
    const next = facingMode === 'environment' ? 'user' : 'environment';
    setFacingMode(next);

    // Stop pose detection temporarily
    cancelAnimationFrame(rafRef.current);
    try { poseRef.current?.close(); } catch { /* ignore */ }
    poseRef.current = null;
    setPoseOk(false);
    setPoseLoading(false);

    await initCamera(next);
  };

  // ── MediaPipe Pose ────────────────────────────────────────────────────────
  const loadPose = async () => {
    try {
      await loadScript(MEDIAPIPE_DRAWING);
      await loadScript(MEDIAPIPE_POSE);
      if (!window.Pose) return;

      const pose = new window.Pose({
        locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.5.1675469404/${f}`,
      });
      pose.setOptions({ modelComplexity: 1, smoothLandmarks: true, minDetectionConfidence: 0.5, minTrackingConfidence: 0.5 });
      pose.onResults(drawPose);
      await pose.initialize();
      poseRef.current = pose;
      setPoseOk(true);
      setPoseLoading(false);
      runDetection();
    } catch {
      setPoseLoading(false);
    }
  };

  const runDetection = () => {
    const detect = async () => {
      if (!poseRef.current || !videoRef.current || videoRef.current.readyState < 2) {
        rafRef.current = requestAnimationFrame(detect);
        return;
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

    const w = video.videoWidth  || 640;
    const h = video.videoHeight || 480;
    canvas.width  = w;
    canvas.height = h;

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, w, h);

    const lm = results.poseLandmarks;

    if (recorderRef.current?.state === 'recording') {
      totalFrames.current += 1;
      if (lm && lm.length > 0) detectedFrames.current += 1;
    }

    if (!lm || lm.length === 0) return;

    ctx.strokeStyle = 'rgba(0,212,255,0.85)';
    ctx.lineWidth   = 2.5;
    ctx.lineCap     = 'round';
    CONNECTIONS.forEach(([a, b]) => {
      const pa = lm[a], pb = lm[b];
      if (!pa || !pb) return;
      if ((pa.visibility ?? 1) < 0.25 || (pb.visibility ?? 1) < 0.25) return;
      ctx.beginPath();
      ctx.moveTo(pa.x * w, pa.y * h);
      ctx.lineTo(pb.x * w, pb.y * h);
      ctx.stroke();
    });

    lm.forEach((pt) => {
      if (!pt || (pt.visibility ?? 1) < 0.25) return;
      ctx.beginPath();
      ctx.arc(pt.x * w, pt.y * h, 4, 0, 2 * Math.PI);
      ctx.fillStyle   = '#00ff88';
      ctx.strokeStyle = 'rgba(0,0,0,0.5)';
      ctx.lineWidth   = 1;
      ctx.fill();
      ctx.stroke();
    });
  };

  // ── Recording ─────────────────────────────────────────────────────────────
  const startRecording = () => {
    chunksRef.current = [];
    detectedFrames.current = 0;
    totalFrames.current    = 0;
    const mimeType = MediaRecorder.isTypeSupported('video/webm;codecs=vp8')
      ? 'video/webm;codecs=vp8' : 'video/webm';
    const recorder = new MediaRecorder(streamRef.current, { mimeType });
    recorder.ondataavailable = (e) => { if (e.data?.size > 0) chunksRef.current.push(e.data); };
    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'video/webm' });
      setRecordedBlob(blob);
      const total    = totalFrames.current;
      const detected = detectedFrames.current;
      const rate     = total > 0 ? detected / total : 0;
      let vResult;
      if (!poseOk || total === 0) {
        vResult = { ok: true, rate: null, msg: null };
      } else if (rate >= 0.6) {
        vResult = { ok: true, rate, msg: `Pose detected in ${Math.round(rate * 100)}% of frames — great quality!` };
      } else if (rate >= 0.3) {
        vResult = { ok: true, rate, msg: `Pose detected in ${Math.round(rate * 100)}% of frames. Try to keep your full body in frame.` };
      } else {
        vResult = { ok: false, rate, msg: `Pose only detected in ${Math.round(rate * 100)}% of frames. Make sure full body is visible side-on in good lighting.` };
      }
      setValidation(vResult);
      setStage('recorded');
    };
    recorder.start(100);
    recorderRef.current = recorder;
    setTimer(0);
    setStage('recording');
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

  const handleAnalyze = () => {
    if (!recordedBlob) return;
    const file = new File([recordedBlob], 'camera_recording.webm', { type: 'video/webm' });
    onVideoReady(file);
    onClose();
  };

  const retake = () => { setRecordedBlob(null); setValidation(null); setStage('ready'); };

  const cleanup = () => {
    cancelAnimationFrame(rafRef.current);
    streamRef.current?.getTracks().forEach(t => t.stop());
    try { poseRef.current?.close(); } catch { /* ignore */ }
    poseRef.current = null;
  };

  // Mirror only when using front camera
  const mirrorStyle = facingMode === 'user' ? { transform: 'scaleX(-1)' } : {};

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      >
        <motion.div className="absolute inset-0 bg-black/80 backdrop-blur-md" onClick={onClose} />

        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 280 }}
          className="relative w-full max-w-3xl glass-strong rounded-2xl overflow-hidden border border-border-soft shadow-[0_32px_100px_rgba(0,0,0,0.8)]"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-border-dim">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-neon-blue/10 border border-neon-blue/20 flex items-center justify-center">
                <Camera size={16} className="text-neon-blue" />
              </div>
              <div>
                <h3 className="font-bold text-white text-sm">Camera Analysis</h3>
                <p className="text-xs text-gray-500">
                  {facingMode === 'user' ? '📱 Front camera' : '📷 Back camera'} · {poseOk ? '✦ AI Pose Active' : 'Position yourself side-on'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {/* Flip camera button */}
              {(canSwitchCamera || true) && stage !== 'recording' && stage !== 'recorded' && (
                <button
                  onClick={flipCamera}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 hover:border-white/20 text-gray-300 hover:text-white text-xs font-medium transition-all"
                  title={facingMode === 'environment' ? 'Switch to front camera' : 'Switch to back camera'}
                >
                  <FlipHorizontal size={13} />
                  {facingMode === 'environment' ? 'Front Cam' : 'Back Cam'}
                </button>
              )}
              <button onClick={onClose} className="p-2 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-all">
                <X size={18} />
              </button>
            </div>
          </div>

          {/* Camera view */}
          <div className="relative bg-black" style={{ aspectRatio: '16/9' }}>
            {stage === 'loading' && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
                <Loader2 size={32} className="text-neon-blue animate-spin" />
                <p className="text-gray-400 text-sm">Starting {facingMode === 'user' ? 'front' : 'back'} camera…</p>
              </div>
            )}

            {stage === 'error' && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 p-8 text-center">
                <AlertCircle size={40} className="text-red-400" />
                <p className="text-white font-medium">{errMsg}</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <button
                    onClick={() => initCamera(facingMode)}
                    className="px-4 py-2 rounded-xl bg-neon-blue text-black text-sm font-bold hover:bg-[#33deff] transition-all"
                  >
                    Try Again
                  </button>
                  {facingMode === 'user' && (
                    <button
                      onClick={() => { setFacingMode('environment'); initCamera('environment'); }}
                      className="px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white text-sm font-medium hover:bg-white/20 transition-all"
                    >
                      Use Back Camera
                    </button>
                  )}
                  {facingMode === 'environment' && (
                    <button
                      onClick={() => { setFacingMode('user'); initCamera('user'); }}
                      className="px-4 py-2 rounded-xl bg-white/10 border border-white/20 text-white text-sm font-medium hover:bg-white/20 transition-all"
                    >
                      Use Front Camera
                    </button>
                  )}
                </div>
              </div>
            )}

            <video
              ref={videoRef}
              muted playsInline
              className={`absolute inset-0 w-full h-full object-cover ${stage === 'loading' || stage === 'error' ? 'opacity-0' : ''}`}
              style={mirrorStyle}
            />
            <canvas
              ref={canvasRef}
              className="absolute inset-0 w-full h-full object-cover pointer-events-none"
              style={mirrorStyle}
            />

            {stage === 'recording' && (
              <div className="absolute top-4 left-4 flex items-center gap-2 bg-red-500/90 backdrop-blur px-3 py-1.5 rounded-full">
                <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
                <span className="text-white text-xs font-bold">REC {fmtTime(timer)}</span>
              </div>
            )}

            {stage === 'recorded' && (
              <div className="absolute inset-0 bg-black/70 backdrop-blur-sm flex flex-col items-center justify-center gap-3 px-6 text-center">
                {validation?.ok === false ? (
                  <>
                    <div className="w-14 h-14 rounded-full bg-red-500/10 border-2 border-red-500/40 flex items-center justify-center">
                      <AlertCircle size={28} className="text-red-400" />
                    </div>
                    <p className="text-white font-bold text-base">Poor Video Quality</p>
                    <p className="text-gray-300 text-sm max-w-xs">{validation.msg}</p>
                    <p className="text-gray-500 text-xs">You can still analyze, or retake for better results.</p>
                  </>
                ) : (
                  <>
                    <div className="w-14 h-14 rounded-full bg-neon-green/10 border-2 border-neon-green/40 flex items-center justify-center">
                      <CheckCircle2 size={28} className="text-neon-green" />
                    </div>
                    <p className="text-white font-bold text-base">Recording Complete</p>
                    {validation?.msg
                      ? <p className="text-neon-green text-xs max-w-xs">{validation.msg}</p>
                      : <p className="text-gray-400 text-sm">{fmtTime(timer)} captured</p>
                    }
                  </>
                )}
              </div>
            )}

            {(stage === 'ready' || stage === 'recording') && (
              <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                <div className="w-[45%] h-[80%] border-2 border-dashed border-white/10 rounded-2xl" />
              </div>
            )}

            {poseLoading && !poseOk && stage !== 'error' && (
              <div className="absolute top-4 right-4 flex items-center gap-1.5 bg-black/60 border border-white/10 backdrop-blur px-2.5 py-1 rounded-full">
                <Loader2 size={10} className="text-gray-400 animate-spin" />
                <span className="text-gray-400 text-[10px] font-semibold">Loading AI Pose…</span>
              </div>
            )}

            {poseOk && stage !== 'recorded' && stage !== 'error' && (
              <div className="absolute top-4 right-4 flex items-center gap-1.5 bg-neon-blue/10 border border-neon-blue/20 backdrop-blur px-2.5 py-1 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-neon-blue animate-pulse" />
                <span className="text-neon-blue text-[10px] font-semibold">POSE AI ON</span>
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="px-6 py-5 flex items-center justify-between gap-4">
            <div className="text-xs text-gray-500">
              {stage === 'ready'     && 'Stand side-on, full body in frame. Max 60 seconds.'}
              {stage === 'recording' && `Recording… auto-stops at 1:00. ${60 - timer}s remaining.`}
              {stage === 'recorded'  && 'Ready to analyze. Or retake if needed.'}
            </div>

            <div className="flex items-center gap-3 flex-shrink-0">
              {stage === 'recorded' && (
                <button onClick={retake} className="px-4 py-2 rounded-xl bg-surface-2 border border-border-soft text-sm font-medium text-gray-300 hover:text-white hover:border-white/20 transition-all">
                  Retake
                </button>
              )}
              {stage === 'ready' && (
                <button onClick={startRecording} className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-red-500 hover:bg-red-400 text-white font-bold text-sm transition-all shadow-[0_0_20px_rgba(239,68,68,0.35)]">
                  <Video size={15} /> Start Recording
                </button>
              )}
              {stage === 'recording' && (
                <button onClick={stopRecording} className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-surface-2 border border-white/20 hover:border-white/40 text-white font-bold text-sm transition-all">
                  <Square size={14} fill="white" /> Stop
                </button>
              )}
              {stage === 'recorded' && (
                <button onClick={handleAnalyze} className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-neon-blue text-black font-bold text-sm hover:bg-[#33deff] transition-all shadow-neon">
                  Analyze Recording
                </button>
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default CameraModal;
