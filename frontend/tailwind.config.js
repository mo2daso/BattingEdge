/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // We will force this to true in index.html/css
  theme: {
    extend: {
      colors: {
        'jet-black': '#050505',
        'surface': '#0A0A0A',
        'surface-highlight': '#121212',
        'neon-blue': '#00F0FF',
        'neon-blue-dim': 'rgba(0, 240, 255, 0.1)',
        'neon-purple': '#7000FF',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'neon': '0 0 20px rgba(0, 240, 255, 0.3)',
        'neon-strong': '0 0 30px rgba(0, 240, 255, 0.5)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}