'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';

interface NavItem {
  name: string;
  path: string;
  icon: string;
  color: string;
}

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navItems: NavItem[] = [
    { name: 'Dashboard', path: '/dashboard', icon: '📊', color: 'from-blue-500 to-indigo-500' },
    { name: 'Trades', path: '/trades', icon: '📝', color: 'from-purple-500 to-violet-500' },
    { name: 'University', path: '/university', icon: '📚', color: 'from-emerald-500 to-teal-500' },
    { name: 'Calendar', path: '/calendar', icon: '📅', color: 'from-amber-500 to-orange-500' },
    { name: 'Profile', path: '/profile', icon: '👤', color: 'from-slate-500 to-slate-600' }
  ];

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      scrolled ? 'bg-slate-950/90 backdrop-blur-xl border-b border-slate-800/50 shadow-lg shadow-black/20' : 'bg-transparent'
    }`}>
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2 group">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:shadow-blue-500/30 transition-shadow">
              <span className="text-white font-bold text-sm">J</span>
            </div>
            <span className="text-xl font-semibold text-white tracking-tight">
              Journex
            </span>
          </Link>
          
          {/* Navigation */}
          <div className="flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = pathname === item.path || pathname.startsWith(`${item.path}/`);
              
              return (
                <Link
                  key={item.path}
                  href={item.path}
                  className={`relative px-3 py-2 rounded-lg transition-all duration-200 flex items-center gap-2 text-sm font-medium ${
                    isActive 
                      ? 'text-white' 
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  {isActive && (
                    <div className={`absolute inset-0 bg-gradient-to-r ${item.color} rounded-lg opacity-10`}></div>
                  )}
                  <span className="relative">{item.icon}</span>
                  <span className="relative hidden sm:inline">{item.name}</span>
                  {isActive && (
                    <div className={`absolute -bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-gradient-to-r ${item.color}`}></div>
                  )}
                </Link>
              );
            })}
          </div>

          {/* Quick actions */}
          <div className="flex items-center gap-3">
            <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-800/50 rounded-lg transition">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
            <Link 
              href="/trades/new" 
              className="hidden sm:flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition shadow-lg shadow-blue-600/20"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              New trade
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
