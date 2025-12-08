import React from 'react';
import { motion } from 'framer-motion';

const Hero = () => {
  return (
    <div className="text-center py-16 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 text-gray-900 dark:text-white">
          Master Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-cricket-green to-emerald-600">Cricket Shot</span>
        </h1>
        <p className="text-gray-600 dark:text-gray-400 text-lg md:text-xl max-w-2xl mx-auto">
          AI-powered biomechanical analysis. Get instant, pro-level feedback on your cricket shots. Become a textbook cricket Batsman today!
        </p>
      </motion.div>
    </div>
  );
};

export default Hero;