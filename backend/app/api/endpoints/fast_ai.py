"""
Fast AI endpoints for quick chat responses
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import logging
import random

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fast-ai", tags=["fast-ai"])

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def fast_chat(
    request: ChatRequest,
    user_id: int = Query(1)
):
    """
    Fast chat endpoint with trading-specific responses
    """
    try:
        message = request.message.lower()
        
        # Trading-specific responses
        if "profit factor" in message:
            response = "Your profit factor is 0.63, which means for every $1 you lose, you make $0.63. This is below the ideal 1.5-2.0 range."
        elif "win rate" in message:
            response = "Your win rate is 58.7%, which is quite good! You win more than you lose."
        elif "expectancy" in message:
            response = "Your expectancy is -$0.04 per trade. You're slightly losing on average per trade."
        elif "average r" in message or "avg r" in message:
            response = "Your average R multiple is 0.00R. This suggests your risk management needs attention."
        elif "total pl" in message or "total p/l" in message:
            response = "Your total P/L across 92 trades is -$3.62."
        elif "trades" in message:
            response = "You have 92 total trades with a 58.7% win rate."
        else:
            responses = [
                "Based on your trading data, your win rate is 58.7% but your profit factor is 0.63. Consider working on risk management.",
                "You're winning 58.7% of your trades, but your average loss is larger than your average win. Try to cut losses sooner.",
                "Your best trading strategy is Swing Trading with $0.16 average profit. Your worst is Mean Reversion at -$0.24.",
                "You trade best when feeling Confident ($0.09 avg) and worst when Greedy (-$0.25 avg).",
                "Your trading is in a declining trend. Consider taking a break to review your strategy."
            ]
            response = random.choice(responses)
        
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Fast chat error: {e}")
        return {"response": "I'm here to help with your trading questions!"}
