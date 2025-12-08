import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import UploadZone from '../components/UploadZone';
import Features from '../components/Features';

const UploadPage = () => {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-cricket-dark transition-colors duration-300">
      <Navbar />
      
      <main className="flex-grow flex flex-col items-center relative overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cricket-green/10 rounded-full blur-[128px] pointer-events-none"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-[128px] pointer-events-none"></div>

        <div className="w-full pt-12 pb-6 z-10">
            <Hero />
        </div>
        
        <div className="w-full px-4 flex justify-center pb-20 z-10">
            <UploadZone />
        </div>
        
        <div className="w-full bg-white dark:bg-cricket-card/50 border-t border-gray-200 dark:border-white/5 z-10">
            <Features />
        </div>
      </main>
      
      <footer className="py-6 text-center text-gray-500 dark:text-gray-600 text-sm bg-white dark:bg-cricket-dark border-t border-gray-200 dark:border-white/5">
        <p>© 2025 BattingEdge AI. Final Year Project.</p>
      </footer>
    </div>
  );
};

export default UploadPage;