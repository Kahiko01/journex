'use client';

import { useState } from 'react';
import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';

interface BalanceData {
  date: string;
  deposits: number;
  withdrawals: number;
  trading_pl: number;
  net_balance: number;
}

interface BalanceCurveProps {
  data: BalanceData[];
  totalDeposits: number;
  totalWithdrawals: number;
  totalTradingPL: number;
  finalBalance: number;
  interval: string;
  onIntervalChange: (interval: string) => void;
}

export default function BalanceCurve({ 
  data, 
  totalDeposits, 
  totalWithdrawals, 
  totalTradingPL, 
  finalBalance,
  interval,
  onIntervalChange
}: BalanceCurveProps) {
  const [showComparison, setShowComparison] = useState(false);

  // Handle empty data
  if (!data || data.length === 0) {
    return (
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 h-96 flex items-center justify-center">
        <p className="text-gray-400">No balance data available</p>
      </div>
    );
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const formatDate = (dateStr: string) => {
    if (interval === 'monthly') {
      const [year, month] = dateStr.split('-');
      return `${month}/${year}`;
    }
    return dateStr;
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 mb-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-white">Balance Curve</h2>
        <div className="flex gap-2">
          <button
            onClick={() => onIntervalChange('daily')}
            className={`px-3 py-1 text-sm rounded ${interval === 'daily' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
          >
            Daily
          </button>
          <button
            onClick={() => onIntervalChange('weekly')}
            className={`px-3 py-1 text-sm rounded ${interval === 'weekly' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
          >
            Weekly
          </button>
          <button
            onClick={() => onIntervalChange('monthly')}
            className={`px-3 py-1 text-sm rounded ${interval === 'monthly' ? 'bg-blue-600' : 'bg-gray-700'} text-white`}
          >
            Monthly
          </button>
          <button
            onClick={() => setShowComparison(!showComparison)}
            className="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700"
          >
            {showComparison ? 'Hide Comparison' : 'Compare'}
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700 p-3 rounded">
          <p className="text-gray-400 text-xs">Total Deposits</p>
          <p className="text-green-400 text-lg font-bold">{formatCurrency(totalDeposits)}</p>
        </div>
        <div className="bg-gray-700 p-3 rounded">
          <p className="text-gray-400 text-xs">Total Withdrawals</p>
          <p className="text-red-400 text-lg font-bold">{formatCurrency(totalWithdrawals)}</p>
        </div>
        <div className="bg-gray-700 p-3 rounded">
          <p className="text-gray-400 text-xs">Trading P/L</p>
          <p className={totalTradingPL >= 0 ? 'text-green-400 text-lg font-bold' : 'text-red-400 text-lg font-bold'}>
            {formatCurrency(totalTradingPL)}
          </p>
        </div>
        <div className="bg-gray-700 p-3 rounded">
          <p className="text-gray-400 text-xs">Final Balance</p>
          <p className="text-blue-400 text-lg font-bold">{formatCurrency(finalBalance)}</p>
        </div>
      </div>

      {/* Chart */}
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis 
              dataKey="date" 
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF', fontSize: 12 }}
              tickFormatter={formatDate}
            />
            <YAxis 
              yAxisId="left"
              stroke="#9CA3AF"
              tick={{ fill: '#9CA3AF', fontSize: 12 }}
              tickFormatter={formatCurrency}
            />
            <YAxis 
              yAxisId="right"
              orientation="right"
              stroke="#10B981"
              tick={{ fill: '#10B981', fontSize: 12 }}
              tickFormatter={formatCurrency}
            />
            
            <Tooltip
              contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '0.5rem' }}
              labelStyle={{ color: '#9CA3AF' }}
              formatter={(value: number, name: string) => {
                if (name === 'deposits') return [formatCurrency(value), 'Deposits'];
                if (name === 'withdrawals') return [formatCurrency(value), 'Withdrawals'];
                if (name === 'trading_pl') return [formatCurrency(value), 'Trading P/L'];
                if (name === 'net_balance') return [formatCurrency(value), 'Net Balance'];
                return [value, name];
              }}
            />
            
            <Legend />
            
            <Bar yAxisId="left" dataKey="deposits" name="Deposits" fill="#10B981" stackId="a" />
            <Bar yAxisId="left" dataKey="withdrawals" name="Withdrawals" fill="#EF4444" stackId="a" />
            
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="net_balance"
              name="Net Balance"
              stroke="#3B82F6"
              strokeWidth={2}
              dot={{ fill: '#3B82F6', r: 4 }}
            />
            
            <ReferenceLine yAxisId="left" y={0} stroke="#6B7280" strokeDasharray="3 3" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-4 text-sm">
        <div className="flex items-center">
          <div className="w-3 h-3 bg-green-500 rounded mr-2"></div>
          <span className="text-gray-300">Deposits</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-red-500 rounded mr-2"></div>
          <span className="text-gray-300">Withdrawals</span>
        </div>
        <div className="flex items-center">
          <div className="w-3 h-3 bg-blue-500 rounded mr-2"></div>
          <span className="text-gray-300">Net Balance</span>
        </div>
      </div>
    </div>
  );
}
