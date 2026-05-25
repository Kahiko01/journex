'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/auth/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import Image from 'next/image';
import axios from 'axios';

interface UserSettings {
  // Profile
  full_name: string;
  bio: string;
  trading_experience: string;
  preferred_markets: string;
  
  // Display
  theme_preference: 'dark' | 'light' | 'cyberpunk' | 'high-contrast';
  accent_color: string;
  default_timeframe: '1W' | '1M' | '3M' | '1Y' | 'ALL';
  chart_preference: 'candles' | 'line' | 'bar';
  currency_display: 'USD' | 'EUR' | 'GBP';
  font_size: 'small' | 'normal' | 'large';
  animations_enabled: boolean;
  compact_mode: boolean;
  
  // Email Notifications
  email_notifications: boolean;
  daily_report: boolean;
  weekly_report: boolean;
  risk_warnings: boolean;
  
  // Trade Alerts
  trade_confirmation: boolean;
  streak_alert: boolean;
  drawdown_alert: boolean;
  profit_target_alert: boolean;
  
  // Sound Settings
  sound_enabled: boolean;
  sound_volume: number;
  sound_type: 'chime' | 'bell' | 'alert' | 'digital';
  
  // Do Not Disturb
  dnd_enabled: boolean;
  dnd_start: string;
  dnd_end: string;
  dnd_priority_threshold: 'low' | 'medium' | 'high' | 'urgent';
  
  // Privacy
  profile_public: boolean;
  show_portfolio: boolean;
  show_trading_stats: boolean;
}

