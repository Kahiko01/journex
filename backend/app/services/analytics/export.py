import csv
import io
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import matplotlib.pyplot as plt
import tempfile
from fastapi import Response
from app.models.trade import Trade
from app.services.analytics.advanced_metrics import AdvancedMetricsService
import numpy as np

class ExportService:
    def __init__(self, db_session, user_id):
        self.db = db_session
        self.user_id = user_id
        self.metrics_service = AdvancedMetricsService(db_session, user_id)
    
    def export_csv(self, start_date=None, end_date=None, strategy=None):
        """Export trade data as CSV"""
        query = self.db.query(Trade).filter(Trade.user_id == self.user_id)
        
        if start_date:
            query = query.filter(Trade.exit_time >= start_date)
        if end_date:
            query = query.filter(Trade.exit_time <= end_date)
        if strategy:
            query = query.filter(Trade.strategy == strategy)
        
        trades = query.order_by(Trade.exit_time).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'Date', 'Symbol', 'Direction', 'Entry Price', 'Exit Price',
            'Lot Size', 'Profit/Loss', 'R-Multiple', 'Strategy',
            'Emotion', 'Rating', 'MAE', 'MFE'
        ])
        
        # Write data
        for trade in trades:
            writer.writerow([
                trade.exit_time.strftime('%Y-%m-%d %H:%M') if trade.exit_time else '',
                trade.symbol,
                trade.direction,
                trade.entry_price,
                trade.exit_price,
                trade.lot_size,
                trade.profit_loss,
                trade.r_multiple,
                trade.strategy,
                trade.emotion,
                trade.rating,
                trade.mae,
                trade.mfe
            ])
        
        return Response(
            content=output.getvalue(),
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename=journex_export_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
    
    def export_pdf(self, start_date=None, end_date=None, strategy=None):
        """Generate professional PDF report"""
        # Calculate metrics
        core = self.metrics_service.calculate_core_metrics()
        risk = self.metrics_service.calculate_risk_metrics()
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#3B82F6'),
            spaceAfter=30
        )
        
        # Title
        story.append(Paragraph(f"Journex Trading Report", title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        summary_data = [
            ['Metric', 'Value', 'Metric', 'Value'],
            ['Total P/L', f"${core['total_pl']:,.2f}", 'Win Rate', f"{core['win_rate']}%"],
            ['Profit Factor', f"{core['profit_factor']:.2f}", 'Expectancy', f"${core['expectancy']:.2f}"],
            ['Sharpe Ratio', f"{risk['sharpe_ratio']:.2f}", 'Max Drawdown', f"{risk['max_drawdown_pct']:.1f}%"],
            ['Total Trades', str(core['total_trades']), 'Avg R', f"{core['avg_r']:.2f}"]
        ]
        
        table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#1F2937')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#374151'))
        ]))
        story.append(table)
        story.append(Spacer(1, 30))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return Response(
            content=buffer.getvalue(),
            media_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename=journex_report_{datetime.now().strftime("%Y%m%d")}.pdf'}
        )
