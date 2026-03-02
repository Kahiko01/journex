"""
Kimi 2.5 Service for NVIDIA API
Direct implementation using your API key and endpoint
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, Generator
from app.core.ai_config import AIConfig

logger = logging.getLogger(__name__)

class KimiService:
    def __init__(self):
        self.api_key = AIConfig.API_KEY
        self.base_url = AIConfig.BASE_URL
        self.model = AIConfig.MODEL
        self.invoke_url = f"{self.base_url}/chat/completions"
        
    def _get_headers(self, stream: bool = False) -> Dict:
        """Get headers for API request"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "text/event-stream" if stream else "application/json",
            "Content-Type": "application/json"
        }
    
    def _prepare_payload(self, messages: list, stream: bool = False, thinking: bool = True) -> Dict:
        """Prepare payload in the format your API expects"""
        return {
            "model": self.model,
            "messages": messages,
            "max_tokens": AIConfig.MAX_TOKENS,
            "temperature": AIConfig.TEMPERATURE,
            "top_p": AIConfig.TOP_P,
            "stream": stream,
            "chat_template_kwargs": {"thinking": thinking}
        }
    
    def chat_completion(self, messages: list, stream: bool = False) -> Dict:
        """
        Send a chat completion request to Kimi 2.5
        
        Args:
            messages: List of message objects [{"role": "user", "content": "..."}]
            stream: Whether to stream the response
        
        Returns:
            API response as dictionary
        """
        try:
            payload = self._prepare_payload(messages, stream)
            headers = self._get_headers(stream)
            
            logger.info(f"Sending request to Kimi 2.5 with {len(messages)} messages")
            
            response = requests.post(
                self.invoke_url,
                headers=headers,
                json=payload,
                stream=stream
            )
            
            if stream:
                return self._handle_stream(response)
            else:
                response.raise_for_status()
                return response.json()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"error": str(e), "fallback": True}
    
    def _handle_stream(self, response):
        """Handle streaming response"""
        collected_messages = []
        
        for line in response.iter_lines():
            if line:
                try:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data != '[DONE]':
                            chunk = json.loads(data)
                            if chunk.get('choices'):
                                content = chunk['choices'][0].get('delta', {}).get('content', '')
                                if content:
                                    collected_messages.append(content)
                                    print(content, end='', flush=True)
                except Exception as e:
                    logger.error(f"Error parsing stream: {e}")
        
        return {"content": ''.join(collected_messages)}
    
    def analyze_with_prompt(self, system_prompt: str, user_prompt: str) -> str:
        """
        Simple interface for analysis tasks
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        result = self.chat_completion(messages, stream=False)
        
        if "error" in result:
            logger.error(f"Analysis failed: {result['error']}")
            return "Analysis unavailable at this time."
        
        try:
            return result['choices'][0]['message']['content']
        except (KeyError, IndexError):
            return str(result)
    
    def analyze_trade(self, trade_data: dict, user_history: list = None) -> dict:
        """
        Specialized method for trade analysis
        """
        system_prompt = """You are an expert trading psychologist and performance coach. 
        Analyze trades for emotional patterns, discipline breaks, and improvement opportunities.
        Be direct, honest, and actionable. Focus on psychology, not just numbers.
        
        Return your analysis as a JSON object with these exact fields:
        {
            "discipline_score": 0-100,
            "emotional_state": "detected emotion",
            "rule_violations": ["list", "of", "violations"],
            "strengths": ["list", "of", "strengths"],
            "improvements": ["list", "of", "improvements"],
            "psychological_insight": "detailed insight"
        }
        """
        
        trade_info = f"""
        Trade Data:
        - Symbol: {trade_data.get('symbol')}
        - Direction: {trade_data.get('direction')}
        - P/L: ${trade_data.get('profit_loss', 0):.2f}
        - R-Multiple: {trade_data.get('r_multiple', 0):.2f}
        - Strategy: {trade_data.get('strategy', 'N/A')}
        - Emotion logged: {trade_data.get('emotion', 'N/A')}
        - Session: {self._get_session(trade_data)}
        
        Recent Trade Count: {len(user_history) if user_history else 0}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": trade_info}
        ]
        
        result = self.chat_completion(messages, stream=False)
        
        try:
            content = result['choices'][0]['message']['content']
            # Try to extract JSON from the response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Return structured fallback
                return {
                    "discipline_score": 75,
                    "emotional_state": trade_data.get('emotion', 'neutral'),
                    "rule_violations": [],
                    "strengths": ["Trade executed"],
                    "improvements": ["Review for patterns"],
                    "psychological_insight": content[:200]
                }
        except Exception as e:
            logger.error(f"Failed to parse trade analysis: {e}")
            return self._generate_fallback_analysis(trade_data)
    
    def _get_session(self, trade):
        """Determine trading session from hour"""
        if not trade.get('exit_time'):
            return 'unknown'
        try:
            hour = int(trade['exit_time'].split('T')[1].split(':')[0])
            if 0 <= hour < 8: return 'Asia'
            if 8 <= hour < 16: return 'London'
            return 'New York'
        except:
            return 'unknown'
    
    def _generate_fallback_analysis(self, trade: dict) -> dict:
        """Basic analysis when AI is unavailable"""
        pl = trade.get('profit_loss', 0)
        return {
            "discipline_score": 70 if abs(pl) < 100 else 50,
            "emotional_state": trade.get('emotion', 'unknown'),
            "rule_violations": [],
            "strengths": ["Trade executed" if pl > 0 else "Risk managed"],
            "improvements": ["Review entry timing"],
            "psychological_insight": "Basic analysis (AI unavailable)"
        }
    
    def generate_weekly_report(self, metrics: dict, trades: list) -> str:
        """
        Generate weekly trading report
        """
        system_prompt = """You are a professional trading coach. Generate a comprehensive weekly report.
        Be encouraging but honest. Focus on actionable insights."""
        
        # Summarize trades
        winning_trades = [t for t in trades if t.get('profit_loss', 0) > 0]
        losing_trades = [t for t in trades if t.get('profit_loss', 0) < 0]
        
        user_prompt = f"""
        Weekly Trading Summary:
        - Total Trades: {len(trades)}
        - Winning Trades: {len(winning_trades)}
        - Losing Trades: {len(losing_trades)}
        - Win Rate: {metrics.get('win_rate', 0):.1f}%
        - Total P/L: ${metrics.get('total_pl', 0):.2f}
        - Profit Factor: {metrics.get('profit_factor', 0):.2f}
        - Best Trade: ${metrics.get('best_trade', 0):.2f}
        - Worst Trade: ${metrics.get('worst_trade', 0):.2f}
        
        Please provide:
        1. Overall performance summary
        2. Key strengths
        3. Areas for improvement
        4. 3 specific actionable recommendations for next week
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        result = self.chat_completion(messages, stream=False)
        
        try:
            return result['choices'][0]['message']['content']
        except:
            return "Weekly report generation failed."
