'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import ProtectedRoute from '@/components/ProtectedRoute';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, Edit, Trash2, Upload, Link2, FileText, 
  X, Check, Image as ImageIcon, Video, File, 
  BookOpen, ChevronRight, Download, Eye,
  Save, RefreshCw, AlertCircle, CheckCircle
} from 'lucide-react';

interface Course {
  id: string;
  title: string;
  description: string;
  category: string;
  difficulty: string;
  duration_minutes: number;
  pdf_filename?: string;
  image_url?: string;
  slug: string;
  status: string;
  created_at: string;
}

interface CourseFormData {
  title: string;
  description: string;
  category: string;
  difficulty: string;
  duration_minutes: number;
  pdf_filename: string;
  image_url: string;
  video_url?: string;
}

function UniversityAdminDashboard() {
  const router = useRouter();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);
  const [formData, setFormData] = useState<CourseFormData>({
    title: '',
    description: '',
    category: '',
    difficulty: 'Beginner',
    duration_minutes: 60,
    pdf_filename: '',
    image_url: '',
    video_url: ''
  });
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/v1/university/courses/', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCourses(response.data.courses || []);
    } catch (error) {
      console.error('Error fetching courses:', error);
      setMessage({ type: 'error', text: 'Failed to load courses' });
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>, type: 'pdf' | 'image') => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (type === 'pdf' && file.type !== 'application/pdf') {
      setMessage({ type: 'error', text: 'Please upload a PDF file' });
      return;
    }
    if (type === 'image' && !file.type.startsWith('image/')) {
      setMessage({ type: 'error', text: 'Please upload an image file' });
      return;
    }

    setUploading(true);
    const uploadFormData = new FormData();
    uploadFormData.append('file', file);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:8000/api/v1/upload/', uploadFormData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      
      if (type === 'pdf') {
        setFormData({ ...formData, pdf_filename: response.data.filename });
      } else {
        setFormData({ ...formData, image_url: response.data.url });
      }
      setMessage({ type: 'success', text: `${type.toUpperCase()} uploaded successfully!` });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      setMessage({ type: 'error', text: `Failed to upload ${type}` });
    } finally {
      setUploading(false);
    }
  };

  const createCourse = async () => {
    if (!formData.title || !formData.description) {
      setMessage({ type: 'error', text: 'Title and description are required' });
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:8000/api/v1/university/courses/', formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setCourses([response.data, ...courses]);
      setShowCreateModal(false);
      resetForm();
      setMessage({ type: 'success', text: 'Course created successfully!' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error creating course:', error);
      setMessage({ type: 'error', text: 'Failed to create course' });
    }
  };

  const updateCourse = async () => {
    if (!editingCourse) return;

    try {
      const token = localStorage.getItem('token');
      const response = await axios.put(`http://localhost:8000/api/v1/university/courses/${editingCourse.id}`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setCourses(courses.map(c => c.id === editingCourse.id ? response.data : c));
      setEditingCourse(null);
      resetForm();
      setMessage({ type: 'success', text: 'Course updated successfully!' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error updating course:', error);
      setMessage({ type: 'error', text: 'Failed to update course' });
    }
  };

  const deleteCourse = async (id: string) => {
    if (!confirm('Are you sure you want to delete this course?')) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://localhost:8000/api/v1/university/courses/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setCourses(courses.filter(c => c.id !== id));
      setMessage({ type: 'success', text: 'Course deleted successfully!' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error deleting course:', error);
      setMessage({ type: 'error', text: 'Failed to delete course' });
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      category: '',
      difficulty: 'Beginner',
      duration_minutes: 60,
      pdf_filename: '',
      image_url: '',
      video_url: ''
    });
  };

  const editCourse = (course: Course) => {
    setEditingCourse(course);
    setFormData({
      title: course.title,
      description: course.description,
      category: course.category || '',
      difficulty: course.difficulty,
      duration_minutes: course.duration_minutes,
      pdf_filename: course.pdf_filename || '',
      image_url: course.image_url || '',
      video_url: ''
    });
  };

  const categories = ['all', ...new Set(courses.map(c => c.category).filter(Boolean))];
  const difficulties = ['Beginner', 'Intermediate', 'Advanced', 'All Levels'];

  const filteredCourses = courses.filter(course => {
    const categoryMatch = selectedCategory === 'all' || course.category === selectedCategory;
    const searchMatch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                        course.description.toLowerCase().includes(searchQuery.toLowerCase());
    return categoryMatch && searchMatch;
  });

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
      {/* Background Effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-[150px]"></div>
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-purple-500/5 rounded-full blur-[150px]"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
              <span className="text-cyan-400 text-xs font-mono uppercase tracking-widest">Admin Panel</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-black mb-2">
              <span className="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                Course Management
              </span>
            </h1>
            <p className="text-gray-400 text-lg">Upload and manage university courses</p>
          </div>
          
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-lg text-white font-medium hover:from-cyan-600 hover:to-purple-700 transition flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            New Course
          </button>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg border ${
            message.type === 'success' 
              ? 'bg-green-500/10 border-green-500/30 text-green-400' 
              : 'bg-red-500/10 border-red-500/30 text-red-400'
          }`}>
            {message.type === 'success' ? <CheckCircle className="w-5 h-5 inline mr-2" /> : <AlertCircle className="w-5 h-5 inline mr-2" />}
            {message.text}
          </div>
        )}

        {/* Search and Filter */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Search courses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-3 bg-gray-900/50 border border-gray-800 rounded-lg text-white placeholder-gray-500 focus:border-cyan-500 transition"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-3 bg-gray-900/50 border border-gray-800 rounded-lg text-white focus:border-cyan-500 transition"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat === 'all' ? 'All Categories' : cat}</option>
            ))}
          </select>
        </div>

        {/* Course Grid */}
        {filteredCourses.length === 0 ? (
          <div className="bg-gray-900/30 border border-gray-800 rounded-2xl p-16 text-center">
            <BookOpen className="w-16 h-16 text-gray-700 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-400 mb-2">No courses found</h3>
            <p className="text-gray-600">Click "New Course" to create your first course</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.map((course) => (
              <motion.div
                key={course.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gray-900/50 border border-gray-800 rounded-2xl overflow-hidden hover:border-cyan-500/30 transition group"
              >
                {/* Course Header */}
                <div className="h-32 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 relative overflow-hidden">
                  {course.image_url ? (
                    <img src={course.image_url} alt={course.title} className="w-full h-full object-cover" />
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center">
                      <BookOpen className="w-12 h-12 text-gray-600" />
                    </div>
                  )}
                  <div className="absolute top-3 right-3 flex gap-2">
                    <button
                      onClick={() => editCourse(course)}
                      className="p-2 bg-gray-900/80 rounded-lg hover:bg-cyan-600 transition"
                      title="Edit"
                    >
                      <Edit className="w-4 h-4 text-gray-400 hover:text-white" />
                    </button>
                    <button
                      onClick={() => deleteCourse(course.id)}
                      className="p-2 bg-gray-900/80 rounded-lg hover:bg-red-600 transition"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4 text-gray-400 hover:text-white" />
                    </button>
                  </div>
                  <div className="absolute bottom-3 left-3">
                    <span className="px-2 py-1 bg-black/50 rounded text-xs">
                      {course.difficulty}
                    </span>
                  </div>
                </div>

                {/* Course Content */}
                <div className="p-5">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-bold text-white group-hover:text-cyan-400 transition">
                      {course.title}
                    </h3>
                    <span className="text-xs text-gray-500 font-mono">{course.duration_minutes} min</span>
                  </div>
                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">{course.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {course.pdf_filename && (
                        <span className="text-xs px-2 py-1 bg-amber-500/20 text-amber-400 rounded-full flex items-center gap-1">
                          <FileText className="w-3 h-3" />
                          PDF
                        </span>
                      )}
                      <span className="text-xs text-gray-600">{course.category || 'Uncategorized'}</span>
                    </div>
                    <button
                      onClick={() => window.open(`/university/${course.slug}`, '_blank')}
                      className="text-cyan-400 hover:text-cyan-300 text-sm flex items-center gap-1"
                    >
                      View
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Create/Edit Modal */}
        <AnimatePresence>
          {(showCreateModal || editingCourse) && (
            <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-gray-900 border border-gray-800 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
              >
                <div className="p-6 border-b border-gray-800 flex justify-between items-center sticky top-0 bg-gray-900">
                  <h2 className="text-2xl font-bold text-white">
                    {editingCourse ? 'Edit Course' : 'Create New Course'}
                  </h2>
                  <button
                    onClick={() => {
                      setShowCreateModal(false);
                      setEditingCourse(null);
                      resetForm();
                    }}
                    className="text-gray-500 hover:text-white transition"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="p-6 space-y-6">
                  {/* Title */}
                  <div>
                    <label className="block text-sm font-mono text-cyan-400 mb-2">Course Title *</label>
                    <input
                      type="text"
                      name="title"
                      value={formData.title}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 transition"
                      placeholder="e.g., Advanced Forex Trading"
                    />
                  </div>

                  {/* Description */}
                  <div>
                    <label className="block text-sm font-mono text-cyan-400 mb-2">Description *</label>
                    <textarea
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      rows={4}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 transition"
                      placeholder="Describe what students will learn..."
                    />
                  </div>

                  {/* Category and Difficulty */}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-mono text-cyan-400 mb-2">Category</label>
                      <input
                        type="text"
                        name="category"
                        value={formData.category}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 transition"
                        placeholder="e.g., Forex, Technical Analysis"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-mono text-cyan-400 mb-2">Difficulty</label>
                      <select
                        name="difficulty"
                        value={formData.difficulty}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 transition"
                      >
                        {difficulties.map(d => (
                          <option key={d} value={d}>{d}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Duration */}
                  <div>
                    <label className="block text-sm font-mono text-cyan-400 mb-2">Duration (minutes)</label>
                    <input
                      type="number"
                      name="duration_minutes"
                      value={formData.duration_minutes}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-cyan-500 transition"
                      placeholder="60"
                    />
                  </div>

                  {/* PDF Upload */}
                  <div>
                    <label className="block text-sm font-mono text-amber-400 mb-2">PDF Material</label>
                    <div className="flex items-center gap-4">
                      <label className="flex-1 flex items-center justify-between px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg cursor-pointer hover:border-amber-500 transition">
                        <span className="text-gray-400">Upload PDF</span>
                        <Upload className="w-5 h-5 text-amber-400" />
                        <input
                          type="file"
                          accept=".pdf"
                          onChange={(e) => handleFileUpload(e, 'pdf')}
                          className="hidden"
                          disabled={uploading}
                        />
                      </label>
                      {formData.pdf_filename && (
                        <span className="text-sm text-amber-400 flex items-center gap-1">
                          <FileText className="w-4 h-4" />
                          {formData.pdf_filename}
                        </span>
                      )}
                    </div>
                    {uploading && <p className="text-xs text-gray-500 mt-1">Uploading...</p>}
                  </div>

                  {/* Image Upload */}
                  <div>
                    <label className="block text-sm font-mono text-purple-400 mb-2">Course Image</label>
                    <div className="flex items-center gap-4">
                      <label className="flex-1 flex items-center justify-between px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg cursor-pointer hover:border-purple-500 transition">
                        <span className="text-gray-400">Upload Image</span>
                        <ImageIcon className="w-5 h-5 text-purple-400" />
                        <input
                          type="file"
                          accept="image/*"
                          onChange={(e) => handleFileUpload(e, 'image')}
                          className="hidden"
                          disabled={uploading}
                        />
                      </label>
                      {formData.image_url && (
                        <span className="text-sm text-purple-400 flex items-center gap-1">
                          <Check className="w-4 h-4" />
                          Uploaded
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Video Link */}
                  <div>
                    <label className="block text-sm font-mono text-blue-400 mb-2">Video URL (Optional)</label>
                    <input
                      type="url"
                      name="video_url"
                      value={formData.video_url}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-blue-500 transition"
                      placeholder="https://www.youtube.com/watch?v=..."
                    />
                  </div>
                </div>

                <div className="p-6 border-t border-gray-800 flex justify-end gap-3">
                  <button
                    onClick={() => {
                      setShowCreateModal(false);
                      setEditingCourse(null);
                      resetForm();
                    }}
                    className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-white transition"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={editingCourse ? updateCourse : createCourse}
                    className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 rounded-lg text-white transition flex items-center gap-2"
                  >
                    <Save className="w-4 h-4" />
                    {editingCourse ? 'Update Course' : 'Create Course'}
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

export default function ProtectedUniversityAdminPage() {
  return (
    <ProtectedRoute>
      <UniversityAdminDashboard />
    </ProtectedRoute>
  );
}
