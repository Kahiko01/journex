'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';
import ProtectedRoute from '@/components/ProtectedRoute';

function NewTradeContent() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    symbol: '',
    direction: 'BUY',
    entry_price: '',
    exit_price: '',
    stop_loss: '',
    take_profit: '',
    lot_size: '0.1',
    strategy: '',
    emotion: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post('http://localhost:8000/api/v1/trades/', {
        ...formData,
        entry_price: parseFloat(formData.entry_price),
        exit_price: formData.exit_price ? parseFloat(formData.exit_price) : null,
        stop_loss: formData.stop_loss ? parseFloat(formData.stop_loss) : null,
        take_profit: formData.take_profit ? parseFloat(formData.take_profit) : null,
        lot_size: parseFloat(formData.lot_size)
      });
      
      router.push('/trades');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create trade');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-gray-100 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <Link href="/trades" className="text-cyan-400 hover:text-cyan-300 font-mono text-sm">
            ← BACK TO TRADES
          </Link>
          <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-600 mt-4 mb-2">
            NEW TRADE
          </h1>
          <p className="text-gray-500 font-mono text-sm">EXECUTE NEW POSITION</p>
        </div>

        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 text-rose-400 px-4 py-3 rounded-lg mb-6 font-mono text-sm">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6 bg-black/50 border border-cyan-500/30 rounded-xl p-8">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-mono text-cyan-400 mb-2">SYMBOL</label>
              <input
                type="text"
                value={formData.symbol}
                onChange={(e) => setFormData({...formData, symbol: e.target.value.toUpperCase()})}
                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400"
                placeholder="EURUSD"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-mono text-cyan-400 mb-2">DIRECTION</label>
              <select
                value={formData.direction}
                onChange={(e) => setFormData({...formData, direction: e.target.value})}
                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400"
              >
                <option value="BUY">BUY</option>
                <option value="SELL">SELL</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-mono text-cyan-400 mb-2">ENTRY PRICE</label>
              <input
                type="number"
                step="0.00001"
                value={formData.entry_price}
                onChange={(e) => setFormData({...formData, entry_price: e.target.value})}
                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400"
                placeholder="1.1050"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-mono text-cyan-400 mb-2">EXIT PRICE</label>
              <input
                type="number"
                step="0.00001"
                value={formData.exit_price}
                onChange={(e) => setFormData({...formData, exit_price: e.target.value})}
                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400"
                placeholder="1.1080"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-mono text-cyan-400 mb-2">STOP LOSS</label>
              <input
                type="number"
                step="0.00001"
                value={formData.stop_loss}
                onChange={(e) => setFormData({...formData, stop_loss: e.target.value})}
                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400"
                placeholder="1.1020"
              />
            </div>

            <div>
              <label className="block text-sm font-mono text-cyan-400 mb-2">TAKE PROFIT</label>
              <input
                type="number"
                step="0.00001"
                value={formData.take_profit}
                onChange={(e) => setFormData({...formData, take_profit: e.target.value})}
                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400"
                placeholder="1.1120"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-mono text-cyan-400 mb-2">LOT SIZE</label>
              <input
                type="number"
                step="0.01"
                value={formData.lot_size}
                onChange={(e) => setFormData({...formData, lot_size: e.target.value})}
                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400"
                placeholder="0.1"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-mono text-cyan-400 mb-2">STRATEGY</label>
              <input
                type="text"
                value={formData.strategy}
                onChange={(e) => setFormData({...formData, strategy: e.target.value})}
                className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400"
                placeholder="Swing Trading"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-mono text-cyan-400 mb-2">EMOTION</label>
            <select
              value={formData.emotion}
              onChange={(e) => setFormData({...formData, emotion: e.target.value})}
              className="w-full bg-black/50 border border-cyan-500/30 rounded-lg px-4 py-3 text-white font-mono focus:outline-none focus:border-cyan-400"
            >
              <option value="">Select emotion</option>
              <option value="Calm">Calm</option>
              <option value="Focused">Focused</option>
              <option value="Confident">Confident</option>
              <option value="Anxious">Anxious</option>
              <option value="Greedy">Greedy</option>
              <option value="Fearful">Fearful</option>
            </select>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-bold py-3 rounded-lg hover:from-cyan-600 hover:to-purple-700 transition-all disabled:opacity-50"
            >
              {loading ? 'EXECUTING...' : 'EXECUTE TRADE'}
            </button>
            <Link
              href="/trades"
              className="px-6 py-3 bg-rose-500/20 border border-rose-500/30 rounded-lg font-mono text-sm hover:bg-rose-500/30 transition"
            >
              CANCEL
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function ProtectedNewTradePage() {
  return (
    <ProtectedRoute>
      <NewTradeContent />
    </ProtectedRoute>
  );
}
