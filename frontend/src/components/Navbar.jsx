import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Zap } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const scrollToSection = (sectionId) => {
    if (location.pathname === '/') {
      const element = document.getElementById(sectionId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      // If on result page, go to home then anchor
      window.location.href = `/#${sectionId}`;
    }
  };

  return (
    <nav className="fixed w-full z-50 top-0 start-0 border-b border-white/10 bg-jet-black/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-20 items-center">
          
          {/* Logo Section */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative w-10 h-10 overflow-hidden rounded-xl border border-white/10 group-hover:border-neon-blue/50 transition-colors">
              <img 
                src="/logo.png" 
                alt="BattingEdge Logo" 
                className="w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-neon-blue/20 blur-md opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </div>
            <span className="text-xl font-bold tracking-tight text-white">
              Batting<span className="text-neon-blue">Edge</span>
            </span>
          </Link>

          {/* Nav Links */}
          <div className="hidden md:flex items-center space-x-8">
            <button 
              onClick={() => scrollToSection('features')} 
              className="text-sm font-medium text-gray-400 hover:text-white transition-colors"
            >
              Technology
            </button>
            
            <button 
              onClick={() => scrollToSection('upload-zone')} 
              className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-surface-highlight border border-white/10 hover:border-neon-blue/50 text-white text-sm font-semibold transition-all hover:shadow-[0_0_15px_rgba(0,240,255,0.15)]"
            >
              <Zap size={16} className="text-neon-blue" />
              Analyze Now
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;