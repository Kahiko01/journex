'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('token');
    const expiresAt = localStorage.getItem('token_expires');

    // Check if token is expired
    if (expiresAt && Date.now() > parseInt(expiresAt)) {
      localStorage.removeItem('token');
      localStorage.removeItem('token_expires');
      setLoading(false);
      return;
    }

    if (token) {
      try {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        const response = await axios.get('http://localhost:8000/api/v1/auth/me');
        setUser(response.data);
        setError(null);
      } catch (err: any) {
        console.error('Auth check failed:', err);
        localStorage.removeItem('token');
        localStorage.removeItem('token_expires');
        delete axios.defaults.headers.common['Authorization'];
        setError('Your session expired. Please sign in again.');
      }
    }
    setLoading(false);
  };

  const login = async (token: string) => {
    try {
      localStorage.setItem('token', token);
      // Set default expiration to 7 days if not provided
      const expiresIn = 7 * 24 * 60 * 60 * 1000; // 7 days
      localStorage.setItem('token_expires', (Date.now() + expiresIn).toString());
      
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const response = await axios.get('http://localhost:8000/api/v1/auth/me');
      setUser(response.data);
      setError(null);
    } catch (err: any) {
      setError('Failed to complete login. Please try again.');
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('token_expires');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
    setError(null);
    router.push('/login');
  };

  const clearError = () => setError(null);

  const value = {
    user,
    loading,
    error,
    login,
    logout,
    isAuthenticated: !!user,
    clearError
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

// Optional: Loading component for auth state
export function AuthLoading({ children }: { children: ReactNode }) {
  const { loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 border-2 border-slate-700 border-t-blue-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400 text-sm">Loading your account...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
