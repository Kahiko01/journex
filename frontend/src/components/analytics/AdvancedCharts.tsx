'use client';

import { useState, useEffect, useRef } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ComposedChart, Scatter, ScatterChart, RadarChart, Radar,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Treemap
} from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Download, Maximize2, Minimize2, RefreshCw, 
  Calendar, Filter, TrendingUp, TrendingDown,
  BarChart3, PieChart as PieChartIcon, LineChart as LineChartIcon,
  Activity, Target, Award, Zap, Clock
} from 'lucide-react';

interface AdvancedChartsProps {
  data?: any;
  equityData?: any[];
  tradeData?: any[];
  performanceData?: any[];
  riskData?: any[];
  isLoading?: boolean;
  onExport?: (format: 'png' | 'svg' | 'csv') => void;
  height?: number;
  width?: number;
}

interface ChartConfig {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  type: 'line' | 'area' | 'bar' | 'pie' | 'scatter' | 'radar' | 'composed' | 'treemap';
  dataKey?: string;
  xAxisKey?: string;
  yAxisKey?: string;
}

export default function AdvancedCharts({
  data,
  equityData = [],
  tradeData = [],
  performanceData = [],
  riskData = [],
  isLoading = false,
  onExport,
  height = 400,
  width = 800
}: AdvancedChartsProps) {
  const [activeChart, setActiveChart] = useState<string>('equity');
  const [timeframe, setTimeframe] = useState<'1W' | '1M' | '3M' | '1Y' | 'ALL'>('1M');
  const [chartType, setChartType] = useState<'line' | 'area' | 'bar'>('line');
  const [fullscreen, setFullscreen] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['equity', 'drawdown']);
  const chartRef = useRef<HTMLDivElement>(null);

  // Sample data generators (replace with real data)
  const generateEquityData = () => {
    const data = [];
    let equity = 10000;
    const now = new Date();
    
    for (let i = 90; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      
      // Simulate equity movement
      const change = (Math.random() - 0.45) * 200;
      equity += change;
      
      // Calculate drawdown
      const peak = Math.max(...data.map(d => d.equity).concat([equity]));
      const drawdown = ((peak - equity) / peak) * 100;
      
      data.push({
        date: date.toISOString().split('T')[0],
        equity: Math.round(equity * 100) / 100,
        drawdown: Math.round(drawdown * 100) / 100,
        trades: Math.floor(Math.random() * 5) + 1,
        volume: Math.floor(Math.random() * 1000) + 100
      });
    }
    return data;
  };

  const generateTradeDistribution = () => {
    return [
      { name: 'Winning Trades', value: 58.7, fill: '#10b981' },
      { name: 'Losing Trades', value: 41.3, fill: '#ef4444' }
    ];
  };

  const generatePerformanceMetrics = () => {
    return [
      { metric: 'Win Rate', value: 58.7, target: 60, color: '#10b981' },
      { metric: 'Profit Factor', value: 1.63, target: 2.0, color: '#3b82f6' },
      { metric: 'Sharpe Ratio', value: 1.2, target: 1.5, color: '#8b5cf6' },
      { metric: 'Max DD', value: -12.5, target: -15, color: '#ef4444' },
      { metric: 'Avg R', value: 1.4, target: 1.5, color: '#f59e0b' },
      { metric: 'Win Streak', value: 7, target: 5, color: '#10b981' }
    ];
  };

  const generateRiskMetrics = () => {
    const data = [];
    for (let i = 0; i < 30; i++) {
      data.push({
        day: i + 1,
        var: Math.random() * 1000 + 500,
        cvar: Math.random() * 1500 + 800,
        volatility: Math.random() * 20 + 10
      });
    }
    return data;
  };

  const generateTradeScatter = () => {
    const data = [];
    for (let i = 0; i < 100; i++) {
      data.push({
        trade: i + 1,
        profit: (Math.random() - 0.5) * 1000,
        risk: Math.random() * 5,
        win: Math.random() > 0.4,
        rMultiple: (Math.random() - 0.5) * 3
      });
    }
    return data;
  };

  const generateHeatmapData = () => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const hours = Array.from({ length: 24 }, (_, i) => i);
    
    return days.map(day => ({
      day,
      ...Object.fromEntries(
        hours.map(hour => [hour, Math.floor(Math.random() * 100)])
      )
    }));
  };

  const chartConfigs: ChartConfig[] = [
    {
      id: 'equity',
      title: 'Equity Curve',
      description: 'Account balance over time with drawdown overlay',
      icon: <TrendingUp className="w-5 h-5" />,
      color: 'from-cyan-500 to-blue-500',
      type: 'composed'
    },
    {
      id: 'distribution',
      title: 'Trade Distribution',
      description: 'Winning vs losing trades analysis',
      icon: <PieChartIcon className="w-5 h-5" />,
      color: 'from-green-500 to-emerald-500',
      type: 'pie'
    },
    {
      id: 'performance',
      title: 'Performance Metrics',
      description: 'Key trading metrics vs targets',
      icon: <Target className="w-5 h-5" />,
      color: 'from-purple-500 to-pink-500',
      type: 'radar'
    },
    {
      id: 'risk',
      title: 'Risk Analysis',
      description: 'VaR, CVaR and volatility trends',
      icon: <Activity className="w-5 h-5" />,
      color: 'from-orange-500 to-red-500',
      type: 'line'
    },
    {
      id: 'scatter',
      title: 'Trade Scatter',
      description: 'Risk vs reward distribution',
      icon: <BarChart3 className="w-5 h-5" />,
      color: 'from-indigo-500 to-purple-500',
      type: 'scatter'
    },
    {
      id: 'heatmap',
      title: 'Trading Heatmap',
      description: 'Trading activity by time',
      icon: <Activity className="w-5 h-5" />,
      color: 'from-amber-500 to-orange-500',
      type: 'treemap'
    }
  ];

  const equityChartData = equityData.length ? equityData : generateEquityData();
  const pieData = generateTradeDistribution();
  const performanceData_ = generatePerformanceMetrics();
  const riskData_ = generateRiskMetrics();
  const scatterData = generateTradeScatter();
  const heatmapData = generateHeatmapData();

  const COLORS = ['#10b981', '#ef4444', '#3b82f6', '#8b5cf6', '#f59e0b'];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 shadow-2xl">
          <p className="text-gray-400 text-xs mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
              <span className="text-gray-500">{entry.name}:</span>
              <span className="text-white font-mono">
                {typeof entry.value === 'number' ? entry.value.toFixed(2) : entry.value}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="min-h-[400px] bg-gray-900/50 border border-gray-800 rounded-xl p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-2 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500 font-mono">LOADING CHARTS...</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={chartRef}
      className={`relative bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden transition-all duration-300 ${
        fullscreen ? 'fixed inset-4 z-50' : ''
      }`}
    >
      {/* Header */}
      <div className="p-4 border-b border-gray-800 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10">
              <Activity className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Advanced Analytics</h2>
              <p className="text-xs text-gray-500 font-mono">REAL-TIME PERFORMANCE METRICS</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Chart Type Selector */}
            <div className="flex gap-1 p-1 bg-gray-800 rounded-lg">
              <button
                onClick={() => setChartType('line')}
                className={`p-2 rounded transition ${
                  chartType === 'line' ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-500 hover:text-gray-400'
                }`}
              >
                <LineChartIcon className="w-4 h-4" />
              </button>
              <button
                onClick={() => setChartType('area')}
                className={`p-2 rounded transition ${
                  chartType === 'area' ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-500 hover:text-gray-400'
                }`}
              >
                <Activity className="w-4 h-4" />
              </button>
              <button
                onClick={() => setChartType('bar')}
                className={`p-2 rounded transition ${
                  chartType === 'bar' ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-500 hover:text-gray-400'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
              </button>
            </div>

            {/* Timeframe Selector */}
            <div className="flex gap-1 p-1 bg-gray-800 rounded-lg">
              {(['1W', '1M', '3M', '1Y', 'ALL'] as const).map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`px-3 py-1.5 text-xs font-mono rounded transition ${
                    timeframe === tf
                      ? 'bg-cyan-500/20 text-cyan-400'
                      : 'text-gray-500 hover:text-gray-400'
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>

            {/* Control Buttons */}
            <button
              onClick={() => setShowControls(!showControls)}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition"
              title="Toggle Controls"
            >
              <Filter className="w-4 h-4 text-gray-400" />
            </button>

            <button
              onClick={() => setFullscreen(!fullscreen)}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition"
              title={fullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
            >
              {fullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>

            {onExport && (
              <button
                onClick={() => onExport('png')}
                className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition"
                title="Export Chart"
              >
                <Download className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Chart Selector */}
        <div className="flex gap-2 mt-4 overflow-x-auto pb-2">
          {chartConfigs.map((config) => (
            <button
              key={config.id}
              onClick={() => setActiveChart(config.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition whitespace-nowrap ${
                activeChart === config.id
                  ? `bg-gradient-to-r ${config.color} text-white border-transparent`
                  : 'bg-gray-800 border-gray-700 text-gray-400 hover:text-white hover:border-gray-600'
              }`}
            >
              {config.icon}
              <span className="text-sm font-medium">{config.title}</span>
            </button>
          ))}
        </div>

        {/* Controls Panel */}
        <AnimatePresence>
          {showControls && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 pt-4 border-t border-gray-800 overflow-hidden"
            >
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-2">Metrics</label>
                  <div className="space-y-2">
                    {['equity', 'drawdown', 'volume', 'trades'].map((metric) => (
                      <label key={metric} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={selectedMetrics.includes(metric)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedMetrics([...selectedMetrics, metric]);
                            } else {
                              setSelectedMetrics(selectedMetrics.filter(m => m !== metric));
                            }
                          }}
                          className="w-4 h-4 rounded border-gray-600 text-cyan-500 focus:ring-cyan-500 focus:ring-offset-0"
                        />
                        <span className="text-sm text-gray-400 capitalize">{metric}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-2">Chart Style</label>
                  <select className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm">
                    <option value="smooth">Smooth Lines</option>
                    <option value="stepline">Step Lines</option>
                    <option value="monotone">Monotone</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-2">Y-Axis Scale</label>
                  <select className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm">
                    <option value="linear">Linear</option>
                    <option value="log">Logarithmic</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-mono text-gray-500 mb-2">Animation</label>
                  <button className="w-full px-3 py-2 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 rounded-lg text-sm font-mono transition">
                    <RefreshCw className="w-4 h-4 inline mr-2" />
                    Refresh Data
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Chart Area */}
      <div 
        className="p-4"
        style={{ height: fullscreen ? 'calc(100vh - 200px)' : height }}
      >
        <ResponsiveContainer width="100%" height="100%">
          {activeChart === 'equity' && (
            <ComposedChart data={equityChartData}>
              <defs>
                <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="drawdownGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.2}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="date" 
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                tickFormatter={(value) => value.split('-').slice(1).join('/')}
              />
              <YAxis 
                yAxisId="left"
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                domain={['auto', 'auto']}
              />
              <YAxis 
                yAxisId="right"
                orientation="right"
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af', fontSize: 12 }}
                domain={[0, 100]}
              />
              
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {selectedMetrics.includes('equity') && (
                <Area
                  yAxisId="left"
                  type="monotone"
                  dataKey="equity"
                  name="Equity"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fill="url(#equityGradient)"
                  dot={false}
                />
              )}
              
              {selectedMetrics.includes('drawdown') && (
                <Area
                  yAxisId="right"
                  type="monotone"
                  dataKey="drawdown"
                  name="Drawdown %"
                  stroke="#ef4444"
                  strokeWidth={2}
                  fill="url(#drawdownGradient)"
                  dot={false}
                />
              )}
              
              {selectedMetrics.includes('volume') && (
                <Bar
                  yAxisId="left"
                  dataKey="volume"
                  name="Volume"
                  fill="#8b5cf6"
                  opacity={0.3}
                />
              )}
            </ComposedChart>
          )}

          {activeChart === 'distribution' && (
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={80}
                outerRadius={120}
                paddingAngle={5}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(1)}%`}
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend />
            </PieChart>
          )}

          {activeChart === 'performance' && (
            <RadarChart outerRadius={150} data={performanceData_}>
              <PolarGrid stroke="#374151" />
              <PolarAngleAxis dataKey="metric" stroke="#9ca3af" />
              <PolarRadiusAxis stroke="#9ca3af" />
              <Radar
                name="Actual"
                dataKey="value"
                stroke="#3b82f6"
                fill="#3b82f6"
                fillOpacity={0.3}
              />
              <Radar
                name="Target"
                dataKey="target"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.3}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
            </RadarChart>
          )}

          {activeChart === 'risk' && (
            <LineChart data={riskData_}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="day" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line
                type="monotone"
                dataKey="var"
                name="VaR 95%"
                stroke="#ef4444"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="cvar"
                name="CVaR"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="volatility"
                name="Volatility"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          )}

          {activeChart === 'scatter' && (
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="rMultiple" 
                name="R-Multiple" 
                stroke="#9ca3af"
                domain={[-3, 3]}
              />
              <YAxis 
                dataKey="profit" 
                name="Profit/Loss" 
                stroke="#9ca3af"
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Scatter
                name="Winning Trades"
                data={scatterData.filter(d => d.win)}
                fill="#10b981"
                shape="circle"
              />
              <Scatter
                name="Losing Trades"
                data={scatterData.filter(d => !d.win)}
                fill="#ef4444"
                shape="circle"
              />
            </ScatterChart>
          )}

          {activeChart === 'heatmap' && (
            <Treemap
              data={heatmapData}
              dataKey="value"
              aspectRatio={4/3}
              stroke="#374151"
              fill="#3b82f6"
            >
              <Tooltip content={<CustomTooltip />} />
            </Treemap>
          )}
        </ResponsiveContainer>
      </div>

      {/* Footer Stats */}
      <div className="p-4 border-t border-gray-800 bg-gray-900/30">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-cyan-400">58.7%</div>
            <div className="text-xs text-gray-500 font-mono">WIN RATE</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-400">1.63</div>
            <div className="text-xs text-gray-500 font-mono">PROFIT FACTOR</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-400">1.2</div>
            <div className="text-xs text-gray-500 font-mono">SHARPE RATIO</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-400">-12.5%</div>
            <div className="text-xs text-gray-500 font-mono">MAX DD</div>
          </div>
        </div>
      </div>
    </div>
  );
}
