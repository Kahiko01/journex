'use client';

import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  Users, Calendar, Lock, Globe, TrendingUp, 
  ChevronRight, Plus, Search, X,
  BarChart3, UserPlus
} from 'lucide-react';

// Types
interface Cohort {
  id: string;
  name: string;
  description: string;
  start_date: string;
  end_date?: string;
  max_members: number;
  is_private: boolean;
  leaderboard_enabled: boolean;
  show_progress: boolean;
  invite_code?: string;
  created_at: string;
  member_count: number;
  course_count: number;
}

interface CohortMember {
  user_id: number;
  username: string;
  avatar_url?: string;
  progress_percentage: number;
  completed_courses: number;
  total_courses: number;
  last_active?: string;
}

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Toggle Switch Component
const ToggleSwitch = ({ 
  checked, 
  onChange, 
  activeColor = 'bg-cyan-500' 
}: { 
  checked: boolean; 
  onChange: () => void;
  activeColor?: string;
}) => (
  <button
    onClick={onChange}
    className={`w-12 h-6 rounded-full transition-all relative ${checked ? activeColor : 'bg-gray-600'}`}
    aria-label={checked ? 'Enabled' : 'Disabled'}
  >
    <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${checked ? 'right-0.5' : 'left-0.5'}`} />
  </button>
);

// Filter Button Component
const FilterButton = ({ 
  active, 
  onClick, 
  icon: Icon, 
  label, 
  colorClass 
}: { 
  active: boolean; 
  onClick: () => void; 
  icon: React.ElementType; 
  label: string; 
  colorClass: string; 
}) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 rounded-lg font-mono text-sm transition flex items-center gap-1 ${
      active ? colorClass : 'bg-gray-800 border border-gray-700 text-gray-400 hover:border-gray-600'
    }`}
  >
    <Icon className="w-4 h-4" />
    {label}
  </button>
);

