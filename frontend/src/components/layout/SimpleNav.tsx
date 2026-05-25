'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/auth/AuthContext';
import NotificationBell from '@/components/notifications/NotificationBell';
import UniversityDropdown from '@/components/university/UniversityDropdown';

export default function SimpleNav() {
  const pathname = usePathname();
  const { user, logout, isAuthenticated } = useAuth();
  
  // Core trading & dashboard links
  const mainLinks = [
    { name: 'Home', path: '/' },
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Trades', path: '/trades' },
    { name: 'Analytics', path: '/analytics' },
  ];

  // User account links
  const accountLinks = [
    { name: 'Notifications', path: '/notifications' },
    { name: 'Settings', path: '/settings' },
  ];

  // Helper to check if user is admin
  const isAdmin = isAuthenticated && (user?.username === 'testuser' || user?.username === 'admin');

  // Check if any main link is active (for styling groups)
  const isMainSectionActive = mainLinks.some(link => pathname === link.path);

  return (
    <nav className="fixed top-0 left-0 right-0 bg-gray-900 border-b border-gray-800 z-50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link 
            href="/" 
            className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent hover:from-blue-300 hover:to-cyan-300 transition-all"
          >
            Journex
          </Link>
          
          <div className="flex items-center gap-1">
            {/* Admin Section - Separated with distinct styling */}
            {isAdmin && (
              <div className="flex items-center gap-1 mr-2 pr-3 border-r border-gray-700">
                <Link
                  href="/admin/university"
                  className="px-3 py-1.5 rounded-md text-xs font-bold tracking-wide text-amber-400 bg-amber-950/40 border border-amber-600/40 hover:bg-amber-900/50 hover:border-amber-500 hover:text-amber-300 transition-all"
                  title="University Admin"
                >
                  📚 ADMIN
                </Link>
                <Link
                  href="/admin/anonymous"
                  className="px-3 py-1.5 rounded-md text-xs font-bold tracking-wide text-emerald-400 bg-emerald-950/40 border border-emerald-600/40 hover:bg-emerald-900/50 hover:border-emerald-500 hover:text-emerald-300 transition-all"
                  title="Anonymous Statistics"
                >
                  📊 ANON
                </Link>
              </div>
            )}
            
            {/* Main Navigation - Trading Focus */}
            <div className="flex items-center gap-1 bg-gray-800/50 rounded-lg p-1 mr-2">
              {mainLinks.map((link) => (
                <Link
                  key={link.path}
                  href={link.path}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                    pathname === link.path
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  {link.name}
                </Link>
              ))}
            </div>

            {/* University Dropdown - Highlighted as key feature */}
            <div className="mr-2">
              <UniversityDropdown />
            </div>
            
            {/* Account & System Section */}
            <div className="flex items-center gap-1 bg-gray-800/30 rounded-lg p-1 mr-2">
              {accountLinks.map((link) => (
                <Link
                  key={link.path}
                  href={link.path}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
                    pathname === link.path
                      ? 'bg-gray-700 text-white'
                      : 'text-gray-500 hover:text-gray-200 hover:bg-gray-700/50'
                  }`}
                >
                  {link.name === 'Notifications' && pathname !== link.path ? (
                    <span className="flex items-center gap-1">
                      <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></span>
                      {link.name}
                    </span>
                  ) : (
                    link.name
                  )}
                </Link>
              ))}
              
              {/* Notification Bell - Integrated with notifications link */}
              <div className="ml-1 pl-1 border-l border-gray-700">
                <NotificationBell />
              </div>
            </div>
            
            {/* Auth Section - Updated */}
            {isAuthenticated ? (
              <div className="flex items-center gap-3 ml-4 pl-4 border-l border-gray-700">
                <Link href={`/profile/${user?.username}`} className="text-sm text-cyan-400 hover:text-cyan-300">
                  {user?.username}
                </Link>
                <button onClick={logout} className="text-sm text-gray-400 hover:text-white transition">
                  Logout
                </button>
              </div>
            ) : (
              <Link href="/login" className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition">
                Login
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
