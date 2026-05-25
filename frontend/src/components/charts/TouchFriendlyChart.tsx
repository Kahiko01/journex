'use client';

import { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';

interface TouchFriendlyChartProps {
  data: any[];
  type?: 'line' | 'bar' | 'area';
  dataKey: string;
  xAxisKey: string;
  color?: string;
  height?: number;
}

export default function TouchFriendlyChart({
  data,
  type = 'line',
  dataKey,
  xAxisKey,
  color = '#3B82F6',
  height = 300
}: TouchFriendlyChartProps) {
  const [chartHeight, setChartHeight] = useState(height);
  const [isTouch, setIsTouch] = useState(false);

  useEffect(() => {
    // Detect touch device
    setIsTouch('ontouchstart' in window);
    
    // Adjust chart height for mobile
    const updateHeight = () => {
      const width = window.innerWidth;
      if (width < 640) {
        setChartHeight(250);
      } else if (width < 1024) {
        setChartHeight(300);
      } else {
        setChartHeight(height);
      }
    };

    updateHeight();
    window.addEventListener('resize', updateHeight);
    
    return () => window.removeEventListener('resize', updateHeight);
  }, [height]);

  const ChartComponent = {
    line: LineChart,
    bar: BarChart,
    area: AreaChart
  }[type];

  const DataComponent = {
    line: Line,
    bar: Bar,
    area: Area
  }[type];

  return (
    <div className="w-full touch-pan-y">
      <ResponsiveContainer width="100%" height={chartHeight}>
        <ChartComponent data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey={xAxisKey} 
            stroke="#9CA3AF"
            tick={{ fill: '#9CA3AF', fontSize: isTouch ? 10 : 12 }}
            tickMargin={isTouch ? 8 : 10}
          />
          <YAxis 
            stroke="#9CA3AF"
            tick={{ fill: '#9CA3AF', fontSize: isTouch ? 10 : 12 }}
            width={isTouch ? 40 : 50}
          />
          <Tooltip
            contentStyle={{ 
              backgroundColor: '#1F2937', 
              border: 'none',
              borderRadius: '0.5rem',
              padding: isTouch ? '4px 8px' : '8px 12px'
            }}
            labelStyle={{ color: '#9CA3AF', fontSize: isTouch ? 10 : 12 }}
          />
          <DataComponent 
            type="monotone" 
            dataKey={dataKey} 
            stroke={color}
            fill={type === 'area' ? color : undefined}
            fillOpacity={type === 'area' ? 0.2 : undefined}
            strokeWidth={isTouch ? 2 : 1.5}
            dot={!isTouch}
            activeDot={{ r: isTouch ? 6 : 8 }}
          />
        </ChartComponent>
      </ResponsiveContainer>
    </div>
  );
}
