"""
Email Report Service
Automatically sends weekly trading reports to users
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import schedule
import time
import threading

from app.models.trade import Trade
from app.services.ai.report_generator import WeeklyReportGenerator

logger = logging.getLogger(__name__)

class EmailReportService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"  # Configure for your email provider
        self.smtp_port = 587
        self.sender_email = "reports@journex.com"  # Your email
        self.sender_password = "your-app-password"  # Use app password for Gmail
        self.report_generator = WeeklyReportGenerator()
        
    def send_report(self, user_email: str, user_id: int, db: Session):
        """Generate and send weekly report to user"""
        try:
            # Get last week's trades
            week_ago = datetime.now() - timedelta(days=7)
            trades = db.query(Trade).filter(
                Trade.user_id == user_id,
                Trade.exit_time >= week_ago
            ).all()
            
            if not trades:
                logger.info(f"No trades for user {user_id} this week")
                return
            
            # Calculate metrics
            metrics = self._calculate_metrics(trades)
            
            # Generate AI report
            report = self.report_generator.generate_report(
                user_id, metrics, trades
            )
            
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Your Weekly Trading Report - {datetime.now().strftime('%B %d, %Y')}"
            msg['From'] = self.sender_email
            msg['To'] = user_email
            
            # Create HTML version
            html = self._create_html_report(metrics, report)
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Weekly report sent to {user_email}")
            
        except Exception as e:
            logger.error(f"Error sending report: {e}")
    
    def _calculate_metrics(self, trades: List[Trade]) -> Dict:
        """Calculate weekly metrics"""
        winning = [t for t in trades if t.profit_loss and t.profit_loss > 0]
        losing = [t for t in trades if t.profit_loss and t.profit_loss < 0]
        
        total_pl = sum(t.profit_loss or 0 for t in trades)
        win_rate = (len(winning) / len(trades) * 100) if trades else 0
        
        gross_profit = sum(t.profit_loss or 0 for t in winning)
        gross_loss = abs(sum(t.profit_loss or 0 for t in losing))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit
        
        return {
            'total_pl': total_pl,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'best_trade': max((t.profit_loss or 0 for t in trades), default=0),
            'worst_trade': min((t.profit_loss or 0 for t in trades), default=0),
        }
    
    def _create_html_report(self, metrics: Dict, report: Dict) -> str:
        """Create HTML email template"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3B82F6, #8B5CF6); color: white; padding: 20px; text-align: center; border-radius: 10px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 20px 0; }}
                .metric {{ background: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #3B82F6; }}
                .metric-label {{ font-size: 12px; color: #6b7280; }}
                .report {{ background: white; border: 1px solid #e5e7eb; padding: 20px; border-radius: 10px; }}
                .footer {{ margin-top: 20px; font-size: 12px; color: #9ca3af; text-align: center; }}
                .positive {{ color: #10b981; }}
                .negative {{ color: #ef4444; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Weekly Trading Report</h1>
                    <p>{datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value {'positive' if metrics['total_pl'] > 0 else 'negative'}">
                            ${metrics['total_pl']:.2f}
                        </div>
                        <div class="metric-label">Total P/L</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{metrics['win_rate']:.1f}%</div>
                        <div class="metric-label">Win Rate</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{metrics['profit_factor']:.2f}</div>
                        <div class="metric-label">Profit Factor</div>
                    </div>
                </div>
                
                <div class="report">
                    <h2>AI Performance Analysis</h2>
                    <p>{report.get('summary', '')}</p>
                    
                    <h3>Key Strengths</h3>
                    <ul>
                        {self._list_to_html(report.get('strengths', []))}
                    </ul>
                    
                    <h3>Areas for Improvement</h3>
                    <ul>
                        {self._list_to_html(report.get('improvements', []))}
                    </ul>
                    
                    <h3>Action Items for Next Week</h3>
                    <ol>
                        {self._list_to_html(report.get('actions', []), 'ol')}
                    </ol>
                    
                    <p style="margin-top: 20px; font-style: italic;">
                        {report.get('closing_note', '')}
                    </p>
                </div>
                
                <div class="footer">
                    <p>This report was generated by Journex AI. For more insights, log in to your dashboard.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _list_to_html(self, items: List, type: str = 'ul') -> str:
        if not items:
            return '<li>No items</li>'
        return ''.join([f'<li>{item}</li>' for item in items])
    
    def start_scheduler(self, db_session_factory):
        """Start the weekly report scheduler"""
        def job():
            # This would need user email mapping
            # For now, just a placeholder
            logger.info("Running weekly report job...")
            
        schedule.every().monday.at("09:00").do(job)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        logger.info("Weekly report scheduler started")
