'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { useAuth } from './auth/AuthContext';

interface ThemeContextType {
  theme: string;
  setTheme: (theme: string) => void;
  accentColor: string;
  setAccentColor: (color: string) => void;
  fontSize: string;
  setFontSize: (size: string) => void;
  animations: boolean;
  setAnimations: (enabled: boolean) => void;
  compactMode: boolean;
  setCompactMode: (enabled: boolean) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const accentColors = {
  cyan: { primary: '#06b6d4', secondary: '#0891b2', glow: 'rgba(6,182,212,0.5)' },
  purple: { primary: '#a855f7', secondary: '#9333ea', glow: 'rgba(168,85,247,0.5)' },
  blue: { primary: '#3b82f6', secondary: '#2563eb', glow: 'rgba(59,130,246,0.5)' },
  green: { primary: '#10b981', secondary: '#059669', glow: 'rgba(16,185,129,0.5)' },
  rose: { primary: '#f43f5e', secondary: '#e11d48', glow: 'rgba(244,63,94,0.5)' },
  amber: { primary: '#f59e0b', secondary: '#d97706', glow: 'rgba(245,158,11,0.5)' },
};

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { user, updateUser } = useAuth();
  const [theme, setTheme] = useState('dark');
  const [accentColor, setAccentColor] = useState('cyan');
  const [fontSize, setFontSize] = useState('normal');
  const [animations, setAnimations] = useState(true);
  const [compactMode, setCompactMode] = useState(false);

  // Load user preferences when available
  useEffect(() => {
    if (user?.theme_preference) {
      setTheme(user.theme_preference);
    }
    if (user?.accent_color) {
      setAccentColor(user.accent_color);
    }
  }, [user]);

  // Apply theme changes to document
  useEffect(() => {
    applyTheme(theme, accentColor, fontSize, animations, compactMode);
  }, [theme, accentColor, fontSize, animations, compactMode]);

  const applyTheme = (
    themeMode: string, 
    accent: string, 
    size: string, 
    animate: boolean,
    compact: boolean
  ) => {
    const root = document.documentElement;
    
    // Remove all theme classes
    root.classList.remove('dark', 'light', 'cyberpunk', 'high-contrast');
    root.classList.add(themeMode);
    
    // Apply accent color as CSS variables
    const color = accentColors[accent as keyof typeof accentColors] || accentColors.cyan;
    root.style.setProperty('--accent-primary', color.primary);
    root.style.setProperty('--accent-secondary', color.secondary);
    root.style.setProperty('--accent-glow', color.glow);
    
    // Apply font size
    root.style.setProperty('--font-scale', 
      size === 'small' ? '0.9' : 
      size === 'large' ? '1.1' : '1'
    );
    
    // Apply animations
    root.style.setProperty('--animations-enabled', animate ? '1' : '0');
    if (!animate) {
      root.classList.add('reduce-motion');
    } else {
      root.classList.remove('reduce-motion');
    }
    
    // Apply compact mode
    root.style.setProperty('--spacing-scale', compact ? '0.8' : '1');
    
    // Save to localStorage for persistence
    localStorage.setItem('theme-preferences', JSON.stringify({
      theme: themeMode,
      accent,
      fontSize: size,
      animations: animate,
      compactMode: compact
    }));
  };

  const handleSetTheme = (newTheme: string) => {
    setTheme(newTheme);
    if (user) {
      updateUser({ ...user, theme_preference: newTheme });
    }
  };

  const handleSetAccentColor = (color: string) => {
    setAccentColor(color);
    if (user) {
      updateUser({ ...user, accent_color: color });
    }
  };

  return (
    <ThemeContext.Provider value={{
      theme,
      setTheme: handleSetTheme,
      accentColor,
      setAccentColor: handleSetAccentColor,
      fontSize,
      setFontSize,
      animations,
      setAnimations,
      compactMode,
      setCompactMode,
    }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
