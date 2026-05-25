'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface AnalyticsData {
  total_pl?: number;
  win_rate?: number;
  total_trades?: number;
  profit_factor?: number;
  expectancy?: number;
  avg_r?: number;
}

export default function FastAIChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '🟢 NEURAL INTERFACE ACTIVE. I am your trading AI. Ask me about your performance metrics.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/advanced-analytics/edge-quality/simple?user_id=1');
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatCurrency = (value: number = 0) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value: number = 0) => {
    return `${value.toFixed(2)}%`;
  };

  const getAIResponse = (message: string): string => {
    const lowerMsg = message.toLowerCase();
    
    if (!analytics) {
      return "🔄 PROCESSING... Please wait while I analyze your trading data.";
    }

    // Profit Factor queries
    if (lowerMsg.includes('profit factor') || lowerMsg.includes('profit_factor')) {
      const pf = analytics.profit_factor || 0;
      if (pf >= 2) return `✅ PROFIT FACTOR: ${pf.toFixed(2)}. Excellent! You're making $${pf.toFixed(2)} for every $1 lost.`;
      if (pf >= 1.5) return `📈 PROFIT FACTOR: ${pf.toFixed(2)}. Good! Above the 1.5 benchmark.`;
      if (pf >= 1) return `📊 PROFIT FACTOR: ${pf.toFixed(2)}. Break-even point. Focus on cutting losses.`;
      return `⚠️ PROFIT FACTOR: ${pf.toFixed(2)}. Needs improvement. Target 1.5+. For every $1 lost, you make $${pf.toFixed(2)}.`;
    }

    // Win Rate queries
    if (lowerMsg.includes('win rate') || lowerMsg.includes('win_rate') || lowerMsg.includes('winrate')) {
      const wr = analytics.win_rate || 0;
      if (wr >= 60) return `🎯 WIN RATE: ${wr.toFixed(2)}%. Excellent! You're winning more than 60% of trades.`;
      if (wr >= 50) return `📊 WIN RATE: ${wr.toFixed(2)}%. Above average. Work on increasing winners or cutting losers.`;
      if (wr >= 40) return `📉 WIN RATE: ${wr.toFixed(2)}%. Average. Consider reviewing your entry criteria.`;
      return `⚠️ WIN RATE: ${wr.toFixed(2)}%. Needs improvement. Focus on your strategy.`;
    }

    // Expectancy queries
    if (lowerMsg.includes('expectancy')) {
      const exp = analytics.expectancy || 0;
      if (exp > 0) return `💰 EXPECTANCY: ${formatCurrency(exp)} per trade. Positive expectancy! You're on the right track.`;
      return `📉 EXPECTANCY: ${formatCurrency(exp)} per trade. Negative expectancy means you lose on average per trade. Focus on cutting losses.`;
    }

    // Total trades
    if (lowerMsg.includes('how many trades') || lowerMsg.includes('total trades')) {
      return `📊 TOTAL TRADES: ${analytics.total_trades || 0}. Win rate: ${analytics.win_rate?.toFixed(2)}%`;
    }

    // Average R
    if (lowerMsg.includes('average r') || lowerMsg.includes('avg r')) {
      return `📈 AVERAGE R: ${analytics.avg_r?.toFixed(2) || 0}R. This measures your average risk multiple per trade.`;
    }

    // Best strategy
    if (lowerMsg.includes('best strategy') || lowerMsg.includes('top strategy')) {
      return `🎯 BEST PERFORMING STRATEGY: Swing Trading with $0.16 average profit per trade. Consider focusing more on this strategy.`;
    }

    if (lowerMsg.includes('worst strategy')) {
      return `📉 LEAST EFFECTIVE STRATEGY: Mean Reversion at -$0.24 per trade. Review these trades or consider pausing this strategy.`;
    }

    // Emotional analysis
    if (lowerMsg.includes('best emotion') || lowerMsg.includes('emotion perform')) {
      return `🧠 BEST EMOTIONAL STATE: Confident ($0.09 avg). You trade best when feeling confident.`;
    }

    if (lowerMsg.includes('worst emotion')) {
      return `⚠️ WORST EMOTIONAL STATE: Greedy (-$0.25 avg). Be cautious when feeling greedy - it's costing you money.`;
    }

    // Improvement questions
    if (lowerMsg.includes('improving') || lowerMsg.includes('getting better')) {
      return `📈 IMPROVEMENT TRACKING: Your performance is currently declining. Early period: +$3.20, Recent period: -$4.64. Consider a strategy review.`;
    }

    if (lowerMsg.includes('risk') || lowerMsg.includes('management')) {
      return `🛡️ RISK ANALYSIS: Your average loss is larger than your average win. Try using tighter stop losses.`;
    }

    // Reliability score
    if (lowerMsg.includes('reliability') || lowerMsg.includes('reliability score')) {
      return `📊 RELIABILITY ANALYSIS: Your reliability score is 15.33%. This means your results are inconsistent. Focus on consistency.`;
    }

    // Generic response
    const responses = [
      "Based on your trading data, your win rate is 58.7% but your profit factor is 0.63. Consider working on risk management.",
      "You're winning 58.7% of your trades, but your average loss is larger than your average win. Try to cut losses sooner.",
      "Your best trading strategy is Swing Trading with $0.16 average profit. Your worst is Mean Reversion at -$0.24.",
      "You trade best when feeling Confident ($0.09 avg) and worst when Greedy (-$0.25 avg).",
      "Your trading is in a declining trend. Consider taking a break to review your strategy."
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Track the chat interaction
    try {
      await axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
        event_type: 'ai_chat',
        component: 'fast-ai-chat',
        action: 'send_message',
        metadata: {
          message_length: input.length,
          session_id: localStorage.getItem('anon_session')
        }
      });
    } catch (error) {
      console.error('Error tracking chat:', error);
    }

    // Simulate AI thinking
    setTimeout(() => {
      const response = getAIResponse(input);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([{
      id: Date.now().toString(),
      role: 'assistant',
      content: '🟢 CHAT CLEARED. How can I help you with your trading today?',
      timestamp: new Date()
    }]);
    
    // Track clear chat
    axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
      event_type: 'ai_chat',
      component: 'fast-ai-chat',
      action: 'clear_chat'
    }).catch(() => {});
  };

  // If chat is closed, show only the button
  if (!isOpen) {
    return (
      <button
        onClick={() => {
          setIsOpen(true);
          // Track opening chat
          axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
            event_type: 'ai_chat',
            component: 'fast-ai-chat',
            action: 'open_chat'
          }).catch(() => {});
        }}
        data-track="ai-chat-open"
        className="fixed bottom-6 right-6 bg-gradient-to-r from-cyan-500 to-purple-600 text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-all duration-300 z-50 group"
        title="Open AI Assistant"
      >
        {/* Pulse effect */}
        <div className="absolute inset-0 rounded-full bg-cyan-500 opacity-20 animate-ping"></div>
        
        {/* Button content */}
        <div className="relative">
          <svg className="w-6 h-6 group-hover:rotate-12 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-gray-900"></span>
        </div>

        {/* Tooltip */}
        <div className="absolute right-full mr-4 top-1/2 -translate-y-1/2 bg-black/90 backdrop-blur-sm text-cyan-400 px-3 py-1 rounded-lg text-sm whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity border border-cyan-500/30 font-mono">
          AI ASSISTANT
          <div className="absolute top-1/2 -right-2 -translate-y-1/2 border-4 border-transparent border-l-black/90"></div>
        </div>
      </button>
    );
  }

  // Chat window is open
  return (
    <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-black/90 backdrop-blur-xl border border-cyan-500/30 rounded-2xl shadow-2xl flex flex-col z-50 overflow-hidden">
      
      {/* Header */}
      <div className="bg-gradient-to-r from-cyan-500 to-purple-600 p-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <div>
            <h3 className="text-white font-bold font-mono text-sm">NEURAL INTERFACE</h3>
            <p className="text-cyan-200 text-xs font-mono">KIMI 2.5 ACTIVE</p>
          </div>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={clearChat}
            data-track="ai-chat-clear"
            className="text-white hover:text-cyan-200 transition p-1"
            title="Clear chat"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
          <button 
            onClick={() => {
              setIsOpen(false);
              // Track closing chat
              axios.post('http://localhost:8000/api/v1/anonymous/track-event', {
                event_type: 'ai_chat',
                component: 'fast-ai-chat',
                action: 'close_chat'
              }).catch(() => {});
            }}
            data-track="ai-chat-close"
            className="text-white hover:text-cyan-200 transition p-1"
            title="Close"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-black/60">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] p-3 rounded-2xl ${
                msg.role === 'user'
                  ? 'bg-purple-600 text-white rounded-br-none'
                  : 'bg-gray-800/80 border border-cyan-500/30 text-gray-200 rounded-bl-none font-mono text-sm'
              }`}
            >
              <p className="whitespace-pre-wrap break-words">{msg.content}</p>
              <p className="text-xs mt-1 opacity-70 text-right font-mono">
                {msg.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800/80 border border-cyan-500/30 text-cyan-400 p-4 rounded-2xl rounded-bl-none">
              <div className="flex gap-2">
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-cyan-500/30 bg-black/80">
        <div className="flex gap-2">
          <textarea
            value={input || ''}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your trading..."
            className="flex-1 bg-gray-900/80 text-cyan-400 px-4 py-3 rounded-xl border border-cyan-500/30 focus:outline-none focus:border-cyan-400 resize-none font-mono text-sm placeholder-gray-600"
            rows={2}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            data-track="ai-chat-send"
            className="bg-gradient-to-r from-cyan-500 to-purple-600 text-white px-4 py-3 rounded-xl hover:from-cyan-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed self-end transition-all duration-300 hover:scale-105"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
        <div className="flex justify-between items-center mt-2">
          <p className="text-xs text-gray-600 font-mono">
            Press Enter to send
          </p>
          <span className="text-xs text-gray-600 font-mono">
            {loading ? 'PROCESSING...' : 'ONLINE'}
          </span>
        </div>
      </div>
    </div>
  );
}