function CohortsPage() {
  const [cohorts, setCohorts] = useState<Cohort[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showJoinModal, setShowJoinModal] = useState(false);
  const [inviteCode, setInviteCode] = useState('');
  const [selectedCohort, setSelectedCohort] = useState<Cohort | null>(null);
  const [members, setMembers] = useState<CohortMember[]>([]);
  const [activeTab, setActiveTab] = useState<'browse' | 'my'>('browse');
  const [filter, setFilter] = useState<'all' | 'public' | 'private'>('all');
  const [error, setError] = useState<string | null>(null);

  // Form state for new cohort
  const [newCohort, setNewCohort] = useState({
    name: '',
    description: '',
    start_date: new Date().toISOString().split('T')[0],
    max_members: 50,
    is_private: false,
    leaderboard_enabled: true,
    show_progress: true,
    course_ids: [] as string[]
  });

  // Memoized fetch function
  const fetchCohorts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = activeTab === 'my' ? '/university/cohorts/my' : '/university/cohorts/';
      const response = await api.get(endpoint);
      let data = response.data;
      
      // Apply filter
      if (filter !== 'all') {
        data = data.filter((c: Cohort) => 
          filter === 'public' ? !c.is_private : c.is_private
        );
      }
      
      setCohorts(data);
    } catch (error) {
      console.error('Error fetching cohorts:', error);
      setError('Failed to load cohorts. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [activeTab, filter]);

  useEffect(() => {
    fetchCohorts();
  }, [fetchCohorts]);

  const fetchCohortDetails = async (cohortId: string) => {
    try {
      const response = await api.get(`/university/cohorts/${cohortId}`);
      setSelectedCohort(response.data);
      setMembers(response.data.members || []);
    } catch (error) {
      console.error('Error fetching cohort details:', error);
      setError('Failed to load cohort details.');
    }
  };

  const createCohort = async () => {
    if (!newCohort.name.trim()) {
      setError('Cohort name is required');
      return;
    }

    try {
      await api.post('/university/cohorts/', newCohort);
      setShowCreateModal(false);
      fetchCohorts();
      // Reset form
      setNewCohort({
        name: '',
        description: '',
        start_date: new Date().toISOString().split('T')[0],
        max_members: 50,
        is_private: false,
        leaderboard_enabled: true,
        show_progress: true,
        course_ids: []
      });
      setError(null);
    } catch (error) {
      console.error('Error creating cohort:', error);
      setError('Failed to create cohort. Please try again.');
    }
  };

  const joinCohort = async () => {
    if (!selectedCohort?.id) return;

    try {
      await api.post(`/university/cohorts/${selectedCohort.id}/join`, {
        invite_code: inviteCode || undefined
      });
      setShowJoinModal(false);
      setInviteCode('');
      fetchCohorts();
      setError(null);
    } catch (error: any) {
      console.error('Error joining cohort:', error);
      setError(error.response?.data?.detail || 'Failed to join cohort. Check your invite code.');
    }
  };

  const leaveCohort = async (cohortId: string) => {
    if (!confirm('Are you sure you want to leave this cohort?')) return;

    try {
      await api.post(`/university/cohorts/${cohortId}/leave`);
      fetchCohorts();
      setSelectedCohort(null);
    } catch (error) {
      console.error('Error leaving cohort:', error);
      setError('Failed to leave cohort.');
    }
  };

  // Memoized filtered cohorts
  const filteredCohorts = cohorts.filter(cohort =>
    cohort.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    cohort.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
        <div className="relative">
          <div className="w-16 h-16 border-2 border-cyan-500/30 rounded-full animate-ping absolute inset-0" />
          <div className="w-16 h-16 border-t-2 border-cyan-500 rounded-full animate-spin relative" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-[150px]" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-[150px]" />
      </div>

      <div className="relative max-w-7xl mx-auto px-6 py-12">
        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400"
          >
            {error}
            <button onClick={() => setError(null)} className="ml-2 text-red-300 hover:text-white">
              <X className="w-4 h-4 inline" />
            </button>
          </motion.div>
        )}

        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
              <span className="text-cyan-400 text-xs font-mono uppercase tracking-widest">Learning Together</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-black mb-2">
              <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                Study Cohorts
              </span>
            </h1>
            <p className="text-gray-400 text-lg">Learn in groups, track progress, compete on leaderboards</p>
          </div>
          
          <div className="flex gap-3">
            <button
              onClick={() => setShowJoinModal(true)}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white font-medium transition flex items-center gap-2"
            >
              <UserPlus className="w-4 h-4" />
              Join with Code
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white font-medium transition flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Create Cohort
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-800">
          {(['browse', 'my'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-4 px-1 font-medium transition relative ${
                activeTab === tab ? 'text-cyan-400' : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {tab === 'browse' ? 'Browse Cohorts' : 'My Cohorts'}
              {activeTab === tab && (
                <motion.div layoutId="tab-indicator" className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400" />
              )}
            </button>
          ))}
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              placeholder="Search cohorts..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-gray-900/50 border border-gray-800 rounded-xl focus:border-cyan-500/50 focus:outline-none transition font-mono text-sm"
            />
          </div>
          
          <div className="flex gap-2">
            <FilterButton
              active={filter === 'all'}
              onClick={() => setFilter('all')}
              icon={() => null}
              label="All"
              colorClass="bg-cyan-500/20 border border-cyan-500/30 text-cyan-400"
            />
            <FilterButton
              active={filter === 'public'}
              onClick={() => setFilter('public')}
              icon={Globe}
              label="Public"
              colorClass="bg-green-500/20 border border-green-500/30 text-green-400"
            />
            <FilterButton
              active={filter === 'private'}
              onClick={() => setFilter('private')}
              icon={Lock}
              label="Private"
              colorClass="bg-purple-500/20 border border-purple-500/30 text-purple-400"
            />
          </div>
        </div>

        {/* Cohort Grid */}
        {filteredCohorts.length === 0 ? (
          <div className="bg-gray-900/30 border border-gray-800 rounded-2xl p-16 text-center">
            <Users className="w-16 h-16 text-gray-700 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-400 mb-2">No cohorts found</h3>
            <p className="text-gray-600">Create a new cohort or adjust your filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCohorts.map((cohort, index) => (
              <motion.div
                key={cohort.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="group relative"
              >
                <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-2xl opacity-0 group-hover:opacity-20 blur transition duration-500" />
                
                <div className="relative bg-gray-900/80 border border-gray-800 rounded-2xl overflow-hidden hover:border-gray-700 transition-all duration-300">
                  {/* Header */}
                  <div className="p-6 border-b border-gray-800">
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="text-xl font-bold text-white group-hover:text-cyan-400 transition">
                        {cohort.name}
                      </h3>
                      {cohort.is_private ? (
                        <Lock className="w-4 h-4 text-purple-400" />
                      ) : (
                        <Globe className="w-4 h-4 text-green-400" />
                      )}
                    </div>
                    
                    <p className="text-gray-400 text-sm line-clamp-2 mb-4">
                      {cohort.description}
                    </p>
                    
                    <div className="flex flex-wrap gap-3 text-sm">
                      <div className="flex items-center gap-1 text-gray-500">
                        <Calendar className="w-4 h-4" />
                        <span>{formatDate(cohort.start_date)}</span>
                      </div>
                      <div className="flex items-center gap-1 text-gray-500">
                        <Users className="w-4 h-4" />
                        <span>{cohort.member_count}/{cohort.max_members}</span>
                      </div>
                      <div className="flex items-center gap-1 text-gray-500">
                        <BarChart3 className="w-4 h-4" />
                        <span>{cohort.course_count} courses</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Footer */}
                  <div className="p-4 bg-gray-900/50 flex items-center justify-between">
                    {cohort.leaderboard_enabled && (
                      <div className="flex items-center gap-1 text-xs text-amber-400">
                        <TrendingUp className="w-3 h-3" />
                        Leaderboard
                      </div>
                    )}
                    
                    <button
                      onClick={() => {
                        setSelectedCohort(cohort);
                        fetchCohortDetails(cohort.id);
                      }}
                      className="text-cyan-400 hover:text-cyan-300 text-sm font-medium flex items-center gap-1 group/btn"
                    >
                      View Details
                      <ChevronRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Create Cohort Modal */}
        <AnimatePresence>
          {showCreateModal && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-gray-900 border border-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              >
                <div className="p-6 border-b border-gray-800 flex justify-between items-center">
                  <h2 className="text-2xl font-bold text-white">Create New Cohort</h2>
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="text-gray-500 hover:text-white transition"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="p-6 space-y-6">
                  <div>
                    <label className="block text-sm font-mono text-cyan-400 mb-2">Cohort Name *</label>
                    <input
                      type="text"
                      value={newCohort.name}
                      onChange={(e) => setNewCohort({...newCohort, name: e.target.value})}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 transition"
                      placeholder="e.g., Forex Mastery - March 2026"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-mono text-cyan-400 mb-2">Description</label>
                    <textarea
                      value={newCohort.description}
                      onChange={(e) => setNewCohort({...newCohort, description: e.target.value})}
                      rows={3}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 transition"
                      placeholder="Describe the cohort's goals and structure..."
                    />
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-mono text-cyan-400 mb-2">Start Date</label>
                      <input
                        type="date"
                        value={newCohort.start_date}
                        onChange={(e) => setNewCohort({...newCohort, start_date: e.target.value})}
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 transition"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-mono text-cyan-400 mb-2">Max Members</label>
                      <input
                        type="number"
                        value={newCohort.max_members}
                        onChange={(e) => setNewCohort({...newCohort, max_members: parseInt(e.target.value) || 50})}
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 transition"
                        min="1"
                        max="1000"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Private Cohort</span>
                        <p className="text-xs text-gray-500 mt-1">Require invite code to join</p>
                      </div>
                      <ToggleSwitch 
                        checked={newCohort.is_private} 
                        onChange={() => setNewCohort({...newCohort, is_private: !newCohort.is_private})}
                        activeColor="bg-purple-500"
                      />
                    </label>
                    
                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Leaderboard Enabled</span>
                        <p className="text-xs text-gray-500 mt-1">Track and compare member progress</p>
                      </div>
                      <ToggleSwitch 
                        checked={newCohort.leaderboard_enabled} 
                        onChange={() => setNewCohort({...newCohort, leaderboard_enabled: !newCohort.leaderboard_enabled})}
                      />
                    </label>
                  </div>
                </div>
                
                <div className="p-6 border-t border-gray-800 flex justify-end gap-3">
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white transition"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={createCohort}
                    disabled={!newCohort.name.trim()}
                    className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Create Cohort
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Join Cohort Modal */}
        <AnimatePresence>
          {showJoinModal && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-gray-900 border border-gray-800 rounded-2xl max-w-md w-full"
              >
                <div className="p-6 border-b border-gray-800 flex justify-between items-center">
                  <h2 className="text-2xl font-bold text-white">Join Cohort</h2>
                  <button
                    onClick={() => setShowJoinModal(false)}
                    className="text-gray-500 hover:text-white transition"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="p-6 space-y-6">
                  <div>
                    <label className="block text-sm font-mono text-purple-400 mb-2">Invite Code</label>
                    <input
                      type="text"
                      value={inviteCode}
                      onChange={(e) => setInviteCode(e.target.value.toUpperCase())}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white font-mono text-center text-xl tracking-widest focus:border-purple-500 transition"
                      placeholder="XXXXXXXX"
                      maxLength={8}
                    />
                    <p className="text-xs text-gray-500 mt-2 text-center">
                      Enter the invite code provided by the cohort creator
                    </p>
                  </div>
                </div>
                
                <div className="p-6 border-t border-gray-800 flex justify-end gap-3">
                  <button
                    onClick={() => setShowJoinModal(false)}
                    className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white transition"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={joinCohort}
                    disabled={inviteCode.length < 8}
                    className="px-6 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Join Cohort
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

        {/* Cohort Details Modal */}
        <AnimatePresence>
          {selectedCohort && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-gray-900 border border-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              >
                <div className="p-6 border-b border-gray-800 flex justify-between items-center">
                  <div>
                    <h2 className="text-2xl font-bold text-white">{selectedCohort.name}</h2>
                    <p className="text-gray-400 text-sm mt-1">{selectedCohort.description}</p>
                  </div>
                  <button
                    onClick={() => setSelectedCohort(null)}
                    className="text-gray-500 hover:text-white transition"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="p-6 space-y-6">
                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-gray-800/30 rounded-lg p-4">
                      <div className="text-2xl font-bold text-white">{selectedCohort.member_count}</div>
                      <div className="text-xs text-gray-500 font-mono">MEMBERS</div>
                    </div>
                    <div className="bg-gray-800/30 rounded-lg p-4">
                      <div className="text-2xl font-bold text-white">{selectedCohort.course_count}</div>
                      <div className="text-xs text-gray-500 font-mono">COURSES</div>
                    </div>
                    <div className="bg-gray-800/30 rounded-lg p-4">
                      <div className="text-2xl font-bold text-white">
                        {selectedCohort.leaderboard_enabled ? 'Yes' : 'No'}
                      </div>
                      <div className="text-xs text-gray-500 font-mono">LEADERBOARD</div>
                    </div>
                    <div className="bg-gray-800/30 rounded-lg p-4">
                      <div className="text-2xl font-bold text-white">{formatDate(selectedCohort.start_date)}</div>
                      <div className="text-xs text-gray-500 font-mono">START DATE</div>
                    </div>
                  </div>

                  {/* Invite Code (if private) */}
                  {selectedCohort.is_private && selectedCohort.invite_code && (
                    <div className="bg-purple-900/30 border border-purple-500/30 rounded-lg p-4">
                      <div className="text-sm font-mono text-purple-400 mb-2">INVITE CODE</div>
                      <div className="text-3xl font-mono text-white tracking-widest text-center">
                        {selectedCohort.invite_code}
                      </div>
                    </div>
                  )}

                  {/* Members List */}
                  <div>
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Users className="w-5 h-5 text-cyan-400" />
                      Members ({members.length})
                    </h3>
                    
                    <div className="space-y-3">
                      {members.map((member) => (
                        <div
                          key={member.user_id}
                          className="bg-gray-800/30 rounded-lg p-4 flex items-center justify-between"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-cyan-500 to-purple-500 p-1">
                              <div className="w-full h-full rounded-full bg-gray-900 flex items-center justify-center overflow-hidden">
                                {member.avatar_url ? (
                                  <img src={member.avatar_url} alt={member.username} className="w-full h-full object-cover" />
                                ) : (
                                  <span className="text-white text-sm font-bold">
                                    {member.username[0]?.toUpperCase() || '?'}
                                  </span>
                                )}
                              </div>
                            </div>
                            <div>
                              <div className="text-white font-medium">{member.username}</div>
                              <div className="text-xs text-gray-500">
                                {member.completed_courses}/{member.total_courses} courses completed
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-4">
                            <div className="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full transition-all"
                                style={{ width: `${Math.min(member.progress_percentage, 100)}%` }}
                              />
                            </div>
                            <span className="text-sm font-mono text-cyan-400">
                              {member.progress_percentage}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex justify-end gap-3 pt-4">
                    {activeTab === 'my' ? (
                      <button
                        onClick={() => leaveCohort(selectedCohort.id)}
                        className="px-6 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white transition"
                      >
                        Leave Cohort
                      </button>
                    ) : (
                      <button
                        onClick={() => {
                          setShowJoinModal(true);
                          setSelectedCohort(null);
                        }}
                        className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white transition"
                      >
                        Join Cohort
                      </button>
                    )}
                    <button
                      onClick={() => setSelectedCohort(null)}
                      className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white transition"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default function ProtectedCohortsPage() {
  return (
    <ProtectedRoute>
      <CohortsPage />
    </ProtectedRoute>
  );
}