function SettingsContent() {
  const { user, updateUser } = useAuth();
  const { 
    theme, setTheme, 
    accentColor, setAccentColor,
    fontSize, setFontSize,
    animations, setAnimations,
    compactMode, setCompactMode
  } = useTheme();
  
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [settings, setSettings] = useState<UserSettings>({
    // Profile
    full_name: '',
    bio: '',
    trading_experience: '',
    preferred_markets: '',
    
    // Display
    theme_preference: 'dark',
    accent_color: 'cyan',
    default_timeframe: '1M',
    chart_preference: 'candles',
    currency_display: 'USD',
    font_size: 'normal',
    animations_enabled: true,
    compact_mode: false,
    
    // Email Notifications
    email_notifications: true,
    daily_report: false,
    weekly_report: true,
    risk_warnings: true,
    
    // Trade Alerts
    trade_confirmation: true,
    streak_alert: true,
    drawdown_alert: true,
    profit_target_alert: true,
    
    // Sound Settings
    sound_enabled: true,
    sound_volume: 70,
    sound_type: 'chime',
    
    // Do Not Disturb
    dnd_enabled: false,
    dnd_start: '22:00',
    dnd_end: '08:00',
    dnd_priority_threshold: 'urgent',
    
    // Privacy
    profile_public: false,
    show_portfolio: true,
    show_trading_stats: true,
  });

  useEffect(() => {
    if (user) {
      fetchSettings();
    }
  }, [user]);

  const fetchSettings = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/auth/settings');
      setSettings(response.data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setMessage({ type: 'error', text: 'Please upload an image file' });
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'File size must be less than 5MB' });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/avatar/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      if (user) {
        updateUser({ ...user, avatar_url: response.data.avatar_url });
      }
      setMessage({ type: 'success', text: 'Avatar uploaded successfully!' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Upload failed' });
    } finally {
      setUploading(false);
    }
  };

  const handleRemoveAvatar = async () => {
    try {
      await axios.delete('http://localhost:8000/api/v1/avatar/remove');
      if (user) {
        updateUser({ ...user, avatar_url: '' });
      }
      setMessage({ type: 'success', text: 'Avatar removed successfully!' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to remove avatar' });
    }
  };

  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      const response = await axios.put('http://localhost:8000/api/v1/auth/settings', settings);
      updateUser(response.data);
      
      // Apply theme settings immediately
      setTheme(settings.theme_preference);
      setAccentColor(settings.accent_color);
      setFontSize(settings.font_size);
      setAnimations(settings.animations_enabled);
      setCompactMode(settings.compact_mode);
      
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save settings' });
    } finally {
      setLoading(false);
    }
  };

  const handleResetSettings = async () => {
    if (!confirm('Are you sure you want to reset all settings to defaults?')) return;
    
    try {
      await axios.post('http://localhost:8000/api/v1/auth/settings/reset');
      await fetchSettings();
      setMessage({ type: 'success', text: 'Settings reset to defaults!' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to reset settings' });
    }
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: '👤' },
    { id: 'appearance', name: 'Appearance', icon: '🎨' },
    { id: 'display', name: 'Display', icon: '📊' },
    { id: 'notifications', name: 'Notifications', icon: '🔔' },
    { id: 'privacy', name: 'Privacy', icon: '🔒' },
  ];

  const accentColors = [
    { id: 'cyan', name: 'Cyan', class: 'bg-cyan-500' },
    { id: 'purple', name: 'Purple', class: 'bg-purple-500' },
    { id: 'blue', name: 'Blue', class: 'bg-blue-500' },
    { id: 'green', name: 'Green', class: 'bg-green-500' },
    { id: 'rose', name: 'Rose', class: 'bg-rose-500' },
    { id: 'amber', name: 'Amber', class: 'bg-amber-500' },
  ];

  const themes = [
    { id: 'dark', name: 'Dark', icon: '🌙', description: 'Easy on the eyes' },
    { id: 'light', name: 'Light', icon: '☀️', description: 'Bright and clean' },
    { id: 'cyberpunk', name: 'Cyberpunk', icon: '🌃', description: 'Neon dreams' },
    { id: 'high-contrast', name: 'High Contrast', icon: '⚡', description: 'Maximum visibility' },
  ];

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg-primary)' }}>
      <div className="max-w-4xl mx-auto py-12 px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-black mb-2" style={{ color: 'var(--text-primary)' }}>
            SETTINGS
          </h1>
          <p style={{ color: 'var(--text-secondary)' }} className="font-mono text-sm">
            CUSTOMIZE YOUR EXPERIENCE
          </p>
        </div>

        {/* Message */}
        {message.text && (
          <div className={`mb-6 p-4 rounded-lg border ${
            message.type === 'success' 
              ? 'bg-green-500/10 border-green-500/30 text-green-400' 
              : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
          } font-mono text-sm`}>
            {message.type === 'success' ? '✓' : '⚠'} {message.text}
          </div>
        )}

        {/* Main Settings Card */}
        <div className="card rounded-2xl overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b" style={{ borderColor: 'var(--border-color)' }}>
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 px-6 py-4 font-mono text-sm transition-all ${
                  activeTab === tab.id
                    ? 'border-b-2'
                    : 'opacity-60 hover:opacity-100'
                }`}
                style={{
                  color: activeTab === tab.id ? 'var(--accent-primary)' : 'var(--text-secondary)',
                  borderColor: 'var(--accent-primary)',
                  backgroundColor: activeTab === tab.id ? 'var(--hover-bg)' : 'transparent'
                }}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="p-8" style={{ backgroundColor: 'var(--card-bg)' }}>
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="space-y-8">
                {/* Avatar Section */}
                <div className="flex items-center gap-8">
                  <div className="relative">
                    <div className="w-24 h-24 rounded-full p-1" style={{ 
                      background: `linear-gradient(to right, var(--accent-primary), var(--accent-secondary))`
                    }}>
                      <div className="w-full h-full rounded-full flex items-center justify-center overflow-hidden"
                           style={{ backgroundColor: 'var(--bg-secondary)' }}>
                        {user?.avatar_url ? (
                          <img 
                            src={`http://localhost:8000${user.avatar_url}`}
                            alt="Avatar"
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <span className="text-4xl" style={{ color: 'var(--accent-primary)' }}>
                            {user?.username?.[0].toUpperCase()}
                          </span>
                        )}
                      </div>
                    </div>
                    {uploading && (
                      <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full animate-ping"
                           style={{ backgroundColor: 'var(--accent-primary)' }}></div>
                    )}
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex gap-3">
                      <label className="relative cursor-pointer group">
                        <div className="absolute -inset-0.5 rounded-lg opacity-0 group-hover:opacity-50 blur transition"
                             style={{ background: `linear-gradient(to right, var(--accent-primary), var(--accent-secondary))` }}></div>
                        <div className="relative px-4 py-2 rounded-lg border font-mono text-sm transition"
                             style={{ 
                               backgroundColor: 'var(--bg-tertiary)',
                               borderColor: 'var(--border-color)',
                               color: 'var(--text-primary)'
                             }}>
                          UPLOAD AVATAR
                          <input
                            type="file"
                            accept="image/*"
                            onChange={handleAvatarUpload}
                            className="absolute inset-0 opacity-0 cursor-pointer"
                          />
                        </div>
                      </label>
                      
                      {user?.avatar_url && (
                        <button
                          onClick={handleRemoveAvatar}
                          className="px-4 py-2 rounded-lg border font-mono text-sm transition hover:bg-opacity-30"
                          style={{ 
                            backgroundColor: 'var(--hover-bg)',
                            borderColor: 'var(--border-color)',
                            color: 'var(--text-secondary)'
                          }}
                        >
                          REMOVE
                        </button>
                      )}
                    </div>
                    <p className="text-xs font-mono" style={{ color: 'var(--text-muted)' }}>
                      Max size: 5MB • JPG, PNG, GIF
                    </p>
                  </div>
                </div>

                {/* Profile Form */}
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-mono mb-2" style={{ color: 'var(--accent-primary)' }}>
                      FULL NAME
                    </label>
                    <input
                      type="text"
                      value={settings.full_name}
                      onChange={(e) => setSettings({...settings, full_name: e.target.value})}
                      className="w-full px-4 py-3 rounded-lg border font-mono focus:outline-none transition"
                      style={{ 
                        backgroundColor: 'var(--bg-tertiary)',
                        borderColor: 'var(--border-color)',
                        color: 'var(--text-primary)'
                      }}
                      placeholder="Enter your full name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-mono mb-2" style={{ color: 'var(--accent-primary)' }}>
                      BIO
                    </label>
                    <textarea
                      value={settings.bio}
                      onChange={(e) => setSettings({...settings, bio: e.target.value})}
                      rows={4}
                      className="w-full px-4 py-3 rounded-lg border font-mono focus:outline-none transition"
                      style={{ 
                        backgroundColor: 'var(--bg-tertiary)',
                        borderColor: 'var(--border-color)',
                        color: 'var(--text-primary)'
                      }}
                      placeholder="Tell us about yourself..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-mono mb-2" style={{ color: 'var(--accent-primary)' }}>
                      TRADING EXPERIENCE
                    </label>
                    <select
                      value={settings.trading_experience}
                      onChange={(e) => setSettings({...settings, trading_experience: e.target.value})}
                      className="w-full px-4 py-3 rounded-lg border font-mono focus:outline-none transition"
                      style={{ 
                        backgroundColor: 'var(--bg-tertiary)',
                        borderColor: 'var(--border-color)',
                        color: 'var(--text-primary)'
                      }}
                    >
                      <option value="">Select experience</option>
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                      <option value="pro">Professional</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-mono mb-2" style={{ color: 'var(--accent-primary)' }}>
                      PREFERRED MARKETS
                    </label>
                    <input
                      type="text"
                      value={settings.preferred_markets}
                      onChange={(e) => setSettings({...settings, preferred_markets: e.target.value})}
                      className="w-full px-4 py-3 rounded-lg border font-mono focus:outline-none transition"
                      style={{ 
                        backgroundColor: 'var(--bg-tertiary)',
                        borderColor: 'var(--border-color)',
                        color: 'var(--text-primary)'
                      }}
                      placeholder="e.g., Forex, Crypto, Stocks"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Appearance Tab */}
            {activeTab === 'appearance' && (
              <div className="space-y-8">
                {/* Theme Selection */}
                <div>
                  <label className="block text-sm font-mono mb-4" style={{ color: 'var(--accent-primary)' }}>
                    THEME
                  </label>
                  <div className="grid grid-cols-2 gap-4">
                    {themes.map((t) => (
                      <button
                        key={t.id}
                        onClick={() => {
                          setSettings({...settings, theme_preference: t.id as any});
                          setTheme(t.id);
                        }}
                        className="p-4 rounded-lg border transition-all text-left"
                        style={{ 
                          backgroundColor: settings.theme_preference === t.id ? 'var(--hover-bg)' : 'var(--bg-tertiary)',
                          borderColor: settings.theme_preference === t.id ? 'var(--accent-primary)' : 'var(--border-color)',
                        }}
                      >
                        <div className="text-2xl mb-2">{t.icon}</div>
                        <div className="font-bold mb-1" style={{ color: 'var(--text-primary)' }}>{t.name}</div>
                        <div className="text-xs" style={{ color: 'var(--text-muted)' }}>{t.description}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Accent Color */}
                <div>
                  <label className="block text-sm font-mono mb-4" style={{ color: 'var(--accent-primary)' }}>
                    ACCENT COLOR
                  </label>
                  <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                    {accentColors.map((color) => (
                      <button
                        key={color.id}
                        onClick={() => {
                          setSettings({...settings, accent_color: color.id});
                          setAccentColor(color.id);
                        }}
                        className="relative group"
                      >
                        <div className={`w-full aspect-square rounded-lg ${color.class} transition-all ${
                          settings.accent_color === color.id ? 'ring-2 scale-110' : ''
                        }`}
                        style={{ 
                          ringColor: 'var(--accent-primary)',
                          boxShadow: settings.accent_color === color.id ? '0 0 15px currentColor' : 'none'
                        }}></div>
                        <span className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 text-xs opacity-0 group-hover:opacity-100 transition font-mono"
                              style={{ color: 'var(--text-muted)' }}>
                          {color.name}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Font Size */}
                <div>
                  <label className="block text-sm font-mono mb-4" style={{ color: 'var(--accent-primary)' }}>
                    FONT SIZE
                  </label>
                  <div className="flex gap-3">
                    {['small', 'normal', 'large'].map((size) => (
                      <button
                        key={size}
                        onClick={() => {
                          setSettings({...settings, font_size: size as any});
                          setFontSize(size);
                        }}
                        className="flex-1 py-3 rounded-lg border font-mono text-sm transition-all capitalize"
                        style={{ 
                          backgroundColor: settings.font_size === size ? 'var(--hover-bg)' : 'var(--bg-tertiary)',
                          borderColor: settings.font_size === size ? 'var(--accent-primary)' : 'var(--border-color)',
                          color: 'var(--text-primary)',
                          fontSize: size === 'small' ? '0.875rem' : size === 'large' ? '1.125rem' : '1rem'
                        }}
                      >
                        {size}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Toggles */}
                <div className="space-y-4">
                  <label className="flex items-center justify-between p-4 rounded-lg border"
                         style={{ backgroundColor: 'var(--bg-tertiary)', borderColor: 'var(--border-color)' }}>
                    <div>
                      <span className="font-mono text-sm" style={{ color: 'var(--text-primary)' }}>Animations</span>
                      <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>Enable smooth transitions and effects</p>
                    </div>
                    <button
                      onClick={() => {
                        setSettings({...settings, animations_enabled: !settings.animations_enabled});
                        setAnimations(!settings.animations_enabled);
                      }}
                      className={`w-12 h-6 rounded-full transition-all relative ${
                        settings.animations_enabled ? 'bg-opacity-100' : 'bg-opacity-30'
                      }`}
                      style={{ backgroundColor: settings.animations_enabled ? 'var(--accent-primary)' : 'var(--border-color)' }}
                    >
                      <div className={`absolute w-5 h-5 rounded-full top-0.5 transition-all ${
                        settings.animations_enabled ? 'right-0.5' : 'left-0.5'
                      }`} style={{ backgroundColor: 'var(--bg-primary)' }}></div>
                    </button>
                  </label>

                  <label className="flex items-center justify-between p-4 rounded-lg border"
                         style={{ backgroundColor: 'var(--bg-tertiary)', borderColor: 'var(--border-color)' }}>
                    <div>
                      <span className="font-mono text-sm" style={{ color: 'var(--text-primary)' }}>Compact Mode</span>
                      <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>Reduce spacing for more content</p>
                    </div>
                    <button
                      onClick={() => {
                        setSettings({...settings, compact_mode: !settings.compact_mode});
                        setCompactMode(!settings.compact_mode);
                      }}
                      className={`w-12 h-6 rounded-full transition-all relative ${
                        settings.compact_mode ? 'bg-opacity-100' : 'bg-opacity-30'
                      }`}
                      style={{ backgroundColor: settings.compact_mode ? 'var(--accent-primary)' : 'var(--border-color)' }}
                    >
                      <div className={`absolute w-5 h-5 rounded-full top-0.5 transition-all ${
                        settings.compact_mode ? 'right-0.5' : 'left-0.5'
                      }`} style={{ backgroundColor: 'var(--bg-primary)' }}></div>
                    </button>
                  </label>
                </div>
              </div>
            )}

            {/* Display Tab */}
            {activeTab === 'display' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-mono mb-2" style={{ color: 'var(--accent-primary)' }}>
                    DEFAULT TIMEFRAME
                  </label>
                  <div className="grid grid-cols-5 gap-2">
                    {['1W', '1M', '3M', '1Y', 'ALL'].map((tf) => (
                      <button
                        key={tf}
                        onClick={() => setSettings({...settings, default_timeframe: tf as any})}
                        className="p-2 rounded-lg border font-mono text-sm transition"
                        style={{ 
                          backgroundColor: settings.default_timeframe === tf ? 'var(--hover-bg)' : 'var(--bg-tertiary)',
                          borderColor: settings.default_timeframe === tf ? 'var(--accent-primary)' : 'var(--border-color)',
                          color: 'var(--text-primary)'
                        }}
                      >
                        {tf}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-mono mb-2" style={{ color: 'var(--accent-primary)' }}>
                    CHART PREFERENCE
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {['candles', 'line', 'bar'].map((chart) => (
                      <button
                        key={chart}
                        onClick={() => setSettings({...settings, chart_preference: chart as any})}
                        className="p-4 rounded-lg border font-mono text-sm capitalize transition"
                        style={{ 
                          backgroundColor: settings.chart_preference === chart ? 'var(--hover-bg)' : 'var(--bg-tertiary)',
                          borderColor: settings.chart_preference === chart ? 'var(--accent-primary)' : 'var(--border-color)',
                          color: 'var(--text-primary)'
                        }}
                      >
                        {chart}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-mono mb-2" style={{ color: 'var(--accent-primary)' }}>
                    CURRENCY DISPLAY
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {['USD', 'EUR', 'GBP'].map((currency) => (
                      <button
                        key={currency}
                        onClick={() => setSettings({...settings, currency_display: currency as any})}
                        className="p-4 rounded-lg border font-mono text-sm transition"
                        style={{ 
                          backgroundColor: settings.currency_display === currency ? 'var(--hover-bg)' : 'var(--bg-tertiary)',
                          borderColor: settings.currency_display === currency ? 'var(--accent-primary)' : 'var(--border-color)',
                          color: 'var(--text-primary)'
                        }}
                      >
                        {currency}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                {/* Email Notifications Section */}
                <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700">
                  <h3 className="text-lg font-mono text-cyan-400 mb-4">EMAIL NOTIFICATIONS</h3>
                  
                  <div className="space-y-4">
                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Enable Email Notifications</span>
                        <p className="text-xs text-gray-500 mt-1">Receive notifications via email</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, email_notifications: !settings.email_notifications})}
                        className={`w-12 h-6 rounded-full transition-all relative ${
                          settings.email_notifications ? 'bg-cyan-500' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${
                          settings.email_notifications ? 'right-0.5' : 'left-0.5'
                        }`}></div>
                      </button>
                    </label>

                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Daily Performance Report</span>
                        <p className="text-xs text-gray-500 mt-1">Get a daily summary of your trading</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, daily_report: !settings.daily_report})}
                        className={`w-12 h-6 rounded-full transition-all relative ${
                          settings.daily_report ? 'bg-cyan-500' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${
                          settings.daily_report ? 'right-0.5' : 'left-0.5'
                        }`}></div>
                      </button>
                    </label>

                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Weekly Performance Report</span>
                        <p className="text-xs text-gray-500 mt-1">Weekly in-depth analysis</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, weekly_report: !settings.weekly_report})}
                        className={`w-12 h-6 rounded-full transition-all relative ${
                          settings.weekly_report ? 'bg-cyan-500' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${
                          settings.weekly_report ? 'right-0.5' : 'left-0.5'
                        }`}></div>
                      </button>
                    </label>

                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Risk Warnings</span>
                        <p className="text-xs text-gray-500 mt-1">Get alerted about high-risk situations</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, risk_warnings: !settings.risk_warnings})}
                        className={`w-12 h-6 rounded-full transition-all relative ${
                          settings.risk_warnings ? 'bg-cyan-500' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${
                          settings.risk_warnings ? 'right-0.5' : 'left-0.5'
                        }`}></div>
                      </button>
                    </label>
                  </div>
                </div>

                {/* Trade Alerts Section */}
                <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700">
                  <h3 className="text-lg font-mono text-purple-400 mb-4">TRADE ALERTS</h3>
                  
                  <div className="space-y-4">
                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Trade Confirmation</span>
                        <p className="text-xs text-gray-500 mt-1">Confirm when trades are executed</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, trade_confirmation: !settings.trade_confirmation})}
                        className={`w-12 h-6 rounded-full transition-all relative ${
                          settings.trade_confirmation ? 'bg-purple-500' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${
                          settings.trade_confirmation ? 'right-0.5' : 'left-0.5'
                        }`}></div>
                      </button>
                    </label>

                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Win/Loss Streak Alerts</span>
                        <p className="text-xs text-gray-500 mt-1">Get notified of trading streaks</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, streak_alert: !settings.streak_alert})}
                        className={`w-12 h-6 rounded-full transition-all relative ${
                          settings.streak_alert ? 'bg-purple-500' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${
                          settings.streak_alert ? 'right-0.5' : 'left-0.5'
                        }`}></div>
                      </button>
                    </label>

                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Drawdown Alerts</span>
                        <p className="text-xs text-gray-500 mt-1">Alert when drawdown exceeds threshold</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, drawdown_alert: !settings.drawdown_alert})}
                        className={`w-12 h-6 rounded-full transition-all relative ${
                          settings.drawdown_alert ? 'bg-purple-500' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${
                          settings.drawdown_alert ? 'right-0.5' : 'left-0.5'
                        }`}></div>
                      </button>
                    </label>

                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Profit Target Alerts</span>
                        <p className="text-xs text-gray-500 mt-1">Notify when profit targets are hit</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, profit_target_alert: !settings.profit_target_alert})}
                        className={`w-12 h-6 rounded-full transition-all relative ${
                          settings.profit_target_alert ? 'bg-purple-500' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${
                          settings.profit_target_alert ? 'right-0.5' : 'left-0.5'
                        }`}></div>
                      </button>
                    </label>
                  </div>
                </div>

                {/* Sound Settings Section */}
                <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700">
                  <h3 className="text-lg font-mono text-green-400 mb-4">SOUND SETTINGS</h3>
                  
                  <div className="space-y-4">
                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Enable Sounds</span>
                        <p className="text-xs text-gray-500 mt-1">Play sounds for notifications</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, sound_enabled: !settings.sound_enabled})}
                        className={`w-12 h-6 rounded-full transition-all relative ${
                          settings.sound_enabled ? 'bg-green-500' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${
                          settings.sound_enabled ? 'right-0.5' : 'left-0.5'
                        }`}></div>
                      </button>
                    </label>

                    {settings.sound_enabled && (
                      <>
                        {/* Volume Control */}
                        <div className="p-4 bg-gray-800/50 rounded-lg">
                          <div className="flex justify-between mb-2">
                            <span className="text-white font-mono text-sm">Volume</span>
                            <span className="text-green-400 font-mono text-sm">{settings.sound_volume}%</span>
                          </div>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={settings.sound_volume}
                            onChange={(e) => setSettings({...settings, sound_volume: parseInt(e.target.value)})}
                            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                            style={{
                              background: `linear-gradient(to right, #10b981 0%, #10b981 ${settings.sound_volume}%, #374151 ${settings.sound_volume}%, #374151 100%)`
                            }}
                          />
                        </div>

                        {/* Sound Type Selection */}
                        <div className="p-4 bg-gray-800/50 rounded-lg">
                          <span className="text-white font-mono text-sm block mb-3">Notification Sound</span>
                          <div className="grid grid-cols-2 gap-2">
                            {['chime', 'bell', 'alert', 'digital'].map((sound) => (
                              <button
                                key={sound}
                                onClick={() => setSettings({...settings, sound_type: sound as any})}
                                className={`p-3 rounded-lg border font-mono text-sm capitalize transition ${
                                  settings.sound_type === sound
                                    ? 'bg-green-500/20 border-green-400 text-green-400'
                                    : 'bg-gray-700 border-gray-600 text-gray-400 hover:border-gray-500'
                                }`}
                              >
                                {sound}
                                {settings.sound_type === sound && (
                                  <span className="ml-2 text-xs">✓</span>
                                )}
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* Test Sound Button */}
                        <div className="flex justify-end">
                          <button
                            onClick={() => {
                              const audio = new Audio(`/sounds/${settings.sound_type}.mp3`);
                              audio.volume = settings.sound_volume / 100;
                              audio.play();
                            }}
                            className="px-4 py-2 bg-green-500/20 border border-green-500/30 rounded-lg text-green-400 hover:bg-green-500/30 transition text-sm font-mono"
                          >
                            🔈 Test Sound
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                </div>

                {/* Do Not Disturb Section */}
                <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700">
                  <h3 className="text-lg font-mono text-amber-400 mb-4">DO NOT DISTURB</h3>
                  
                  <div className="space-y-4">
                    <label className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg">
                      <div>
                        <span className="text-white font-mono">Quiet Hours</span>
                        <p className="text-xs text-gray-500 mt-1">Mute notifications during specific hours</p>
                      </div>
                      <button
                        onClick={() => setSettings({...settings, dnd_enabled: !settings.dnd_enabled})}
                        className={`w-12 h-6 rounded-full transition-all relative ${
                          settings.dnd_enabled ? 'bg-amber-500' : 'bg-gray-600'
                        }`}
                      >
                        <div className={`absolute w-5 h-5 rounded-full bg-white top-0.5 transition-all ${
                          settings.dnd_enabled ? 'right-0.5' : 'left-0.5'
                        }`}></div>
                      </button>
                    </label>

                    {settings.dnd_enabled && (
                      <>
                        {/* Time Range */}
                        <div className="grid grid-cols-2 gap-4 p-4 bg-gray-800/50 rounded-lg">
                          <div>
                            <label className="block text-xs text-gray-500 mb-1 font-mono">Start Time</label>
                            <input
                              type="time"
                              value={settings.dnd_start}
                              onChange={(e) => setSettings({...settings, dnd_start: e.target.value})}
                              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white font-mono"
                            />
                          </div>
                          <div>
                            <label className="block text-xs text-gray-500 mb-1 font-mono">End Time</label>
                            <input
                              type="time"
                              value={settings.dnd_end}
                              onChange={(e) => setSettings({...settings, dnd_end: e.target.value})}
                              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white font-mono"
                            />
                          </div>
                        </div>

                        {/* Priority Threshold */}
                        <div className="p-4 bg-gray-800/50 rounded-lg">
                          <span className="text-white font-mono text-sm block mb-3">Allow Priority</span>
                          <div className="grid grid-cols-2 gap-2">
                            {[
                              { value: 'urgent', label: 'Urgent Only' },
                              { value: 'high', label: 'High + Urgent' },
                              { value: 'medium', label: 'Medium & Above' },
                              { value: 'low', label: 'All' }
                            ].map((option) => (
                              <button
                                key={option.value}
                                onClick={() => setSettings({...settings, dnd_priority_threshold: option.value as any})}
                                className={`p-2 rounded-lg border font-mono text-xs transition ${
                                  settings.dnd_priority_threshold === option.value
                                    ? 'bg-amber-500/20 border-amber-400 text-amber-400'
                                    : 'bg-gray-700 border-gray-600 text-gray-400 hover:border-gray-500'
                                }`}
                              >
                                {option.label}
                              </button>
                            ))}
                          </div>
                          <p className="text-xs text-gray-600 mt-2">
                            Only notifications at or above this priority will play during quiet hours
                          </p>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Privacy Tab */}
            {activeTab === 'privacy' && (
              <div className="space-y-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-mono mb-4" style={{ color: 'var(--accent-primary)' }}>
                    PROFILE VISIBILITY
                  </h3>
                  
                  {[
                    { key: 'profile_public', label: 'Make profile public' },
                    { key: 'show_portfolio', label: 'Show portfolio to others' },
                    { key: 'show_trading_stats', label: 'Show trading statistics' },
                  ].map((item) => (
                    <label key={item.key} className="flex items-center justify-between p-4 rounded-lg border"
                           style={{ backgroundColor: 'var(--bg-tertiary)', borderColor: 'var(--border-color)' }}>
                      <span className="font-mono text-sm" style={{ color: 'var(--text-primary)' }}>{item.label}</span>
                      <input
                        type="checkbox"
                        checked={settings[item.key as keyof UserSettings] as boolean}
                        onChange={(e) => setSettings({...settings, [item.key]: e.target.checked})}
                        className="w-5 h-5"
                        style={{ accentColor: 'var(--accent-primary)' }}
                      />
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between items-center p-8 border-t"
               style={{ backgroundColor: 'var(--card-bg)', borderColor: 'var(--border-color)' }}>
            <button
              onClick={handleResetSettings}
              className="px-6 py-3 rounded-lg border font-mono text-sm transition hover:bg-opacity-30"
              style={{ 
                backgroundColor: 'var(--hover-bg)',
                borderColor: 'var(--border-color)',
                color: 'var(--text-secondary)'
              }}
            >
              RESET TO DEFAULTS
            </button>
            
            <button
              onClick={handleSaveSettings}
              disabled={loading}
              className="relative group"
            >
              <div className="absolute -inset-0.5 rounded-lg opacity-70 group-hover:opacity-100 blur transition"
                   style={{ background: `linear-gradient(to right, var(--accent-primary), var(--accent-secondary))` }}></div>
              <div className="relative px-8 py-3 rounded-lg font-mono text-sm"
                   style={{ backgroundColor: 'var(--bg-primary)', color: 'var(--text-primary)' }}>
                {loading ? 'SAVING...' : 'SAVE CHANGES'}
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ProtectedSettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  );
}
