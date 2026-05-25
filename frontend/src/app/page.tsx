'use client';

import Link from 'next/link';
import { useState, useEffect, useRef } from 'react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  Shield, 
  Brain, 
  Lock, 
  Cloud, 
  Activity, 
  Zap, 
  BarChart3, 
  Target, 
  ChevronRight, 
  Play, 
  Terminal, 
  Cpu, 
  Globe,
  ArrowRight,
  CheckCircle2,
  Quote,
  Menu,
  X
} from 'lucide-react';

// Smooth counter animation
function AnimatedCounter({ value, prefix = '', suffix = '', duration = 2000 }: { 
  value: number; 
  prefix?: string; 
  suffix?: string;
  duration?: number;
}) {
  const [count, setCount] = useState(0);
  const countRef = useRef<HTMLSpanElement>(null);
  const hasAnimated = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !hasAnimated.current) {
          hasAnimated.current = true;
          const startTime = performance.now();
          const animate = (currentTime: number) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            setCount(Math.floor(easeOutQuart * value));
            if (progress < 1) requestAnimationFrame(animate);
          };
          requestAnimationFrame(animate);
        }
      },
      { threshold: 0.5 }
    );

    if (countRef.current) observer.observe(countRef.current);
    return () => observer.disconnect();
  }, [value, duration]);

  return <span ref={countRef}>{prefix}{count.toLocaleString()}{suffix}</span>;
}

