'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';
import ProtectedRoute from '@/components/ProtectedRoute';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, MapPin, Calendar, TrendingUp, TrendingDown, 
  Activity, Award, Users, BookOpen, Star, 
  Twitter, Globe, Mail, Send, Copy, Check,
  Heart, MessageCircle, Share2, Eye,
  ChevronRight, BarChart3, Target, Zap
} from 'lucide-react';

interface TraderProfile {
  user_id: number;
  username: string;
  avatar_url?: string;
  is_public: boolean;
  bio?: string;
  trading_style?: string;
  favorite_markets?: string[];
  social_links?: {
    twitter?: string;
    telegram?: string;
    website?: string;
  };
  total_followers: number;
  total_following: number;
  total_strategies: number;
  stats?: {
    total_trades: number;
    win_rate: number;
    total_pl: number;
    avg_r: number;
  };
}

interface Strategy {
  id: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  likes_count: number;
  comments_count: number;
  views_count: number;
  created_at: string;
  is_liked_by_user: boolean;
}

function ProfilePage() {
  const params = useParams();
  const username = params.username as string;
  const [profile, setProfile] = useState<TraderProfile | null>(null);
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [loading, setLoading] = useState(true);
  const [following, setFollowing] = useState(false);
  const [followingLoading, setFollowingLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'strategies' | 'stats' | 'about'>('strategies');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchProfile();
    fetchStrategies();
    checkFollowStatus();
  }, [username]);

  const fetchProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:8000/api/v1/social/profile/${username}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProfile(response.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const fetchStrategies = async () => {
    try {
      const token = localStorage.getItem('token');
      // This would need a user strategies endpoint
      // For now, we'll fetch all strategies and filter by user_id
      const response = await axios.get('http://localhost:8000/api/v1/social/strategies', {
        headers: { Authorization: `Bearer ${token}` }
      });
      // Filter strategies by user_id (if we had that info)
      // This is a placeholder - you'll need a proper endpoint
      setStrategies(response.data.strategies || []);
    } catch (error) {
      console.error('Error fetching strategies:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkFollowStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const currentUser = await axios.get('http://localhost:8000/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (currentUser.data.id !== profile?.user_id) {
        // Check if following - would need a specific endpoint
        // For now, placeholder
        setFollowing(false);
      }
    } catch (error) {
      console.error('Error checking follow status:', error);
    }
  };

  const handleFollow = async () => {
    if (!profile) return;
    
    setFollowingLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (following) {
        await axios.delete(`http://localhost:8000/api/v1/social/follow/${profile.user_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setFollowing(false);
        setProfile({ ...profile, total_followers: profile.total_followers - 1 });
      } else {
        await axios.post(`http://localhost:8000/api/v1/social/follow/${profile.user_id}`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setFollowing(true);
        setProfile({ ...profile, total_followers: profile.total_followers + 1 });
      }
    } catch (error) {
      console.error('Error following/unfollowing:', error);
    } finally {
      setFollowingLoading(false);
    }
  };

  const copyProfileLink = () => {
    const url = `${window.location.origin}/profile/${username}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-2 border-cyan-500/30 rounded-full animate-ping absolute inset-0"></div>
          <div className="w-16 h-16 border-t-2 border-cyan-500 rounded-full animate-spin relative"></div>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <div className="w-24 h-24 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <User className="w-12 h-12 text-gray-600" />
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Trader Not Found</h1>
          <p className="text-gray-500 mb-6">The profile you're looking for doesn't exist or is private.</p>
          <Link href="/" className="text-cyan-400 hover:text-cyan-300">
            ← Back to Home
          </Link>
        </div>
      </div>
    );
  }

  const isOwnProfile = false; // Would need to check current user

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-[150px]"></div>
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-[150px]"></div>
      </div>

      <div className="relative max-w-4xl mx-auto px-6 py-12">
        {/* Profile Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-900/50 border border-gray-800 rounded-2xl p-8 mb-8 backdrop-blur-sm"
        >
          <div className="flex flex-col md:flex-row items-start gap-6">
            {/* Avatar */}
            <div className="relative">
              <div className="w-32 h-32 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 p-1">
                <div className="w-full h-full rounded-full bg-gray-900 overflow-hidden">
                  {profile.avatar_url ? (
                    <img 
                      src={`http://localhost:8000${profile.avatar_url}`} 
                      alt={profile.username}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-4xl font-bold text-cyan-400">
                      {profile.username[0].toUpperCase()}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Profile Info */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-3xl font-bold text-white">{profile.username}</h1>
                {profile.is_public && (
                  <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs border border-green-500/30">
                    Public
                  </span>
                )}
              </div>
              
              {profile.bio && (
                <p className="text-gray-400 mb-4">{profile.bio}</p>
              )}
              
              <div className="flex flex-wrap gap-4 mb-4">
                {profile.trading_style && (
                  <div className="flex items-center gap-1 text-sm text-gray-500">
                    <Target className="w-4 h-4" />
                    <span>{profile.trading_style}</span>
                  </div>
                )}
                {profile.favorite_markets && profile.favorite_markets.length > 0 && (
                  <div className="flex items-center gap-1 text-sm text-gray-500">
                    <BarChart3 className="w-4 h-4" />
                    <span>{profile.favorite_markets.join(', ')}</span>
                  </div>
                )}
                <div className="flex items-center gap-1 text-sm text-gray-500">
                  <Calendar className="w-4 h-4" />
                  <span>Joined {formatDate(profile.created_at)}</span>
                </div>
              </div>

              {/* Stats Row */}
              <div className="flex gap-6 mb-6">
                <div>
                  <div className="text-xl font-bold text-white">{formatNumber(profile.total_followers)}</div>
                  <div className="text-xs text-gray-500">Followers</div>
                </div>
                <div>
                  <div className="text-xl font-bold text-white">{formatNumber(profile.total_following)}</div>
                  <div className="text-xs text-gray-500">Following</div>
                </div>
                <div>
                  <div className="text-xl font-bold text-white">{formatNumber(profile.total_strategies)}</div>
                  <div className="text-xs text-gray-500">Strategies</div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                {!isOwnProfile && (
                  <button
                    onClick={handleFollow}
                    disabled={followingLoading}
                    className={`px-6 py-2 rounded-lg font-medium transition flex items-center gap-2 ${
                      following
                        ? 'bg-gray-700 hover:bg-gray-600 text-white border border-gray-600'
                        : 'bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white'
                    }`}
                  >
                    {following ? (
                      <>
                        <Users className="w-4 h-4" />
                        Following
                      </>
                    ) : (
                      <>
                        <UserPlus className="w-4 h-4" />
                        Follow
                      </>
                    )}
                  </button>
                )}
                
                <button
                  onClick={copyProfileLink}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition flex items-center gap-2"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4 text-green-400" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Share
                    </>
                  )}
                </button>

                {profile.social_links?.twitter && (
                  <a
                    href={profile.social_links.twitter}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition"
                  >
                    <Twitter className="w-5 h-5" />
                  </a>
                )}
              </div>
            </div>
          </div>
        </motion.div>

        {/* Trading Stats Card */}
        {profile.stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 mb-8"
          >
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-cyan-400" />
              Trading Performance
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-2xl font-bold text-white">{profile.stats.total_trades}</div>
                <div className="text-xs text-gray-500">Total Trades</div>
              </div>
              <div>
                <div className={`text-2xl font-bold ${profile.stats.win_rate >= 50 ? 'text-green-400' : 'text-red-400'}`}>
                  {profile.stats.win_rate.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500">Win Rate</div>
              </div>
              <div>
                <div className={`text-2xl font-bold ${profile.stats.total_pl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  ${profile.stats.total_pl.toFixed(2)}
                </div>
                <div className="text-xs text-gray-500">Total P/L</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-white">{profile.stats.avg_r.toFixed(2)}R</div>
                <div className="text-xs text-gray-500">Avg R-Multiple</div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Tabs */}
        <div className="flex gap-4 border-b border-gray-800 mb-6">
          <button
            onClick={() => setActiveTab('strategies')}
            className={`pb-3 px-2 font-medium transition relative ${
              activeTab === 'strategies'
                ? 'text-cyan-400'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Strategies ({profile.total_strategies})
            {activeTab === 'strategies' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"></div>
            )}
          </button>
          <button
            onClick={() => setActiveTab('stats')}
            className={`pb-3 px-2 font-medium transition relative ${
              activeTab === 'stats'
                ? 'text-cyan-400'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Detailed Stats
            {activeTab === 'stats' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"></div>
            )}
          </button>
          <button
            onClick={() => setActiveTab('about')}
            className={`pb-3 px-2 font-medium transition relative ${
              activeTab === 'about'
                ? 'text-cyan-400'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            About
            {activeTab === 'about' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"></div>
            )}
          </button>
        </div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'strategies' && (
            <motion.div
              key="strategies"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {strategies.length === 0 ? (
                <div className="bg-gray-900/30 border border-gray-800 rounded-2xl p-12 text-center">
                  <BookOpen className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                  <h3 className="text-lg font-bold text-gray-400 mb-2">No strategies yet</h3>
                  <p className="text-gray-600">This trader hasn't shared any strategies.</p>
                </div>
              ) : (
                strategies.map((strategy) => (
                  <Link
                    key={strategy.id}
                    href={`/social/strategies/${strategy.id}`}
                    className="block bg-gray-900/50 border border-gray-800 rounded-xl p-6 hover:border-cyan-500/30 transition group"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-bold text-white group-hover:text-cyan-400 transition">
                          {strategy.title}
                        </h3>
                        <div className="flex flex-wrap gap-2 mt-2">
                          <span className="text-xs px-2 py-1 bg-cyan-500/10 text-cyan-400 rounded-full">
                            {strategy.category}
                          </span>
                          {strategy.tags?.slice(0, 3).map((tag, idx) => (
                            <span key={idx} className="text-xs px-2 py-1 bg-gray-800 text-gray-400 rounded-full">
                              #{tag}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Heart className="w-3 h-3" /> {strategy.likes_count}
                        </span>
                        <span className="flex items-center gap-1">
                          <MessageCircle className="w-3 h-3" /> {strategy.comments_count}
                        </span>
                        <span className="flex items-center gap-1">
                          <Eye className="w-3 h-3" /> {strategy.views_count}
                        </span>
                      </div>
                    </div>
                    <p className="text-gray-400 text-sm line-clamp-2">{strategy.description}</p>
                    <div className="mt-4 flex items-center justify-between">
                      <span className="text-xs text-gray-600">
                        {formatDate(strategy.created_at)}
                      </span>
                      <ChevronRight className="w-4 h-4 text-gray-500 group-hover:text-cyan-400 transition" />
                    </div>
                  </Link>
                ))
              )}
            </motion.div>
          )}

          {activeTab === 'stats' && profile.stats && (
            <motion.div
              key="stats"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6"
            >
              <div className="space-y-6">
                <div>
                  <h3 className="text-sm font-mono text-cyan-400 mb-3">Performance Metrics</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-800/50 rounded-lg p-4">
                      <div className="text-xs text-gray-500 mb-1">Profit Factor</div>
                      <div className="text-xl font-bold text-white">
                        {(profile.stats.total_pl / 100).toFixed(2)}
                      </div>
                    </div>
                    <div className="bg-gray-800/50 rounded-lg p-4">
                      <div className="text-xs text-gray-500 mb-1">Risk/Reward</div>
                      <div className="text-xl font-bold text-white">
                        {profile.stats.avg_r.toFixed(2)}R
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-mono text-cyan-400 mb-3">Trade Distribution</h3>
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <div className="flex justify-between mb-2">
                      <span className="text-sm text-gray-400">Winning Trades</span>
                      <span className="text-sm text-green-400">
                        {Math.round(profile.stats.total_trades * profile.stats.win_rate / 100)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full"
                        style={{ width: `${profile.stats.win_rate}%` }}
                      />
                    </div>
                    <div className="flex justify-between mt-2">
                      <span className="text-xs text-gray-500">Losing Trades</span>
                      <span className="text-xs text-red-400">
                        {Math.round(profile.stats.total_trades * (100 - profile.stats.win_rate) / 100)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'about' && (
            <motion.div
              key="about"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6"
            >
              <div className="space-y-4">
                {profile.bio && (
                  <div>
                    <h3 className="text-sm font-mono text-cyan-400 mb-2">Bio</h3>
                    <p className="text-gray-300">{profile.bio}</p>
                  </div>
                )}
                
                {profile.trading_style && (
                  <div>
                    <h3 className="text-sm font-mono text-cyan-400 mb-2">Trading Style</h3>
                    <p className="text-gray-300">{profile.trading_style}</p>
                  </div>
                )}
                
                {profile.favorite_markets && profile.favorite_markets.length > 0 && (
                  <div>
                    <h3 className="text-sm font-mono text-cyan-400 mb-2">Favorite Markets</h3>
                    <div className="flex flex-wrap gap-2">
                      {profile.favorite_markets.map((market, idx) => (
                        <span key={idx} className="px-3 py-1 bg-gray-800 rounded-full text-sm text-gray-300">
                          {market}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {profile.social_links && Object.keys(profile.social_links).length > 0 && (
                  <div>
                    <h3 className="text-sm font-mono text-cyan-400 mb-2">Social Links</h3>
                    <div className="flex gap-3">
                      {profile.social_links.twitter && (
                        <a href={profile.social_links.twitter} target="_blank" rel="noopener noreferrer" className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition">
                          <Twitter className="w-5 h-5" />
                        </a>
                      )}
                      {profile.social_links.telegram && (
                        <a href={profile.social_links.telegram} target="_blank" rel="noopener noreferrer" className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition">
                          <Send className="w-5 h-5" />
                        </a>
                      )}
                      {profile.social_links.website && (
                        <a href={profile.social_links.website} target="_blank" rel="noopener noreferrer" className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition">
                          <Globe className="w-5 h-5" />
                        </a>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default function ProtectedProfilePage() {
  return (
    <ProtectedRoute>
      <ProfilePage />
    </ProtectedRoute>
  );
}
