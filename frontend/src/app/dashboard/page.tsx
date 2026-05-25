'use client';

import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import TradingCalendar from '@/components/calendar/TradingCalendar';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target, 
  BarChart3, 
  Calendar, 
  BookOpen, 
  Plus, 
  History,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  Zap
} from 'lucide-react';

interface AnalyticsData {
  total_pl: number;
  win_rate: number;
  total_trades: number;
  profit_factor: number;
  expectancy: number;
  avg_r: number;
  monthly_return?: number;
  max_drawdown?: number;
}

interface Trade {
  id: string;
  symbol: string;
  profit_loss: number;
  entry_date: string;
  exit_date?: string;
  status: 'open' | 'closed';
  strategy?: string;
}

// Professional number formatter
const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    signDisplay: 'exceptZero',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

const formatPercent = (value: number, decimals: number = 1) => {
  return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
};

// Animated metric component
const MetricCard = ({ 
  label, 
  value, 
  subValue, 
  trend, 
  icon: Icon, 
  color = 'blue',
  delay = 0 
}: {
  label: string;
  value: string;
  subValue?: string;
  trend?: 'up' | 'down' | 'neutral';
  icon: React.ElementType;
  color?: 'blue' | 'green' | 'purple' | 'amber' | 'red';
  delay?: number;
}) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  const colorClasses = {
    blue: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30 text-blue-400',
    green: 'from-emerald-500/20 to-green-500/20 border-emerald-500/30 text-emerald-400',
    purple: 'from-violet-500/20 to-purple-500/20 border-violet-500/30 text-violet-400',
    amber: 'from-amber-500/20 to-yellow-500/20 border-amber-500/30 text-amber-400',
    red: 'from-rose-500/20 to-red-500/20 border-rose-500/30 text-rose-400'
  };

  return (
    <div className={`group relative overflow-hidden rounded-xl border bg-gradient-to-br ${colorClasses[color]} backdrop-blur-sm transition-all duration-500 hover:scale-[1.02] ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
      <div className="absolute inset-0 bg-[linear-gradient(45deg,transparent_25%,rgba(255,255,255,0.05)_50%,transparent_75%)] translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
      
      <div className="relative p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="p-2 rounded-lg bg-white/5">
            <Icon className="w-5 h-5" />
          </div>
          {trend && (
            <div className={`flex items-center gap-1 text-xs font-medium ${trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-rose-400' : 'text-gray-400'}`}>
              {trend === 'up' ? <ArrowUpRight className="w-3 h-3" /> : trend === 'down' ? <ArrowDownRight className="w-3 h-3" /> : null}
              {trend === 'up' ? 'Bullish' : trend === 'down' ? 'Bearish' : 'Neutral'}
            </div>
          )}
        </div>
        
        <div className="space-y-1">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wider">{label}</p>
          <p className="text-2xl font-bold text-white tracking-tight">{value}</p>
          {subValue && <p className="text-xs text-gray-500">{subValue}</p>}
        </div>
      </div>
    </div>
  );
};

