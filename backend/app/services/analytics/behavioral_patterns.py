"""
Behavioral Pattern Detection Service
Identifies psychological patterns and emotional biases in trading
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from scipy import stats

class BehavioralPatternService:
    
    def analyze_patterns(self, trades: List[Dict]) -> Dict[str, Any]:
        """
        Comprehensive behavioral pattern analysis
        """
        if not trades:
            return self._empty_response()
        
        # Sort trades by date
        trades = sorted(trades, key=lambda x: x.get('exit_time', ''))
        
        # Overtrading detection
        overtrading = self._detect_overtrading(trades)
        
        # Revenge trading detection
        revenge_trading = self._detect_revenge_trading(trades)
        
        # Emotional bias patterns
        emotional_patterns = self._analyze_emotional_patterns(trades)
        
        # Post-loss behavior
        post_loss = self._analyze_post_loss_behavior(trades)
        
        # Win-chasing behavior
        win_chasing = self._detect_win_chasing(trades)
        
        # Time-based patterns
        time_patterns = self._analyze_time_patterns(trades)
        
        # Consecutive streaks
        streaks = self._analyze_streaks(trades)
        
        return {
            "overtrading": overtrading,
            "revenge_trading": revenge_trading,
            "emotional_patterns": emotional_patterns,
            "post_loss_behavior": post_loss,
            "win_chasing": win_chasing,
            "time_patterns": time_patterns,
            "streaks": streaks,
            "behavioral_score": self._calculate_behavioral_score(trades)
        }
    
    def _detect_overtrading(self, trades: List[Dict]) -> Dict[str, Any]:
        """Detect overtrading patterns"""
        if len(trades) < 10:
            return {"detected": False, "score": 0, "clusters": []}
        
        # Group by day
        daily_trades = defaultdict(list)
        for trade in trades:
            if trade.get('exit_time'):
                date = trade['exit_time'].split('T')[0]
                daily_trades[date].append(trade)
        
        # Calculate statistics
        daily_counts = [len(t) for t in daily_trades.values()]
        avg_daily = np.mean(daily_counts)
        std_daily = np.std(daily_counts) if len(daily_counts) > 1 else 0
        
        # Detect overtrading days (more than 2 std deviations above mean)
        threshold = avg_daily + 2 * std_daily
        overtrading_days = []
        
        for date, day_trades in daily_trades.items():
            if len(day_trades) > threshold and threshold > 3:
                # Analyze these trades
                pls = [t.get('profit_loss', 0) for t in day_trades]
                avg_pl = np.mean(pls)
                
                overtrading_days.append({
                    "date": date,
                    "trade_count": len(day_trades),
                    "avg_pl": round(avg_pl, 2),
                    "total_pl": round(sum(pls), 2),
                    "profitable": avg_pl > 0
                })
        
        # Calculate overtrading score (percentage of days that are overtrading)
        overtrading_score = len(overtrading_days) / len(daily_trades) * 100 if daily_trades else 0
        
        return {
            "detected": len(overtrading_days) > 0,
            "score": round(overtrading_score, 2),
            "clusters": overtrading_days,
            "avg_daily_trades": round(avg_daily, 1),
            "max_daily_trades": max(daily_counts) if daily_counts else 0,
            "threshold": round(threshold, 1)
        }
    
    def _detect_revenge_trading(self, trades: List[Dict]) -> Dict[str, Any]:
        """Detect revenge trading patterns (trading immediately after loss)"""
        revenge_instances = []
        
        for i in range(1, len(trades)):
            prev_trade = trades[i-1]
            curr_trade = trades[i]
            
            # Check if previous trade was a loss
            if prev_trade.get('profit_loss', 0) < 0:
                # Check time difference (within 30 minutes)
                if prev_trade.get('exit_time') and curr_trade.get('exit_time'):
                    try:
                        prev_time = datetime.fromisoformat(prev_trade['exit_time'].replace('Z', '+00:00'))
                        curr_time = datetime.fromisoformat(curr_trade['exit_time'].replace('Z', '+00:00'))
                        
                        time_diff = (curr_time - prev_time).total_seconds() / 60
                        
                        if time_diff < 30:  # Within 30 minutes
                            revenge_instances.append({
                                "date": curr_trade['exit_time'].split('T')[0],
                                "time": curr_trade['exit_time'],
                                "prev_loss": round(prev_trade.get('profit_loss', 0), 2),
                                "current_pl": round(curr_trade.get('profit_loss', 0), 2),
                                "symbol": curr_trade.get('symbol', ''),
                                "time_diff_min": round(time_diff, 1)
                            })
                    except:
                        continue
        
        # Calculate statistics
        if revenge_instances:
            avg_pl = np.mean([i["current_pl"] for i in revenge_instances])
            profitable_count = len([i for i in revenge_instances if i["current_pl"] > 0])
        else:
            avg_pl = 0
            profitable_count = 0
        
        return {
            "detected": len(revenge_instances) > 0,
            "instances": revenge_instances[-10:],  # Last 10 instances
            "total_count": len(revenge_instances),
            "avg_pl": round(avg_pl, 2),
            "profitable_percentage": round(profitable_count / len(revenge_instances) * 100, 2) if revenge_instances else 0,
            "severity": "high" if len(revenge_instances) > len(trades) * 0.1 else "medium" if len(revenge_instances) > len(trades) * 0.05 else "low"
        }
    
    def _analyze_emotional_patterns(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns based on emotional tagging"""
        emotion_data = defaultdict(lambda: {"count": 0, "total_pl": 0, "pls": [], "avg_r": []})
        
        for trade in trades:
            emotion = trade.get('emotion', 'unknown')
            if not emotion or emotion == 'unknown':
                emotion = 'not_logged'
            
            emotion_data[emotion]["count"] += 1
            emotion_data[emotion]["total_pl"] += trade.get('profit_loss', 0)
            emotion_data[emotion]["pls"].append(trade.get('profit_loss', 0))
            emotion_data[emotion]["avg_r"].append(trade.get('r_multiple', 0))
        
        # Calculate statistics for each emotion
        emotion_stats = []
        for emotion, data in emotion_data.items():
            if data["count"] > 0:
                avg_pl = np.mean(data["pls"]) if data["pls"] else 0
                avg_r = np.mean(data["avg_r"]) if data["avg_r"] else 0
                win_rate = len([p for p in data["pls"] if p > 0]) / data["count"] * 100
                
                emotion_stats.append({
                    "emotion": emotion,
                    "count": data["count"],
                    "percentage": round(data["count"] / len(trades) * 100, 2),
                    "avg_pl": round(avg_pl, 2),
                    "avg_r": round(avg_r, 2),
                    "total_pl": round(data["total_pl"], 2),
                    "win_rate": round(win_rate, 2),
                    "color": self._get_emotion_color(emotion)
                })
        
        # Sort by count
        emotion_stats = sorted(emotion_stats, key=lambda x: x["count"], reverse=True)
        
        # Create frequency chart data
        frequency_data = []
        for stat in emotion_stats[:10]:  # Top 10 emotions
            frequency_data.append({
                "emotion": stat["emotion"],
                "count": stat["count"],
                "avg_pl": stat["avg_pl"],
                "win_rate": stat["win_rate"]
            })
        
        return {
            "emotion_stats": emotion_stats,
            "frequency_chart": frequency_data,
            "most_common_emotion": emotion_stats[0]["emotion"] if emotion_stats else "none",
            "best_emotion": max(emotion_stats, key=lambda x: x["avg_pl"])["emotion"] if emotion_stats else "none",
            "worst_emotion": min(emotion_stats, key=lambda x: x["avg_pl"])["emotion"] if emotion_stats else "none"
        }
    
    def _analyze_post_loss_behavior(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze behavior after taking a loss"""
        if len(trades) < 5:
            return {"patterns": [], "avg_recovery": 0}
        
        loss_indices = [i for i, t in enumerate(trades) if t.get('profit_loss', 0) < 0]
        
        post_loss_behaviors = []
        
        for idx in loss_indices:
            if idx < len(trades) - 1:
                next_trade = trades[idx + 1]
                
                # Check if next trade was taken soon after loss
                time_diff = None
                if trades[idx].get('exit_time') and next_trade.get('exit_time'):
                    try:
                        loss_time = datetime.fromisoformat(trades[idx]['exit_time'].replace('Z', '+00:00'))
                        next_time = datetime.fromisoformat(next_trade['exit_time'].replace('Z', '+00:00'))
                        time_diff = (next_time - loss_time).total_seconds() / 60
                    except:
                        pass
                
                post_loss_behaviors.append({
                    "loss_amount": round(trades[idx].get('profit_loss', 0), 2),
                    "next_pl": round(next_trade.get('profit_loss', 0), 2),
                    "next_r": round(next_trade.get('r_multiple', 0), 2),
                    "time_diff_min": round(time_diff, 1) if time_diff else None,
                    "recovered": next_trade.get('profit_loss', 0) > 0,
                    "symbol": next_trade.get('symbol', '')
                })
        
        # Calculate statistics
        if post_loss_behaviors:
            recovery_rate = len([b for b in post_loss_behaviors if b["recovered"]]) / len(post_loss_behaviors) * 100
            avg_next_pl = np.mean([b["next_pl"] for b in post_loss_behaviors])
            avg_time_to_next = np.mean([b["time_diff_min"] for b in post_loss_behaviors if b["time_diff_min"]])
        else:
            recovery_rate = 0
            avg_next_pl = 0
            avg_time_to_next = 0
        
        return {
            "patterns": post_loss_behaviors[-20:],  # Last 20 instances
            "recovery_rate": round(recovery_rate, 2),
            "avg_next_pl": round(avg_next_pl, 2),
            "avg_time_to_next_min": round(avg_time_to_next, 1) if avg_time_to_next else 0,
            "total_instances": len(post_loss_behaviors)
        }
    
    def _detect_win_chasing(self, trades: List[Dict]) -> Dict[str, Any]:
        """Detect win-chasing behavior (increasing size after wins)"""
        win_chase_instances = []
        
        for i in range(1, len(trades)):
            prev_trade = trades[i-1]
            curr_trade = trades[i]
            
            # Check if previous trade was a win
            if prev_trade.get('profit_loss', 0) > 0:
                # Check if position size increased significantly
                prev_size = prev_trade.get('lot_size', 0)
                curr_size = curr_trade.get('lot_size', 0)
                
                if curr_size > prev_size * 1.5:  # 50% increase
                    win_chase_instances.append({
                        "date": curr_trade.get('exit_time', '').split('T')[0],
                        "prev_size": prev_size,
                        "curr_size": curr_size,
                        "increase_pct": round((curr_size - prev_size) / prev_size * 100, 1),
                        "prev_pl": round(prev_trade.get('profit_loss', 0), 2),
                        "curr_pl": round(curr_trade.get('profit_loss', 0), 2),
                        "profitable": curr_trade.get('profit_loss', 0) > 0
                    })
        
        # Calculate statistics
        if win_chase_instances:
            success_rate = len([i for i in win_chase_instances if i["profitable"]]) / len(win_chase_instances) * 100
            avg_increase = np.mean([i["increase_pct"] for i in win_chase_instances])
        else:
            success_rate = 0
            avg_increase = 0
        
        return {
            "detected": len(win_chase_instances) > 0,
            "instances": win_chase_instances[-10:],
            "total_count": len(win_chase_instances),
            "success_rate": round(success_rate, 2),
            "avg_increase_pct": round(avg_increase, 1),
            "severity": "high" if len(win_chase_instances) > len(trades) * 0.1 else "medium" if len(win_chase_instances) > len(trades) * 0.05 else "low"
        }
    
    def _analyze_time_patterns(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze trading patterns by time of day"""
        hourly_performance = defaultdict(lambda: {"count": 0, "total_pl": 0, "wins": 0})
        
        for trade in trades:
            if trade.get('exit_time'):
                try:
                    dt = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
                    hour = dt.hour
                    
                    hourly_performance[hour]["count"] += 1
                    hourly_performance[hour]["total_pl"] += trade.get('profit_loss', 0)
                    if trade.get('profit_loss', 0) > 0:
                        hourly_performance[hour]["wins"] += 1
                except:
                    continue
        
        # Create chart data
        hour_data = []
        for hour in range(24):
            data = hourly_performance[hour]
            if data["count"] > 0:
                avg_pl = data["total_pl"] / data["count"]
                win_rate = data["wins"] / data["count"] * 100
            else:
                avg_pl = 0
                win_rate = 0
            
            hour_data.append({
                "hour": hour,
                "count": data["count"],
                "avg_pl": round(avg_pl, 2),
                "win_rate": round(win_rate, 2),
                "total_pl": round(data["total_pl"], 2)
            })
        
        # Find best and worst hours
        best_hour = max(hour_data, key=lambda x: x["avg_pl"]) if any(h["count"] > 0 for h in hour_data else []) else {"hour": 0, "avg_pl": 0}
        worst_hour = min(hour_data, key=lambda x: x["avg_pl"]) if any(h["count"] > 0 for h in hour_data else []) else {"hour": 0, "avg_pl": 0}
        
        return {
            "hourly_data": hour_data,
            "best_hour": best_hour["hour"],
            "best_hour_avg_pl": round(best_hour["avg_pl"], 2),
            "worst_hour": worst_hour["hour"],
            "worst_hour_avg_pl": round(worst_hour["avg_pl"], 2),
            "most_active_hour": max(hour_data, key=lambda x: x["count"])["hour"] if any(h["count"] > 0 for h in hour_data) else 0
        }
    
    def _analyze_streaks(self, trades: List[Dict]) -> Dict[str, Any]:
        """Analyze winning and losing streaks"""
        if not trades:
            return {"win_streaks": [], "loss_streaks": []}
        
        win_streaks = []
        loss_streaks = []
        current_streak = 0
        current_type = None
        
        for trade in trades:
            is_win = trade.get('profit_loss', 0) > 0
            
            if is_win:
                if current_type == 'win':
                    current_streak += 1
                else:
                    if current_type == 'loss':
                        loss_streaks.append(current_streak)
                    current_type = 'win'
                    current_streak = 1
            else:
                if current_type == 'loss':
                    current_streak += 1
                else:
                    if current_type == 'win':
                        win_streaks.append(current_streak)
                    current_type = 'loss'
                    current_streak = 1
        
        # Add last streak
        if current_type == 'win':
            win_streaks.append(current_streak)
        elif current_type == 'loss':
            loss_streaks.append(current_streak)
        
        return {
            "win_streaks": win_streaks,
            "loss_streaks": loss_streaks,
            "max_win_streak": max(win_streaks) if win_streaks else 0,
            "max_loss_streak": max(loss_streaks) if loss_streaks else 0,
            "avg_win_streak": round(np.mean(win_streaks), 1) if win_streaks else 0,
            "avg_loss_streak": round(np.mean(loss_streaks), 1) if loss_streaks else 0,
            "streak_chart": self._create_streak_chart(trades[-50:])  # Last 50 trades
        }
    
    def _create_streak_chart(self, recent_trades: List[Dict]) -> List[Dict]:
        """Create streak visualization data"""
        chart_data = []
        streak = 0
        streak_type = None
        
        for i, trade in enumerate(recent_trades):
            is_win = trade.get('profit_loss', 0) > 0
            
            if streak_type == ('win' if is_win else 'loss'):
                streak += 1
            else:
                streak = 1
                streak_type = 'win' if is_win else 'loss'
            
            chart_data.append({
                "trade_number": i + 1,
                "streak": streak,
                "type": streak_type,
                "pl": round(trade.get('profit_loss', 0), 2)
            })
        
        return chart_data
    
    def _get_emotion_color(self, emotion: str) -> str:
        """Get color for emotion visualization"""
        emotion_colors = {
            "calm": "#10B981",  # green
            "focused": "#3B82F6",  # blue
            "confident": "#8B5CF6",  # purple
            "neutral": "#6B7280",  # gray
            "anxious": "#F59E0B",  # orange
            "fearful": "#EF4444",  # red
            "greedy": "#EC4899",  # pink
            "euphoric": "#F97316",  # orange-red
            "frustrated": "#DC2626",  # dark red
            "tired": "#6B7280",  # gray
            "not_logged": "#9CA3AF"  # light gray
        }
        return emotion_colors.get(emotion, "#6B7280")
    
    def _calculate_behavioral_score(self, trades: List[Dict]) -> float:
        """Calculate overall behavioral health score (0-100)"""
        if len(trades) < 10:
            return 0
        
        score = 100
        
        # Deduct for overtrading
        overtrading = self._detect_overtrading(trades)
        score -= overtrading["score"] * 0.3
        
        # Deduct for revenge trading
        revenge = self._detect_revenge_trading(trades)
        if revenge["severity"] == "high":
            score -= 20
        elif revenge["severity"] == "medium":
            score -= 10
        elif revenge["detected"]:
            score -= 5
        
        # Deduct for win chasing
        win_chasing = self._detect_win_chasing(trades)
        if win_chasing["severity"] == "high":
            score -= 15
        elif win_chasing["severity"] == "medium":
            score -= 8
        elif win_chasing["detected"]:
            score -= 3
        
        # Emotional variety (traders who log emotions tend to be more aware)
        emotions_logged = len([t for t in trades if t.get('emotion') and t.get('emotion') != 'unknown'])
        if emotions_logged > len(trades) * 0.7:
            score += 10
        elif emotions_logged > len(trades) * 0.3:
            score += 5
        
        return round(max(0, min(100, score)), 2)
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response when no trades"""
        return {
            "overtrading": {"detected": False, "score": 0, "clusters": [], "avg_daily_trades": 0, "max_daily_trades": 0, "threshold": 0},
            "revenge_trading": {"detected": False, "instances": [], "total_count": 0, "avg_pl": 0, "profitable_percentage": 0, "severity": "none"},
            "emotional_patterns": {"emotion_stats": [], "frequency_chart": [], "most_common_emotion": "none", "best_emotion": "none", "worst_emotion": "none"},
            "post_loss_behavior": {"patterns": [], "recovery_rate": 0, "avg_next_pl": 0, "avg_time_to_next_min": 0, "total_instances": 0},
            "win_chasing": {"detected": False, "instances": [], "total_count": 0, "success_rate": 0, "avg_increase_pct": 0, "severity": "none"},
            "time_patterns": {"hourly_data": [], "best_hour": 0, "best_hour_avg_pl": 0, "worst_hour": 0, "worst_hour_avg_pl": 0, "most_active_hour": 0},
            "streaks": {"win_streaks": [], "loss_streaks": [], "max_win_streak": 0, "max_loss_streak": 0, "avg_win_streak": 0, "avg_loss_streak": 0, "streak_chart": []},
            "behavioral_score": 0
        }
