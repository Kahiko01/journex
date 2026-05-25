'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

interface ChecklistItem {
  id: string;
  text: string;
  required: boolean;
  order: number;
}

interface Checklist {
  id: string;
  name: string;
  description: string;
  type: string;
  items: ChecklistItem[];
  created_at: string;
}

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  items: ChecklistItem[];
}

export default function ChecklistPage() {
  const [checklists, setChecklists] = useState<Checklist[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'my-lists' | 'templates' | 'analytics'>('my-lists');
  const [selectedChecklist, setSelectedChecklist] = useState<Checklist | null>(null);
  const [completionStatus, setCompletionStatus] = useState<Record<string, boolean>>({});
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newChecklist, setNewChecklist] = useState({
    name: '',
    description: '',
    type: 'pre-trade',
    items: [{ text: '', required: true }]
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch user checklists
      const checklistsRes = await axios.get('http://localhost:8000/api/v1/checklist/user');
      setChecklists(checklistsRes.data.checklists);

      // Fetch templates
      const templatesRes = await axios.get('http://localhost:8000/api/v1/checklist/templates');
      setTemplates(templatesRes.data.templates);
    } catch (error) {
      console.error('Error fetching checklist data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteChecklist = async (checklistId: string) => {
    try {
      const response = await axios.post('http://localhost:8000/api/v1/checklist/complete', {
        checklist_id: checklistId,
        completion_data: completionStatus
      });
      
      alert('Checklist completed!');
      setSelectedChecklist(null);
      setCompletionStatus({});
      fetchData(); // Refresh
    } catch (error) {
      console.error('Error completing checklist:', error);
    }
  };

  const handleCreateFromTemplate = async (templateId: string) => {
    try {
      await axios.post(`http://localhost:8000/api/v1/checklist/templates/${templateId}/create`);
      fetchData();
      setActiveTab('my-lists');
    } catch (error) {
      console.error('Error creating from template:', error);
    }
  };

  const handleCreateCustom = async () => {
    try {
      // Filter out empty items
      const items = newChecklist.items
        .filter(item => item.text.trim() !== '')
        .map((item, index) => ({
          ...item,
          id: Math.random().toString(36).substring(7),
          order: index
        }));

      await axios.post('http://localhost:8000/api/v1/checklist/user', {
        name: newChecklist.name,
        description: newChecklist.description,
        checklist_type: newChecklist.type,
        items
      });

      setShowCreateModal(false);
      setNewChecklist({
        name: '',
        description: '',
        type: 'pre-trade',
        items: [{ text: '', required: true }]
      });
      fetchData();
    } catch (error) {
      console.error('Error creating checklist:', error);
    }
  };

  const addItemField = () => {
    setNewChecklist({
      ...newChecklist,
      items: [...newChecklist.items, { text: '', required: true }]
    });
  };

  const updateItem = (index: number, field: string, value: any) => {
    const updatedItems = [...newChecklist.items];
    updatedItems[index] = { ...updatedItems[index], [field]: value };
    setNewChecklist({ ...newChecklist, items: updatedItems });
  };

  const removeItem = (index: number) => {
    const updatedItems = newChecklist.items.filter((_, i) => i !== index);
    setNewChecklist({ ...newChecklist, items: updatedItems });
  };

  const getTypeColor = (type: string) => {
    switch(type) {
      case 'pre-trade': return 'bg-blue-600';
      case 'post-trade': return 'bg-purple-600';
      case 'daily': return 'bg-green-600';
      case 'weekly': return 'bg-orange-600';
      default: return 'bg-gray-600';
    }
  };

  const getTypeLabel = (type: string) => {
    switch(type) {
      case 'pre-trade': return 'Pre-Trade';
      case 'post-trade': return 'Post-Trade';
      case 'daily': return 'Daily';
      case 'weekly': return 'Weekly';
      default: return type;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading checklists...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-white">Trading Checklists</h1>
          <div className="flex gap-4">
            <button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              + New Checklist
            </button>
            <Link href="/dashboard" className="bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-600">
              Dashboard
            </Link>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-700">
          <button
            onClick={() => setActiveTab('my-lists')}
            className={`px-4 py-2 ${activeTab === 'my-lists' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400'}`}
          >
            My Checklists
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`px-4 py-2 ${activeTab === 'templates' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400'}`}
          >
            Templates
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`px-4 py-2 ${activeTab === 'analytics' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400'}`}
          >
            Analytics
          </button>
        </div>

        {/* My Checklists Tab */}
        {activeTab === 'my-lists' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {checklists.length === 0 ? (
              <div className="col-span-3 text-center py-12">
                <p className="text-gray-400 text-lg mb-4">No checklists yet</p>
                <button
                  onClick={() => setActiveTab('templates')}
                  className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
                >
                  Browse Templates
                </button>
              </div>
            ) : (
              checklists.map(checklist => (
                <div key={checklist.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <span className={`text-xs px-2 py-1 rounded ${getTypeColor(checklist.type)} text-white`}>
                        {getTypeLabel(checklist.type)}
                      </span>
                      <h3 className="text-xl font-semibold text-white mt-2">{checklist.name}</h3>
                    </div>
                  </div>
                  <p className="text-gray-400 text-sm mb-4">{checklist.description}</p>
                  <div className="mb-4">
                    <p className="text-gray-300 text-sm mb-2">{checklist.items.length} items</p>
                  </div>
                  <button
                    onClick={() => setSelectedChecklist(checklist)}
                    className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
                  >
                    Use Checklist
                  </button>
                </div>
              ))
            )}
          </div>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map(template => (
              <div key={template.id} className="bg-gray-800 rounded-lg border border-gray-700 p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <span className={`text-xs px-2 py-1 rounded ${getTypeColor(template.category)} text-white`}>
                      {getTypeLabel(template.category)}
                    </span>
                    <h3 className="text-xl font-semibold text-white mt-2">{template.name}</h3>
                  </div>
                  <span className="bg-blue-600 text-xs text-white px-2 py-1 rounded">Default</span>
                </div>
                <p className="text-gray-400 text-sm mb-4">{template.description}</p>
                <div className="mb-4">
                  <p className="text-gray-300 text-sm mb-2">Includes:</p>
                  <ul className="text-gray-400 text-sm space-y-1">
                    {template.items.slice(0, 3).map((item, i) => (
                      <li key={i} className="flex items-center">
                        <span className="text-green-400 mr-2">✓</span>
                        {item.text}
                      </li>
                    ))}
                    {template.items.length > 3 && (
                      <li className="text-gray-500">+{template.items.length - 3} more items</li>
                    )}
                  </ul>
                </div>
                <button
                  onClick={() => handleCreateFromTemplate(template.id)}
                  className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
                >
                  Use Template
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h2 className="text-2xl font-semibold text-white mb-6">Checklist Adherence</h2>
            <p className="text-gray-400">Analytics coming soon...</p>
          </div>
        )}

        {/* Checklist Modal */}
        {selectedChecklist && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <span className={`text-xs px-2 py-1 rounded ${getTypeColor(selectedChecklist.type)} text-white`}>
                    {getTypeLabel(selectedChecklist.type)}
                  </span>
                  <h3 className="text-2xl font-semibold text-white mt-2">{selectedChecklist.name}</h3>
                </div>
                <button
                  onClick={() => setSelectedChecklist(null)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>
              
              <p className="text-gray-400 mb-6">{selectedChecklist.description}</p>

              <div className="space-y-4 mb-6">
                {selectedChecklist.items.sort((a, b) => a.order - b.order).map(item => (
                  <div key={item.id} className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={completionStatus[item.id] || false}
                      onChange={(e) => setCompletionStatus({
                        ...completionStatus,
                        [item.id]: e.target.checked
                      })}
                      className="mt-1 w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded"
                    />
                    <div className="flex-1">
                      <p className="text-white">{item.text}</p>
                      {item.required && (
                        <span className="text-xs text-red-400">Required</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => handleCompleteChecklist(selectedChecklist.id)}
                  className="flex-1 bg-green-600 text-white py-2 rounded hover:bg-green-700"
                >
                  Complete & Log
                </button>
                <button
                  onClick={() => setSelectedChecklist(null)}
                  className="flex-1 bg-gray-700 text-white py-2 rounded hover:bg-gray-600"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Create Checklist Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-2xl font-semibold text-white">Create Custom Checklist</h3>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-gray-300 mb-2">Name</label>
                  <input
                    type="text"
                    value={newChecklist.name}
                    onChange={(e) => setNewChecklist({...newChecklist, name: e.target.value})}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded border border-gray-600"
                    placeholder="e.g., My Pre-Trade Routine"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Description</label>
                  <textarea
                    value={newChecklist.description}
                    onChange={(e) => setNewChecklist({...newChecklist, description: e.target.value})}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded border border-gray-600"
                    rows={2}
                    placeholder="What is this checklist for?"
                  />
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Type</label>
                  <select
                    value={newChecklist.type}
                    onChange={(e) => setNewChecklist({...newChecklist, type: e.target.value})}
                    className="w-full bg-gray-700 text-white px-4 py-2 rounded border border-gray-600"
                  >
                    <option value="pre-trade">Pre-Trade</option>
                    <option value="post-trade">Post-Trade</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                  </select>
                </div>

                <div>
                  <label className="block text-gray-300 mb-2">Checklist Items</label>
                  {newChecklist.items.map((item, index) => (
                    <div key={index} className="flex gap-2 mb-2">
                      <input
                        type="text"
                        value={item.text}
                        onChange={(e) => updateItem(index, 'text', e.target.value)}
                        className="flex-1 bg-gray-700 text-white px-4 py-2 rounded border border-gray-600"
                        placeholder={`Item ${index + 1}`}
                      />
                      <label className="flex items-center text-gray-300">
                        <input
                          type="checkbox"
                          checked={item.required}
                          onChange={(e) => updateItem(index, 'required', e.target.checked)}
                          className="mr-1"
                        />
                        Required
                      </label>
                      <button
                        onClick={() => removeItem(index)}
                        className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={addItemField}
                    className="mt-2 text-blue-400 hover:text-blue-300"
                  >
                    + Add Item
                  </button>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleCreateCustom}
                  className="flex-1 bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
                >
                  Create Checklist
                </button>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 bg-gray-700 text-white py-2 rounded hover:bg-gray-600"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
