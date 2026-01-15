import React, { useState, useRef } from 'react';
import { Upload, FileVideo, Loader2, AlertCircle, X, Info } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { uploadVideo, triggerAnalysis } from '../utils/api';
import { useNavigate } from 'react-router-dom';

const UploadZone = () => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [status, setStatus] = useState('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (!file) return;
    try {
      setStatus('uploading');
      const uploadRes = await uploadVideo(file, setUploadProgress);
      setStatus('analyzing');
      await triggerAnalysis(uploadRes.video_id);
      setTimeout(() => navigate(`/result/${uploadRes.video_id}`), 500);
    } catch (err) {
      setErrorMessage(err.message || "Upload failed");
      setStatus('error');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.[0]) setFile(e.dataTransfer.files[0]);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <motion.div
        layout
        className={`
          relative overflow-hidden rounded-3xl border-2 border-dashed transition-all duration-300
          ${isDragging 
            ? 'border-neon-blue bg-neon-blue/5 scale-[1.02]' 
            : 'border-white/10 hover:border-white/20 bg-surface'
          }
        `}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <div className="p-12 flex flex-col items-center justify-center min-h-[400px] text-center">
          <AnimatePresence mode="wait">
            {!file ? (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center"
              >
                <div 
                  onClick={() => fileInputRef.current?.click()}
                  className="w-20 h-20 mb-6 rounded-full bg-surface-highlight flex items-center justify-center cursor-pointer hover:bg-white/5 transition-colors group"
                >
                  <Upload className="w-8 h-8 text-gray-400 group-hover:text-neon-blue transition-colors" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">Upload Analysis Video</h3>
                <p className="text-gray-400 max-w-sm mb-6">
                  Drag & drop your shot video here or click to browse. Supports MP4, MOV, AVI (Max 100MB).
                </p>

                {/* --- ADDED NOTE HERE --- */}
                <div className="bg-neon-blue/10 border border-neon-blue/20 rounded-xl p-4 max-w-sm mb-8 flex items-start gap-3 text-left">
                  <Info className="w-5 h-5 text-neon-blue shrink-0 mt-0.5" />
                  <div className="text-xs text-blue-200 leading-relaxed">
                    <strong className="text-neon-blue block mb-1">For Best Accuracy:</strong>
                    Ensure only <u>one person</u> is in the frame and record from a <u>Front View</u> (Bowler's perspective).
                  </div>
                </div>
                {/* ----------------------- */}

                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-3 rounded-xl bg-white text-black font-bold hover:bg-gray-200 transition-colors"
                >
                  Select File
                </button>
              </motion.div>
            ) : (
              <motion.div
                key="selected"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="w-full max-w-md"
              >
                {status === 'idle' && (
                  <div className="bg-surface-highlight border border-white/10 rounded-2xl p-6 flex items-center gap-4 mb-8">
                    <div className="w-12 h-12 rounded-lg bg-neon-blue/10 flex items-center justify-center">
                      <FileVideo className="text-neon-blue" />
                    </div>
                    <div className="flex-1 text-left overflow-hidden">
                      <p className="text-white font-medium truncate">{file.name}</p>
                      <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                    </div>
                    <button onClick={() => setFile(null)} className="p-2 hover:bg-white/10 rounded-full">
                      <X size={20} className="text-gray-400" />
                    </button>
                  </div>
                )}

                {status === 'idle' ? (
                  <button
                    onClick={handleAnalyze}
                    className="w-full py-4 rounded-xl bg-neon-blue text-black font-bold text-lg hover:bg-[#33f3ff] transition-all shadow-neon hover:shadow-neon-strong"
                  >
                    Start Analysis
                  </button>
                ) : (
                  <div className="text-center">
                    <Loader2 className="w-10 h-10 text-neon-blue animate-spin mx-auto mb-4" />
                    <h4 className="text-xl font-bold text-white mb-2">
                      {status === 'uploading' ? 'Uploading Video...' : 'Analyzing Biomechanics...'}
                    </h4>
                    <p className="text-gray-400 text-sm">This typically takes 10-15 seconds.</p>
                    {status === 'uploading' && (
                      <div className="w-full h-1 bg-white/10 rounded-full mt-6 overflow-hidden">
                        <motion.div 
                          className="h-full bg-neon-blue"
                          initial={{ width: 0 }}
                          animate={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
          
          {status === 'error' && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-400">
              <AlertCircle size={20} />
              <span>{errorMessage}</span>
              <button onClick={() => setStatus('idle')} className="ml-auto underline text-xs">Retry</button>
            </div>
          )}
        </div>
        <input type="file" ref={fileInputRef} className="hidden" accept="video/*" onChange={(e) => e.target.files[0] && setFile(e.target.files[0])} />
      </motion.div>
    </div>
  );
};

export default UploadZone;