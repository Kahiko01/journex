"""
Optimized Kimi 2.5 Service with timeout handling
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class FastKimiService:
    def __init__(self):
        self.api_key = "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"
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.model = "moonshotai/kimi-k2.5"
        self.invoke_url = f"{self.base_url}/chat/completions"
        
    def chat_completion(self, messages: list, timeout: int = 30) -> Dict:
        """
        Send a chat completion request with timeout
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 1024,  # Reduced for faster response
                "temperature": 0.7,   # Lower temperature for faster, more deterministic responses
                "top_p": 0.9,
                "stream": False
            }
            
            logger.info(f"Sending request to Kimi with timeout={timeout}s")
            
            # Add timeout to prevent hanging
            response = requests.post(
                self.invoke_url,
                headers=headers,
                json=payload,
                timeout=timeout
            )
            
            response.raise_for_status()
            return response.json()
                
        except requests.exceptions.Timeout:
            logger.error("Kimi API request timed out")
            return self._get_fallback_response("timeout")
        except requests.exceptions.RequestException as e:
            logger.error(f"Kimi API request failed: {e}")
            return self._get_fallback_response("error")
    
    def _get_fallback_response(self, reason: str) -> Dict:
        """Return a fallback response when API fails"""
        if reason == "timeout":
            content = "I'm currently processing your request. The AI service is a bit slow right now. Please try again in a moment."
        else:
            content = "I'm having trouble connecting to the AI service. Please check your connection and try again."
        
        return {
            "choices": [{
                "message": {
                    "content": content,
                    "reasoning_content": "Fallback response due to API timeout"
                }
            }]
        }
    
    def quick_chat(self, message: str) -> str:
        """Quick chat method with simple prompt"""
        messages = [
            {"role": "system", "content": "You are a helpful trading assistant. Keep responses brief and under 100 words."},
            {"role": "user", "content": message}
        ]
        
        result = self.chat_completion(messages, timeout=15)  # 15 second timeout
        
        try:
            return result['choices'][0]['message']['content']
        except:
            return "I'm here to help with your trading questions. What would you like to know?"
