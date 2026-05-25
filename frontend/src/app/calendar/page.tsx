'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

interface EconomicEvent {
  id: number;
  date: string;
  currency: string;
  event: string;
  impact: 'Low' | 'Medium' | 'High';
  actual: number;
  forecast: number;
  previous: number;
  description: string;
  is_relevant: boolean;
}

export default function EconomicCalendarPage() {
  const [events, setEvents] = useState<EconomicEvent[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<EconomicEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCurrency, setSelectedCurrency] = useState('all');
  const [selectedImpact, setSelectedImpact] = useState('all');
  const [dateRange, setDateRange] = useState('week');
  const [currencies, setCurrencies] = useState<string[]>([]);
  const [impacts, setImpacts] = useState<string[]>([]);

  useEffect(() => {
    fetchEvents();
    fetchMetadata();
  }, [dateRange]);

  useEffect(() => {
    filterEvents();
  }, [events, selectedCurrency, selectedImpact]);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      // Calculate date range
      const today = new Date();
      let dateFrom = new Date();
      let dateTo = new Date();

      if (dateRange === 'day') {
        dateTo.setDate(today.getDate() + 1);
      } else if (dateRange === 'week') {
        dateTo.setDate(today.getDate() + 7);
      } else if (dateRange === 'month') {
        dateTo.setMonth(today.getMonth() + 1);
      }

      const response = await axios.get('http://localhost:8000/api/v1/economic-calendar/events', {
        params: {
          date_from: dateFrom.toISOString().split('T')[0],
          date_to: dateTo.toISOString().split('T')[0]
        }
      });
      
      setEvents(response.data.events);
    } catch (error) {
      console.error('Error fetching economic events:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMetadata = async () => {
    try {
      const currenciesRes = await axios.get('http://localhost:8000/api/v1/economic-calendar/currencies');
      setCurrencies(currenciesRes.data.currencies);
      
      const impactsRes = await axios.get('http://localhost:8000/api/v1/economic-calendar/impacts');
      setImpacts(impactsRes.data.impacts);
    } catch (error) {
      console.error('Error fetching metadata:', error);
    }
  };

  const filterEvents = () => {
    let filtered = [...events];

    if (selectedCurrency !== 'all') {
      filtered = filtered.filter(e => e.currency === selectedCurrency);
    }

    if (selectedImpact !== 'all') {
      filtered = filtered.filter(e => e.impact === selectedImpact);
    }

    setFilteredEvents(filtered);
  };

  const toggleRelevant = async (eventId: number, currentRelevant: boolean) => {
    try {
      await axios.post(`http://localhost:8000/api/v1/economic-calendar/events/${eventId}/relevant?relevant=${!currentRelevant}`);
      
      // Update local state
      setEvents(events.map(e => 
        e.id === eventId ? { ...e, is_relevant: !currentRelevant } : e
      ));
    } catch (error) {
      console.error('Error toggling relevance:', error);
    }
  };

  const getImpactColor = (impact: string) => {
    switch(impact) {
      case 'High': return 'bg-red-600';
      case 'Medium': return 'bg-yellow-600';
      case 'Low': return 'bg-green-600';
      default: return 'bg-gray-600';
    }
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
  };

  const formatNumber = (num: number) => {
    return num > 0 ? `+${num}` : num.toString();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading economic calendar...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold text-white">Economic Calendar</h1>
          <div className="flex gap-4">
            <Link 
              href="/dashboard" 
              className="bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Dashboard
            </Link>
            <Link 
              href="/" 
              className="bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Home
            </Link>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Date Range */}
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded border border-gray-600"
            >
              <option value="day">Next 24 Hours</option>
              <option value="week">Next 7 Days</option>
              <option value="month">Next 30 Days</option>
            </select>

            {/* Currency Filter */}
            <select
              value={selectedCurrency}
              onChange={(e) => setSelectedCurrency(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded border border-gray-600"
            >
              <option value="all">All Currencies</option>
              {currencies.map(curr => (
                <option key={curr} value={curr}>{curr}</option>
              ))}
            </select>

            {/* Impact Filter */}
            <select
              value={selectedImpact}
              onChange={(e) => setSelectedImpact(e.target.value)}
              className="bg-gray-700 text-white px-4 py-2 rounded border border-gray-600"
            >
              <option value="all">All Impact Levels</option>
              {impacts.map(imp => (
                <option key={imp} value={imp}>{imp}</option>
              ))}
            </select>

            {/* Event Count */}
            <div className="bg-gray-700 px-4 py-2 rounded flex items-center justify-between">
              <span className="text-gray-400">Events:</span>
              <span className="text-white font-bold">{filteredEvents.length}</span>
            </div>
          </div>
        </div>

        {/* Events Table */}
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-700">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Date/Time</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Curr</th>
                  <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Event</th>
                  <th className="px-4 py-3 text-center text-sm font-medium text-gray-300">Impact</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Actual</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Forecast</th>
                  <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Previous</th>
                  <th className="px-4 py-3 text-center text-sm font-medium text-gray-300">Track</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredEvents.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-8 text-center text-gray-400">
                      No economic events found for the selected filters
                    </td>
                  </tr>
                ) : (
                  filteredEvents.map((event) => {
                    const { date, time } = formatDateTime(event.date);
                    return (
                      <tr key={event.id} className="hover:bg-gray-750 transition">
                        <td className="px-4 py-3">
                          <div className="text-white text-sm">{date}</div>
                          <div className="text-gray-400 text-xs">{time}</div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-white font-medium">{event.currency}</span>
                        </td>
                        <td className="px-4 py-3">
                          <div className="text-white text-sm">{event.event}</div>
                          <div className="text-gray-400 text-xs">{event.description}</div>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span className={`px-2 py-1 rounded text-xs text-white ${getImpactColor(event.impact)}`}>
                            {event.impact}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <span className="text-white font-mono">{formatNumber(event.actual)}</span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <span className="text-gray-400 font-mono">{formatNumber(event.forecast)}</span>
                        </td>
                        <td className="px-4 py-3 text-right">
                          <span className="text-gray-400 font-mono">{formatNumber(event.previous)}</span>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <button
                            onClick={() => toggleRelevant(event.id, event.is_relevant)}
                            className={`px-3 py-1 rounded text-xs ${
                              event.is_relevant 
                                ? 'bg-blue-600 text-white' 
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                            }`}
                          >
                            {event.is_relevant ? '★ Tracking' : '☆ Track'}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-6 flex flex-wrap gap-4 text-sm">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-red-600 rounded mr-2"></div>
            <span className="text-gray-300">High Impact</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-yellow-600 rounded mr-2"></div>
            <span className="text-gray-300">Medium Impact</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-600 rounded mr-2"></div>
            <span className="text-gray-300">Low Impact</span>
          </div>
        </div>
      </div>
    </div>
  );
}