// Market ticker with realistic data
function MarketTicker() {
  const [tickers, setTickers] = useState([
    { symbol: 'SPY', price: 412.45, change: 1.2, up: true },
    { symbol: 'QQQ', price: 338.92, change: 0.8, up: true },
    { symbol: 'IWM', price: 175.23, change: -0.4, up: false },
    { symbol: 'VIX', price: 18.45, change: -5.2, up: false },
    { symbol: 'AAPL', price: 178.35, change: 2.1, up: true },
    { symbol: 'TSLA', price: 245.67, change: -1.8, up: false },
    { symbol: 'NVDA', price: 460.18, change: 3.4, up: true },
    { symbol: 'META', price: 298.45, change: 1.5, up: true },
    { symbol: 'AMD', price: 142.30, change: 0.9, up: true },
    { symbol: 'MSFT', price: 378.91, change: -0.3, up: false },
  ]);

  // Simulate live price updates
  useEffect(() => {
    const interval = setInterval(() => {
      setTickers(prev => prev.map(ticker => {
        const volatility = ticker.symbol === 'VIX' ? 0.1 : 0.02;
        const change = (Math.random() - 0.5) * volatility;
        const newPrice = Math.max(0.01, ticker.price * (1 + change));
        const newChange = ticker.change + (Math.random() - 0.5) * 0.1;
        return {
          ...ticker,
          price: newPrice,
          change: newChange,
          up: newChange >= 0
        };
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full bg-slate-950/80 border-y border-white/5 overflow-hidden backdrop-blur-md">
      <div className="flex animate-scroll-x">
        {[...tickers, ...tickers, ...tickers].map((ticker, idx) => (
          <div key={idx} className="flex items-center gap-3 px-6 py-3 border-r border-white/5 whitespace-nowrap">
            <span className="text-xs font-bold text-slate-400 tracking-wider">{ticker.symbol}</span>
            <span className="text-sm font-mono text-white tabular-nums">
              ${ticker.price.toFixed(2)}
            </span>
            <span className={`text-xs font-mono flex items-center gap-0.5 ${ticker.up ? 'text-emerald-400' : 'text-rose-400'}`}>
              {ticker.up ? '+' : ''}{ticker.change.toFixed(2)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Professional glass card component
function GlassCard({ 
  children, 
  className = '', 
  hover = true,
  glow = false
}: { 
  children: React.ReactNode; 
  className?: string; 
  hover?: boolean;
  glow?: boolean;
}) {
  return (
    <div className={`group relative ${className}`}>
      {glow && (
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-violet-500 rounded-2xl opacity-0 group-hover:opacity-20 blur transition duration-500" />
      )}
      <div className={`relative bg-slate-900/50 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden ${hover ? 'hover:border-white/20 hover:bg-slate-800/50' : ''} transition-all duration-300 h-full`}>
        {children}
      </div>
    </div>
  );
}

// Testimonial component
function Testimonial({ quote, author, role, firm }: { quote: string; author: string; role: string; firm: string }) {
  return (
    <GlassCard className="p-6" hover={false}>
      <Quote className="w-8 h-8 text-blue-500/30 mb-4" />
      <p className="text-slate-300 mb-6 leading-relaxed italic">"{quote}"</p>
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center text-white font-bold text-sm">
          {author.split(' ').map(n => n[0]).join('')}
        </div>
        <div>
          <div className="text-white font-medium text-sm">{author}</div>
          <div className="text-slate-500 text-xs">{role}, {firm}</div>
        </div>
      </div>
    </GlassCard>
  );
}

export default function HomePage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { scrollYProgress } = useScroll();
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.2], [1, 0.95]);

  const stats = [
    { label: 'Active Traders', value: 2847, suffix: '+', prefix: '' },
    { label: 'Trades Analyzed', value: 156432, suffix: '', prefix: '' },
    { label: 'Data Points', value: 12, suffix: 'M+', prefix: '' },
    { label: 'Avg Improvement', value: 34, suffix: '%', prefix: '+' },
  ];

  const features = [
    {
      icon: Brain,
      title: 'Behavioral Analytics',
      description: 'Identify psychological patterns that impact your P&L. Track emotional states and their correlation with trade outcomes.',
      color: 'violet'
    },
    {
      icon: Target,
      title: 'Edge Quantification',
      description: 'Statistical analysis of your setups. Know exactly which strategies work in specific market conditions.',
      color: 'blue'
    },
    {
      icon: Activity,
      title: 'Risk Intelligence',
      description: 'Real-time risk metrics and position sizing recommendations based on your historical performance.',
      color: 'emerald'
    },
    {
      icon: Zap,
      title: 'Pattern Recognition',
      description: 'AI-powered detection of recurring setups across thousands of historical trades.',
      color: 'amber'
    }
  ];

  const testimonials = [
    {
      quote: "Journex helped me identify that 73% of my losses came from trading the first hour. My win rate jumped 40% after adjusting.",
      author: "Michael Chen",
      role: "Senior Trader",
      firm: "Topstep"
    },
    {
      quote: "The psychological profiling is game-changing. I finally understand why I revenge trade and how to stop it.",
      author: "Sarah Williams",
      role: "Prop Trader",
      firm: "FTMO"
    },
    {
      quote: "Passed my prop firm evaluation on the first try using Journex analytics. The edge analysis is worth 10x the price.",
      author: "James Rodriguez",
      role: "Independent Trader",
      firm: "The5ers"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-blue-500/30 overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/5 bg-slate-950/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white group-hover:text-blue-400 transition-colors">
                JOURNEX
              </span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-8">
              <Link href="#features" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">Features</Link>
              <Link href="#analytics" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">Analytics</Link>
              <Link href="#testimonials" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">Testimonials</Link>
              <Link href="/login" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">Sign In</Link>
              <Link href="/signup">
                <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-all hover:shadow-lg hover:shadow-blue-500/25">
                  Get Started
                </button>
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button 
              className="md:hidden p-2 text-slate-400 hover:text-white"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden border-t border-white/5 bg-slate-950"
            >
              <div className="px-6 py-4 space-y-4">
                <Link href="#features" className="block text-slate-400 hover:text-white">Features</Link>
                <Link href="#analytics" className="block text-slate-400 hover:text-white">Analytics</Link>
                <Link href="#testimonials" className="block text-slate-400 hover:text-white">Testimonials</Link>
                <Link href="/login" className="block text-slate-400 hover:text-white">Sign In</Link>
                <Link href="/signup" className="block w-full py-2 bg-blue-600 text-white text-center rounded-lg">Get Started</Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      {/* Market Ticker */}
      <div className="pt-16">
        <MarketTicker />
      </div>

      {/* Hero Section */}
      <motion.section 
        style={{ opacity, scale }}
        className="relative min-h-[85vh] flex items-center justify-center px-6 pt-12 pb-24 overflow-hidden"
      >
        {/* Background Effects */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(59,130,246,0.15),transparent)]" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:64px_64px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]" />
        
        <div className="relative z-10 max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-medium mb-8"
          >
            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
            Now with AI-Powered Edge Analysis
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-white mb-6"
          >
            Trade Smarter.
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-violet-400 to-blue-400 bg-[length:200%_auto] animate-gradient">
              Journal Better.
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Professional-grade trading analytics that transform raw data into actionable edge. 
            Trusted by prop traders, hedge funds, and independent professionals.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
          >
            <Link href="/signup">
              <button className="group px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-all hover:shadow-xl hover:shadow-blue-500/25 flex items-center justify-center gap-2">
                Start Free Trial
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
            </Link>
            <Link href="/demo">
              <button className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold rounded-xl transition-all flex items-center justify-center gap-2">
                <Play className="w-4 h-4" />
                Watch Demo
              </button>
            </Link>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-3xl mx-auto"
          >
            {stats.map((stat, idx) => (
              <div key={idx} className="text-center">
                <div className="text-2xl md:text-3xl font-bold text-white tabular-nums">
                  <AnimatedCounter value={stat.value} prefix={stat.prefix} suffix={stat.suffix} />
                </div>
                <div className="text-xs text-slate-500 uppercase tracking-wider mt-1">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </motion.section>

      {/* Dashboard Preview */}
      <section id="analytics" className="relative py-24 px-6 border-y border-white/5 bg-slate-900/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Your Trading Command Center
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Institutional-grade analytics previously reserved for hedge funds. Now available to individual traders.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            {[
              { label: 'Total P&L', value: '+$24,532.40', change: '+12.4%', positive: true, chart: [40, 60, 45, 80, 65, 90, 85] },
              { label: 'Win Rate', value: '58.3%', change: '+3.2%', positive: true, chart: [30, 45, 40, 55, 50, 58, 58] },
              { label: 'Profit Factor', value: '1.67', change: '+0.23', positive: true, chart: [20, 35, 30, 45, 55, 60, 67] },
            ].map((metric, idx) => (
              <GlassCard key={idx} glow>
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-slate-400">{metric.label}</span>
                    <span className={`text-xs font-medium ${metric.positive ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {metric.change}
                    </span>
                  </div>
                  <div className="text-2xl font-bold text-white mb-4">{metric.value}</div>
                  <div className="h-12 flex items-end gap-1">
                    {metric.chart.map((h, i) => (
                      <div 
                        key={i} 
                        className="flex-1 bg-blue-500/20 rounded-sm hover:bg-blue-500/40 transition-colors"
                        style={{ height: `${h}%` }}
                      />
                    ))}
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>

          <GlassCard className="p-8 md:p-12" glow>
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-xs font-medium mb-6">
                  <Brain className="w-3 h-3" />
                  AI-Powered Insights
                </div>
                <h3 className="text-2xl md:text-3xl font-bold text-white mb-4">
                  Discover Your Hidden Edge
                </h3>
                <p className="text-slate-400 mb-6 leading-relaxed">
                  Our machine learning models analyze your trading history to identify patterns invisible to the naked eye. 
                  Understand which setups, timeframes, and market conditions maximize your profitability.
                </p>
                <ul className="space-y-3">
                  {[
                    'Setup performance by market regime',
                    'Psychological bias detection',
                    'Optimal risk parameters',
                    'Session-based edge analysis'
                  ].map((item, idx) => (
                    <li key={idx} className="flex items-center gap-3 text-slate-300 text-sm">
                      <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-violet-500 rounded-2xl blur-2xl opacity-20" />
                <div className="relative bg-slate-950 rounded-xl border border-white/10 p-6 font-mono text-sm">
                  <div className="flex items-center gap-2 mb-4 text-slate-500 border-b border-white/10 pb-3">
                    <Terminal className="w-4 h-4" />
                    <span>edge_analysis.py</span>
                  </div>
                  <div className="space-y-2 text-slate-300">
                    <div><span className="text-violet-400">class</span> <span className="text-blue-400">EdgeProfile</span>:</div>
                    <div className="pl-4"><span className="text-slate-500"># Analyzing 1,247 trades...</span></div>
                    <div className="pl-4">win_rate = <span className="text-emerald-400">0.583</span></div>
                    <div className="pl-4">profit_factor = <span className="text-emerald-400">1.67</span></div>
                    <div className="pl-4">optimal_risk = <span className="text-amber-400">1.5</span>%</div>
                    <div className="pl-4 mt-4"><span className="text-violet-400">def</span> <span className="text-blue-400">get_recommendation</span>(self):</div>
                    <div className="pl-8"><span className="text-violet-400">return</span> <span className="text-amber-400">"Avoid first hour trading"</span></div>
                  </div>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Everything You Need to Improve
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Comprehensive tools designed by traders, for traders. No fluff, just edge.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, idx) => (
              <GlassCard key={idx} className="p-6 group">
                <div className={`w-12 h-12 rounded-xl bg-${feature.color}-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <feature.icon className={`w-6 h-6 text-${feature.color}-400`} />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{feature.description}</p>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-24 px-6 bg-slate-900/30 border-y border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Trusted by Professional Traders
            </h2>
            <p className="text-slate-400">
              Join thousands of traders who have transformed their performance.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {testimonials.map((t, idx) => (
              <Testimonial key={idx} {...t} />
            ))}
          </div>
        </div>
      </section>

      {/* Security Section */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Bank-Grade Security
            </h2>
            <p className="text-slate-400">Your data is yours. Period.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Lock, title: 'End-to-End Encryption', desc: 'AES-256 encryption ensures your journal entries remain private.', color: 'emerald' },
              { icon: Shield, title: 'Zero-Knowledge Architecture', desc: 'We cannot read your data. Even if subpoenaed, we have nothing to provide.', color: 'blue' },
              { icon: Cloud, title: 'Secure Cloud Sync', desc: 'Encrypted backups across multiple regions with 99.99% uptime.', color: 'violet' },
            ].map((item, idx) => (
              <GlassCard key={idx} className="p-6 text-center">
                <div className={`w-14 h-14 mx-auto rounded-2xl bg-${item.color}-500/10 flex items-center justify-center mb-4`}>
                  <item.icon className={`w-7 h-7 text-${item.color}-400`} />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-sm text-slate-400">{item.desc}</p>
              </GlassCard>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <GlassCard className="p-12 text-center relative overflow-hidden" glow>
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-violet-500/10" />
            <div className="relative z-10">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Ready to Find Your Edge?
              </h2>
              <p className="text-slate-400 mb-8 max-w-xl mx-auto">
                Start your 14-day free trial today. No credit card required. Cancel anytime.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/signup">
                  <button className="px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-all hover:shadow-xl hover:shadow-blue-500/25 w-full sm:w-auto">
                    Get Started Free
                  </button>
                </Link>
                <Link href="/pricing">
                  <button className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-semibold rounded-xl transition-all w-full sm:w-auto">
                    View Pricing
                  </button>
                </Link>
              </div>
              <p className="mt-6 text-xs text-slate-500">
                Used by traders at Citadel, Jane Street, Two Sigma, and hundreds of prop firms worldwide.
              </p>
            </div>
          </GlassCard>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 bg-slate-950 py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-bold text-white">JOURNEX</span>
              </div>
              <p className="text-slate-500 text-sm">
                Professional trading journal and analytics platform for serious traders.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4 text-sm">Product</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><Link href="/features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4 text-sm">Resources</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><Link href="/university" className="hover:text-white transition-colors">Trading University</Link></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="/api" className="hover:text-white transition-colors">API</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4 text-sm">Company</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-slate-600 text-sm">© 2024 Journex. All rights reserved.</p>
            <div className="flex items-center gap-2 text-slate-500 text-sm">
              <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
              All Systems Operational
            </div>
          </div>
        </div>
      </footer>

      {/* Global Styles */}
      <style jsx global>{`
        @keyframes scroll-x {
          0% { transform: translateX(0); }
          100% { transform: translateX(-33.33%); }
        }
        .animate-scroll-x {
          animation: scroll-x 30s linear infinite;
        }
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .animate-gradient {
          animation: gradient 8s ease infinite;
        }
      `}</style>
    </div>
  );
}
