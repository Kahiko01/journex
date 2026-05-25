'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
import { 
  Trophy, Medal, Award, TrendingUp, TrendingDown, 
  Minus, ChevronLeft, ChevronRight, Search, Filter,
  Star, Zap, Crown, Target, Clock, BarChart3
} from 'lucide-react';

interface LeaderboardEntry {
  rank: number;
  user_id: number;
  username: string;
  avatar_url?: string;
  progress_percentage: number;
  completed_courses: number;
  total_courses: number;
  last_active?: string;
  streak?: number;
  total_points?: number;
}

interface LeaderboardTableProps {
  cohortId?: string;
  entries?: LeaderboardEntry[];
  title?: string;
  showFilters?: boolean;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export default function LeaderboardTable({ 
  cohortId,
  entries: propEntries,
  title = "Leaderboard",
  showFilters = true,
  onRefresh,
  isLoading: propLoading
}: LeaderboardTableProps) {
  const [entries, setEntries] = useState<LeaderboardEntry[]>(propEntries || []);
  const [loading, setLoading] = useState(propLoading || false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [sortBy, setSortBy] = useState<'rank' | 'progress' | 'completed' | 'streak'>('rank');
  const [searchQuery, setSearchQuery] = useState('');
  const [hoveredRank, setHoveredRank] = useState<number | null>(null);

  useEffect(() => {
    if (propEntries) {
      setEntries(propEntries);
    } else if (cohortId) {
      fetchLeaderboard();
    }
  }, [cohortId, propEntries]);

  useEffect(() => {
    if (propLoading !== undefined) {
      setLoading(propLoading);
    }
  }, [propLoading]);

  const fetchLeaderboard = async () => {
    if (!cohortId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/university/cohorts/${cohortId}/leaderboard`);
      const data = await response.json();
      setEntries(data.rankings || []);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    switch(rank) {
      case 1:
        return <Crown className="w-5 h-5 text-yellow-400" />;
      case 2:
        return <Medal className="w-5 h-5 text-gray-400" />;
      case 3:
        return <Medal className="w-5 h-5 text-amber-600" />;
      default:
        return <span className="text-gray-600 font-mono text-sm">#{rank}</span>;
    }
  };

  const getRankColor = (rank: number) => {
    switch(rank) {
      case 1:
        return 'bg-gradient-to-r from-yellow-500/20 to-amber-500/20 border-yellow-500/30';
      case 2:
        return 'bg-gradient-to-r from-gray-500/20 to-slate-500/20 border-gray-500/30';
      case 3:
        return 'bg-gradient-to-r from-amber-700/20 to-orange-700/20 border-amber-700/30';
      default:
        return 'bg-gray-800/30 border-gray-800';
    }
  };

  const getTrendIcon = (rank: number, previousRank?: number) => {
    if (!previousRank) return <Minus className="w-4 h-4 text-gray-500" />;
    if (rank < previousRank) return <TrendingUp className="w-4 h-4 text-green-400" />;
    if (rank > previousRank) return <TrendingDown className="w-4 h-4 text-red-400" />;
    return <Minus className="w-4 h-4 text-gray-500" />;
  };

  const filteredEntries = entries
    .filter(entry => 
      entry.username.toLowerCase().includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      switch(sortBy) {
        case 'progress':
          return b.progress_percentage - a.progress_percentage;
        case 'completed':
          return b.completed_courses - a.completed_courses;
        case 'streak':
          return (b.streak || 0) - (a.streak || 0);
        default:
          return a.rank - b.rank;
      }
    });

  const totalPages = Math.ceil(filteredEntries.length / itemsPerPage);
  const paginatedEntries = filteredEntries.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  if (loading) {
    return (
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-8">
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gray-800 rounded-full"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-800 rounded w-1/4 mb-2"></div>
                <div className="h-3 bg-gray-800 rounded w-1/3"></div>
              </div>
              <div className="w-24 h-8 bg-gray-800 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/10">
              <Trophy className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">{title}</h2>
              <p className="text-xs text-gray-500 font-mono">TOP PERFORMERS</p>
            </div>
          </div>

          {showFilters && (
            <div className="flex flex-wrap gap-3">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="text"
                  placeholder="Search users..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:border-amber-500/50 focus:outline-none transition"
                />
              </div>

              {/* Sort Filter */}
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="pl-10 pr-8 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm appearance-none cursor-pointer focus:border-amber-500/50 focus:outline-none transition"
                >
                  <option value="rank">Sort by Rank</option>
                  <option value="progress">Sort by Progress</option>
                  <option value="completed">Sort by Completed</option>
                  <option value="streak">Sort by Streak</option>
                </select>
              </div>

              {/* Refresh Button */}
              {onRefresh && (
                <button
                  onClick={onRefresh}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white text-sm transition flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Refresh
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Leaderboard Entries */}
      {paginatedEntries.length === 0 ? (
        <div className="p-12 text-center">
          <Trophy className="w-16 h-16 text-gray-700 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-gray-400 mb-2">No entries found</h3>
          <p className="text-gray-600">Be the first to join the leaderboard!</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-800">
          {paginatedEntries.map((entry, index) => {
            const previousRank = index > 0 ? paginatedEntries[index - 1].rank : undefined;
            const isHovered = hoveredRank === entry.rank;

            return (
              <motion.div
                key={entry.user_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                onMouseEnter={() => setHoveredRank(entry.rank)}
                onMouseLeave={() => setHoveredRank(null)}
                className={`relative p-4 transition-all duration-300 ${
                  isHovered ? 'bg-gray-800/50' : ''
                }`}
              >
                {/* Glow effect for top 3 */}
                {entry.rank <= 3 && (
                  <div className={`absolute inset-0 opacity-0 ${isHovered ? 'opacity-100' : ''} transition-opacity duration-500`}>
                    <div className={`absolute -inset-0.5 bg-gradient-to-r ${
                      entry.rank === 1 ? 'from-yellow-500 to-amber-500' :
                      entry.rank === 2 ? 'from-gray-500 to-slate-500' :
                      'from-amber-700 to-orange-700'
                    } rounded-xl blur opacity-20`}></div>
                  </div>
                )}

                <div className="relative flex items-center gap-4">
                  {/* Rank Badge */}
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${getRankColor(entry.rank)} border`}>
                    {getRankIcon(entry.rank)}
                  </div>

                  {/* User Avatar */}
                  <div className="w-12 h-12 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 p-1 flex-shrink-0">
                    <div className="w-full h-full rounded-full bg-gray-900 overflow-hidden">
                      {entry.avatar_url ? (
                        <img 
                          src={entry.avatar_url} 
                          alt={entry.username}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-white font-bold">
                          {entry.username[0].toUpperCase()}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* User Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Link 
                        href={`/profile/${entry.user_id}`}
                        className="text-white font-medium hover:text-cyan-400 transition"
                      >
                        {entry.username}
                      </Link>
                      {entry.streak && entry.streak > 0 && (
                        <span className="flex items-center gap-1 text-xs px-2 py-0.5 bg-orange-500/20 text-orange-400 rounded-full border border-orange-500/30">
                          <Zap className="w-3 h-3" />
                          {entry.streak} day streak
                        </span>
                      )}
                      {entry.rank <= 3 && (
                        <span className="flex items-center gap-1 text-xs px-2 py-0.5 bg-amber-500/20 text-amber-400 rounded-full border border-amber-500/30">
                          <Star className="w-3 h-3" />
                          Top {entry.rank}
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <Target className="w-4 h-4 text-cyan-400" />
                        <span className="text-gray-400">Progress:</span>
                        <span className="text-white font-mono">{entry.progress_percentage}%</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <BarChart3 className="w-4 h-4 text-purple-400" />
                        <span className="text-gray-400">Courses:</span>
                        <span className="text-white font-mono">{entry.completed_courses}/{entry.total_courses}</span>
                      </div>
                      {entry.last_active && (
                        <div className="flex items-center gap-1">
                          <Clock className="w-4 h-4 text-gray-500" />
                          <span className="text-gray-500 text-xs">
                            {new Date(entry.last_active).toLocaleDateString()}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Progress Bar */}
                    <div className="mt-2 w-full max-w-md">
                      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-500 ${
                            entry.rank === 1 ? 'bg-gradient-to-r from-yellow-500 to-amber-500' :
                            entry.rank === 2 ? 'bg-gradient-to-r from-gray-500 to-slate-500' :
                            entry.rank === 3 ? 'bg-gradient-to-r from-amber-700 to-orange-700' :
                            'bg-gradient-to-r from-cyan-500 to-purple-500'
                          }`}
                          style={{ width: `${entry.progress_percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Points/Trend */}
                  <div className="flex items-center gap-3">
                    {entry.total_points && (
                      <div className="text-right">
                        <div className="text-sm text-gray-500 font-mono">Points</div>
                        <div className="text-lg font-bold text-white">{entry.total_points}</div>
                      </div>
                    )}
                    {previousRank !== undefined && (
                      <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center">
                        {getTrendIcon(entry.rank, previousRank)}
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="p-4 border-t border-gray-800 flex items-center justify-between">
          <div className="text-sm text-gray-500">
            Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, filteredEntries.length)} of {filteredEntries.length} entries
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="px-4 py-2 bg-gray-800 rounded-lg text-white font-mono">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {/* Footer Stats */}
      <div className="p-4 bg-gray-900/30 border-t border-gray-800">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-yellow-400">
              {entries.filter(e => e.progress_percentage >= 90).length}
            </div>
            <div className="text-xs text-gray-500 font-mono">NEAR COMPLETION</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-cyan-400">
              {Math.round(entries.reduce((acc, e) => acc + e.progress_percentage, 0) / entries.length)}%
            </div>
            <div className="text-xs text-gray-500 font-mono">AVG PROGRESS</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-400">
              {entries.reduce((acc, e) => acc + e.completed_courses, 0)}
            </div>
            <div className="text-xs text-gray-500 font-mono">TOTAL COMPLETED</div>
          </div>
        </div>
      </div>
    </div>
  );
}
