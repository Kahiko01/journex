'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell 
} from 'recharts';

interface AnonymousStats {
  overview: {
    total_sessions: number;
    total_events: number;
    total_errors: number;
    active_today: number;
    avg_session_duration: number;
    error_rate: number;
  };
  devices: Array<{ type: string; count: number }>;
  browsers: Array<{ name: string; count: number }>;
  top_pages: Array<{ page: string; views: number }>;
  top_features: Array<{ feature: string; uses: number }>;
  feature_feedback: Array<{
    feature: string;
    positive: number;
    negative: number;
    score: number;
  }>;
  error_types: Array<{ type: string; count: number }>;
  daily_activity: Array<{ date: string; sessions: number; events: number }>;
}

function AnonymousDashboardContent() {
  const [stats, setStats] = useState<AnonymousStats | null>(null);
  const [realtime, setRealtime] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchStats();
    fetchRealtime();
    
    // Refresh realtime every 30 seconds
    const interval = setInterval(fetchRealtime, 30000);
    return () => clearInterval(interval);
  }, [days]);

  const fetchStats = async () => {
    try {
      const response = await axios.get(
        `http://localhost:8000/api/v1/anonymous-dashboard/stats?days=${days}`
      );
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching anonymous stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRealtime = async () => {
    try {
      const response = await axios.get(
        'http://localhost:8000/api/v1/anonymous-dashboard/realtime'
      );
      setRealtime(response.data);
    } catch (error) {
      console.error('Error fetching realtime stats:', error);
    }
  };

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-cyan-400 font-mono">LOADING ANONYMOUS DATA...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-gray-100 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-cyan-400 mb-2">
              ANONYMOUS ANALYTICS
            </h1>
            <p className="text-gray-500 font-mono text-sm">USER BEHAVIOR • PRIVACY SAFE</p>
          </div>
          <Link
            href="/dashboard"
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm font-mono hover:bg-gray-700 transition"
          >
            ← BACK TO DASHBOARD
          </Link>
        </div>

        {/* Realtime Stats */}
        {realtime && (
          <div className="bg-gradient-to-r from-green-900/30 to-cyan-900/30 border border-green-500/30 rounded-xl p-6 mb-8">
            <h2 className="text-lg font-mono text-green-400 mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              REAL-TIME ACTIVITY
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-black/50 rounded-lg p-4">
                <div className="text-3xl font-bold text-white">{realtime.active_users_now}</div>
                <div className="text-sm text-gray-500">Active Users Now</div>
              </div>
              <div className="bg-black/50 rounded-lg p-4">
                <div className="text-3xl font-bold text-white">{realtime.events_last_hour}</div>
                <div className="text-sm text-gray-500">Events (Last Hour)</div>
              </div>
              <div className="bg-black/50 rounded-lg p-4">
                <div className="text-sm text-gray-400 mb-2">Top Pages Now</div>
                {realtime.current_pages.map((page: any, idx: number) => (
                  <div key={idx} className="flex justify-between text-xs font-mono">
                    <span className="text-cyan-400">{page.page}</span>
                    <span className="text-gray-500">{page.views}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Time Range Selector */}
        <div className="flex gap-2 mb-8">
          {[7, 14, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-4 py-2 rounded-lg font-mono text-sm transition ${
                days === d
                  ? 'bg-green-500/20 border border-green-400 text-green-400'
                  : 'bg-gray-800 border border-gray-700 text-gray-400 hover:border-gray-600'
              }`}
            >
              {d} DAYS
            </button>
          ))}
        </div>

        {/* Overview Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-gray-400 text-xs">Total Sessions</div>
              <div className="text-2xl font-bold text-white">{stats.overview.total_sessions}</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-gray-400 text-xs">Total Events</div>
              <div className="text-2xl font-bold text-white">{stats.overview.total_events}</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-gray-400 text-xs">Active Today</div>
              <div className="text-2xl font-bold text-green-400">{stats.overview.active_today}</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-gray-400 text-xs">Error Rate</div>
              <div className="text-2xl font-bold text-rose-400">{stats.overview.error_rate}%</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
              <div className="text-gray-400 text-xs">Avg Session</div>
              <div className="text-2xl font-bold text-white">{stats.overview.avg_session_duration}s</div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-gray-800">
          {['overview', 'pages', 'features', 'errors', 'devices'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-mono text-sm capitalize ${
                activeTab === tab
                  ? 'text-green-400 border-b-2 border-green-400'
                  : 'text-gray-500 hover:text-gray-400'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {stats && (
          <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800 rounded-xl p-6">
            {activeTab === 'overview' && (
              <div>
                <h3 className="text-lg font-mono text-white mb-4">Daily Activity</h3>
                <div className="h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={stats.daily_activity}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="date" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
                        labelStyle={{ color: '#9CA3AF' }}
                      />
                      <Line type="monotone" dataKey="sessions" stroke="#10B981" />
                      <Line type="monotone" dataKey="events" stroke="#3B82F6" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {activeTab === 'pages' && (
              <div>
                <h3 className="text-lg font-mono text-white mb-4">Top Pages</h3>
                <div className="space-y-3">
                  {stats.top_pages.map((page, idx) => (
                    <div key={idx} className="flex items-center gap-4">
                      <div className="w-8 text-gray-500 text-sm font-mono">#{idx + 1}</div>
                      <div className="flex-1">
                        <div className="flex justify-between mb-1">
                          <span className="text-cyan-400 font-mono text-sm">{page.page}</span>
                          <span className="text-white font-mono">{page.views} views</span>
                        </div>
                        <div className="w-full bg-gray-700 h-2 rounded-full overflow-hidden">
                          <div 
                            className="bg-gradient-to-r from-cyan-500 to-blue-500 h-full rounded-full"
                            style={{ width: `${(page.views / stats.top_pages[0].views) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'features' && (
              <div>
                <h3 className="text-lg font-mono text-white mb-4">Feature Usage</h3>
                <div className="grid gap-4">
                  {stats.top_features.map((feature, idx) => {
                    const feedback = stats.feature_feedback.find(f => f.feature === feature.feature);
                    return (
                      <div key={idx} className="bg-gray-800/30 rounded-lg p-4">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-white font-mono">{feature.feature}</span>
                          <span className="text-green-400 font-mono">{feature.uses} uses</span>
                        </div>
                        {feedback && (
                          <div className="flex gap-4 text-xs">
                            <span className="text-green-400">👍 {feedback.positive}</span>
                            <span className="text-rose-400">👎 {feedback.negative}</span>
                            <span className="text-cyan-400">Score: {feedback.score}%</span>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {activeTab === 'errors' && (
              <div>
                <h3 className="text-lg font-mono text-white mb-4">Error Types</h3>
                <div className="grid gap-3">
                  {stats.error_types.map((error, idx) => (
                    <div key={idx} className="flex justify-between items-center bg-rose-500/10 border border-rose-500/30 rounded-lg p-4">
                      <span className="text-rose-400 font-mono">{error.type}</span>
                      <span className="text-white font-mono">{error.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'devices' && (
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-mono text-white mb-4">Devices</h3>
                  <div className="space-y-3">
                    {stats.devices.map((device, idx) => (
                      <div key={idx} className="flex justify-between items-center">
                        <span className="text-gray-400 capitalize">{device.type}</span>
                        <span className="text-white font-mono">{device.count}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-mono text-white mb-4">Browsers</h3>
                  <div className="space-y-3">
                    {stats.browsers.map((browser, idx) => (
                      <div key={idx} className="flex justify-between items-center">
                        <span className="text-gray-400">{browser.name}</span>
                        <span className="text-white font-mono">{browser.count}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function AnonymousDashboardPage() {
  return (
    <ProtectedRoute>
      <AnonymousDashboardContent />
    </ProtectedRoute>
  );
}
