'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  BookOpen, Clock, CheckCircle, Circle, Award,
  TrendingUp, BarChart3, Target, Calendar, Filter,
  ChevronRight, PlayCircle, Zap, Brain, Shield,
  Download, X, Trophy, Star, Sparkles
} from 'lucide-react';

interface Course {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  duration_minutes: number;
  pdf_filename?: string;
}

interface Progress {
  course_id: string;
  course_title: string;
  completed: boolean;
  completed_at?: string;
  time_spent_minutes: number;
  average_score: number;
  modules_completed: string[];
  last_accessed?: string;
}

interface Cohort {
  id: string;
  name: string;
  progress_percentage: number;
  completed_courses: number;
  total_courses: number;
  rank?: number;
}

interface Certificate {
  id: string;
  certificate_number: string;
  course_title: string;
  issue_date: string;
  grade?: string;
  score?: number;
  verification_hash: string;
}

function ProgressPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [progress, setProgress] = useState<Progress[]>([]);
  const [cohorts, setCohorts] = useState<Cohort[]>([]);
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'courses' | 'cohorts' | 'certificates'>('courses');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [showCertificateModal, setShowCertificateModal] = useState(false);
  const [selectedCertificate, setSelectedCertificate] = useState<Certificate | null>(null);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      // Fetch courses
      const coursesRes = await axios.get('http://localhost:8000/api/v1/university/courses/');
      setCourses(coursesRes.data.courses || []);

      // Fetch progress for each course (this would be a real endpoint in production)
      // For now, we'll simulate progress data
      const mockProgress: Progress[] = (coursesRes.data.courses || []).map((course: Course, index: number) => ({
        course_id: course.id,
        course_title: course.title,
        completed: index < 3,
        completed_at: index < 3 ? new Date().toISOString() : undefined,
        time_spent_minutes: Math.floor(Math.random() * 300) + 60,
        average_score: Math.floor(Math.random() * 30) + 70,
        modules_completed: index < 3 ? ['Module 1', 'Module 2', 'Module 3'].slice(0, Math.floor(Math.random() * 3) + 1) : [],
        last_accessed: new Date().toISOString()
      }));
      setProgress(mockProgress);

      // Fetch user's cohorts
      const cohortsRes = await axios.get('http://localhost:8000/api/v1/university/cohorts/my');
      const mockCohortProgress = (cohortsRes.data || []).map((cohort: any) => ({
        id: cohort.id,
        name: cohort.name,
        progress_percentage: Math.floor(Math.random() * 100),
        completed_courses: Math.floor(Math.random() * 5),
        total_courses: 8,
        rank: Math.floor(Math.random() * 20) + 1
      }));
      setCohorts(mockCohortProgress);

      // Mock certificates
      const mockCertificates: Certificate[] = [
        {
          id: '1',
          certificate_number: 'JRNX-20260311-001',
          course_title: 'Babypips Forex School',
          issue_date: new Date().toISOString(),
          grade: 'Distinction',
          score: 94,
          verification_hash: 'ABC123DEF456'
        },
        {
          id: '2',
          certificate_number: 'JRNX-20260310-002',
          course_title: 'Advanced Technical Analysis',
          issue_date: new Date(Date.now() - 86400000).toISOString(),
          grade: 'Merit',
          score: 87,
          verification_hash: 'GHI789JKL012'
        }
      ];
      setCertificates(mockCertificates);

    } catch (error) {
      console.error('Error fetching progress data:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = ['all', ...new Set(courses.map(c => c.category).filter(Boolean))];
  const difficulties = ['all', 'Beginner', 'Intermediate', 'Advanced'];

  const filteredCourses = courses.filter(course => {
    const progressItem = progress.find(p => p.course_id === course.id);
    if (activeTab === 'courses') return true;
    if (activeTab === 'cohorts') return false;
    return false;
  });

  const getDifficultyColor = (difficulty: string) => {
    switch(difficulty?.toLowerCase()) {
      case 'beginner': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'intermediate': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      case 'advanced': return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
      default: return 'text-gray-400 bg-gray-500/10 border-gray-500/20';
    }
  };

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getProgressForCourse = (courseId: string) => {
    return progress.find(p => p.course_id === courseId);
  };

  const calculateOverallProgress = () => {
    if (courses.length === 0) return 0;
    const completed = progress.filter(p => p.completed).length;
    return Math.round((completed / courses.length) * 100);
  };

  const calculateTotalTimeSpent = () => {
    return progress.reduce((acc, p) => acc + p.time_spent_minutes, 0);
  };

  const calculateAverageScore = () => {
    const scores = progress.filter(p => p.average_score > 0).map(p => p.average_score);
    if (scores.length === 0) return 0;
    return Math.round(scores.reduce((acc, s) => acc + s, 0) / scores.length);
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

  const overallProgress = calculateOverallProgress();
  const totalTimeSpent = calculateTotalTimeSpent();
  const averageScore = calculateAverageScore();

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-[150px]"></div>
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-[150px]"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
            <span className="text-cyan-400 text-xs font-mono uppercase tracking-widest">Track Your Journey</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-black mb-4">
            <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
              Learning Progress
            </span>
          </h1>
          <p className="text-gray-400 text-lg">Monitor your course completion and achievements</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-cyan-500/10">
                <Target className="w-5 h-5 text-cyan-400" />
              </div>
              <span className="text-2xl font-bold">{overallProgress}%</span>
            </div>
            <span className="text-xs text-gray-500 font-mono uppercase">Overall Progress</span>
            <div className="mt-3 h-2 bg-gray-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${overallProgress}%` }}
              ></div>
            </div>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-green-500/10">
                <CheckCircle className="w-5 h-5 text-green-400" />
              </div>
              <span className="text-2xl font-bold">{progress.filter(p => p.completed).length}/{courses.length}</span>
            </div>
            <span className="text-xs text-gray-500 font-mono uppercase">Courses Completed</span>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-amber-500/10">
                <Clock className="w-5 h-5 text-amber-400" />
              </div>
              <span className="text-2xl font-bold">{formatTime(totalTimeSpent)}</span>
            </div>
            <span className="text-xs text-gray-500 font-mono uppercase">Total Time Spent</span>
          </div>

          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-purple-500/10">
                <Award className="w-5 h-5 text-purple-400" />
              </div>
              <span className="text-2xl font-bold">{averageScore}%</span>
            </div>
            <span className="text-xs text-gray-500 font-mono uppercase">Average Quiz Score</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-800">
          <button
            onClick={() => setActiveTab('courses')}
            className={`pb-4 px-1 font-medium transition relative ${
              activeTab === 'courses'
                ? 'text-cyan-400'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Course Progress
            {activeTab === 'courses' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"></div>
            )}
          </button>
          <button
            onClick={() => setActiveTab('cohorts')}
            className={`pb-4 px-1 font-medium transition relative ${
              activeTab === 'cohorts'
                ? 'text-cyan-400'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Cohort Rankings
            {activeTab === 'cohorts' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"></div>
            )}
          </button>
          <button
            onClick={() => setActiveTab('certificates')}
            className={`pb-4 px-1 font-medium transition relative ${
              activeTab === 'certificates'
                ? 'text-cyan-400'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Certificates
            {activeTab === 'certificates' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-400"></div>
            )}
          </button>
        </div>

        {/* Filters (for courses tab) */}
        {activeTab === 'courses' && (
          <div className="flex flex-wrap gap-3 mb-6">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="pl-10 pr-8 py-2 bg-gray-900/50 border border-gray-800 rounded-lg focus:border-cyan-500/50 focus:outline-none transition font-mono text-sm appearance-none cursor-pointer hover:border-gray-700"
              >
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat === 'all' ? 'All Categories' : cat}</option>
                ))}
              </select>
            </div>
            
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="px-4 py-2 bg-gray-900/50 border border-gray-800 rounded-lg focus:border-cyan-500/50 focus:outline-none transition font-mono text-sm appearance-none cursor-pointer hover:border-gray-700"
            >
              {difficulties.map(diff => (
                <option key={diff} value={diff}>{diff === 'all' ? 'All Levels' : diff}</option>
              ))}
            </select>
          </div>
        )}

        {/* Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'courses' && (
            <motion.div
              key="courses"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-4"
            >
              {courses.map((course) => {
                const progressItem = getProgressForCourse(course.id);
                const isCompleted = progressItem?.completed;
                const progressPercentage = isCompleted ? 100 : progressItem ? 
                  (progressItem.modules_completed.length / 6) * 100 : 0;

                return (
                  <div
                    key={course.id}
                    className="bg-gray-900/30 border border-gray-800 rounded-xl p-6 hover:border-cyan-500/30 transition group"
                  >
                    <div className="flex flex-col md:flex-row items-start gap-6">
                      {/* Course Icon */}
                      <div className={`w-16 h-16 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center flex-shrink-0
                        ${isCompleted ? 'ring-2 ring-green-500/50' : ''}`}>
                        {isCompleted ? (
                          <CheckCircle className="w-8 h-8 text-green-400" />
                        ) : (
                          <BookOpen className="w-8 h-8 text-cyan-400" />
                        )}
                      </div>

                      {/* Course Info */}
                      <div className="flex-1">
                        <div className="flex flex-wrap items-start justify-between gap-4 mb-2">
                          <div>
                            <h3 className="text-xl font-bold text-white group-hover:text-cyan-400 transition">
                              {course.title}
                            </h3>
                            <div className="flex items-center gap-3 mt-1">
                              <span className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(course.difficulty)}`}>
                                {course.difficulty || 'Beginner'}
                              </span>
                              <span className="text-xs text-gray-500 font-mono">{course.category || 'General'}</span>
                              {course.pdf_filename && (
                                <span className="text-xs px-2 py-1 bg-amber-500/20 text-amber-400 rounded-full border border-amber-500/30">
                                  📄 PDF
                                </span>
                              )}
                            </div>
                          </div>

                          {isCompleted && (
                            <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-mono border border-green-500/30">
                              Completed
                            </span>
                          )}
                        </div>

                        <p className="text-gray-400 text-sm mb-4 line-clamp-2">{course.description}</p>

                        {/* Progress Bar */}
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-500 font-mono">Progress</span>
                            <span className="text-cyan-400 font-mono">{Math.round(progressPercentage)}%</span>
                          </div>
                          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div 
                              className={`h-full rounded-full transition-all duration-500 ${
                                isCompleted 
                                  ? 'bg-gradient-to-r from-green-500 to-emerald-500' 
                                  : 'bg-gradient-to-r from-cyan-500 to-purple-500'
                              }`}
                              style={{ width: `${progressPercentage}%` }}
                            ></div>
                          </div>
                        </div>

                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-4 mt-4">
                          <div>
                            <div className="text-xs text-gray-500 font-mono">Time Spent</div>
                            <div className="text-white font-bold">
                              {progressItem ? formatTime(progressItem.time_spent_minutes) : '0h 0m'}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500 font-mono">Quiz Score</div>
                            <div className="text-white font-bold">
                              {progressItem?.average_score ? `${progressItem.average_score}%` : 'N/A'}
                            </div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500 font-mono">Last Access</div>
                            <div className="text-white font-bold text-sm">
                              {progressItem?.last_accessed ? formatDate(progressItem.last_accessed) : 'Never'}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Action Button */}
                      <Link
                        href={`/university/${course.slug}`}
                        className="flex items-center gap-2 px-4 py-2 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 rounded-lg transition group/btn flex-shrink-0"
                      >
                        <span className="text-sm font-mono">Continue</span>
                        <ChevronRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </motion.div>
          )}

          {activeTab === 'cohorts' && (
            <motion.div
              key="cohorts"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 gap-6"
            >
              {cohorts.map((cohort) => (
                <div
                  key={cohort.id}
                  className="bg-gray-900/30 border border-gray-800 rounded-xl p-6 hover:border-cyan-500/30 transition group"
                >
                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20 flex items-center justify-center">
                        <Trophy className="w-6 h-6 text-amber-400" />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-white">{cohort.name}</h3>
                        <div className="flex items-center gap-3 mt-1">
                          <span className="text-xs text-gray-500 font-mono">Rank #{cohort.rank}</span>
                          <span className="text-xs text-gray-500 font-mono">{cohort.completed_courses}/{cohort.total_courses} courses</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-6 flex-1 max-w-md">
                      <div className="flex-1">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-gray-500 font-mono">Progress</span>
                          <span className="text-cyan-400 font-mono">{cohort.progress_percentage}%</span>
                        </div>
                        <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full"
                            style={{ width: `${cohort.progress_percentage}%` }}
                          ></div>
                        </div>
                      </div>
                      <Link
                        href={`/cohorts/${cohort.id}`}
                        className="text-cyan-400 hover:text-cyan-300 text-sm font-mono flex items-center gap-1"
                      >
                        View Details
                        <ChevronRight className="w-4 h-4" />
                      </Link>
                    </div>
                  </div>
                </div>
              ))}

              {cohorts.length === 0 && (
                <div className="bg-gray-900/30 border border-gray-800 rounded-2xl p-16 text-center">
                  <Users className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-gray-400 mb-2">No cohorts joined</h3>
                  <p className="text-gray-600 mb-4">Join a cohort to track your progress against others</p>
                  <Link
                    href="/cohorts"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg transition"
                  >
                    Browse Cohorts
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'certificates' && (
            <motion.div
              key="certificates"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
            >
              {certificates.map((cert) => (
                <div
                  key={cert.id}
                  className="bg-gray-900/30 border border-gray-800 rounded-xl overflow-hidden hover:border-cyan-500/30 transition group cursor-pointer"
                  onClick={() => {
                    setSelectedCertificate(cert);
                    setShowCertificateModal(true);
                  }}
                >
                  <div className="h-32 bg-gradient-to-r from-amber-500/20 to-purple-500/20 relative overflow-hidden">
                    <div className="absolute inset-0 opacity-10">
                      <div className="absolute inset-0 bg-[url('/grid.svg')] bg-repeat opacity-20"></div>
                    </div>
                    <div className="absolute top-4 right-4">
                      <Award className="w-12 h-12 text-amber-400/30" />
                    </div>
                    <div className="absolute bottom-4 left-4">
                      <span className="text-xs font-mono text-amber-400 bg-amber-500/20 px-2 py-1 rounded-full border border-amber-500/30">
                        {cert.grade}
                      </span>
                    </div>
                  </div>
                  
                  <div className="p-6">
                    <h3 className="text-lg font-bold text-white mb-2">{cert.course_title}</h3>
                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500 font-mono">Certificate #</span>
                        <span className="text-white font-mono text-xs">{cert.certificate_number}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500 font-mono">Issue Date</span>
                        <span className="text-white">{formatDate(cert.issue_date)}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-500 font-mono">Score</span>
                        <span className="text-cyan-400 font-bold">{cert.score}%</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between pt-4 border-t border-gray-800">
                      <div className="flex items-center gap-1">
                        <Sparkles className="w-4 h-4 text-amber-400" />
                        <span className="text-xs text-gray-500">Click to view</span>
                      </div>
                      <button className="text-cyan-400 hover:text-cyan-300">
                        <Download className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}

              {certificates.length === 0 && (
                <div className="col-span-2 bg-gray-900/30 border border-gray-800 rounded-2xl p-16 text-center">
                  <Award className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-gray-400 mb-2">No certificates yet</h3>
                  <p className="text-gray-600">Complete courses to earn certificates</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Certificate Modal */}
        <AnimatePresence>
          {showCertificateModal && selectedCertificate && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-gray-900 border border-gray-800 rounded-2xl max-w-2xl w-full overflow-hidden"
              >
                <div className="p-6 border-b border-gray-800 flex justify-between items-center">
                  <h2 className="text-2xl font-bold text-white">Certificate of Achievement</h2>
                  <button
                    onClick={() => setShowCertificateModal(false)}
                    className="text-gray-500 hover:text-white transition"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="p-8">
                  <div className="bg-gradient-to-br from-amber-900/30 to-purple-900/30 border border-amber-500/30 rounded-xl p-8 text-center">
                    <Award className="w-20 h-20 text-amber-400 mx-auto mb-4" />
                    
                    <h3 className="text-2xl font-bold text-white mb-2">Journex University</h3>
                    <p className="text-gray-400 mb-6">This certificate is awarded to</p>
                    
                    <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-purple-400 mb-4">
                      Test User
                    </div>
                    
                    <p className="text-gray-300 mb-2">for successfully completing</p>
                    <p className="text-xl font-bold text-white mb-6">{selectedCertificate.course_title}</p>
                    
                    <div className="grid grid-cols-2 gap-4 mb-6">
                      <div>
                        <div className="text-xs text-gray-500 font-mono">Grade</div>
                        <div className="text-white font-bold">{selectedCertificate.grade}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 font-mono">Score</div>
                        <div className="text-white font-bold">{selectedCertificate.score}%</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 font-mono">Issue Date</div>
                        <div className="text-white font-bold">{formatDate(selectedCertificate.issue_date)}</div>
                      </div>
                      <div>
                        <div className="text-xs text-gray-500 font-mono">Certificate #</div>
                        <div className="text-white font-mono text-sm">{selectedCertificate.certificate_number}</div>
                      </div>
                    </div>
                    
                    <div className="border-t border-amber-500/20 pt-6">
                      <p className="text-xs text-gray-500 font-mono mb-2">Verification Hash</p>
                      <p className="text-sm font-mono text-cyan-400 bg-black/30 p-2 rounded-lg">
                        {selectedCertificate.verification_hash}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="p-6 border-t border-gray-800 flex justify-end gap-3">
                  <button
                    onClick={() => setShowCertificateModal(false)}
                    className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white transition"
                  >
                    Close
                  </button>
                  <button className="px-6 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg text-white transition flex items-center gap-2">
                    <Download className="w-4 h-4" />
                    Download PDF
                  </button>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default function ProtectedProgressPage() {
  return (
    <ProtectedRoute>
      <ProgressPage />
    </ProtectedRoute>
  );
}
