'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ChevronDown } from 'lucide-react';

export default function UniversityDropdown() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-2 rounded-md text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white inline-flex items-center gap-1"
      >
        University
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-1 w-48 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-50">
            <Link
              href="/university"
              className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white rounded-t-lg"
              onClick={() => setIsOpen(false)}
            >
              📚 All Courses
            </Link>
            <Link
              href="/progress"
              className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white"
              onClick={() => setIsOpen(false)}
            >
              📊 My Progress
            </Link>
            <Link
              href="/cohorts"
              className="block px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white rounded-b-lg"
              onClick={() => setIsOpen(false)}
            >
              👥 Study Cohorts
            </Link>
          </div>
        </>
      )}
    </div>
  );
}
