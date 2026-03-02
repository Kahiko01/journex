"""
Weekly Performance Report Generator
Uses Kimi 2.5 for comprehensive analysis
"""

from app.services.ai.kimi_service import KimiService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WeeklyReportGenerator:
    def __init__(self):
        self.kimi = KimiService()
    
    def generate_report(self, user_id: int, metrics: dict, trades: list) -> dict:
        """Generate comprehensive weekly report"""
        
        # Prepare trade summary
        winning_trades = [t for t in trades if t.get('profit_loss', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit_loss', 0) < 0]
        
        # Get performance analysis
        perf_analysis = self._analyze_performance(metrics, trades)
        
        # Get psychological insights
        psych_insights = self._analyze_psychology(trades)
        
        # Get recommendations
        recommendations = self._generate_recommendations(metrics, trades)
        
        # Generate HTML report
        html_report = self._create_html_report(metrics, {
            'performance': perf_analysis,
            'psychology': psych_insights,
            'recommendations': recommendations
        })
        
        return {
            "html": html_report,
            "metrics": metrics,
            "insights": {
                "performance": perf_analysis,
                "psychology": psych_insights,
                "recommendations": recommendations
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def _analyze_performance(self, metrics: dict, trades: list) -> str:
        """Analyze trading performance"""
        prompt = f"""
        Analyze this trader's weekly performance:
        - Total Trades: {len(trades)}
        - Win Rate: {metrics.get('win_rate', 0):.1f}%
        - Profit Factor: {metrics.get('profit_factor', 0):.2f}
        - Total P/L: ${metrics.get('total_pl', 0):.2f}
        
        Provide a concise performance analysis (3-4 sentences).
        """
        
        return self.kimi.analyze_with_prompt(
            "You are a professional trading performance analyst.",
            prompt
        )
    
    def _analyze_psychology(self, trades: list) -> str:
        """Analyze psychological patterns"""
        # Count emotions
        emotions = {}
        for trade in trades:
            emotion = trade.get('emotion', 'unknown')
            emotions[emotion] = emotions.get(emotion, 0) + 1
        
        prompt = f"""
        Analyze the psychological patterns in these {len(trades)} trades:
        Emotional distribution: {emotions}
        
        Provide psychological insights and recommendations (3-4 sentences).
        """
        
        return self.kimi.analyze_with_prompt(
            "You are a trading psychologist specializing in behavioral finance.",
            prompt
        )
    
    def _generate_recommendations(self, metrics: dict, trades: list) -> str:
        """Generate actionable recommendations"""
        prompt = f"""
        Based on this trader's weekly data, provide 3 specific, actionable recommendations.
        Focus on concrete improvements they can make next week.
        
        Keep recommendations brief and actionable (1 sentence each).
        """
        
        return self.kimi.analyze_with_prompt(
            "You are a trading coach providing actionable advice.",
            prompt
        )
    
    def _create_html_report(self, metrics: dict, insights: dict) -> str:
        """Generate HTML report"""
        # Your existing HTML template here (same as before)
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Journex Weekly Trading Report</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                       background: #111827; color: #fff; line-height: 1.6; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ text-align: center; padding: 40px 20px; 
                         background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
                         border-radius: 16px; margin-bottom: 30px; }}
                .header h1 {{ font-size: 2.5em; margin: 0; }}
                .header p {{ color: rgba(255,255,255,0.9); font-size: 1.2em; }}
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                                gap: 20px; margin-bottom: 30px; }}
                .metric-card {{ background: #1F2937; padding: 25px; border-radius: 12px;
                               border: 1px solid #374151; text-align: center; }}
                .metric-card h3 {{ color: #9CA3AF; font-size: 0.9em; text-transform: uppercase;
                                  letter-spacing: 1px; margin: 0 0 10px 0; }}
                .metric-card .value {{ font-size: 2.5em; font-weight: bold; color: #3B82F6; }}
                .insight-section {{ background: #1F2937; padding: 30px; border-radius: 12px;
                                   border: 1px solid #374151; margin-bottom: 30px; }}
                .insight-section h2 {{ color: #3B82F6; margin-top: 0; }}
                .footer {{ text-align: center; margin-top: 40px; color: #6B7280; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Journex Weekly Trading Report</h1>
                    <p>Generated on {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Total P/L</h3>
                        <div class="value">${metrics.get('total_pl', 0):.2f}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Win Rate</h3>
                        <div class="value">{metrics.get('win_rate', 0):.1f}%</div>
                    </div>
                    <div class="metric-card">
                        <h3>Profit Factor</h3>
                        <div class="value">{metrics.get('profit_factor', 0):.2f}</div>
                    </div>
                    <div class="metric-card">
                        <h3>Total Trades</h3>
                        <div class="value">{metrics.get('total_trades', 0)}</div>
                    </div>
                </div>
                
                <div class="insight-section">
                    <h2>📈 Performance Analysis</h2>
                    <p>{insights.get('performance', 'Analysis unavailable')}</p>
                </div>
                
                <div class="insight-section">
                    <h2>🧠 Psychological Insights</h2>
                    <p>{insights.get('psychology', 'Analysis unavailable')}</p>
                </div>
                
                <div class="insight-section">
                    <h2>🎯 Recommendations</h2>
                    <p>{insights.get('recommendations', 'No recommendations available')}</p>
                </div>
                
                <div class="footer">
                    <p>Powered by Kimi 2.5 AI • Journex Trading Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
