"""
AI Features API Endpoints for Kimi 2.5 Integration
Using PostgreSQL database instead of in-memory trades_db
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from app.db.session import get_db
from app.models.trade import Trade
from app.services.ai.kimi_service import KimiService
from app.services.ai.analysis_service import AITradeAnalysisService
from app.services.ai.support_service import AISupportService
from app.services.ai.report_generator import WeeklyReportGenerator
import traceback
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Define router FIRST
router = APIRouter(prefix="/ai", tags=["ai"])

# Initialize services
kimi_service = KimiService()
analysis_service = AITradeAnalysisService()
support_service = AISupportService()
report_generator = WeeklyReportGenerator()

# Pydantic models for request bodies
class SupportRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str
    stream: bool = False
    thinking: bool = True

class BatchAnalyzeRequest(BaseModel):
    trade_ids: List[int]

@router.post("/chat")
async def chat_with_kimi(
    request: ChatRequest,
    user_id: int = Query(1)
):
    """
    Direct chat with Kimi 2.5
    """
    try:
        messages = [
            {"role": "system", "content": "You are a helpful trading assistant."},
            {"role": "user", "content": request.message}
        ]
        
        result = kimi_service.chat_completion(messages, stream=request.stream)
        return result
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-trade/{trade_id}")
async def analyze_trade(
    trade_id: int,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered analysis of a specific trade using Kimi 2.5
    """
    try:
        # Get trade from database
        trade = db.query(Trade).filter(
            Trade.id == trade_id,
            Trade.user_id == user_id
        ).first()
        
        if not trade:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        # Convert to dict for analysis
        trade_dict = {
            'id': trade.id,
            'symbol': trade.symbol,
            'direction': trade.direction,
            'entry_price': trade.entry_price,
            'exit_price': trade.exit_price,
            'lot_size': trade.lot_size,
            'profit_loss': trade.profit_loss,
            'r_multiple': trade.r_multiple,
            'strategy': trade.strategy,
            'emotion': trade.emotion,
            'rating': trade.rating,
            'entry_time': trade.entry_time.isoformat() if trade.entry_time else None,
            'exit_time': trade.exit_time.isoformat() if trade.exit_time else None,
        }
        
        # Get recent history for context
        recent_trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.id != trade_id
        ).order_by(Trade.exit_time.desc()).limit(10).all()
        
        recent_list = []
        for t in recent_trades:
            recent_list.append({
                'id': t.id,
                'profit_loss': t.profit_loss,
                'emotion': t.emotion,
                'exit_time': t.exit_time.isoformat() if t.exit_time else None
            })
        
        # Analyze using Kimi
        analysis = analysis_service.analyze_trade(trade_dict, recent_list)
        
        return {
            "trade_id": trade_id,
            "analysis": analysis,
            "model": kimi_service.model if hasattr(kimi_service, 'model') else "moonshotai/kimi-k2.5"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing trade: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-batch")
async def analyze_batch_trades(
    request: BatchAnalyzeRequest,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """
    Analyze multiple trades in batch
    """
    try:
        trades = db.query(Trade).filter(
            Trade.id.in_(request.trade_ids),
            Trade.user_id == user_id
        ).all()
        
        # Get all user trades for context
        all_user_trades = db.query(Trade).filter(
            Trade.user_id == user_id
        ).order_by(Trade.exit_time.desc()).limit(50).all()
        
        context_list = []
        for t in all_user_trades:
            context_list.append({
                'id': t.id,
                'profit_loss': t.profit_loss,
                'emotion': t.emotion
            })
        
        results = []
        for trade in trades:
            trade_dict = {
                'id': trade.id,
                'symbol': trade.symbol,
                'direction': trade.direction,
                'profit_loss': trade.profit_loss,
                'emotion': trade.emotion,
                'strategy': trade.strategy,
            }
            analysis = analysis_service.analyze_trade(trade_dict, context_list)
            results.append({
                "trade_id": trade.id,
                "analysis": analysis
            })
        
        return {
            "analyzed": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/support")
async def get_support(
    request: SupportRequest,
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """
    Get AI support response with context
    """
    try:
        # Get user context from database
        trades = db.query(Trade).filter(
            Trade.user_id == user_id
        ).order_by(Trade.exit_time.desc()).limit(50).all()
        
        # Calculate basic metrics for context
        context = request.context
        if trades and not context:
            recent_pl = sum(t.profit_loss or 0 for t in trades[:20])
            winning = [t for t in trades if t.profit_loss and t.profit_loss > 0]
            win_rate = (len(winning) / len(trades) * 100) if trades else 0
            
            context = {
                'recent_pl': recent_pl,
                'win_rate': win_rate,
                'total_trades': len(trades)
            }
        
        response = support_service.get_response(user_id, request.message, context)
        
        return {
            "response": response,
            "user_id": user_id
        }
        
    except Exception as e:
        logger.error(f"Support error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weekly-report")
async def get_weekly_report(
    user_id: int = Query(1),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered weekly trading report using Kimi 2.5
    """
    try:
        # Calculate date range for last week
        week_ago = datetime.now() - timedelta(days=7)
        
        # Get trades from last week
        week_trades = db.query(Trade).filter(
            Trade.user_id == user_id,
            Trade.exit_time >= week_ago
        ).order_by(Trade.exit_time).all()
        
        if not week_trades:
            return {"message": "No trades in the last week"}
        
        # Calculate weekly metrics
        winning_trades = [t for t in week_trades if t.profit_loss and t.profit_loss > 0]
        losing_trades = [t for t in week_trades if t.profit_loss and t.profit_loss < 0]
        
        total_pl = sum(t.profit_loss or 0 for t in week_trades)
        win_rate = (len(winning_trades) / len(week_trades) * 100) if week_trades else 0
        
        gross_profit = sum(t.profit_loss or 0 for t in winning_trades)
        gross_loss = abs(sum(t.profit_loss or 0 for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit
        
        # Convert trades to dict for analysis
        trade_list = []
        for t in week_trades:
            trade_list.append({
                'id': t.id,
                'symbol': t.symbol,
                'direction': t.direction,
                'profit_loss': t.profit_loss,
                'emotion': t.emotion,
                'strategy': t.strategy,
                'exit_time': t.exit_time.isoformat() if t.exit_time else None
            })
        
        weekly_metrics = {
            'total_pl': total_pl,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'total_trades': len(week_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'best_trade': max((t.profit_loss or 0 for t in week_trades), default=0),
            'worst_trade': min((t.profit_loss or 0 for t in week_trades), default=0),
        }
        
        # Generate report
        report = report_generator.generate_report(user_id, weekly_metrics, trade_list)
        
        return report
        
    except Exception as e:
        logger.error(f"Report generation error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/conversation/reset")
async def reset_conversation(user_id: int = Query(1)):
    """
    Reset the AI support conversation for a user
    """
    try:
        if hasattr(support_service, 'conversations') and user_id in support_service.conversations:
            del support_service.conversations[user_id]
        return {"message": "Conversation reset", "user_id": user_id}
    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_model_info():
    """
    Get information about the current AI model
    """
    return {
        "model": kimi_service.model if hasattr(kimi_service, 'model') else "moonshotai/kimi-k2.5",
        "provider": "NVIDIA API",
        "capabilities": {
            "thinking": True,
            "max_tokens": 16384,
            "temperature_range": [0, 2]
        }
    }
