import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext({});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('datapulse_token');
    if (token) {
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, []);

  async function fetchProfile() {
    try {
      const { data } = await api.get('/users/me');
      setUser(data);
    } catch {
      localStorage.removeItem('datapulse_token');
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  async function login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const { data } = await api.post('/auth/login/access-token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    localStorage.setItem('datapulse_token', data.access_token);
    await fetchProfile();
  }

  async function register(fullName, email, password) {
    await api.post('/users/', {
      user_name: fullName,
      email,
      password,
    });
    await login(email, password);
  }

  function logout() {
    localStorage.removeItem('datapulse_token');
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);