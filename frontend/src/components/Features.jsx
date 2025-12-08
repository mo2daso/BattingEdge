import React from 'react';
import { Target, Activity, Eye } from 'lucide-react';

const Features = () => {
  const features = [
    {
      icon: <Target className="w-8 h-8 text-blue-400" />,
      title: "Shot Classification",
      desc: "Instant recognition of Drives, Pulls, Cuts, and Sweeps using Bi-LSTM Deep Learning models."
    },
    {
      icon: <Activity className="w-8 h-8 text-cricket-green" />,
      title: "Biomech Analysis",
      desc: "Detailed breakdown of elbow angles, head stability, and footwork mechanics."
    },
    {
      icon: <Eye className="w-8 h-8 text-purple-400" />,
      title: "Visual Feedback",
      desc: "Frame-by-frame skeleton overlay and HUD to visualize errors in real-time."
    }
  ];

  return (
    <div id="features" className="py-20 bg-cricket-card/30">
      <div className="max-w-6xl mx-auto px-4 grid md:grid-cols-3 gap-8">
        {features.map((f, i) => (
          <div key={i} className="p-8 rounded-2xl bg-cricket-card border border-white/5 hover:border-cricket-green/30 transition-all">
            <div className="mb-4 bg-gray-800/50 w-fit p-3 rounded-xl">{f.icon}</div>
            <h3 className="text-xl font-bold mb-2">{f.title}</h3>
            <p className="text-gray-400 leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Features;