'use client';

import { useState } from 'react';
import Link from 'next/link';
import ProtectedRoute from '@/components/ProtectedRoute';
import NotificationCenter from '@/components/notifications/NotificationCenter';

function NotificationsPage() {
  const [filter, setFilter] = useState<'all' | 'unread'>('unread');

  return (
    <div className="min-h-screen bg-[#0a0a0f] py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400 mb-2">
              NOTIFICATIONS
            </h1>
            <p className="text-gray-500 font-mono text-sm">YOUR ACTIVITY FEED</p>
          </div>
          <Link
            href="/dashboard"
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm font-mono hover:bg-gray-700 transition"
          >
            ← BACK
          </Link>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setFilter('unread')}
            className={`px-4 py-2 rounded-lg font-mono text-sm transition ${
              filter === 'unread'
                ? 'bg-cyan-500/20 border border-cyan-400 text-cyan-400'
                : 'bg-gray-800 border border-gray-700 text-gray-400 hover:border-gray-600'
            }`}
          >
            UNREAD
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-mono text-sm transition ${
              filter === 'all'
                ? 'bg-cyan-500/20 border border-cyan-400 text-cyan-400'
                : 'bg-gray-800 border border-gray-700 text-gray-400 hover:border-gray-600'
            }`}
          >
            ALL
          </button>
        </div>

        {/* Notification Center Component */}
        <NotificationCenter filter={filter} />
      </div>
    </div>
  );
}

export default function ProtectedNotificationsPage() {
  return (
    <ProtectedRoute>
      <NotificationsPage />
    </ProtectedRoute>
  );
}
