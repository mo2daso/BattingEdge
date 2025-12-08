import React, { useState, useRef } from 'react';
import { Upload, FileVideo, Loader2, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { uploadVideo, triggerAnalysis } from '../utils/api';
import { useNavigate } from 'react-router-dom';

const UploadZone = () => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [status, setStatus] = useState('idle'); // idle, uploading, analyzing, error
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setIsDragging(true);
    else setIsDragging(false);
  };

  const validateAndSetFile = (selectedFile) => {
    const validTypes = ['video/mp4', 'video/x-msvideo', 'video/quicktime']; // mp4, avi, mov
    if (!validTypes.includes(selectedFile.type) && !selectedFile.name.endsWith('.mkv')) {
        alert("Invalid file type. Please upload MP4, AVI, or MOV.");
        return;
    }
    if (selectedFile.size > 100 * 1024 * 1024) { // 100MB
        alert("File too large. Max 100MB.");
        return;
    }
    setFile(selectedFile);
    setStatus('idle');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    
    try {
        setStatus('uploading');
        // 1. Upload
        const uploadRes = await uploadVideo(file, (percent) => setUploadProgress(percent));
        const videoId = uploadRes.video_id;

        // 2. Trigger Analysis
        setStatus('analyzing');
        await triggerAnalysis(videoId);

        // 3. Navigate
        setTimeout(() => navigate(`/result/${videoId}`), 1000);

    } catch (error) {
        console.error(error);
        setStatus('error');
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 mb-20">
      <motion.div 
        layout
        className={`relative border-2 border-dashed rounded-2xl p-10 text-center transition-colors cursor-pointer
          ${isDragging ? 'border-cricket-green bg-cricket-green/10' : 'border-gray-700 hover:border-gray-500 bg-cricket-card'}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current.click()}
      >
        <input 
            type="file" 
            ref={fileInputRef} 
            className="hidden" 
            accept=".mp4,.avi,.mov" 
            onChange={(e) => e.target.files[0] && validateAndSetFile(e.target.files[0])}
        />

        <AnimatePresence mode="wait">
            {!file ? (
                <motion.div 
                    key="prompt"
                    initial={{ opacity: 0 }} 
                    animate={{ opacity: 1 }} 
                    exit={{ opacity: 0 }}
                    className="flex flex-col items-center gap-4"
                >
                    <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center">
                        <Upload className="w-8 h-8 text-gray-400" />
                    </div>
                    <div>
                        <p className="text-xl font-semibold">Click to upload or drag and drop</p>
                        <p className="text-sm text-gray-500 mt-2">MP4, AVI, MOV (Max 100MB)</p>
                    </div>
                </motion.div>
            ) : (
                <motion.div 
                    key="file-selected"
                    initial={{ opacity: 0, scale: 0.9 }} 
                    animate={{ opacity: 1, scale: 1 }}
                    className="flex flex-col items-center gap-4"
                >
                    <FileVideo className="w-16 h-16 text-cricket-green" />
                    <div>
                        <p className="text-xl font-semibold">{file.name}</p>
                        <p className="text-sm text-gray-500 mt-1">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                    </div>
                    {status === 'idle' && (
                        <p className="text-sm text-cricket-green cursor-pointer hover:underline" onClick={(e) => {
                            e.stopPropagation();
                            setFile(null);
                        }}>Remove file</p>
                    )}
                </motion.div>
            )}
        </AnimatePresence>

        {/* Progress Bar Overlay */}
        {status === 'uploading' && (
            <div className="absolute inset-0 bg-cricket-card/90 flex flex-col items-center justify-center rounded-2xl z-10">
                <div className="w-64 h-2 bg-gray-700 rounded-full overflow-hidden mb-4">
                    <motion.div 
                        className="h-full bg-cricket-green" 
                        initial={{ width: 0 }}
                        animate={{ width: `${uploadProgress}%` }}
                    />
                </div>
                <p className="text-cricket-green font-medium">Uploading... {uploadProgress}%</p>
            </div>
        )}
      </motion.div>

      {/* Action Button */}
      <div className="mt-8 flex justify-center">
        <button
            onClick={handleAnalyze}
            disabled={!file || status !== 'idle'}
            className={`
                px-8 py-4 rounded-full font-bold text-lg flex items-center gap-2 transition-all
                ${!file || status !== 'idle'
                    ? 'bg-gray-800 text-gray-500 cursor-not-allowed' 
                    : 'bg-cricket-green text-black hover:bg-cricket-hover hover:scale-105 shadow-[0_0_20px_rgba(0,200,81,0.3)]'}
            `}
        >
            {status === 'idle' && <>Analyze Shot</>}
            {status === 'uploading' && <><Loader2 className="animate-spin" /> Uploading</>}
            {status === 'analyzing' && <><Loader2 className="animate-spin" /> Processing AI</>}
            {status === 'error' && <><AlertCircle /> Error - Try Again</>}
        </button>
      </div>
    </div>
  );
};

export default UploadZone;