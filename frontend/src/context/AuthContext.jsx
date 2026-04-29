import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getMe, mergeGuestHistory } from '../utils/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser]     = useState(null);
  const [token, setToken]   = useState(() => localStorage.getItem('be_token'));
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    if (!token) { setLoading(false); return; }
    try {
      const u = await getMe();
      setUser(u);
    } catch {
      localStorage.removeItem('be_token');
      setToken(null);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchUser(); }, [fetchUser]);

  const login = (newToken, userData) => {
    localStorage.setItem('be_token', newToken);
    setToken(newToken);
    setUser(userData);
    // Pull any guest-session analyses into this user's history
    if (userData?.id) mergeGuestHistory(userData.id);
  };

  const logout = () => {
    localStorage.removeItem('be_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, logout, refetch: fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
