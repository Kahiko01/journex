'use client';

import Link from 'next/link';
import { useState } from 'react';

interface AnalyticsButtonProps {
  variant?: 'floating' | 'navbar' | 'dashboard';
  className?: string;
}

export default function AnalyticsButton({ variant = 'dashboard', className = '' }: AnalyticsButtonProps) {
  const [isHovered, setIsHovered] = useState(false);

  if (variant === 'floating') {
    return (
      <Link
        href="/analytics"
        className={`fixed bottom-24 right-6 group z-40 ${className}`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Outer glow rings */}
        <div className="absolute inset-0 rounded-full bg-purple-500 opacity-20 animate-ping"></div>
        <div className="absolute inset-0 rounded-full bg-pink-500 opacity-30 animate-pulse"></div>
        
        {/* Main button */}
        <div className="relative bg-gradient-to-r from-purple-600 via-pink-600 to-rose-600 text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-all duration-300 hover:shadow-purple-500/50">
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-gray-900 animate-pulse"></div>
          <svg className="w-6 h-6 group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          
          {/* Tooltip */}
          <div className="absolute right-full mr-4 top-1/2 -translate-y-1/2 bg-gray-800 text-white px-3 py-1 rounded-lg text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300 border border-gray-700">
            Neural Analytics
            <div className="absolute top-1/2 -right-2 -translate-y-1/2 border-8 border-transparent border-l-gray-800"></div>
          </div>
        </div>
      </Link>
    );
  }

  if (variant === 'navbar') {
    return (
      <Link
        href="/analytics"
        className={`relative group ${className}`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg opacity-0 group-hover:opacity-100 blur transition duration-300"></div>
        <div className="relative bg-gray-800 px-4 py-2 rounded-lg flex items-center gap-2 border border-gray-700 group-hover:border-transparent transition">
          <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span className="text-white font-medium">Analytics</span>
        </div>
      </Link>
    );
  }

  // Default dashboard variant
  return (
    <Link
      href="/analytics"
      className={`relative group block ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl opacity-0 group-hover:opacity-50 blur transition duration-500"></div>
      <div className="relative bg-gray-800/90 backdrop-blur-sm border border-gray-700 rounded-2xl p-6 hover:border-transparent transition-all duration-300 overflow-hidden">
        {/* Scanline effect */}
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/5 to-transparent translate-y-full group-hover:translate-y-[-100%] transition-transform duration-1000"></div>
        
        {/* Corner accents */}
        <div className="absolute top-0 right-0 w-16 h-16 overflow-hidden">
          <div className="absolute top-0 right-0 w-px h-8 bg-gradient-to-b from-purple-500/50 to-transparent"></div>
          <div className="absolute top-0 right-0 h-px w-8 bg-gradient-to-l from-purple-500/50 to-transparent"></div>
        </div>
        
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <span className="text-4xl group-hover:scale-110 transition-transform duration-300">📊</span>
            <span className="text-xs font-mono text-purple-400/60 border border-purple-500/30 rounded-full px-3 py-1">
              ADVANCED
            </span>
          </div>
          
          <h3 className="text-xl font-bold text-white mb-2 group-hover:text-purple-400 transition-colors">
            Neural Analytics
          </h3>
          
          <p className="text-gray-400 text-sm mb-4 font-mono">
            AI-powered insights • Risk metrics • Performance analysis
          </p>
          
          <div className="flex items-center gap-2 text-sm font-mono">
            <span className="text-purple-400">ACCESS_TERMINAL</span>
            <svg className="w-4 h-4 text-purple-400 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </div>
        </div>
      </div>
    </Link>
  );
}
