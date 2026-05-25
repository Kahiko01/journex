'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth/AuthContext';
import axios from 'axios';

export default function SignupPage() {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { signup } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Track signup attempt
    try {
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'auth',
        component: 'signup',
        action: 'attempt',
        metadata: {
          email_provider: formData.email.split('@')[1],
          username_length: formData.username.length,
          has_full_name: !!formData.full_name,
          timestamp: new Date().toISOString()
        }
      });
    } catch (error) {
      console.error('Error tracking signup attempt:', error);
    }

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      
      // Track validation error
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'auth',
        component: 'signup',
        action: 'validation_error',
        metadata: { reason: 'password_mismatch' }
      }).catch(() => {});
      
      return;
    }

    // Validate password strength
    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      setLoading(false);
      
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'auth',
        component: 'signup',
        action: 'validation_error',
        metadata: { reason: 'password_too_short' }
      }).catch(() => {});
      
      return;
    }

    if (!/[A-Z]/.test(formData.password)) {
      setError('Password must contain at least one uppercase letter');
      setLoading(false);
      
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'auth',
        component: 'signup',
        action: 'validation_error',
        metadata: { reason: 'no_uppercase' }
      }).catch(() => {});
      
      return;
    }

    if (!/[0-9]/.test(formData.password)) {
      setError('Password must contain at least one number');
      setLoading(false);
      
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'auth',
        component: 'signup',
        action: 'validation_error',
        metadata: { reason: 'no_number' }
      }).catch(() => {});
      
      return;
    }

    try {
      await signup(
        formData.email,
        formData.username,
        formData.password,
        formData.full_name || undefined
      );
      
      // Track successful signup
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'auth',
        component: 'signup',
        action: 'success'
      });
      
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Signup failed');
      
      // Track failed signup
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'auth',
        component: 'signup',
        action: 'failed',
        metadata: {
          reason: err.message || 'server_error'
        }
      }).catch(() => {});
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center relative overflow-hidden">
      {/* Cyberpunk Background */}
      <div className="fixed inset-0">
        <div className="absolute inset-0 bg-[linear-gradient(rgba(168,85,247,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(168,85,247,0.05)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse"></div>
      </div>

      {/* Floating particles */}
      <div className="fixed inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-purple-400/30 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
            }}
          />
        ))}
      </div>

      <div className="relative z-10 w-full max-w-md">
        <div className="bg-black/60 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-8 shadow-2xl">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400 mb-2">
              INITIALIZE
            </h1>
            <p className="text-gray-400 font-mono text-sm">CREATE ACCOUNT</p>
          </div>

          {/* Error message */}
          {error && (
            <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 px-4 py-3 rounded-lg mb-6 font-mono text-sm">
              ⚠️ {error}
            </div>
          )}

          {/* Signup form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-mono text-purple-400 mb-2">
                EMAIL
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                data-track="signup-email"
                className="w-full bg-black/50 border border-purple-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-purple-400 focus:shadow-[0_0_10px_rgba(168,85,247,0.3)] transition-all"
                placeholder="Enter email"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-mono text-purple-400 mb-2">
                USERNAME
              </label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                data-track="signup-username"
                className="w-full bg-black/50 border border-purple-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-purple-400 focus:shadow-[0_0_10px_rgba(168,85,247,0.3)] transition-all"
                placeholder="Choose username"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-mono text-purple-400 mb-2">
                FULL NAME (OPTIONAL)
              </label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                data-track="signup-fullname"
                className="w-full bg-black/50 border border-purple-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-purple-400 focus:shadow-[0_0_10px_rgba(168,85,247,0.3)] transition-all"
                placeholder="Enter full name"
              />
            </div>

            <div>
              <label className="block text-sm font-mono text-purple-400 mb-2">
                PASSWORD
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                data-track="signup-password"
                className="w-full bg-black/50 border border-purple-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-purple-400 focus:shadow-[0_0_10px_rgba(168,85,247,0.3)] transition-all"
                placeholder="Create password"
                required
              />
              <p className="text-xs text-gray-600 mt-1 font-mono">
                Min 8 chars, 1 uppercase, 1 number
              </p>
            </div>

            <div>
              <label className="block text-sm font-mono text-purple-400 mb-2">
                CONFIRM PASSWORD
              </label>
              <input
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                data-track="signup-confirm-password"
                className="w-full bg-black/50 border border-purple-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-purple-400 focus:shadow-[0_0_10px_rgba(168,85,247,0.3)] transition-all"
                placeholder="Confirm password"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              data-track="signup-submit"
              className="w-full bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-bold py-3 rounded-lg hover:from-purple-600 hover:to-cyan-600 transition-all disabled:opacity-50 relative group overflow-hidden mt-6"
            >
              <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
              <span className="relative font-mono">
                {loading ? 'PROCESSING...' : '▶ CREATE ACCOUNT'}
              </span>
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-gray-600 font-mono text-sm">
              ALREADY HAVE AN ACCOUNT?{' '}
              <Link 
                href="/login" 
                data-track="signup-to-login"
                className="text-purple-400 hover:text-purple-300 hover:underline"
              >
                LOGIN
              </Link>
            </p>
          </div>

          {/* Password Requirements */}
          <div className="mt-6 pt-6 border-t border-purple-500/20">
            <div className="text-xs font-mono text-gray-600 text-center">
              <p>🔒 All data encrypted • No plain text storage</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
