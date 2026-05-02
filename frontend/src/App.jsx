import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, useNavigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider }   from './context/ThemeContext';
import AuthModal           from './components/AuthModal';
import ChatBot             from './components/ChatBot';
import LandingPage         from './pages/LandingPage';
import AnalyzePage         from './pages/AnalyzePage';
import ResultPage          from './pages/ResultPage';
import DashboardPage       from './pages/DashboardPage';
import VerifyEmailPage     from './pages/VerifyEmailPage';
import ResetPasswordPage   from './pages/ResetPasswordPage';
import MobilePage          from './pages/MobilePage';
import SettingsPage        from './pages/SettingsPage';
import FAQPage             from './pages/FAQPage';

const ProtectedRoute = ({ children, onOpenAuth }) => {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !user) {
      navigate('/', { replace: true });
      onOpenAuth('login');
    }
  }, [loading, user]);

  if (loading || !user) return null;
  return children;
};

// Inner component so useLocation works inside Router
const AppInner = ({ authOpen, setAuthOpen, authDefault, openAuth }) => {
  const location = useLocation();
  const isMobile = location.pathname === '/mobile';

  return (
    <div className="min-h-screen antialiased" style={{ background: 'var(--bg)', color: 'var(--text)' }}>
      <Toaster
        position="bottom-center"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'var(--surface-2)',
            color: 'var(--text)',
            border: '1px solid var(--border-soft)',
            borderRadius: '12px',
            fontSize: '14px',
          },
          success: { iconTheme: { primary: '#00ff88', secondary: '#141420' } },
          error:   { iconTheme: { primary: '#ef4444', secondary: '#141420' } },
        }}
      />

      <AuthModal
        isOpen={authOpen}
        onClose={() => setAuthOpen(false)}
        defaultTab={authDefault}
      />

      {/* ChatBot hidden on /mobile — phone is for recording only */}
      {!isMobile && <ChatBot />}

      <Routes>
        <Route path="/"                element={<LandingPage      onOpenAuth={openAuth} />} />
        <Route path="/analyze"         element={<ProtectedRoute onOpenAuth={openAuth}><AnalyzePage onOpenAuth={openAuth} /></ProtectedRoute>} />
        <Route path="/result/:videoId" element={<ResultPage       onOpenAuth={openAuth} />} />
        <Route path="/dashboard"       element={<DashboardPage    onOpenAuth={openAuth} />} />
        <Route path="/settings"        element={<SettingsPage     onOpenAuth={openAuth} />} />
        <Route path="/verify"          element={<VerifyEmailPage />} />
        <Route path="/reset-password"  element={<ResetPasswordPage />} />
        <Route path="/mobile"          element={<MobilePage />} />
        <Route path="/faq"             element={<FAQPage          onOpenAuth={openAuth} />} />
      </Routes>
    </div>
  );
};

const App = () => {
  const [authOpen,    setAuthOpen]    = useState(false);
  const [authDefault, setAuthDefault] = useState('login');

  const openAuth = (tab = 'login') => { setAuthDefault(tab); setAuthOpen(true); };

  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <AppInner
            authOpen={authOpen}
            setAuthOpen={setAuthOpen}
            authDefault={authDefault}
            openAuth={openAuth}
          />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
