'use client';

import AdvancedCharts from '@/components/analytics/AdvancedCharts';
import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import ProtectedRoute from '@/components/ProtectedRoute';
import AnalyticsButton from '@/components/analytics/AnalyticsButton';
import AnalyticsEdgeQuality from '@/components/analytics/AnalyticsEdgeQuality';

interface AnalyticsData {
  edge_quality: any;
  monte_carlo: any;
  trade_clustering: any;
  stability_metrics: any;
  improvement_tracking: any;
}

function AnalyticsContent() {
  const [activeTab, setActiveTab] = useState('edge-quality');
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [hoveredCard, setHoveredCard] = useState<string | null>(null);

  useEffect(() => {
    fetchAllAnalytics();
  }, []);

  const fetchAllAnalytics = async () => {
    setLoading(true);
    try {
      const [
        edgeQuality,
        monteCarlo,
        tradeClustering,
        stabilityMetrics,
        improvementTracking
      ] = await Promise.all([
        axios.get('http://localhost:8000/api/v1/advanced-analytics/edge-quality').catch(() => null),
        axios.get('http://localhost:8000/api/v1/advanced-analytics/monte-carlo').catch(() => null),
        axios.get('http://localhost:8000/api/v1/advanced-analytics/trade-clustering').catch(() => null),
        axios.get('http://localhost:8000/api/v1/advanced-analytics/stability-metrics').catch(() => null),
        axios.get('http://localhost:8000/api/v1/advanced-analytics/improvement-tracking').catch(() => null),
      ]);

      setData({
        edge_quality: edgeQuality?.data,
        monte_carlo: monteCarlo?.data,
        trade_clustering: tradeClustering?.data,
        stability_metrics: stabilityMetrics?.data,
        improvement_tracking: improvementTracking?.data,
      });
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'edge-quality', name: 'EDGE QUALITY', icon: '📈', color: 'cyan' },
    { id: 'monte-carlo', name: 'MONTE CARLO', icon: '🎲', color: 'purple' },
    { id: 'clustering', name: 'TRADE CLUSTERING', icon: '🔮', color: 'pink' },
    { id: 'stability', name: 'STABILITY METRICS', icon: '📊', color: 'green' },
    { id: 'improvement', name: 'IMPROVEMENT', icon: '📈', color: 'amber' },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-24 h-24 mx-auto mb-6">
            <div className="absolute inset-0 border-2 border-cyan-500/30 rounded-full animate-ping"></div>
            <div className="absolute inset-2 border-2 border-purple-500/50 rounded-full animate-pulse"></div>
            <div className="absolute inset-4 border-2 border-pink-500 rounded-full animate-spin border-t-transparent"></div>
          </div>
          <p className="text-cyan-400 text-lg font-mono animate-pulse">LOADING NEURAL ANALYTICS...</p>
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
            <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 mb-2">
              NEURAL ANALYTICS
            </h1>
            <p className="text-gray-500 font-mono text-sm">ADVANCED TRADING INTELLIGENCE</p>
          </div>
          <Link
            href="/dashboard"
            className="relative group"
          >
            <div className="absolute -inset-0.5 bg-gradient-to-r from-gray-600 to-gray-800 rounded-lg opacity-0 group-hover:opacity-50 blur transition"></div>
            <div className="relative bg-black/50 border border-gray-700 px-6 py-3 rounded-lg flex items-center gap-2 hover:border-gray-600 transition">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span className="font-mono text-sm">BACK TO DASHBOARD</span>
            </div>
          </Link>
        </div>

        {/* Analytics Tabs */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`relative group p-4 rounded-xl border transition-all ${
                activeTab === tab.id
                  ? `border-${tab.color}-400 bg-${tab.color}-500/10`
                  : 'border-gray-800 hover:border-gray-600'
              }`}
              onMouseEnter={() => setHoveredCard(tab.id)}
              onMouseLeave={() => setHoveredCard(null)}
            >
              <div className={`absolute -inset-0.5 bg-gradient-to-r from-${tab.color}-500 to-${tab.color}-600 rounded-xl opacity-0 group-hover:opacity-20 blur transition`}></div>
              <div className="relative text-center">
                <div className={`text-3xl mb-2 ${activeTab === tab.id ? `text-${tab.color}-400` : 'text-gray-500'}`}>
                  {tab.icon}
                </div>
                <div className={`text-xs font-mono ${activeTab === tab.id ? `text-${tab.color}-400` : 'text-gray-500'}`}>
                  {tab.name}
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Analytics Content */}
        <div className="bg-black/50 backdrop-blur-xl border border-gray-800 rounded-2xl p-8">
          {activeTab === 'edge-quality' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-cyan-400 font-mono mb-6">EDGE QUALITY ANALYSIS</h2>
              {data?.edge_quality ? (
                <AnalyticsEdgeQuality data={data.edge_quality} />
              ) : (
                <p className="text-gray-500 font-mono">No edge quality data available</p>
              )}
            </div>
          )}

          {activeTab === 'monte-carlo' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-purple-400 font-mono mb-6">MONTE CARLO SIMULATION</h2>
              {data?.monte_carlo ? (
                <pre className="text-gray-300 font-mono text-sm overflow-auto">
                  {JSON.stringify(data.monte_carlo, null, 2)}
                </pre>
              ) : (
                <p className="text-gray-500 font-mono">No Monte Carlo data available</p>
              )}
            </div>
          )}

          {activeTab === 'clustering' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-pink-400 font-mono mb-6">TRADE CLUSTERING</h2>
              {data?.trade_clustering ? (
                <pre className="text-gray-300 font-mono text-sm overflow-auto">
                  {JSON.stringify(data.trade_clustering, null, 2)}
                </pre>
              ) : (
                <p className="text-gray-500 font-mono">No clustering data available</p>
              )}
            </div>
          )}

          {activeTab === 'stability' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-green-400 font-mono mb-6">STABILITY METRICS</h2>
              {data?.stability_metrics ? (
                <pre className="text-gray-300 font-mono text-sm overflow-auto">
                  {JSON.stringify(data.stability_metrics, null, 2)}
                </pre>
              ) : (
                <p className="text-gray-500 font-mono">No stability metrics available</p>
              )}
            </div>
          )}

          {activeTab === 'improvement' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-amber-400 font-mono mb-6">IMPROVEMENT TRACKING</h2>
              {data?.improvement_tracking ? (
                <pre className="text-gray-300 font-mono text-sm overflow-auto">
                  {JSON.stringify(data.improvement_tracking, null, 2)}
                </pre>
              ) : (
                <p className="text-gray-500 font-mono">No improvement data available</p>
              )}
            </div>
          )}
        </div>

        {/* Analytics Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-black/30 border border-gray-800 rounded-xl p-6">
            <div className="text-cyan-400 text-2xl mb-2">📊</div>
            <div className="text-white font-bold mb-1">92 Trades Analyzed</div>
            <div className="text-gray-500 text-sm font-mono">Win Rate: 58.7%</div>
          </div>
          <div className="bg-black/30 border border-gray-800 rounded-xl p-6">
            <div className="text-purple-400 text-2xl mb-2">🎲</div>
            <div className="text-white font-bold mb-1">1000 Simulations</div>
            <div className="text-gray-500 text-sm font-mono">Risk of Ruin: 0%</div>
          </div>
          <div className="bg-black/30 border border-gray-800 rounded-xl p-6">
            <div className="text-pink-400 text-2xl mb-2">🔮</div>
            <div className="text-white font-bold mb-1">6 Strategies</div>
            <div className="text-gray-500 text-sm font-mono">Best: Swing Trading</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ProtectedAnalyticsPage() {
  return (
    <ProtectedRoute>
      <AnalyticsContent />
    </ProtectedRoute>
  );
}
