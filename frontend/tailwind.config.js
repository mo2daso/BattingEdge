/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'jet-black': '#0a0a0f',
        'surface':   '#0d0d14',
        'surface-2': '#141420',
        'surface-3': '#1a1a2e',
        'neon-blue':  '#00d4ff',
        'neon-green': '#00ff88',
        'neon-purple':'#7c3aed',
        'border-dim': 'rgba(255,255,255,0.06)',
        'border-soft':'rgba(255,255,255,0.10)',
        // legacy aliases kept so old components don't break
        'surface-highlight': '#141420',
        'neon-blue-dim': 'rgba(0,212,255,0.1)',
      },
      fontFamily: {
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Space Grotesk"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'neon':        '0 0 20px rgba(0,212,255,0.25)',
        'neon-strong': '0 0 40px rgba(0,212,255,0.45)',
        'neon-green':  '0 0 20px rgba(0,255,136,0.25)',
        'card':        '0 4px 24px rgba(0,0,0,0.5)',
        'glow':        '0 0 80px rgba(0,212,255,0.12)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'float':      'float 6s ease-in-out infinite',
        'shimmer':    'shimmer 2.5s linear infinite',
        'spin-slow':  'spin 10s linear infinite',
        'gradient':   'gradientShift 12s ease infinite',
      },
      keyframes: {
        float: {
          '0%,100%': { transform: 'translateY(0px)' },
          '50%':     { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        gradientShift: {
          '0%,100%': { backgroundPosition: '0% 50%' },
          '50%':     { backgroundPosition: '100% 50%' },
        },
      },
      backgroundSize: { '200%': '200% 200%' },
    },
  },
  plugins: [],
}