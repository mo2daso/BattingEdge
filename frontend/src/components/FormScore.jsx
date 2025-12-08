import React from 'react';
import { motion } from 'framer-motion';

const FormScore = ({ score }) => {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  
  let color = "text-red-500";
  if (score >= 80) color = "text-cricket-green";
  else if (score >= 60) color = "text-yellow-400";
  else if (score >= 40) color = "text-orange-500";

  return (
    <div className="relative w-32 h-32 flex items-center justify-center">
      <svg className="w-full h-full transform -rotate-90">
        {/* Background Circle */}
        <circle
          cx="64" cy="64" r={radius}
          className="stroke-gray-700"
          strokeWidth="8" fill="transparent"
        />
        {/* Progress Circle */}
        <motion.circle
          cx="64" cy="64" r={radius}
          className={`stroke-current ${color} drop-shadow-[0_0_10px_rgba(0,200,81,0.4)]`}
          strokeWidth="8" fill="transparent"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className={`text-3xl font-bold ${color}`}>{score}</span>
        <span className="text-[10px] text-gray-400 uppercase tracking-widest">Score</span>
      </div>
    </div>
  );
};

export default FormScore;