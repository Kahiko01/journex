'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import axios from 'axios';
import ProtectedRoute from '@/components/ProtectedRoute';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import {
  ArrowLeft, Heart, MessageCircle, Share2, Eye,
  Clock, Award, TrendingUp, Shield, Zap,
  BookOpen, Copy, Check, Send
} from 'lucide-react';

interface StrategyDetail {
  id: number;
  title: string;
  description: string;
  category: string;
  tags: string[];
  entry_rules?: string;
  exit_rules?: string;
  risk_management?: string;
  likes: number;
  comments_count: number;
  views: number;
  created_at: string;
  is_liked: boolean;
  creator: {
    username: string;
    avatar: string | null;
    display_name: string | null;
  };
}

interface Comment {
  id: number;
  content: string;
  created_at: string;
  user: {
    username: string;
    avatar: string | null;
    display_name: string | null;
  };
}

function StrategyDetailContent() {
  const params = useParams();
  const router = useRouter();
  const [strategy, setStrategy] = useState<StrategyDetail | null>(null);
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [commentText, setCommentText] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showShareMenu, setShowShareMenu] = useState(false);

  const strategyId = params.id as string;

  useEffect(() => {
    fetchStrategyDetail();
  }, [strategyId]);

  const fetchStrategyDetail = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:8000/api/v1/social/strategies/${strategyId}`);
      setStrategy(response.data.strategy);
      setComments(response.data.comments);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    if (!strategy) return;
    try {
      const response = await axios.post(`http://localhost:8000/api/v1/social/strategies/${strategyId}/like`);
      setStrategy({
        ...strategy,
        likes: response.data.likes_count,
        is_liked: response.data.liked
      });
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim() || submitting) return;
    setSubmitting(true);
    try {
      const response = await axios.post(
        `http://localhost:8000/api/v1/social/strategies/${strategyId}/comment`,
        { content: commentText }
      );
      setComments([response.data.comment, ...comments]);
      setCommentText('');
      if (strategy) {
        setStrategy({
          ...strategy,
          comments_count: response.data.comments_count
        });
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="w-16 h-16 border-t-2 border-cyan-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!strategy) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <BookOpen className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl text-gray-400">Strategy not found</h3>
          <button onClick={() => router.push('/dashboard')} className="mt-4 px-6 py-2 bg-cyan-500 rounded-lg">
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      <div className="max-w-5xl mx-auto px-6 py-12">
        <button onClick={() => router.back()} className="mb-8 text-gray-400 hover:text-cyan-400">
          ← Back
        </button>

        <div className="mb-8">
          <span className="px-3 py-1 bg-cyan-500/10 border border-cyan-500/30 rounded-full text-sm">
            {strategy.category}
          </span>
          <h1 className="text-4xl font-bold mt-4 mb-4">{strategy.title}</h1>
          <div className="flex items-center gap-6 text-gray-400">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500"></div>
              <span>{strategy.creator.display_name || strategy.creator.username}</span>
            </div>
            <span>{formatDistanceToNow(new Date(strategy.created_at))} ago</span>
            <span>👁️ {strategy.views} views</span>
          </div>
        </div>

        <div className="bg-gray-900/30 border border-gray-800 rounded-2xl p-6 mb-8">
          <p className="text-gray-300">{strategy.description}</p>
        </div>

        <div className="flex items-center gap-4 mb-12">
          <button onClick={handleLike} className={`flex items-center gap-2 px-6 py-3 rounded-xl ${
            strategy.is_liked ? 'bg-rose-500/20 text-rose-400' : 'bg-gray-900/50 text-gray-400'
          }`}>
            <Heart className={strategy.is_liked ? 'fill-rose-400' : ''} />
            <span>{strategy.likes}</span>
          </button>
          
          <button onClick={() => setShowShareMenu(!showShareMenu)} className="flex items-center gap-2 px-6 py-3 bg-gray-900/50 rounded-xl">
            <Share2 />
            Share
          </button>
        </div>

        <div>
          <h2 className="text-xl font-bold mb-6">Comments ({strategy.comments_count})</h2>
          
          <form onSubmit={handleComment} className="mb-8">
            <textarea
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Share your thoughts..."
              rows={3}
              className="w-full px-4 py-3 bg-gray-900/50 border border-gray-800 rounded-xl"
            />
            <button type="submit" disabled={!commentText.trim()} className="mt-2 px-6 py-2 bg-cyan-500 rounded-lg">
              Post Comment
            </button>
          </form>
          
          {comments.map((comment) => (
            <div key={comment.id} className="bg-gray-900/30 border border-gray-800 rounded-xl p-4 mb-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-8 h-8 rounded-full bg-purple-500"></div>
                <div>
                  <div className="font-medium">{comment.user.display_name || comment.user.username}</div>
                  <div className="text-xs text-gray-500">{formatDistanceToNow(new Date(comment.created_at))} ago</div>
                </div>
              </div>
              <p className="text-gray-300">{comment.content}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function StrategyDetailPage() {
  return (
    <ProtectedRoute>
      <StrategyDetailContent />
    </ProtectedRoute>
  );
}
