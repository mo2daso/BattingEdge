import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'

export default defineConfig(({ mode }) => {
  const isDev = mode === 'development';

  return {
    plugins: isDev ? [react(), basicSsl()] : [react()],

    server: {
      port: 5173,
      host: true,   // expose to LAN for mobile QR recording
      https: true,  // required for camera access on mobile over LAN
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        },
        '/auth': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          secure: false,
        },
      },
    },

    // In production the frontend is served from Vercel.
    // All /api and /auth calls go directly to the Render backend via VITE_API_URL.
    // Set VITE_API_URL in Vercel project settings → Environment Variables.
    define: {
      __API_URL__: JSON.stringify(process.env.VITE_API_URL || ''),
    },
  };
});
