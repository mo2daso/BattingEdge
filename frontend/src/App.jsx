import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import UploadPage from './pages/UploadPage';
import ResultPage from './pages/ResultPage'; // <--- IMPORT THIS

function App() {
  return (
    <Router>
      <Toaster 
        position="top-center"
        toastOptions={{
          style: {
            background: '#111625',
            color: '#fff',
            border: '1px solid rgba(255,255,255,0.1)'
          }
        }}
      />
      <Routes>
        <Route path="/" element={<UploadPage />} />
        {/* The line below MUST look like this: */}
        <Route path="/result/:videoId" element={<ResultPage />} />
      </Routes>
    </Router>
  );
}

export default App;