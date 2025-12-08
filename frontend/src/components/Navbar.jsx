import React, { useState, useEffect } from 'react';
import { Sun, Moon, Menu, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

const Navbar = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <nav className="w-full bg-white dark:bg-cricket-dark/90 backdrop-blur-md sticky top-0 z-50 border-b border-gray-200 dark:border-white/5 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
        
        {/* LOGO */}
        <Link to="/" className="flex items-center gap-3 group z-50">
          <img 
            src="/logo.jpg" 
            alt="BattingEdge Logo" 
            className="h-10 w-auto object-contain rounded-md" 
          />
          <span className="text-xl font-extrabold tracking-tight text-gray-900 dark:text-white">
            Batting<span className="text-cricket-green">Edge</span>
          </span>
        </Link>
        
        {/* DESKTOP MENU (Hidden on Mobile) */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600 dark:text-gray-400">
          <Link to="/" className="hover:text-cricket-green dark:hover:text-white transition-colors">Home</Link>
          <a href="#features" className="hover:text-cricket-green dark:hover:text-white transition-colors">Features</a>
          
          {/* Dark Mode Toggle */}
          <button 
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors border border-transparent dark:border-white/10"
          >
            {darkMode ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-gray-600" />}
          </button>
        </div>

        {/* MOBILE ACTIONS (Hamburger + Theme) */}
        <div className="flex items-center gap-4 md:hidden z-50">
          <button 
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            {darkMode ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-gray-600" />}
          </button>
          
          <button 
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="p-2 text-gray-600 dark:text-white"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* MOBILE DROPDOWN MENU */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-white dark:bg-[#0a0e1a] border-b border-gray-200 dark:border-white/5 overflow-hidden"
          >
            <div className="flex flex-col p-6 gap-4 text-center font-bold text-gray-800 dark:text-gray-200">
              <Link 
                to="/" 
                onClick={() => setIsMenuOpen(false)}
                className="py-3 hover:bg-gray-100 dark:hover:bg-white/5 rounded-xl transition-colors"
              >
                Home
              </Link>
              <a 
                href="#features" 
                onClick={() => setIsMenuOpen(false)}
                className="py-3 hover:bg-gray-100 dark:hover:bg-white/5 rounded-xl transition-colors"
              >
                Features
              </a>
              <div className="pt-4 border-t border-gray-200 dark:border-white/5">
                <p className="text-xs text-gray-500 uppercase tracking-widest mb-2">Developed for</p>
                <p className="text-sm text-cricket-green">Final Year Project 2025</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;