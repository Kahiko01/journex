'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth/AuthContext';
import axios from 'axios';

export default function LoginPage() {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Track login attempt
    try {
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'auth',
        component: 'login',
        action: 'attempt',
        metadata: {
          username_length: formData.username.length,
          timestamp: new Date().toISOString()
        }
      });
    } catch (error) {
      console.error('Error tracking login attempt:', error);
    }

    try {
      await login(formData.username, formData.password);
      
      // Track successful login
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'auth',
        component: 'login',
        action: 'success'
      });
      
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed');
      
      // Track failed login
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'auth',
        component: 'login',
        action: 'failed',
        metadata: {
          reason: err.message || 'invalid_credentials'
        }
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center relative overflow-hidden">
      {/* Cyberpunk Background */}
      <div className="fixed inset-0">
        <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.05)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
      </div>

      {/* Floating particles */}
      <div className="fixed inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-cyan-400/30 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 w-full max-w-md">
        <div className="bg-black/60 backdrop-blur-xl border border-cyan-500/30 rounded-2xl p-8 shadow-2xl">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-600 mb-2">
              JOURNEX
            </h1>
            <p className="text-gray-400 font-mono text-sm">ACCESS TERMINAL</p>
          </div>

          {/* Error message */}
          {error && (
            <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 px-4 py-3 rounded-lg mb-6 font-mono text-sm">
              ⚠️ {error}
            </div>
          )}

          {/* Login form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-mono text-cyan-400 mb-2">
                USERNAME
              </label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                data-track="login-username"
                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400 focus:shadow-[0_0_10px_rgba(6,182,212,0.3)] transition-all"
                placeholder="Enter username"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-mono text-cyan-400 mb-2">
                PASSWORD
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                data-track="login-password"
                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400 focus:shadow-[0_0_10px_rgba(6,182,212,0.3)] transition-all"
                placeholder="Enter password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              data-track="login-submit"
              className="w-full bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold py-3 rounded-lg hover:from-cyan-600 hover:to-purple-700 transition-all disabled:opacity-50 relative group overflow-hidden"
            >
              <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
              <span className="relative font-mono">
                {loading ? 'AUTHENTICATING...' : '▶ LOGIN'}
              </span>
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-gray-600 font-mono text-sm">
              NO ACCOUNT?{' '}
              <Link 
                href="/signup" 
                data-track="login-to-signup"
                className="text-cyan-400 hover:text-cyan-300 hover:underline"
              >
                INITIALIZE
              </Link>
            </p>
          </div>

          {/* System Status */}
          <div className="mt-6 pt-6 border-t border-cyan-500/20">
            <div className="flex items-center justify-center gap-4 text-xs font-mono">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span className="text-gray-600">SYSTEM ONLINE</span>
              </div>
              <span className="text-gray-700">|</span>
              <span className="text-cyan-400">v2.5.0</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
