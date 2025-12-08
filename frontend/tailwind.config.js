/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cricket: {
          green: "#00c851",    // Main Brand Color
          dark: "#0a0e1a",     // Background
          card: "#111625",     // Card Background
          hover: "#00e25b",    // Hover State
          surface: "#1a2133"   // Secondary Surface
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}