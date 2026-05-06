import React, { useRef, useState, useEffect } from 'react';
import { Scissors } from 'lucide-react';

/**
 * VideoTrimmer — draggable-handle clip selector.
 *
 * Props:
 *   file            — File | Blob to preview
 *   onTrimComplete  — (file, startTimeSec, endTimeSec) => void
 *   onSkip          — () => void  (upload full video as-is)
 */
const VideoTrimmer = ({ file, onTrimComplete, onSkip }) => {
  const [duration,   setDuration]  = useState(0);
  const [startTime,  setStartTime] = useState(0);
  const [endTime,    setEndTime]   = useState(0);
  const [videoUrl,   setVideoUrl]  = useState('');
  const [videoError, setVideoError] = useState(false);

  const videoRef    = useRef(null);
  const timelineRef = useRef(null);

  // stateRef keeps values accessible inside pointer-event closures without
  // stale-closure issues (handlers are created once per drag, not per render).
  const stateRef = useRef({ start: 0, end: 0, dur: 0 });

  // Keep stateRef in sync with React state
  useEffect(() => { stateRef.current.start = startTime; }, [startTime]);
  useEffect(() => { stateRef.current.end   = endTime;   }, [endTime]);
  useEffect(() => { stateRef.current.dur   = duration;  }, [duration]);

  // Build object URL for the video preview
  useEffect(() => {
    if (!file) return;
    setVideoError(false);
    const url = URL.createObjectURL(file);
    setVideoUrl(url);

    const vid = document.createElement('video');
    vid.src = url;
    vid.onloadedmetadata = () => {
      const dur = vid.duration || 0;
      setDuration(dur);
      setEndTime(dur);
      stateRef.current.dur = dur;
      stateRef.current.end = dur;
    };
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const fmt = (t) => {
    const m = Math.floor(t / 60);
    const s = Math.floor(t % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  /** Convert a clientX pixel position to a time value within [0, duration] */
  const clientXToTime = (clientX) => {
    const rect = timelineRef.current?.getBoundingClientRect();
    if (!rect || !stateRef.current.dur) return 0;
    const ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    return ratio * stateRef.current.dur;
  };

  /**
   * Begin dragging a handle.
   * Creates self-contained move/up closures so removeEventListener always
   * removes the exact same function reference that was added.
   */
  const startDrag = (which) => (e) => {
    e.preventDefault();

    const onMove = (ev) => {
      // PointerEvent carries clientX for both mouse and touch
      const clientX = ev.clientX ?? 0;
      const t = clientXToTime(clientX);

      if (which === 'start') {
        const v = Math.max(0, Math.min(t, stateRef.current.end - 0.5));
        stateRef.current.start = v;
        setStartTime(v);
        if (videoRef.current) videoRef.current.currentTime = v;
      } else {
        const v = Math.max(stateRef.current.start + 0.5, Math.min(t, stateRef.current.dur));
        stateRef.current.end = v;
        setEndTime(v);
        if (videoRef.current) videoRef.current.currentTime = v;
      }
    };

    const onUp = () => {
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup',   onUp);
    };

    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup',   onUp);
  };

  const startPct = duration > 0 ? (startTime / duration) * 100 : 0;
  const endPct   = duration > 0 ? (endTime   / duration) * 100 : 100;
  const selectedSec = Math.max(0, Math.round(endTime - startTime));

  // Handle styles reused for both handles
  const handleStyle = {
    position: 'absolute',
    top: '50%',
    transform: 'translate(-50%, -50%)',
    width: 44,
    height: 44,
    borderRadius: '50%',
    background: '#00d4ff',
    boxShadow: '0 2px 12px rgba(0,212,255,0.5)',
    cursor: 'grab',
    touchAction: 'none',
    zIndex: 10,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    userSelect: 'none',
  };

  return (
    <div
      className="rounded-2xl border border-border-dim overflow-hidden"
      style={{ background: 'var(--surface-2)' }}
    >
      {/* ── Header ── */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
        <Scissors size={13} className="text-neon-blue" />
        <span className="text-sm font-semibold text-white">Trim Clip</span>
        <span className="ml-auto text-xs font-mono text-neon-green">
          {selectedSec}s selected
        </span>
      </div>

      {/* ── Video preview ── */}
      <div className="bg-black relative" style={{ minHeight: '80px' }}>
        {!videoError ? (
          <video
            ref={videoRef}
            src={videoUrl}
            className="w-full max-h-48 object-contain"
            muted
            playsInline
            preload="metadata"
            onError={() => setVideoError(true)}
          />
        ) : (
          <div className="flex flex-col items-center justify-center py-6 gap-1.5 text-center px-4">
            <p className="text-sm text-gray-400">Preview unavailable</p>
            <p className="text-xs text-gray-500">
              This format may not be supported in browser — the video will still be sent for analysis
            </p>
          </div>
        )}
      </div>

      {/* Broadcast video warning */}
      <div className="px-4 pt-3 pb-0">
        <div className="flex items-start gap-2 bg-yellow-500/5 border border-yellow-500/15 rounded-xl p-3 text-left">
          <span className="text-yellow-400 text-xs leading-tight flex-shrink-0 mt-0.5">⚠️</span>
          <p className="text-xs text-yellow-200/70 leading-relaxed">
            <span className="text-yellow-300 font-semibold">Professional / broadcast videos may fail — </span>
            the AI needs a single player, filmed side-on at close range. TV footage with wide angles or multiple players will not analyse correctly.
          </p>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {/* ── Timeline ── */}
        <div
          ref={timelineRef}
          className="relative rounded-lg select-none"
          style={{ height: 40, background: 'rgba(255,255,255,0.04)' }}
        >
          {/* Left trimmed-out region */}
          <div
            style={{
              position: 'absolute', top: 0, left: 0, height: '100%',
              width: `${startPct}%`,
              background: 'rgba(255,255,255,0.04)',
              borderRadius: '8px 0 0 8px',
            }}
          />

          {/* Selected region (highlighted) */}
          <div
            style={{
              position: 'absolute', top: 0, height: '100%',
              left: `${startPct}%`,
              width: `${endPct - startPct}%`,
              background: 'rgba(0,212,255,0.30)',
              borderLeft:  '2px solid #00d4ff',
              borderRight: '2px solid #00d4ff',
            }}
          />

          {/* Right trimmed-out region */}
          <div
            style={{
              position: 'absolute', top: 0, right: 0, height: '100%',
              width: `${100 - endPct}%`,
              background: 'rgba(255,255,255,0.04)',
              borderRadius: '0 8px 8px 0',
            }}
          />

          {/* Start handle */}
          <div
            style={{ ...handleStyle, left: `${startPct}%` }}
            onPointerDown={startDrag('start')}
          >
            <div style={{ width: 3, height: 16, background: 'rgba(0,0,0,0.45)', borderRadius: 2 }} />
          </div>

          {/* End handle */}
          <div
            style={{ ...handleStyle, left: `${endPct}%` }}
            onPointerDown={startDrag('end')}
          >
            <div style={{ width: 3, height: 16, background: 'rgba(0,0,0,0.45)', borderRadius: 2 }} />
          </div>
        </div>

        {/* ── Legend ── */}
        <div className="flex items-center gap-4 text-[11px]">
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm border border-border-dim"
                 style={{ background: 'rgba(255,255,255,0.06)' }} />
            <span style={{ color: 'var(--text-dim)' }}>Trimmed out</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm border-2 border-[#00d4ff]"
                 style={{ background: 'rgba(0,212,255,0.25)' }} />
            <span className="text-neon-blue">Sent for analysis</span>
          </div>
        </div>

        {/* ── Time labels ── */}
        <div className="flex justify-between text-xs font-mono" style={{ color: 'var(--text-dim)' }}>
          <span>
            Start:&nbsp;
            <span className="text-white font-bold">{fmt(startTime)}</span>
          </span>
          <span>
            End:&nbsp;
            <span className="text-white font-bold">{fmt(endTime)}</span>
          </span>
        </div>

        {/* ── Action buttons ── */}
        <div className="flex gap-3">
          <button
            onClick={() => onTrimComplete(file, startTime, endTime)}
            className="flex-1 min-h-[44px] py-3 rounded-xl font-bold text-sm transition-all hover:opacity-90"
            style={{ background: '#00d4ff', color: '#000' }}
          >
            Trim &amp; Analyze
          </button>
          <button
            onClick={onSkip}
            className="flex-1 min-h-[44px] py-3 rounded-xl border border-border-dim font-semibold text-sm transition-all hover:border-border-soft"
            style={{ background: 'var(--surface-3)', color: 'var(--text-muted)' }}
          >
            Skip &amp; Analyze
          </button>
        </div>
      </div>
    </div>
  );
};

export default VideoTrimmer;
