'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  BookOpen, Clock, ChevronRight, Filter, 
  Search, PlayCircle, Award, BarChart3, 
  TrendingUp, Shield, Brain, Zap, X
} from 'lucide-react';

interface Course {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  duration_minutes: number;
  slug: string;
  status: string;
  created_at: string;
  lessons_count?: number;
  students_count?: number;
  rating?: number;
}

const categoryIcons: Record<string, React.ReactNode> = {
  'Technical Analysis': <BarChart3 className="w-5 h-5" />,
  'Risk Management': <Shield className="w-5 h-5" />,
  'Psychology': <Brain className="w-5 h-5" />,
  'Strategy': <TrendingUp className="w-5 h-5" />,
  'Fundamentals': <BookOpen className="w-5 h-5" />,
  'Advanced': <Zap className="w-5 h-5" />,
};

const difficultyConfig = {
  Beginner: { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', icon: '🌱' },
  Intermediate: { color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20', icon: '🚀' },
  Advanced: { color: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20', icon: '⚡' },
};

function UniversityContent() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [hoveredCourse, setHoveredCourse] = useState<string | null>(null);

  useEffect(() => {
    fetchCourses();
  }, []);

  // UPDATED: Added console.log for debugging API structure
  const fetchCourses = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/v1/university/courses/');
      
      console.log('API Response:', response.data); 
      
      // We assume response.data.courses is the array based on your requirement
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['all', ...new Set(courses.map(c => c.category).filter(Boolean))];
  const difficulties = ['all', 'Beginner', 'Intermediate', 'Advanced'];

  const filteredCourses = courses.filter(course => {
    const categoryMatch = selectedCategory === 'all' || course.category === selectedCategory;
    const difficultyMatch = selectedDifficulty === 'all' || course.difficulty === selectedDifficulty;
    const searchMatch = !searchQuery || 
      course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.description.toLowerCase().includes(searchQuery.toLowerCase());
    return categoryMatch && difficultyMatch && searchMatch;
  });

  const stats = {
    total: courses.length,
    completed: 0,
    hours: Math.floor(courses.reduce((acc, c) => acc + c.duration_minutes, 0) / 60),
    certificates: 0,
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

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-[150px]"></div>
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-[150px]"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-6 py-12">
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
            <span className="text-cyan-400 text-xs font-mono uppercase tracking-widest">Education Center</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-black mb-4">
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              Trading University
            </span>
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl">
            Master the markets with our comprehensive curriculum designed by professional traders.
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          {[
            { label: 'Total Courses', value: stats.total, icon: BookOpen, color: 'cyan' },
            { label: 'Hours of Content', value: stats.hours, icon: Clock, color: 'purple' },
            { label: 'Completed', value: stats.completed, icon: Award, color: 'emerald' },
            { label: 'Certificates', value: stats.certificates, icon: Award, color: 'amber' },
          ].map((stat, idx) => (
            <div key={idx} className="bg-gray-900/50 border border-gray-800 rounded-xl p-4 backdrop-blur-sm">
              <div className="flex items-center gap-3 mb-2">
                <div className={`p-2 rounded-lg bg-${stat.color}-500/10`}>
                  <stat.icon className={`w-5 h-5 text-${stat.color}-400`} />
                </div>
                <span className="text-2xl font-bold">{stat.value}</span>
              </div>
              <span className="text-xs text-gray-500 font-mono uppercase">{stat.label}</span>
            </div>
          ))}
        </div>

        <div className="flex flex-col md:flex-row gap-4 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              placeholder="Search courses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-gray-900/50 border border-gray-800 rounded-xl focus:border-cyan-500/50 focus:outline-none transition font-mono text-sm"
            />
          </div>
          
          <div className="flex gap-3">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="pl-10 pr-8 py-3 bg-gray-900/50 border border-gray-800 rounded-xl focus:border-cyan-500/50 focus:outline-none transition font-mono text-sm appearance-none cursor-pointer hover:border-gray-700"
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat === 'all' ? 'All Categories' : cat}</option>
                ))}
              </select>
            </div>
            
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="px-4 py-3 bg-gray-900/50 border border-gray-800 rounded-xl focus:border-cyan-500/50 focus:outline-none transition font-mono text-sm appearance-none cursor-pointer hover:border-gray-700"
            >
              {difficulties.map(diff => (
                <option key={diff} value={diff}>{diff === 'all' ? 'All Levels' : diff}</option>
              ))}
            </select>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {filteredCourses.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gray-900/30 border border-gray-800 rounded-2xl p-16 text-center"
            >
              <div className="w-24 h-24 mx-auto mb-6 bg-gray-800 rounded-full flex items-center justify-center">
                <BookOpen className="w-10 h-10 text-gray-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-400 mb-2">No courses found</h3>
              <p className="text-gray-600">Try adjusting your search or filters</p>
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCourses.map((course, idx) => {
                const diff = difficultyConfig[course.difficulty] || difficultyConfig.Beginner;
                const isHovered = hoveredCourse === course.id;
                
                return (
                  <motion.div
                    key={course.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    onMouseEnter={() => setHoveredCourse(course.id)}
                    onMouseLeave={() => setHoveredCourse(null)}
                    className="group relative"
                  >
                    <div className={`absolute -inset-0.5 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-2xl opacity-0 group-hover:opacity-20 blur transition duration-500 ${isHovered ? 'opacity-20' : ''}`}></div>
                    
                    <div className="relative bg-gray-900/80 border border-gray-800 rounded-2xl overflow-hidden hover:border-gray-700 transition-all duration-300">
                      <div className="h-48 bg-gradient-to-br from-gray-800 to-gray-900 relative overflow-hidden">
                        <div className="absolute inset-0 opacity-5" 
                             style={{ 
                               backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)',
                               backgroundSize: '40px 40px'
                             }}>
                        </div>
                        
                        <div className={`absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 transition-opacity duration-500 ${isHovered ? 'opacity-100' : 'opacity-0'}`}></div>
                        
                        <div className="absolute top-4 left-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium border ${diff.bg} ${diff.color} ${diff.border}`}>
                            {diff.icon} {course.difficulty}
                          </span>
                        </div>
                        
                        <div className="absolute bottom-4 left-4 right-4">
                          <div className="flex items-center gap-3 text-gray-400 text-xs">
                            <span className="flex items-center gap-1">
                              <Clock className="w-4 h-4" />
                              {course.duration_minutes} min
                            </span>
                          </div>
                        </div>
                        
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-10 group-hover:opacity-20 transition-opacity">
                          {categoryIcons[course.category] || <BookOpen className="w-24 h-24" />}
                        </div>
                      </div>
                      
                      <div className="p-6">
                        <h3 className="text-lg font-bold text-white group-hover:text-cyan-400 transition-colors line-clamp-1 mb-3">
                          {course.title}
                        </h3>
                        
                        <p className="text-sm text-gray-400 mb-4 line-clamp-2 leading-relaxed">
                          {course.description}
                        </p>
                        
                        <div className="flex items-center justify-between pt-4 border-t border-gray-800">
                          <div className="flex items-center gap-2 text-xs text-gray-500">
                            {categoryIcons[course.category] && (
                              <span className="text-gray-600">{categoryIcons[course.category]}</span>
                            )}
                            <span className="font-mono">{course.category || 'General'}</span>
                          </div>
                          
                          <Link href={`/university/${course.slug}`}>
                            <button className="flex items-center gap-2 text-sm font-medium text-cyan-400 hover:text-cyan-300 transition group/btn">
                              Start
                              <ChevronRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                            </button>
                          </Link>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </AnimatePresence>

        <div className="mt-16 text-center">
          <p className="text-gray-500 mb-4">Can't find what you're looking for?</p>
          <button className="px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-xl text-sm font-mono transition">
            Request New Course
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ProtectedUniversityPage() {
  return (
    <ProtectedRoute>
      <UniversityContent />
    </ProtectedRoute>
  );
}
