'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface TradeInsightsProps {
  tradeId: number;
  userId?: number;
}

export default function TradeInsights({ tradeId, userId = 1 }: TradeInsightsProps) {
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState<any>(null);
  const [expanded, setExpanded] = useState(false);

  const fetchInsights = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/v1/ai/analyze-trade/${tradeId}?user_id=${userId}`
      );
      setInsights(response.data.analysis);
    } catch (error) {
      console.error('Error fetching insights:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, [tradeId]);

  if (loading) {
    return (
      <div className="text-xs text-gray-400 flex items-center gap-1">
        <div className="w-1 h-1 bg-blue-400 rounded-full animate-pulse"></div>
        <div className="w-1 h-1 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-1 h-1 bg-blue-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
        <span className="ml-1">AI analyzing...</span>
      </div>
    );
  }

  if (!insights) return null;

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="mt-2 text-sm border-t border-gray-700 pt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-blue-400 hover:text-blue-300 transition"
      >
        <svg className={`w-4 h-4 transition-transform ${expanded ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
        AI Trading Insights
      </button>

      {expanded && (
        <div className="mt-3 space-y-3 animate-fadeIn">
          {/* Discipline Score */}
          {insights.discipline_score && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Discipline Score:</span>
              <span className={`font-bold ${getScoreColor(insights.discipline_score)}`}>
                {insights.discipline_score}/100
              </span>
            </div>
          )}

          {/* Emotional State */}
          {insights.emotional_state && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Emotional State:</span>
              <span className="text-white capitalize">{insights.emotional_state}</span>
            </div>
          )}

          {/* Rule Violations */}
          {insights.rule_violations && insights.rule_violations.length > 0 && (
            <div>
              <span className="text-gray-400 block mb-1">⚠️ Rule Violations:</span>
              <ul className="list-disc list-inside text-red-400 text-xs">
                {insights.rule_violations.map((violation: string, i: number) => (
                  <li key={i}>{violation}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Strengths */}
          {insights.strengths && insights.strengths.length > 0 && (
            <div>
              <span className="text-gray-400 block mb-1">✅ Strengths:</span>
              <ul className="list-disc list-inside text-green-400 text-xs">
                {insights.strengths.map((strength: string, i: number) => (
                  <li key={i}>{strength}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Improvements */}
          {insights.improvements && insights.improvements.length > 0 && (
            <div>
              <span className="text-gray-400 block mb-1">📈 To Improve:</span>
              <ul className="list-disc list-inside text-yellow-400 text-xs">
                {insights.improvements.map((improvement: string, i: number) => (
                  <li key={i}>{improvement}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Psychological Insight */}
          {insights.psychological_insight && (
            <div className="mt-2 p-2 bg-gray-700/50 rounded-lg">
              <p className="text-xs text-gray-300 italic">
                "{insights.psychological_insight}"
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
