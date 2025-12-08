import React from 'react';

const ShotBadge = ({ shot, confidence }) => {
  const colors = {
    drive: "bg-blue-500/20 text-blue-400 border-blue-500/50",
    pull: "bg-green-500/20 text-green-400 border-green-500/50",
    cut: "bg-orange-500/20 text-orange-400 border-orange-500/50",
    sweep: "bg-purple-500/20 text-purple-400 border-purple-500/50",
    unknown: "bg-gray-500/20 text-gray-400 border-gray-500/50"
  };

  const style = colors[shot?.toLowerCase()] || colors.unknown;

  return (
    <div className={`flex items-center gap-3 px-6 py-3 rounded-2xl border ${style} backdrop-blur-sm`}>
      <div>
        <p className="text-xs font-bold uppercase opacity-70 tracking-wider">Detected Shot</p>
        <h2 className="text-2xl font-black tracking-tight">{shot.toUpperCase()}</h2>
      </div>
      <div className="h-8 w-[1px] bg-current opacity-20"></div>
      <div className="text-right">
        <p className="text-xs opacity-70">Confidence</p>
        <p className="font-bold">{confidence.toFixed(1)}%</p>
      </div>
    </div>
  );
};

export default ShotBadge;