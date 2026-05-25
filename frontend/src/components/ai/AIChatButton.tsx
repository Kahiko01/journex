'use client';

import { useState } from 'react';
import AIChat from './AIChat';

export default function AIChatButton() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating AI Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 group z-40"
      >
        {/* Outer glow rings */}
        <div className="absolute inset-0 rounded-full bg-blue-500 opacity-20 animate-ping"></div>
        <div className="absolute inset-0 rounded-full bg-purple-500 opacity-30 animate-pulse"></div>
        
        {/* Main button */}
        <div className="relative bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-all duration-300 hover:shadow-blue-500/50">
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-gray-900 animate-pulse"></div>
          <svg className="w-6 h-6 group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          
          {/* Tooltip */}
          <div className="absolute right-full mr-4 top-1/2 -translate-y-1/2 bg-gray-800 text-white px-3 py-1 rounded-lg text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300 border border-gray-700">
            AI Assistant
            <div className="absolute top-1/2 -right-2 -translate-y-1/2 border-8 border-transparent border-l-gray-800"></div>
          </div>
        </div>
      </button>

      {/* AI Chat Modal */}
      {isOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="relative w-full max-w-4xl h-[80vh]">
            <button
              onClick={() => setIsOpen(false)}
              className="absolute -top-12 right-0 text-white hover:text-gray-300 text-2xl bg-gray-800/50 backdrop-blur-sm rounded-full p-2 w-10 h-10 flex items-center justify-center border border-gray-700 hover:border-gray-600 transition"
            >
              ✕
            </button>
            <AIChat onClose={() => setIsOpen(false)} initialOpen={true} />
          </div>
        </div>
      )}
    </>
  );
}
