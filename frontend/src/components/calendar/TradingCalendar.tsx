'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

interface CalendarDay {
  day: number;
  date: string;
  pl: number;
  trades: number;
  color: string;
  icons: string[];
  has_data: boolean;
  empty?: boolean;
}

interface MonthData {
  year: number;
  month: number;
  month_name: string;
  heatmap: CalendarDay[][];
  has_data: boolean;
}

interface TradingCalendarProps {
  userId?: number;
  onDayClick?: (date: string, trades: any[]) => void;
}

export default function TradingCalendar({ userId = 1, onDayClick }: TradingCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [monthData, setMonthData] = useState<MonthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [dayTrades, setDayTrades] = useState<any[]>([]);

  useEffect(() => {
    fetchCalendarData();
    fetchTrades();
  }, [currentDate]);

  const fetchCalendarData = async () => {
    try {
      setLoading(true);
      const year = currentDate.getFullYear();
      const month = currentDate.getMonth() + 1;
      
      console.log('Fetching calendar for:', year, month);
      
      const response = await axios.get(
        `http://localhost:8000/api/v1/advanced-analytics/calendar/${year}/${month}?user_id=${userId}`
      );
      
      console.log('Calendar response:', response.data);
      
      setMonthData({
        year,
        month,
        month_name: currentDate.toLocaleString('default', { month: 'long' }),
        heatmap: response.data.heatmap,
        has_data: true
      });
    } catch (error) {
      console.error('Error fetching calendar:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrades = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/trades/?user_id=${userId}`);
      setDayTrades(response.data);
    } catch (error) {
      console.error('Error fetching trades:', error);
    }
  };

  const changeMonth = (delta: number) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + delta);
    setCurrentDate(newDate);
    setSelectedDay(null);
  };

  const handleDayClick = (date: string) => {
    setSelectedDay(date);
    const tradesForDay = getDayTrades(date);
    if (onDayClick) {
      onDayClick(date, tradesForDay);
    }
  };

  const getDayTrades = (date: string) => {
    return dayTrades.filter((trade: any) => {
      if (!trade.exit_time) return false;
      return trade.exit_time.split('T')[0] === date;
    });
  };

  const formatCurrency = (value: number) => {
    if (Math.abs(value) < 0.01) return `$${(value * 100000).toFixed(0)}`;
    if (Math.abs(value) < 1) return `$${(value * 1000).toFixed(1)}`;
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD', 
      minimumFractionDigits: 0,
      maximumFractionDigits: 0 
    }).format(value);
  };

  const getProfitLossSummary = () => {
    if (!monthData) return { total: 0, winning: 0, losing: 0 };
    
    let total = 0;
    let winning = 0;
    let losing = 0;
    
    monthData.heatmap.forEach(week => {
      week.forEach(day => {
        if (day.has_data) {
          total += day.pl;
          if (day.pl > 0) winning += day.pl;
          if (day.pl < 0) losing += Math.abs(day.pl);
        }
      });
    });
    
    return { total, winning, losing };
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-7 gap-1 mb-2">
            {[...Array(7)].map((_, i) => (
              <div key={i} className="h-4 bg-gray-700 rounded"></div>
            ))}
          </div>
          <div className="space-y-1">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="grid grid-cols-7 gap-1">
                {[...Array(7)].map((_, j) => (
                  <div key={j} className="h-16 bg-gray-700 rounded"></div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const summary = getProfitLossSummary();

  return (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      {/* Header with Month Navigation */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-white flex items-center gap-2">
          <span className="text-2xl">📅</span>
          Trading Calendar
        </h2>
        <div className="flex items-center gap-3">
          <button
            onClick={() => changeMonth(-1)}
            className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-1.5 rounded-lg transition flex items-center gap-1"
          >
            <span>←</span> Prev
          </button>
          <span className="text-white font-medium min-w-[140px] text-center">
            {monthData?.month_name} {monthData?.year}
          </span>
          <button
            onClick={() => changeMonth(1)}
            className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-1.5 rounded-lg transition flex items-center gap-1"
          >
            Next <span>→</span>
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-gray-700/50 p-3 rounded-lg">
          <p className="text-gray-400 text-xs">Month Total</p>
          <p className={`text-lg font-bold ${summary.total >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatCurrency(summary.total)}
          </p>
        </div>
        <div className="bg-gray-700/50 p-3 rounded-lg">
          <p className="text-gray-400 text-xs">Winning Days</p>
          <p className="text-lg font-bold text-green-400">
            {formatCurrency(summary.winning)}
          </p>
        </div>
        <div className="bg-gray-700/50 p-3 rounded-lg">
          <p className="text-gray-400 text-xs">Losing Days</p>
          <p className="text-lg font-bold text-red-400">
            {formatCurrency(summary.losing)}
          </p>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-gray-900/50 rounded-xl p-4">
        {/* Day headers */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map(day => (
            <div key={day} className="text-center text-gray-400 text-sm font-medium py-2">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar weeks */}
        <div className="space-y-1">
          {monthData?.heatmap.map((week, weekIndex) => (
            <div key={weekIndex} className="grid grid-cols-7 gap-1">
              {week.map((day, dayIndex) => (
                <div key={dayIndex}>
                  {day.empty ? (
                    <div className="aspect-square bg-gray-800/50 rounded-lg opacity-50"></div>
                  ) : (
                    <button
                      onClick={() => day.has_data && handleDayClick(day.date)}
                      className={`w-full aspect-square rounded-lg p-1 transition-all ${
                        day.has_data 
                          ? `${day.color} hover:ring-2 hover:ring-blue-500 cursor-pointer transform hover:scale-105` 
                          : 'bg-gray-800 cursor-default'
                      }`}
                      disabled={!day.has_data}
                    >
                      <div className="text-white text-sm font-bold">{day.day}</div>
                      {day.has_data && (
                        <>
                          <div className={`text-xs font-bold ${day.pl > 0 ? 'text-green-200' : 'text-red-200'}`}>
                            {formatCurrency(day.pl)}
                          </div>
                          {day.trades > 1 && (
                            <div className="text-[10px] text-gray-300 mt-0.5">
                              {day.trades} trades
                            </div>
                          )}
                        </>
                      )}
                    </button>
                  )}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded"></div>
          <span className="text-gray-400">Profitable Day</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded"></div>
          <span className="text-gray-400">Losing Day</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-500 rounded"></div>
          <span className="text-gray-400">Mixed/Break Even</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gray-700 rounded"></div>
          <span className="text-gray-400">No Trades</span>
        </div>
      </div>

      {/* Selected Day Trades */}
      {selectedDay && (
        <div className="mt-4 p-4 bg-gray-700/30 rounded-lg">
          <h3 className="text-white font-medium mb-2">
            Trades on {new Date(selectedDay).toLocaleDateString()}
          </h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {getDayTrades(selectedDay).map((trade: any, index: number) => (
              <Link
                key={trade.id || index}
                href={`/trades/${trade.id}`}
                className="block p-2 bg-gray-700 rounded hover:bg-gray-600 transition"
              >
                <div className="flex justify-between items-center">
                  <span className="text-white text-sm">{trade.symbol}</span>
                  <span className={trade.profit_loss > 0 ? 'text-green-400' : 'text-red-400'}>
                    ${trade.profit_loss?.toFixed(2)}
                  </span>
                </div>
                <div className="text-xs text-gray-400">
                  {trade.strategy || 'No strategy'} • {trade.direction}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
