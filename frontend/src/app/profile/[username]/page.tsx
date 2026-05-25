'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';
import ProtectedRoute from '@/components/ProtectedRoute';
import { User, Calendar, Users, BookOpen, Heart, MessageCircle, Eye, ChevronRight, Target, BarChart3 } from 'lucide-react';

interface TraderProfile {
  user_id: number;
  username: string;
  avatar_url?: string;
  is_public: boolean;
  bio?: string;
  trading_style?: string;
  favorite_markets?: string[];
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
}

function ProfilePage() {
  const params = useParams();
  const username = params.username as string;
  const [profile, setProfile] = useState<TraderProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [following, setFollowing] = useState(false);

  useEffect(() => {
    fetchProfile();
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
    } finally {
      setLoading(false);
    }
  };

  const handleFollow = async () => {
    if (!profile) return;
    
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
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
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

  return (
    <div className="min-h-screen bg-[#0a0a0f] py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Profile Header */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-8 mb-8">
          <div className="flex flex-col md:flex-row items-start gap-6">
            {/* Avatar */}
            <div className="w-24 h-24 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 p-1">
              <div className="w-full h-full rounded-full bg-gray-900 overflow-hidden">
                {profile.avatar_url ? (
                  <img 
                    src={`http://localhost:8000${profile.avatar_url}`} 
                    alt={profile.username}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-2xl font-bold text-cyan-400">
                    {profile.username[0].toUpperCase()}
                  </div>
                )}
              </div>
            </div>

            {/* Profile Info */}
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-white mb-2">{profile.username}</h1>
              
              {profile.bio && (
                <p className="text-gray-400 mb-4">{profile.bio}</p>
              )}
              
              <div className="flex gap-6 mb-4">
                <div>
                  <div className="text-xl font-bold text-white">{profile.total_followers}</div>
                  <div className="text-xs text-gray-500">Followers</div>
                </div>
                <div>
                  <div className="text-xl font-bold text-white">{profile.total_following}</div>
                  <div className="text-xs text-gray-500">Following</div>
                </div>
                <div>
                  <div className="text-xl font-bold text-white">{profile.total_strategies}</div>
                  <div className="text-xs text-gray-500">Strategies</div>
                </div>
              </div>

              {/* Follow Button */}
              <button
                onClick={handleFollow}
                className={`px-6 py-2 rounded-lg font-medium transition ${
                  following
                    ? 'bg-gray-700 hover:bg-gray-600 text-white'
                    : 'bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white'
                }`}
              >
                {following ? 'Following' : 'Follow'}
              </button>
            </div>
          </div>
        </div>

        {/* Trading Stats */}
        {profile.stats && (
          <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 mb-8">
            <h2 className="text-lg font-bold text-white mb-4">Trading Performance</h2>
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
          </div>
        )}

        {/* Strategies Section */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6">
          <h2 className="text-lg font-bold text-white mb-4">Shared Strategies</h2>
          {profile.total_strategies === 0 ? (
            <p className="text-gray-500 text-center py-8">No strategies shared yet</p>
          ) : (
            <p className="text-gray-500 text-center py-8">Strategies coming soon...</p>
          )}
        </div>
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
