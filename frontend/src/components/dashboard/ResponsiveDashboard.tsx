'use client';

import { useState, useEffect } from 'react';

interface ResponsiveDashboardProps {
  children: React.ReactNode;
  title: string;
}

export default function ResponsiveDashboard({ children, title }: ResponsiveDashboardProps) {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      const width = window.innerWidth;
      setIsMobile(width < 640);
      setIsTablet(width >= 640 && width < 1024);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  const getGridCols = () => {
    if (isMobile) return 'grid-cols-1';
    if (isTablet) return 'grid-cols-2';
    return 'grid-cols-4';
  };

  const getPadding = () => {
    if (isMobile) return 'p-2';
    if (isTablet) return 'p-4';
    return 'p-8';
  };

  const getTextSize = () => {
    if (isMobile) return 'text-2xl';
    if (isTablet) return 'text-3xl';
    return 'text-4xl';
  };

  return (
    <div className={`min-h-screen bg-gray-900 ${getPadding()}`}>
      <h1 className={`${getTextSize()} font-bold text-white mb-4 md:mb-8`}>{title}</h1>
      <div className={`grid ${getGridCols()} gap-2 md:gap-4`}>
        {children}
      </div>
    </div>
  );
}

// Responsive Card Component
export const ResponsiveCard = ({ children, title, icon }: any) => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    setIsMobile(window.innerWidth < 640);
  }, []);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-3 md:p-4 hover:border-blue-500 transition">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl md:text-2xl">{icon}</span>
        <h3 className="text-sm md:text-base font-medium text-gray-300">{title}</h3>
      </div>
      <div className="text-lg md:text-xl font-bold text-white">
        {children}
      </div>
    </div>
  );
};