// Inner dashboard component
function DashboardContent() {
  const router = useRouter();
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        await Promise.all([fetchAnalytics(), fetchRecentTrades()]);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/advanced-analytics/edge-quality/simple`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAnalytics(response.data);
    } catch (error) {
      console.error('Analytics fetch failed:', error);
    }
  };

  const fetchRecentTrades = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/trades/?limit=5`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRecentTrades(response.data || []);
    } catch (error) {
      console.error('Trades fetch failed:', error);
    }
  };

  const stats = useMemo(() => {
    if (!analytics) return null;
    
    const totalPL = analytics.total_pl || 0;
    const winRate = analytics.win_rate || 0;
    const totalTrades = analytics.total_trades || 0;
    
    return {
      pnl: {
        value: formatCurrency(totalPL),
        trend: totalPL >= 0 ? 'up' : 'down' as const,
        subValue: `${analytics.monthly_return ? formatPercent(analytics.monthly_return) : 'N/A'} MTD`
      },
      winRate: {
        value: `${winRate.toFixed(1)}%`,
        trend: winRate >= 50 ? 'up' : 'down' as const,
        subValue: `${Math.round(winRate * totalTrades / 100)}W / ${totalTrades - Math.round(winRate * totalTrades / 100)}L`
      },
      trades: {
        value: totalTrades.toString(),
        trend: 'neutral' as const,
        subValue: `Avg R: ${analytics.avg_r?.toFixed(2) || 'N/A'}`
      },
      expectancy: {
        value: formatCurrency(analytics.expectancy || 0),
        trend: (analytics.expectancy || 0) >= 0 ? 'up' : 'down' as const,
        subValue: `PF: ${analytics.profit_factor?.toFixed(2) || 'N/A'}`
      }
    };
  }, [analytics]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="relative w-16 h-16 mx-auto">
            <div className="absolute inset-0 border-2 border-blue-500/20 rounded-full animate-ping" />
            <div className="absolute inset-0 border-2 border-t-blue-500 border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin" />
          </div>
          <p className="text-gray-500 text-sm font-medium tracking-widest uppercase">Loading Portfolio</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-gray-100">
      {/* Subtle grid background */}
      <div className="fixed inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none" />
      
      {/* Top gradient glow */}
      <div className="fixed top-0 left-0 right-0 h-96 bg-gradient-to-b from-blue-900/10 to-transparent pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Bar */}
        <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-6 border-b border-white/5">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <h1 className="text-2xl font-bold text-white tracking-tight">Trading Dashboard</h1>
              <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium border border-emerald-500/20">
                Live
              </span>
            </div>
            <p className="text-sm text-gray-500">
              {currentTime.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
              {' • '}
              <span className="font-mono text-gray-400">{currentTime.toLocaleTimeString('en-US', { hour12: false })}</span>
              {' UTC'}
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/analytics"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm font-medium text-gray-300 hover:bg-white/10 hover:text-white transition-colors"
            >
              <BarChart3 className="w-4 h-4" />
              Advanced Analytics
            </Link>
            <button
              onClick={() => router.push('/trades/new')}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-500 transition-colors shadow-lg shadow-blue-600/20"
            >
              <Plus className="w-4 h-4" />
              New Trade
            </button>
          </div>
        </header>

        {/* Metrics Grid */}
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <MetricCard
              label="Total P&L"
              value={stats.pnl.value}
              subValue={stats.pnl.subValue}
              trend={stats.pnl.trend}
              icon={stats.pnl.trend === 'up' ? TrendingUp : TrendingDown}
              color={stats.pnl.trend === 'up' ? 'green' : 'red'}
              delay={0}
            />
            <MetricCard
              label="Win Rate"
              value={stats.winRate.value}
              subValue={stats.winRate.subValue}
              trend={stats.winRate.trend}
              icon={Target}
              color="blue"
              delay={100}
            />
            <MetricCard
              label="Total Trades"
              value={stats.trades.value}
              subValue={stats.trades.subValue}
              trend={stats.trades.trend}
              icon={Activity}
              color="purple"
              delay={200}
            />
            <MetricCard
              label="Expectancy"
              value={stats.expectancy.value}
              subValue={stats.expectancy.subValue}
              trend={stats.expectancy.trend}
              icon={Zap}
              color={stats.expectancy.trend === 'up' ? 'amber' : 'red'}
              delay={300}
            />
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
          {[
            { href: '/trades/new', icon: Plus, label: 'Log Trade', color: 'bg-blue-600 hover:bg-blue-500' },
            { href: '/trades', icon: History, label: 'Trade History', color: 'bg-white/5 hover:bg-white/10 border border-white/10' },
            { href: '/university', icon: BookOpen, label: 'University', color: 'bg-white/5 hover:bg-white/10 border border-white/10' },
            { href: '/calendar', icon: Calendar, label: 'Calendar', color: 'bg-white/5 hover:bg-white/10 border border-white/10' }
          ].map((action) => (
            <Link
              key={action.href}
              href={action.href}
              className={`group flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${action.color}`}
            >
              <action.icon className="w-4 h-4 text-white/80" />
              <span className="text-sm font-medium text-white">{action.label}</span>
            </Link>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Calendar Section */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-400" />
                Trading Calendar
              </h2>
              <Link href="/calendar" className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                View Full →
              </Link>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.02] backdrop-blur-sm overflow-hidden">
              <TradingCalendar />
            </div>
          </div>

          {/* Recent Trades Sidebar */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-400" />
                Recent Activity
              </h2>
              <Link href="/trades" className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                All Trades →
              </Link>
            </div>

            <div className="rounded-xl border border-white/10 bg-white/[0.02] backdrop-blur-sm divide-y divide-white/5">
              {recentTrades.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  <p className="text-sm">No recent trades</p>
                  <Link href="/trades/new" className="text-sm text-blue-400 hover:text-blue-300 mt-2 inline-block">
                    Log your first trade
                  </Link>
                </div>
              ) : (
                recentTrades.map((trade) => (
                  <Link
                    key={trade.id}
                    href={`/trades/${trade.id}`}
                    className="group flex items-center justify-between p-4 hover:bg-white/5 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${trade.profit_loss > 0 ? 'bg-emerald-500' : trade.profit_loss < 0 ? 'bg-rose-500' : 'bg-gray-500'}`} />
                      <div>
                        <p className="text-sm font-medium text-white group-hover:text-blue-400 transition-colors">
                          {trade.symbol}
                        </p>
                        <p className="text-xs text-gray-500">
                          {trade.strategy || 'Manual'} • {new Date(trade.entry_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-medium ${trade.profit_loss > 0 ? 'text-emerald-400' : trade.profit_loss < 0 ? 'text-rose-400' : 'text-gray-400'}`}>
                        {formatCurrency(trade.profit_loss)}
                      </p>
                      <p className="text-xs text-gray-500 uppercase">
                        {trade.status}
                      </p>
                    </div>
                  </Link>
                ))
              )}
            </div>

            {/* Market Status */}
            <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
              <h3 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">Market Status</h3>
              <div className="space-y-2">
                {[
                  { market: 'NYSE', status: 'Open', time: '9:30 AM - 4:00 PM EST', color: 'text-emerald-400' },
                  { market: 'NASDAQ', status: 'Open', time: '9:30 AM - 4:00 PM EST', color: 'text-emerald-400' },
                  { market: 'Forex', status: '24H', time: 'Sun 5PM - Fri 5PM EST', color: 'text-blue-400' },
                  { market: 'Crypto', status: '24/7', time: 'Always Open', color: 'text-purple-400' }
                ].map((m) => (
                  <div key={m.market} className="flex items-center justify-between text-sm">
                    <span className="text-gray-300 font-medium">{m.market}</span>
                    <div className="text-right">
                      <span className={`${m.color} font-medium`}>{m.status}</span>
                      <p className="text-xs text-gray-500">{m.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Export wrapped with ProtectedRoute
export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
