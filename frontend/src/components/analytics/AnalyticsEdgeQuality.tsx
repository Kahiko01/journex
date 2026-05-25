'use client';

interface AnalyticsEdgeQualityProps {
  data: any;
}

export default function AnalyticsEdgeQuality({ data }: AnalyticsEdgeQualityProps) {
  if (!data || !data.analysis) return null;

  const { core_metrics } = data.analysis;

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Total Trades</div>
          <div className="text-2xl font-bold text-white">{data.total_trades}</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Win Rate</div>
          <div className="text-2xl font-bold text-green-400">{core_metrics?.win_rate}%</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Profit Factor</div>
          <div className="text-2xl font-bold text-white">{core_metrics?.profit_factor?.toFixed(2)}</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm">Expectancy</div>
          <div className={`text-2xl font-bold ${(core_metrics?.expectancy || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {formatCurrency(core_metrics?.expectancy || 0)}
          </div>
        </div>
      </div>

      {/* Core Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/30 rounded-lg p-3">
          <div className="text-gray-500 text-xs">Avg Win</div>
          <div className="text-green-400 font-bold">{formatCurrency(core_metrics?.avg_win || 0)}</div>
        </div>
        <div className="bg-gray-800/30 rounded-lg p-3">
          <div className="text-gray-500 text-xs">Avg Loss</div>
          <div className="text-red-400 font-bold">{formatCurrency(core_metrics?.avg_loss || 0)}</div>
        </div>
        <div className="bg-gray-800/30 rounded-lg p-3">
          <div className="text-gray-500 text-xs">Largest Win</div>
          <div className="text-green-400 font-bold">{formatCurrency(core_metrics?.largest_win || 0)}</div>
        </div>
        <div className="bg-gray-800/30 rounded-lg p-3">
          <div className="text-gray-500 text-xs">Largest Loss</div>
          <div className="text-red-400 font-bold">{formatCurrency(core_metrics?.largest_loss || 0)}</div>
        </div>
      </div>

      {/* Win/Loss Streaks */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-2">Longest Win Streak</div>
          <div className="text-3xl font-bold text-green-400">{core_metrics?.win_streak}</div>
        </div>
        <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700">
          <div className="text-gray-400 text-sm mb-2">Longest Loss Streak</div>
          <div className="text-3xl font-bold text-red-400">{core_metrics?.loss_streak}</div>
        </div>
      </div>
    </div>
  );
}
