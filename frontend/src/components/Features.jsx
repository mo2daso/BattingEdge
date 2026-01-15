import React from 'react';
import { Scan, BrainCircuit, BarChart3, Layers } from 'lucide-react';

const Features = () => {
  const features = [
    {
      icon: <Scan size={32} />,
      title: "Skeletal Tracking",
      desc: "Our vision engine maps 33 distinct body landmarks at 60fps to analyze your stance, swing, and follow-through with millimeter precision."
    },
    {
      icon: <BrainCircuit size={32} />,
      title: "Neural Classification",
      desc: "Powered by a V9.5 Stacking Ensemble model that identifies shots (Drive, Pull, Cut, Sweep) with 94.7% validation accuracy."
    },
    {
      icon: <BarChart3 size={32} />,
      title: "Biomechanics Metrics",
      desc: "Get quantitative data on elbow extension angles, head stability drift, foot placement, and rotational velocity."
    },
    {
      icon: <Layers size={32} />,
      title: "Pro Benchmarking",
      desc: "Compare your technique against elite standards derived from ECB Level 3 coaching manuals and professional match data."
    }
  ];

  return (
    <section id="features" className="py-24 bg-surface">
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold text-white mb-4">Why BattingEdge?</h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            We move beyond simple video playback. Our system understands the physics of cricket.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((f, i) => (
            <div key={i} className="p-8 rounded-2xl bg-surface-highlight border border-white/5 hover:border-neon-blue/30 transition-all group">
              <div className="w-14 h-14 rounded-xl bg-jet-black flex items-center justify-center text-neon-blue mb-6 group-hover:scale-110 transition-transform border border-white/10">
                {f.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{f.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;