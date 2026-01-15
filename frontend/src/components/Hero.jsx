import React from 'react';
import { motion } from 'framer-motion';
import { Activity, ShieldCheck, Scale } from 'lucide-react';

const Hero = () => {
  return (
    <div className="relative flex flex-col items-center justify-center text-center px-4 py-20 lg:py-32 overflow-hidden">
      
      {/* Background Glows */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-neon-blue/10 rounded-full blur-[120px] pointer-events-none"></div>
      
      {/* Badge */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-neon-blue/10 border border-neon-blue/20 text-neon-blue text-xs font-semibold tracking-wide uppercase mb-8"
      >
        <span className="w-2 h-2 rounded-full bg-neon-blue animate-pulse"></span>
        V9.5 AI Engine Live
      </motion.div>

      {/* Heading */}
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="text-5xl lg:text-7xl font-black tracking-tight text-white mb-6 relative z-10 max-w-4xl leading-[1.1]"
      >
        Master Your Shot with <br />
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-neon-blue to-neon-purple text-glow">
          BattingEdge AI
        </span>
      </motion.h1>

      {/* Subtitle */}
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="text-lg text-gray-400 max-w-2xl mb-10 leading-relaxed"
      >
        BattingEdge uses advanced computer vision to break down your cricket technique in milliseconds. Upload your video and get professional-grade biomechanical feedback instantly.
      </motion.p>

      {/* Stats / Trust Indicators */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="flex flex-wrap justify-center gap-6 lg:gap-10 text-sm font-medium text-gray-500"
      >
        <div className="flex items-center gap-2">
          <Activity className="text-neon-blue" size={20} />
          <span>95% Accuracy</span>
        </div>
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-neon-blue" size={20} />
          <span>ECB & MCC Coaching Standards</span>
        </div>
        <div className="flex items-center gap-2">
          <Scale className="text-neon-blue" size={20} />
          <span>Rule-Based Shot Analysis</span>
        </div>
      </motion.div>
    </div>
  );
};

export default Hero;