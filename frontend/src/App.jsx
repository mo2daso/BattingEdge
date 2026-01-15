import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import UploadPage from './pages/UploadPage';
import ResultPage from './pages/ResultPage';

const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-jet-black text-white antialiased selection:bg-neon-blue selection:text-black">
        <Toaster 
          position="bottom-center"
          toastOptions={{
            style: {
              background: '#121212',
              color: '#fff',
              border: '1px solid rgba(0,240,255,0.2)',
            },
            success: {
              iconTheme: {
                primary: '#00F0FF',
                secondary: 'black',
              },
            },
          }}
        />
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/result/:videoId" element={<ResultPage />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;