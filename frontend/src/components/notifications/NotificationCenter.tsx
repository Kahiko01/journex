'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import axios from 'axios';
import { formatDistanceToNow } from 'date-fns';
import { 
  Bell, CheckCheck, X, Trash2, Filter, 
  Volume2, VolumeX, Moon, Sun, Settings,
  TrendingUp, TrendingDown, Award, AlertTriangle,
  Zap, Clock, ChevronRight, Star, Crown,
  Info, AlertCircle, CheckCircle, XCircle
} from 'lucide-react';

interface Notification {
  id: number;
  type: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  title: string;
  message: string;
  data?: any;
  is_read: boolean;
  is_archived: boolean;
  created_at: string;
  expires_at?: string;
}

interface NotificationCounts {
  total: number;
  unread: number;
  by_type: Record<string, number>;
}

interface NotificationCenterProps {
  userId?: number;
  onNotificationClick?: (notification: Notification) => void;
  onMarkAsRead?: (id: number) => void;
  onDelete?: (id: number) => void;
  maxHeight?: string;
}

export default function NotificationCenter({ 
  userId = 1,
  onNotificationClick,
  onMarkAsRead,
  onDelete,
  maxHeight = "600px"
}: NotificationCenterProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [counts, setCounts] = useState<NotificationCounts>({ total: 0, unread: 0, by_type: {} });
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread' | 'archived'>('unread');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [dndEnabled, setDndEnabled] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const notificationSound = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    fetchNotifications();
    fetchCounts();
    
    // Set up polling every 30 seconds
    const interval = setInterval(() => {
      fetchCounts();
      if (filter === 'unread') {
        fetchNotifications();
      }
    }, 30000);
    
    // Initialize audio
    if (typeof window !== 'undefined') {
      notificationSound.current = new Audio('/sounds/notification.mp3');
      notificationSound.current.volume = 0.5;
    }
    
    return () => clearInterval(interval);
  }, [filter, priorityFilter, typeFilter]);

  const fetchNotifications = async () => {
    try {
      let url = `http://localhost:8000/api/v1/notifications/?include_read=${filter === 'all'}&limit=50`;
      if (filter === 'archived') {
        url += '&archived=true';
      }
      const response = await axios.get(url);
      let data = response.data;
      
      // Apply filters
      if (priorityFilter !== 'all') {
        data = data.filter((n: Notification) => n.priority === priorityFilter);
      }
      if (typeFilter !== 'all') {
        data = data.filter((n: Notification) => n.type === typeFilter);
      }
      
      setNotifications(data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCounts = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/notifications/count');
      const oldCount = counts.unread;
      setCounts(response.data);
      
      // Play sound if new notification arrived and sound is enabled
      if (response.data.unread > oldCount && soundEnabled && !dndEnabled) {
        playNotificationSound();
      }
    } catch (error) {
      console.error('Error fetching notification counts:', error);
    }
  };

  const playNotificationSound = () => {
    if (notificationSound.current) {
      notificationSound.current.play().catch(e => console.log('Sound play failed:', e));
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await axios.put(`http://localhost:8000/api/v1/notifications/${id}/read`);
      setNotifications(notifications.filter(n => n.id !== id));
      fetchCounts();
      if (onMarkAsRead) onMarkAsRead(id);
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await axios.post('http://localhost:8000/api/v1/notifications/read-all');
      setNotifications([]);
      fetchCounts();
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  const deleteNotification = async (id: number) => {
    if (!confirm('Delete this notification?')) return;
    try {
      await axios.delete(`http://localhost:8000/api/v1/notifications/${id}`);
      setNotifications(notifications.filter(n => n.id !== id));
      fetchCounts();
      if (onDelete) onDelete(id);
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch(priority) {
      case 'urgent': return <AlertCircle className="w-5 h-5 text-red-400" />;
      case 'high': return <AlertTriangle className="w-5 h-5 text-orange-400" />;
      case 'medium': return <Info className="w-5 h-5 text-yellow-400" />;
      default: return <CheckCircle className="w-5 h-5 text-blue-400" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch(priority) {
      case 'urgent': return 'bg-red-500/20 border-red-500/30 text-red-400';
      case 'high': return 'bg-orange-500/20 border-orange-500/30 text-orange-400';
      case 'medium': return 'bg-yellow-500/20 border-yellow-500/30 text-yellow-400';
      default: return 'bg-blue-500/20 border-blue-500/30 text-blue-400';
    }
  };

  const getTypeIcon = (type: string) => {
    switch(type) {
      case 'streak_alert': return <Zap className="w-4 h-4" />;
      case 'risk_warning': return <AlertTriangle className="w-4 h-4" />;
      case 'goal_achievement': return <Award className="w-4 h-4" />;
      case 'trade_confirmation': return <CheckCircle className="w-4 h-4" />;
      case 'drawdown_alert': return <TrendingDown className="w-4 h-4" />;
      case 'profit_target_alert': return <TrendingUp className="w-4 h-4" />;
      default: return <Bell className="w-4 h-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch(type) {
      case 'streak_alert': return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'risk_warning': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'goal_achievement': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'trade_confirmation': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'drawdown_alert': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'profit_target_alert': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const priorities = ['all', 'low', 'medium', 'high', 'urgent'];
  const types = ['all', 'streak_alert', 'risk_warning', 'goal_achievement', 'trade_confirmation', 'drawdown_alert', 'profit_target_alert'];

  if (loading) {
    return (
      <div className="min-h-[400px] bg-gray-900/50 border border-gray-800 rounded-xl p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500 font-mono">LOADING NOTIFICATIONS...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-gray-800 bg-gradient-to-r from-gray-900 to-gray-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <Bell className="w-6 h-6 text-cyan-400" />
                {counts.unread > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full text-xs text-white flex items-center justify-center">
                    {counts.unread > 9 ? '9+' : counts.unread}
                  </span>
                )}
              </div>
              <div>
                <h2 className="text-lg font-bold text-white">Notification Center</h2>
                <p className="text-xs text-gray-500 font-mono">
                  {counts.unread} unread · {counts.total} total
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Sound Toggle */}
              <button
                onClick={() => setSoundEnabled(!soundEnabled)}
                className={`p-2 rounded-lg transition ${
                  soundEnabled ? 'bg-cyan-500/20 text-cyan-400' : 'bg-gray-800 text-gray-500'
                }`}
                title={soundEnabled ? 'Sound On' : 'Sound Off'}
              >
                {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </button>

              {/* DND Toggle */}
              <button
                onClick={() => setDndEnabled(!dndEnabled)}
                className={`p-2 rounded-lg transition ${
                  dndEnabled ? 'bg-purple-500/20 text-purple-400' : 'bg-gray-800 text-gray-500'
                }`}
                title={dndEnabled ? 'Do Not Disturb On' : 'Do Not Disturb Off'}
              >
                {dndEnabled ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
              </button>

              {/* Settings */}
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition"
              >
                <Settings className="w-5 h-5 text-gray-400" />
              </button>

              {/* Mark All Read */}
              {notifications.length > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="px-3 py-2 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 rounded-lg text-sm font-mono transition flex items-center gap-1"
                >
                  <CheckCheck className="w-4 h-4" />
                  Mark All Read
                </button>
              )}
            </div>
          </div>

          {/* Settings Panel */}
          <AnimatePresence>
            {showSettings && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 pt-4 border-t border-gray-800 overflow-hidden"
              >
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {/* Priority Filter */}
                  <div>
                    <label className="block text-xs font-mono text-gray-500 mb-2">Priority</label>
                    <select
                      value={priorityFilter}
                      onChange={(e) => setPriorityFilter(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:border-cyan-500 transition"
                    >
                      {priorities.map(p => (
                        <option key={p} value={p}>{p.toUpperCase()}</option>
                      ))}
                    </select>
                  </div>

                  {/* Type Filter */}
                  <div>
                    <label className="block text-xs font-mono text-gray-500 mb-2">Type</label>
                    <select
                      value={typeFilter}
                      onChange={(e) => setTypeFilter(e.target.value)}
                      className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:border-cyan-500 transition"
                    >
                      {types.map(t => (
                        <option key={t} value={t}>{t.replace('_', ' ').toUpperCase()}</option>
                      ))}
                    </select>
                  </div>

                  {/* Status Filter */}
                  <div>
                    <label className="block text-xs font-mono text-gray-500 mb-2">Status</label>
                    <div className="flex gap-2">
                      {['all', 'unread', 'archived'].map((f) => (
                        <button
                          key={f}
                          onClick={() => setFilter(f as any)}
                          className={`px-3 py-1 rounded-lg text-xs font-mono transition ${
                            filter === f
                              ? 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-400'
                              : 'bg-gray-800 text-gray-500 hover:text-gray-400'
                          }`}
                        >
                          {f.toUpperCase()}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="bg-gray-800/50 rounded-lg p-3">
                    <div className="text-xs text-gray-500 font-mono mb-1">TODAY</div>
                    <div className="text-lg font-bold text-white">
                      {notifications.filter(n => 
                        new Date(n.created_at).toDateString() === new Date().toDateString()
                      ).length}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Notifications List */}
        <div 
          className="overflow-y-auto"
          style={{ maxHeight }}
        >
          {notifications.length === 0 ? (
            <div className="p-12 text-center">
              <div className="w-20 h-20 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
                <Bell className="w-8 h-8 text-gray-600" />
              </div>
              <h3 className="text-lg font-bold text-gray-400 mb-2">All caught up!</h3>
              <p className="text-gray-600">No notifications to show</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-800">
              {notifications.map((notification) => (
                <motion.div
                  key={notification.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className={`relative p-4 hover:bg-gray-800/50 transition cursor-pointer group ${
                    !notification.is_read ? 'bg-cyan-500/5' : ''
                  }`}
                  onClick={() => {
                    setSelectedNotification(notification);
                    setShowDetailModal(true);
                    if (onNotificationClick) onNotificationClick(notification);
                  }}
                >
                  {/* Unread Indicator */}
                  {!notification.is_read && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-cyan-400 rounded-r-full"></div>
                  )}

                  <div className="flex gap-4">
                    {/* Priority Icon */}
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                      getPriorityColor(notification.priority)
                    }`}>
                      {getPriorityIcon(notification.priority)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-1">
                        <div className="flex items-center gap-2">
                          <h4 className={`font-medium truncate ${
                            !notification.is_read ? 'text-white' : 'text-gray-400'
                          }`}>
                            {notification.title}
                          </h4>
                          <span className={`text-xs px-2 py-0.5 rounded-full flex items-center gap-1 ${getTypeColor(notification.type)}`}>
                            {getTypeIcon(notification.type)}
                            <span>{notification.type.replace('_', ' ')}</span>
                          </span>
                        </div>
                        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          {!notification.is_read && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                markAsRead(notification.id);
                              }}
                              className="p-1 hover:bg-gray-700 rounded transition"
                              title="Mark as read"
                            >
                              <CheckCheck className="w-4 h-4 text-cyan-400" />
                            </button>
                          )}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteNotification(notification.id);
                            }}
                            className="p-1 hover:bg-gray-700 rounded transition"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4 text-red-400" />
                          </button>
                        </div>
                      </div>

                      <p className="text-sm text-gray-400 mb-2 line-clamp-2">
                        {notification.message}
                      </p>

                      <div className="flex items-center gap-3 text-xs">
                        <span className="text-gray-600 font-mono">
                          {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                        </span>
                        {notification.expires_at && (
                          <span className="text-gray-600 font-mono">
                            Expires {formatDistanceToNow(new Date(notification.expires_at), { addSuffix: true })}
                          </span>
                        )}
                        {notification.data?.streak && (
                          <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded-full border border-purple-500/30 text-xs">
                            {notification.data.streak} streak
                          </span>
                        )}
                      </div>
                    </div>

                    <ChevronRight className="w-5 h-5 text-gray-600 flex-shrink-0 self-center" />
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-800 bg-gray-900/50">
          <Link
            href="/notifications"
            className="block text-center text-sm text-cyan-400 hover:text-cyan-300 font-mono"
          >
            VIEW ALL NOTIFICATIONS
          </Link>
        </div>
      </div>

      {/* Detail Modal */}
      <AnimatePresence>
        {showDetailModal && selectedNotification && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-gray-900 border border-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6 border-b border-gray-800 flex justify-between items-center">
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    getPriorityColor(selectedNotification.priority)
                  }`}>
                    {getPriorityIcon(selectedNotification.priority)}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">{selectedNotification.title}</h2>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`text-xs px-2 py-1 rounded-full flex items-center gap-1 ${getTypeColor(selectedNotification.type)}`}>
                        {getTypeIcon(selectedNotification.type)}
                        {selectedNotification.type.replace('_', ' ')}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(selectedNotification.priority)}`}>
                        {selectedNotification.priority.toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-500 hover:text-white transition"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="p-6 space-y-6">
                {/* Message */}
                <div>
                  <h3 className="text-sm font-mono text-cyan-400 mb-2">MESSAGE</h3>
                  <p className="text-white text-lg">{selectedNotification.message}</p>
                </div>

                {/* Data */}
                {selectedNotification.data && (
                  <div>
                    <h3 className="text-sm font-mono text-cyan-400 mb-2">DETAILS</h3>
                    <div className="bg-gray-800/50 rounded-lg p-4 space-y-2">
                      {Object.entries(selectedNotification.data).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-gray-500 font-mono text-sm">{key}:</span>
                          <span className="text-white font-mono">{String(value)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Metadata */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <h3 className="text-sm font-mono text-cyan-400 mb-2">RECEIVED</h3>
                    <p className="text-white">
                      {new Date(selectedNotification.created_at).toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {formatDistanceToNow(new Date(selectedNotification.created_at), { addSuffix: true })}
                    </p>
                  </div>
                  {selectedNotification.expires_at && (
                    <div>
                      <h3 className="text-sm font-mono text-cyan-400 mb-2">EXPIRES</h3>
                      <p className="text-white">
                        {new Date(selectedNotification.expires_at).toLocaleString()}
                      </p>
                    </div>
                  )}
                </div>
              </div>

              <div className="p-6 border-t border-gray-800 flex justify-end gap-3">
                {!selectedNotification.is_read && (
                  <button
                    onClick={() => {
                      markAsRead(selectedNotification.id);
                      setShowDetailModal(false);
                    }}
                    className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white transition flex items-center gap-2"
                  >
                    <CheckCheck className="w-4 h-4" />
                    Mark as Read
                  </button>
                )}
                <button
                  onClick={() => {
                    deleteNotification(selectedNotification.id);
                    setShowDetailModal(false);
                  }}
                  className="px-6 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition flex items-center gap-2"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white transition"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}
