"""
AI Customer Care Service
Uses Kimi 2.5 for intelligent support
"""

from app.services.ai.kimi_service import KimiService
import logging

logger = logging.getLogger(__name__)

class AISupportService:
    def __init__(self):
        self.kimi = KimiService()
        self.conversations = {}
    
    def get_response(self, user_id: int, message: str, context: dict = None) -> str:
        """Get AI support response"""
        
        system_prompt = """You are JournexAI, a professional trading support assistant. 
        You help traders with:
        - Platform features and navigation
        - Trading psychology and discipline
        - Performance analysis interpretation
        - Risk management questions
        
        Be supportive, knowledgeable, and concise. Use trading terminology correctly.
        """
        
        # Build conversation history
        if user_id not in self.conversations:
            self.conversations[user_id] = [
                {"role": "system", "content": system_prompt}
            ]
        
        # Add context if available
        enhanced_message = message
        if context:
            context_str = f"[User Context: "
            if context.get('recent_pl'):
                context_str += f"Recent P/L: ${context['recent_pl']:.2f}, "
            if context.get('win_rate'):
                context_str += f"Win Rate: {context['win_rate']:.1f}%, "
            context_str += "]"
            enhanced_message = f"{context_str}\n\n{message}"
        
        # Add user message
        self.conversations[user_id].append({"role": "user", "content": enhanced_message})
        
        # Keep conversation manageable
        if len(self.conversations[user_id]) > 11:  # system + 5 exchanges
            self.conversations[user_id] = [self.conversations[user_id][0]] + self.conversations[user_id][-10:]
        
        try:
            result = self.kimi.chat_completion(self.conversations[user_id], stream=False)
            
            if "error" in result:
                return f"Sorry, I'm having trouble connecting. Please try again. (Error: {result['error']})"
            
            reply = result['choices'][0]['message']['content']
            self.conversations[user_id].append({"role": "assistant", "content": reply})
            
            return reply
            
        except Exception as e:
            logger.error(f"Support service error: {e}")
            return "I'm here to help! Could you please rephrase your question?"
