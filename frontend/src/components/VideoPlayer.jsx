import React from 'react';
import { Download } from 'lucide-react';

const VideoPlayer = ({ videoUrl }) => {
  return (
    <div className="relative group rounded-2xl overflow-hidden border border-white/10 bg-black/40 shadow-2xl">
      <video 
        src={videoUrl} 
        className="w-full h-auto max-h-[70vh] object-contain"
        controls 
        autoPlay 
        loop
      />
      <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <a 
          href={videoUrl} 
          download="battingedge_analysis.mp4"
          className="flex items-center gap-2 bg-black/80 hover:bg-cricket-green hover:text-black text-white px-4 py-2 rounded-full text-sm font-bold transition-all backdrop-blur-md"
        >
          <Download className="w-4 h-4" /> Download
        </a>
      </div>
    </div>
  );
};

export default VideoPlayer;