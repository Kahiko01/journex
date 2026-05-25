'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import ProtectedRoute from '@/components/ProtectedRoute';

interface Trade {
  id: number;
  symbol: string;
  direction: string;
  entry_price: number;
  exit_price: number | null;
  stop_loss: number | null;
  take_profit: number | null;
  lot_size: number;
  profit_loss: number | null;
  r_multiple: number | null;
  strategy: string | null;
  emotion: string | null;
  rating: number | null;
  entry_time: string;
  exit_time: string | null;
}

function TradesContent() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, winning, losing
  const [sortBy, setSortBy] = useState('date'); // date, profit, symbol

  useEffect(() => {
    fetchTrades();
  }, []);

  const fetchTrades = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/trades/');
      setTrades(response.data);
    } catch (error) {
      console.error('Error fetching trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number | null) => {
    if (value === null) return '—';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTime = (dateString: string | null) => {
    if (!dateString) return '—';
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFilteredTrades = () => {
    let filtered = [...trades];
    
    if (filter === 'winning') {
      filtered = filtered.filter(t => t.profit_loss && t.profit_loss > 0);
    } else if (filter === 'losing') {
      filtered = filtered.filter(t => t.profit_loss && t.profit_loss < 0);
    }
    
    if (sortBy === 'date') {
      filtered.sort((a, b) => new Date(b.exit_time || '').getTime() - new Date(a.exit_time || '').getTime());
    } else if (sortBy === 'profit') {
      filtered.sort((a, b) => (b.profit_loss || 0) - (a.profit_loss || 0));
    } else if (sortBy === 'symbol') {
      filtered.sort((a, b) => a.symbol.localeCompare(b.symbol));
    }
    
    return filtered;
  };

  const stats = {
    total: trades.length,
    winning: trades.filter(t => t.profit_loss && t.profit_loss > 0).length,
    losing: trades.filter(t => t.profit_loss && t.profit_loss < 0).length,
    totalPl: trades.reduce((sum, t) => sum + (t.profit_loss || 0), 0)
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <div className="relative w-24 h-24 mx-auto mb-6">
            <div className="absolute inset-0 border-2 border-cyan-500/30 rounded-full animate-ping"></div>
            <div className="absolute inset-2 border-2 border-cyan-500/50 rounded-full animate-pulse"></div>
            <div className="absolute inset-4 border-2 border-cyan-500 rounded-full animate-spin border-t-transparent"></div>
          </div>
          <p className="text-cyan-400 text-lg font-mono">LOADING TRADES...</p>
        </div>
      </div>
    );
  }

  const filteredTrades = getFilteredTrades();

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-gray-100 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header with New Trade Button */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-600 mb-2">
              TRADE JOURNAL
            </h1>
            <p className="text-gray-500 font-mono text-sm">EXECUTION HISTORY</p>
          </div>
          
          <Link 
            href="/trades/new" 
            data-track="new-trade-button"
            className="relative group"
          >
            <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-lg opacity-0 group-hover:opacity-100 blur transition duration-300"></div>
            <div className="relative bg-black/80 border border-cyan-500/30 px-6 py-3 rounded-lg flex items-center gap-2 hover:border-cyan-400 transition">
              <span className="text-2xl">➕</span>
              <span className="font-mono text-sm">NEW EXECUTION</span>
            </div>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-black/50 border border-cyan-500/30 rounded-lg p-4">
            <p className="text-gray-500 text-xs font-mono mb-1">TOTAL TRADES</p>
            <p className="text-2xl font-bold text-white">{stats.total}</p>
          </div>
          <div className="bg-black/50 border border-green-500/30 rounded-lg p-4">
            <p className="text-gray-500 text-xs font-mono mb-1">WINNING</p>
            <p className="text-2xl font-bold text-green-400">{stats.winning}</p>
          </div>
          <div className="bg-black/50 border border-rose-500/30 rounded-lg p-4">
            <p className="text-gray-500 text-xs font-mono mb-1">LOSING</p>
            <p className="text-2xl font-bold text-rose-400">{stats.losing}</p>
          </div>
          <div className="bg-black/50 border border-purple-500/30 rounded-lg p-4">
            <p className="text-gray-500 text-xs font-mono mb-1">TOTAL P/L</p>
            <p className={`text-2xl font-bold ${stats.totalPl >= 0 ? 'text-green-400' : 'text-rose-400'}`}>
              {formatCurrency(stats.totalPl)}
            </p>
          </div>
        </div>

        {/* Filters and Sort */}
        <div className="flex flex-wrap gap-4 mb-6">
          <div className="flex gap-2">
            <button
              data-track="filter-all"
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-mono text-sm transition ${
                filter === 'all' 
                  ? 'bg-cyan-500/20 border border-cyan-400 text-cyan-400' 
                  : 'bg-black/50 border border-gray-800 text-gray-500 hover:border-gray-600'
              }`}
            >
              ALL
            </button>
            <button
              data-track="filter-winning"
              onClick={() => setFilter('winning')}
              className={`px-4 py-2 rounded-lg font-mono text-sm transition ${
                filter === 'winning' 
                  ? 'bg-green-500/20 border border-green-400 text-green-400' 
                  : 'bg-black/50 border border-gray-800 text-gray-500 hover:border-gray-600'
              }`}
            >
              WINNING
            </button>
            <button
              data-track="filter-losing"
              onClick={() => setFilter('losing')}
              className={`px-4 py-2 rounded-lg font-mono text-sm transition ${
                filter === 'losing' 
                  ? 'bg-rose-500/20 border border-rose-400 text-rose-400' 
                  : 'bg-black/50 border border-gray-800 text-gray-500 hover:border-gray-600'
              }`}
            >
              LOSING
            </button>
          </div>

          <div className="flex gap-2 ml-auto">
            <button
              data-track="sort-date"
              onClick={() => setSortBy('date')}
              className={`px-4 py-2 rounded-lg font-mono text-sm transition ${
                sortBy === 'date' 
                  ? 'bg-purple-500/20 border border-purple-400 text-purple-400' 
                  : 'bg-black/50 border border-gray-800 text-gray-500 hover:border-gray-600'
              }`}
            >
              SORT BY DATE
            </button>
            <button
              data-track="sort-profit"
              onClick={() => setSortBy('profit')}
              className={`px-4 py-2 rounded-lg font-mono text-sm transition ${
                sortBy === 'profit' 
                  ? 'bg-purple-500/20 border border-purple-400 text-purple-400' 
                  : 'bg-black/50 border border-gray-800 text-gray-500 hover:border-gray-600'
              }`}
            >
              SORT BY PROFIT
            </button>
            <button
              data-track="sort-symbol"
              onClick={() => setSortBy('symbol')}
              className={`px-4 py-2 rounded-lg font-mono text-sm transition ${
                sortBy === 'symbol' 
                  ? 'bg-purple-500/20 border border-purple-400 text-purple-400' 
                  : 'bg-black/50 border border-gray-800 text-gray-500 hover:border-gray-600'
              }`}
            >
              SORT BY SYMBOL
            </button>
          </div>
        </div>

        {/* Trades List */}
        {filteredTrades.length === 0 ? (
          <div className="bg-black/50 border border-cyan-500/30 rounded-xl p-12 text-center">
            <div className="text-6xl mb-4 opacity-30">📝</div>
            <p className="text-gray-500 font-mono text-lg mb-4">NO TRADES FOUND</p>
            <Link 
              href="/trades/new" 
              data-track="empty-state-new-trade"
              className="inline-block bg-gradient-to-r from-cyan-500 to-purple-600 text-white px-6 py-3 rounded-lg font-mono text-sm hover:from-cyan-600 hover:to-purple-700 transition"
            >
              EXECUTE FIRST TRADE
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredTrades.map((trade) => (
              <Link
                key={trade.id}
                href={`/trades/${trade.id}`}
                data-track="trade-row"
                className="block group relative"
              >
                <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-xl opacity-0 group-hover:opacity-20 blur transition duration-300"></div>
                <div className="relative bg-black/80 border border-gray-800 rounded-xl p-6 hover:border-cyan-500/50 transition">
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    {/* Left side - Trade info */}
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-xl font-bold ${
                        trade.profit_loss && trade.profit_loss > 0 
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                          : trade.profit_loss && trade.profit_loss < 0
                          ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                      }`}>
                        {trade.symbol[0]}
                      </div>
                      
                      <div>
                        <div className="flex items-center gap-3 mb-1">
                          <span className="text-white font-bold text-lg">{trade.symbol}</span>
                          <span className={`text-xs px-2 py-1 rounded-full font-mono ${
                            trade.direction === 'BUY' 
                              ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                              : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                          }`}>
                            {trade.direction}
                          </span>
                          {trade.strategy && (
                            <span className="text-xs text-gray-500 font-mono">
                              {trade.strategy}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-4 text-sm">
                          <span className="text-gray-400">
                            Entry: <span className="text-white font-mono">${trade.entry_price}</span>
                          </span>
                          {trade.exit_price && (
                            <span className="text-gray-400">
                              Exit: <span className="text-white font-mono">${trade.exit_price}</span>
                            </span>
                          )}
                          <span className="text-gray-400">
                            Lots: <span className="text-white font-mono">{trade.lot_size}</span>
                          </span>
                        </div>

                        <div className="flex items-center gap-4 mt-2 text-xs">
                          <span className="text-gray-600 font-mono">
                            {formatDate(trade.exit_time)} {formatTime(trade.exit_time)}
                          </span>
                          {trade.emotion && (
                            <span className="text-gray-600 font-mono">
                              Emotion: {trade.emotion}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Right side - P/L */}
                    <div className="text-right">
                      <div className={`text-2xl font-bold font-mono ${
                        trade.profit_loss && trade.profit_loss > 0 
                          ? 'text-green-400' 
                          : trade.profit_loss && trade.profit_loss < 0
                          ? 'text-rose-400'
                          : 'text-gray-400'
                      }`}>
                        {trade.profit_loss && trade.profit_loss > 0 ? '+' : ''}
                        {formatCurrency(trade.profit_loss)}
                      </div>
                      {trade.r_multiple && (
                        <div className="text-sm text-gray-500 font-mono mt-1">
                          {trade.r_multiple.toFixed(2)}R
                        </div>
                      )}
                      {trade.rating && (
                        <div className="text-xs text-gray-600 font-mono mt-1">
                          Rating: {'⭐'.repeat(trade.rating)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ProtectedTradesPage() {
  return (
    <ProtectedRoute>
      <TradesContent />
    </ProtectedRoute>
  );
}
