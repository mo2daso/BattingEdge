import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import UploadZone from '../components/UploadZone';
import Features from '../components/Features';

const UploadPage = () => {
  return (
    <div className="min-h-screen bg-jet-black text-white selection:bg-neon-blue selection:text-black">
      <Navbar />
      
      {/* Hero & Upload Section */}
      <div className="relative pt-24 pb-20 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 relative z-10">
          <Hero />
          
          {/* Added ID here for the scroll target */}
          <div id="upload-zone" className="mt-[-40px] relative z-20 scroll-mt-32">
            <UploadZone />
          </div>
        </div>
      </div>

      {/* Features Section */}
      <Features />

      {/* Footer */}
      <footer className="py-8 bg-jet-black border-t border-white/10 text-center">
        <div className="flex items-center justify-center gap-2 mb-4 opacity-50">
          <img src="/logo.png" alt="Logo" className="w-6 h-6 grayscale" />
          <span className="font-bold text-sm">BattingEdge AI</span>
        </div>
        <p className="text-xs text-gray-600">
          © 2026 BattingEdge. All rights reserved. Final Year Project.
        </p>
      </footer>
    </div>
  );
};

export default UploadPage;