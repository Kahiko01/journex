'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

interface Trade {
  id: number;
  symbol: string;
  profit_loss: number;
  emotion: string;
  strategy: string;
  exit_time: string;
}

interface Insight {
  trade_id: number;
  analysis: {
    discipline_score?: number;
    emotional_state?: string;
    psychological_insight?: string;
  };
}

export default function AIInsightsWidget({ userId = 1 }) {
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [insights, setInsights] = useState<Record<number, Insight>>({});
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchRecentTrades();
  }, []);

  const fetchRecentTrades = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/trades?user_id=${userId}&limit=5`);
      setRecentTrades(response.data);
      
      // Auto-analyze the most recent trade
      if (response.data.length > 0) {
        analyzeTrade(response.data[0].id);
      }
    } catch (error) {
      console.error('Error fetching trades:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeTrade = async (tradeId: number) => {
    setAnalyzing(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/v1/ai/analyze-trade/${tradeId}?user_id=${userId}`
      );
      setInsights(prev => ({
        ...prev,
        [tradeId]: {
          trade_id: tradeId,
          analysis: response.data.analysis
        }
      }));
    } catch (error) {
      console.error('Error analyzing trade:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const analyzeAll = async () => {
    setAnalyzing(true);
    for (const trade of recentTrades) {
      await analyzeTrade(trade.id);
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    setAnalyzing(false);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="bg-gray-800/90 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-700 rounded"></div>
            <div className="h-4 bg-gray-700 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative group">
      {/* Glow effect */}
      <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-500 to-pink-500 opacity-0 group-hover:opacity-20 blur-xl transition-all duration-500"></div>
      
      <div className="relative bg-gray-800/90 backdrop-blur-sm rounded-2xl p-6 border border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <span className="text-2xl">🧠</span>
            AI Trade Insights
          </h2>
          {recentTrades.length > 0 && (
            <button
              onClick={analyzeAll}
              disabled={analyzing}
              className="relative group/btn"
            >
              <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-purple-500 opacity-0 group-hover/btn:opacity-50 blur-lg transition-all duration-300"></div>
              <div className="relative bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-600 transition-all">
                {analyzing ? (
                  <span className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    Analyzing...
                  </span>
                ) : (
                  'Analyze All Trades'
                )}
              </div>
            </button>
          )}
        </div>

        {recentTrades.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-400 mb-4">No trades to analyze yet</p>
            <Link 
              href="/trades/new"
              className="inline-block bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-3 rounded-lg hover:from-blue-600 hover:to-purple-600 transition-all transform hover:scale-105"
            >
              Add Your First Trade
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {recentTrades.map((trade, index) => (
              <div 
                key={trade.id} 
                className="border border-gray-700 rounded-xl p-4 hover:border-blue-500/50 transition-all transform hover:scale-[1.02]"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <Link href={`/trades/${trade.id}`} className="text-white font-medium hover:text-blue-400 transition">
                      {trade.symbol} - {trade.strategy || 'No Strategy'}
                    </Link>
                    <div className="text-xs text-gray-500 mt-1">
                      {formatDate(trade.exit_time)}
                    </div>
                  </div>
                  <div className={`font-bold ${trade.profit_loss > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${trade.profit_loss?.toFixed(2)}
                  </div>
                </div>

                {/* AI Insights */}
                {insights[trade.id] ? (
                  <div className="mt-3 text-sm">
                    <div className="flex items-center gap-4 mb-2">
                      {insights[trade.id].analysis.discipline_score && (
                        <div className="bg-gray-700/50 px-3 py-1 rounded-full">
                          <span className="text-gray-400 text-xs">Discipline:</span>
                          <span className={`ml-1 font-bold ${getScoreColor(insights[trade.id].analysis.discipline_score)}`}>
                            {insights[trade.id].analysis.discipline_score}/100
                          </span>
                        </div>
                      )}
                      {insights[trade.id].analysis.emotional_state && (
                        <div className="bg-gray-700/50 px-3 py-1 rounded-full">
                          <span className="text-gray-400 text-xs">Emotion:</span>
                          <span className="ml-1 text-white capitalize">
                            {insights[trade.id].analysis.emotional_state}
                          </span>
                        </div>
                      )}
                    </div>
                    
                    {insights[trade.id].analysis.psychological_insight && (
                      <p className="text-xs text-gray-300 italic border-l-2 border-purple-500 pl-3 py-1">
                        "{insights[trade.id].analysis.psychological_insight.substring(0, 120)}..."
                      </p>
                    )}
                  </div>
                ) : (
                  <button
                    onClick={() => analyzeTrade(trade.id)}
                    disabled={analyzing}
                    className="mt-2 text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 transition"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Get AI Insights
                  </button>
                )}
              </div>
            ))}

            <Link 
              href="/trades"
              className="block text-center text-sm text-blue-400 hover:text-blue-300 mt-4 transition"
            >
              View All Trades →
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
