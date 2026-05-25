'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';
import { motion } from 'framer-motion';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  BookOpen, Clock, ChevronLeft, Download, 
  PlayCircle, Award, BarChart3, TrendingUp, 
  Shield, Brain, Zap, ExternalLink, FileText
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
  image_url?: string;
}

const difficultyConfig = {
  Beginner: { color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', icon: '🌱' },
  Intermediate: { color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20', icon: '🚀' },
  Advanced: { color: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20', icon: '⚡' },
};

const categoryIcons: Record<string, React.ReactNode> = {
  'Technical Analysis': <BarChart3 className="w-5 h-5" />,
  'Risk Management': <Shield className="w-5 h-5" />,
  'Psychology': <Brain className="w-5 h-5" />,
  'Strategy': <TrendingUp className="w-5 h-5" />,
  'Forex': <TrendingUp className="w-5 h-5" />,
  'Fundamentals': <BookOpen className="w-5 h-5" />,
  'Advanced': <Zap className="w-5 h-5" />,
};

function CourseDetailContent() {
  const params = useParams();
  const slug = params.slug as string;
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCourse();
  }, [slug]);

  const fetchCourse = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:8000/api/v1/university/courses/${slug}/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setCourse(response.data);
    } catch (error: any) {
      console.error('Error fetching course:', error);
      setError(error.message || 'Failed to load course');
    } finally {
      setLoading(false);
    }
  };

  // Check if this is the Babypips course
  const isBabypips = course?.slug === 'babypips-forex-school' || 
                     course?.title?.toLowerCase().includes('babypips');

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

  if (error || !course) {
    return (
      <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error || 'Course not found'}</p>
          <Link href="/university" className="text-cyan-400 hover:text-cyan-300">
            ← Back to Trading University
          </Link>
        </div>
      </div>
    );
  }

  const diff = difficultyConfig[course.difficulty] || difficultyConfig.Beginner;

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-[150px]"></div>
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-[150px]"></div>
      </div>

      <div className="relative max-w-4xl mx-auto px-6 py-12">
        {/* Back Button */}
        <Link 
          href="/university" 
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition mb-8 group"
        >
          <ChevronLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-mono">BACK TO UNIVERSITY</span>
        </Link>

        {/* Course Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-4">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${diff.bg} ${diff.color} ${diff.border}`}>
              {diff.icon} {course.difficulty}
            </span>
            <span className="text-sm text-gray-500 font-mono flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {course.duration_minutes} minutes
            </span>
          </div>

          <h1 className="text-4xl md:text-5xl font-black mb-4 bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
            {course.title}
          </h1>

          <div className="flex items-center gap-2 text-gray-500 mb-6">
            {categoryIcons[course.category] && (
              <span className="text-gray-600">{categoryIcons[course.category]}</span>
            )}
            <span className="font-mono text-sm">{course.category || 'General'}</span>
          </div>

          <p className="text-gray-300 text-lg leading-relaxed border-l-4 border-cyan-500/50 pl-6 py-2">
            {course.description}
          </p>
        </motion.div>

        {/* PDF Download Section - Only for Babypips course */}
        {isBabypips && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-12"
          >
            <div className="relative group">
              <div className="absolute -inset-0.5 bg-gradient-to-r from-amber-500 to-cyan-500 rounded-2xl opacity-20 group-hover:opacity-30 blur transition duration-500"></div>
              
              <div className="relative bg-gray-900/90 border border-gray-800 rounded-2xl p-8 backdrop-blur-sm">
                <div className="flex flex-col md:flex-row items-start gap-6">
                  {/* PDF Icon */}
                  <div className="w-20 h-20 bg-gradient-to-br from-amber-500/20 to-cyan-500/20 rounded-2xl flex items-center justify-center">
                    <FileText className="w-10 h-10 text-amber-400" />
                  </div>

                  {/* Content */}
                  <div className="flex-1">
                    <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
                      Course Materials
                      <span className="text-xs font-mono bg-amber-500/20 text-amber-400 px-2 py-1 rounded-full">
                        PDF
                      </span>
                    </h2>
                    
                    <p className="text-gray-400 mb-4">
                      Download the complete Babypips Forex School PDF guide. This comprehensive resource covers everything from basic concepts to advanced trading strategies, perfect for offline study.
                    </p>

                    <div className="flex flex-wrap gap-4">
                      {/* Download Button */}
                      <a 
                        href="http://localhost:8000/static/courses/babypips.pdf" 
                        download
                        className="inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white rounded-xl transition group/btn"
                      >
                        <Download className="w-5 h-5 group-hover/btn:-translate-y-1 transition-transform" />
                        <div>
                          <div className="font-bold">Download PDF</div>
                          <div className="text-xs text-amber-200">~2.8 MB</div>
                        </div>
                      </a>

                      {/* View in Browser Button */}
                      <a 
                        href="http://localhost:8000/static/courses/babypips.pdf" 
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-gray-800 hover:bg-gray-700 text-white rounded-xl transition group/btn"
                      >
                        <ExternalLink className="w-5 h-5" />
                        <span>View Online</span>
                      </a>
                    </div>
                  </div>

                  {/* File Info */}
                  <div className="text-right text-sm text-gray-500 font-mono whitespace-nowrap">
                    <div>2.8 MB</div>
                    <div>PDF</div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Course Modules Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-12"
        >
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <PlayCircle className="w-6 h-6 text-cyan-400" />
            Course Modules
          </h2>

          <div className="space-y-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div
                key={i}
                className="bg-gray-900/30 border border-gray-800 rounded-xl p-5 opacity-60 hover:opacity-80 transition cursor-not-allowed"
              >
                <div className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-lg bg-gray-800 flex items-center justify-center text-gray-600 font-mono">
                    {i}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-1">
                      <span className="text-white font-medium">Module {i}</span>
                      <span className="text-xs text-gray-600 bg-gray-800 px-2 py-1 rounded-full">
                        Coming Soon
                      </span>
                    </div>
                    <div className="h-2 w-32 bg-gray-800 rounded-full overflow-hidden">
                      <div className="h-full w-0 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full"></div>
                    </div>
                  </div>
                  <Clock className="w-4 h-4 text-gray-600" />
                </div>
              </div>
            ))}
          </div>

          <p className="text-center text-gray-500 mt-6 text-sm font-mono">
            Interactive lessons and quizzes are under development
          </p>
        </motion.div>

        {/* Related Courses Suggestion */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="text-center"
        >
          <Link
            href="/university"
            className="inline-flex items-center gap-2 px-6 py-3 bg-gray-800 hover:bg-gray-700 rounded-xl transition font-mono text-sm group"
          >
            <BookOpen className="w-4 h-4" />
            Browse More Courses
            <ChevronLeft className="w-4 h-4 rotate-180 group-hover:translate-x-1 transition-transform" />
          </Link>
        </motion.div>
      </div>
    </div>
  );
}

export default function ProtectedCourseDetailPage() {
  return (
    <ProtectedRoute>
      <CourseDetailContent />
    </ProtectedRoute>
  );
}
