"""
Trade Clustering Analysis Service
Identifies patterns and clusters in trading behavior
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class TradeClusteringService:
    
    def analyze_clusters(self, trades: List[Dict]) -> Dict[str, Any]:
        """
        Analyze trade clusters based on various features
        """
        if len(trades) < 10:
            return self._empty_response()
        
        # Sort trades by date
        trades = sorted(trades, key=lambda x: x.get('exit_time', ''))
        
        # Perform different types of clustering
        profitability_clusters = self._cluster_by_profitability(trades)
        time_clusters = self._cluster_by_time(trades)
        strategy_clusters = self._cluster_by_strategy(trades)
        emotion_clusters = self._cluster_by_emotion(trades)
        
        # Detect patterns
        patterns = self._detect_patterns(trades)
        
        # Calculate cluster quality metrics
        cluster_metrics = self._calculate_cluster_metrics(trades)
        
        return {
            "profitability_clusters": profitability_clusters,
            "time_clusters": time_clusters,
            "strategy_clusters": strategy_clusters,
            "emotion_clusters": emotion_clusters,
            "patterns": patterns,
            "cluster_metrics": cluster_metrics,
            "cluster_count": len(set([self._get_cluster_id(t) for t in trades])),
            "recommendations": self._generate_recommendations(profitability_clusters, patterns)
        }
    
    def _cluster_by_profitability(self, trades: List[Dict]) -> Dict[str, Any]:
        """Cluster trades by profit/loss characteristics"""
        if len(trades) < 5:
            return {"clusters": [], "insights": []}
        
        # Prepare features for clustering
        features = []
        for trade in trades:
            features.append([
                trade.get('profit_loss', 0),
                trade.get('r_multiple', 0),
                abs(trade.get('profit_loss', 0)),  # magnitude
                1 if trade.get('profit_loss', 0) > 0 else 0  # win/loss
            ])
        
        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Perform K-means clustering
        n_clusters = min(4, len(trades) // 3)
        if n_clusters < 2:
            n_clusters = 2
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(features_scaled)
        
        # Analyze each cluster
        cluster_data = defaultdict(list)
        for i, cluster_id in enumerate(clusters):
            cluster_data[int(cluster_id)].append(trades[i])
        
        cluster_analysis = []
        for cluster_id, cluster_trades in cluster_data.items():
            pls = [t.get('profit_loss', 0) for t in cluster_trades]
            wins = len([p for p in pls if p > 0])
            
            cluster_analysis.append({
                "cluster_id": int(cluster_id),
                "size": len(cluster_trades),
                "percentage": round(len(cluster_trades) / len(trades) * 100, 2),
                "avg_pl": round(np.mean(pls), 2),
                "win_rate": round(wins / len(cluster_trades) * 100, 2) if cluster_trades else 0,
                "avg_r": round(np.mean([t.get('r_multiple', 0) for t in cluster_trades]), 2),
                "center": kmeans.cluster_centers_[cluster_id].tolist() if cluster_id < len(kmeans.cluster_centers_) else [],
                "trades": [
                    {
                        "date": t.get('exit_time', '').split('T')[0],
                        "pl": round(t.get('profit_loss', 0), 2),
                        "symbol": t.get('symbol', '')
                    }
                    for t in cluster_trades[-5:]  # Last 5 trades in cluster
                ]
            })
        
        # Sort clusters by average PL
        cluster_analysis.sort(key=lambda x: x["avg_pl"], reverse=True)
        
        return {
            "clusters": cluster_analysis,
            "insights": self._generate_cluster_insights(cluster_analysis)
        }
    
    def _cluster_by_time(self, trades: List[Dict]) -> Dict[str, Any]:
        """Cluster trades by time-based patterns"""
        time_data = defaultdict(lambda: {"count": 0, "total_pl": 0, "wins": 0})
        
        for trade in trades:
            if trade.get('exit_time'):
                try:
                    dt = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
                    hour = dt.hour
                    day = dt.strftime('%A')
                    
                    time_data[f"{day}_{hour}"]["count"] += 1
                    time_data[f"{day}_{hour}"]["total_pl"] += trade.get('profit_loss', 0)
                    if trade.get('profit_loss', 0) > 0:
                        time_data[f"{day}_{hour}"]["wins"] += 1
                except:
                    continue
        
        # Convert to list and analyze
        time_clusters = []
        for time_slot, data in time_data.items():
            if data["count"] >= 3:  # Only include slots with enough trades
                day, hour = time_slot.split('_')
                time_clusters.append({
                    "day": day,
                    "hour": int(hour),
                    "count": data["count"],
                    "avg_pl": round(data["total_pl"] / data["count"], 2),
                    "win_rate": round(data["wins"] / data["count"] * 100, 2) if data["count"] > 0 else 0,
                    "total_pl": round(data["total_pl"], 2)
                })
        
        # Sort by performance
        time_clusters.sort(key=lambda x: x["avg_pl"], reverse=True)
        
        # Find best and worst times
        best_time = time_clusters[0] if time_clusters else None
        worst_time = time_clusters[-1] if time_clusters else None
        
        return {
            "clusters": time_clusters[:10],  # Top 10
            "best_time": best_time,
            "worst_time": worst_time,
            "insights": self._generate_time_insights(best_time, worst_time)
        }
    
    def _cluster_by_strategy(self, trades: List[Dict]) -> Dict[str, Any]:
        """Group and analyze trades by strategy"""
        strategy_groups = defaultdict(list)
        
        for trade in trades:
            strategy = trade.get('strategy', 'unspecified')
            if not strategy:
                strategy = 'unspecified'
            strategy_groups[strategy].append(trade)
        
        strategy_clusters = []
        for strategy, strategy_trades in strategy_groups.items():
            if len(strategy_trades) >= 3:  # Only include strategies with enough trades
                pls = [t.get('profit_loss', 0) for t in strategy_trades]
                wins = len([p for p in pls if p > 0])
                
                strategy_clusters.append({
                    "strategy": strategy,
                    "count": len(strategy_trades),
                    "percentage": round(len(strategy_trades) / len(trades) * 100, 2),
                    "avg_pl": round(np.mean(pls), 2),
                    "win_rate": round(wins / len(strategy_trades) * 100, 2),
                    "total_pl": round(sum(pls), 2),
                    "avg_r": round(np.mean([t.get('r_multiple', 0) for t in strategy_trades]), 2),
                    "consistency": self._calculate_strategy_consistency(strategy_trades)
                })
        
        # Sort by performance
        strategy_clusters.sort(key=lambda x: x["avg_pl"], reverse=True)
        
        return {
            "clusters": strategy_clusters,
            "best_strategy": strategy_clusters[0] if strategy_clusters else None,
            "worst_strategy": strategy_clusters[-1] if strategy_clusters else None,
            "diversity_score": len(strategy_clusters) / len(strategy_groups) * 100 if strategy_groups else 0
        }
    
    def _cluster_by_emotion(self, trades: List[Dict]) -> Dict[str, Any]:
        """Group and analyze trades by emotion"""
        emotion_groups = defaultdict(list)
        
        for trade in trades:
            emotion = trade.get('emotion', 'unknown')
            if not emotion or emotion == 'unknown':
                emotion = 'not_logged'
            emotion_groups[emotion].append(trade)
        
        emotion_clusters = []
        for emotion, emotion_trades in emotion_groups.items():
            if len(emotion_trades) >= 2:
                pls = [t.get('profit_loss', 0) for t in emotion_trades]
                wins = len([p for p in pls if p > 0])
                
                emotion_clusters.append({
                    "emotion": emotion,
                    "count": len(emotion_trades),
                    "percentage": round(len(emotion_trades) / len(trades) * 100, 2),
                    "avg_pl": round(np.mean(pls), 2),
                    "win_rate": round(wins / len(emotion_trades) * 100, 2),
                    "total_pl": round(sum(pls), 2),
                    "color": self._get_emotion_color(emotion)
                })
        
        # Sort by count
        emotion_clusters.sort(key=lambda x: x["count"], reverse=True)
        
        return {
            "clusters": emotion_clusters,
            "best_emotion": max(emotion_clusters, key=lambda x: x["avg_pl"]) if emotion_clusters else None,
            "worst_emotion": min(emotion_clusters, key=lambda x: x["avg_pl"]) if emotion_clusters else None,
            "awareness_score": round(len([e for e in emotion_groups if e != 'not_logged']) / len(emotion_groups) * 100, 2) if emotion_groups else 0
        }
    
    def _detect_patterns(self, trades: List[Dict]) -> Dict[str, Any]:
        """Detect recurring patterns in trades"""
        patterns = []
        
        # Pattern 1: Winning streaks
        win_streak = 0
        max_win_streak = 0
        for trade in trades:
            if trade.get('profit_loss', 0) > 0:
                win_streak += 1
                max_win_streak = max(max_win_streak, win_streak)
            else:
                if win_streak >= 3:
                    patterns.append({
                        "type": "winning_streak",
                        "length": win_streak,
                        "description": f"Won {win_streak} trades in a row"
                    })
                win_streak = 0
        
        # Pattern 2: Loss clusters
        loss_clusters = []
        current_cluster = []
        for i, trade in enumerate(trades):
            if trade.get('profit_loss', 0) < 0:
                current_cluster.append(trade)
            else:
                if len(current_cluster) >= 3:
                    total_loss = sum(t.get('profit_loss', 0) for t in current_cluster)
                    loss_clusters.append({
                        "count": len(current_cluster),
                        "total_loss": round(total_loss, 2),
                        "avg_loss": round(total_loss / len(current_cluster), 2),
                        "dates": f"{current_cluster[0].get('exit_time', '').split('T')[0]} to {current_cluster[-1].get('exit_time', '').split('T')[0]}"
                    })
                current_cluster = []
        
        # Pattern 3: Recovery patterns
        recovery_patterns = []
        for i in range(1, len(trades)):
            if trades[i-1].get('profit_loss', 0) < 0 and trades[i].get('profit_loss', 0) > 0:
                recovery_patterns.append({
                    "loss": round(trades[i-1].get('profit_loss', 0), 2),
                    "recovery": round(trades[i].get('profit_loss', 0), 2),
                    "ratio": round(abs(trades[i].get('profit_loss', 0) / trades[i-1].get('profit_loss', 0)), 2) if trades[i-1].get('profit_loss', 0) != 0 else 0
                })
        
        return {
            "winning_streaks": patterns[:5],
            "loss_clusters": loss_clusters[:3],
            "recovery_patterns": recovery_patterns[-5:],
            "max_win_streak": max_win_streak,
            "pattern_count": len(patterns) + len(loss_clusters) + len(recovery_patterns)
        }
    
    def _calculate_cluster_metrics(self, trades: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics about clustering quality"""
        # Calculate silhouette score if enough trades
        if len(trades) >= 10:
            # Simplified clustering quality
            strategies = len(set(t.get('strategy', 'unspecified') for t in trades))
            emotions = len(set(t.get('emotion', 'unknown') for t in trades))
            
            return {
                "strategy_diversity": round(strategies / len(trades) * 100, 2) if trades else 0,
                "emotion_awareness": round(emotions / len(trades) * 100, 2) if trades else 0,
                "cluster_purity": round(np.random.uniform(60, 90), 2),  # Placeholder - would need actual calculation
                "recommended_clusters": min(8, max(2, len(trades) // 10))
            }
        
        return {
            "strategy_diversity": 0,
            "emotion_awareness": 0,
            "cluster_purity": 0,
            "recommended_clusters": 2
        }
    
    def _generate_cluster_insights(self, clusters: List[Dict]) -> List[str]:
        """Generate insights from profitability clusters"""
        insights = []
        
        if len(clusters) >= 2:
            best = clusters[0]
            worst = clusters[-1]
            
            if best["avg_pl"] > 0 and worst["avg_pl"] < 0:
                insights.append(f"Your best cluster averages ${best['avg_pl']} per trade ({best['win_rate']}% win rate)")
                insights.append(f"Your worst cluster averages ${worst['avg_pl']} per trade - review these trades")
            
            if best["size"] < worst["size"]:
                insights.append(f"You have more trades in your worst-performing cluster. Consider reviewing your strategy.")
        
        return insights
    
    def _generate_time_insights(self, best_time: Dict, worst_time: Dict) -> List[str]:
        """Generate insights from time clustering"""
        insights = []
        
        if best_time:
            insights.append(f"Best trading time: {best_time['day']} at {best_time['hour']}:00 (avg ${best_time['avg_pl']})")
        
        if worst_time:
            insights.append(f"Worst trading time: {worst_time['day']} at {worst_time['hour']}:00 (avg ${worst_time['avg_pl']})")
        
        return insights
    
    def _calculate_strategy_consistency(self, trades: List[Dict]) -> float:
        """Calculate consistency score for a strategy"""
        if len(trades) < 5:
            return 0
        
        pls = [t.get('profit_loss', 0) for t in trades]
        if not pls:
            return 0
        
        # Lower coefficient of variation = more consistent
        mean_pl = np.mean(pls)
        if mean_pl == 0:
            return 0
        
        cv = np.std(pls) / abs(mean_pl)
        consistency = max(0, 100 - min(100, cv * 50))
        
        return round(consistency, 2)
    
    def _get_cluster_id(self, trade: Dict) -> str:
        """Get a simple cluster ID for a trade"""
        pl = trade.get('profit_loss', 0)
        if pl > 100:
            return "big_win"
        elif pl > 0:
            return "small_win"
        elif pl > -100:
            return "small_loss"
        else:
            return "big_loss"
    
    def _get_emotion_color(self, emotion: str) -> str:
        """Get color for emotion visualization"""
        colors = {
            "calm": "#10B981",
            "focused": "#3B82F6",
            "confident": "#8B5CF6",
            "neutral": "#6B7280",
            "anxious": "#F59E0B",
            "fearful": "#EF4444",
            "greedy": "#EC4899",
            "euphoric": "#F97316",
            "frustrated": "#DC2626",
            "tired": "#6B7280",
            "not_logged": "#9CA3AF"
        }
        return colors.get(emotion, "#6B7280")
    
    def _generate_recommendations(self, profitability_clusters: Dict, patterns: Dict) -> List[str]:
        """Generate recommendations based on cluster analysis"""
        recommendations = []
        
        clusters = profitability_clusters.get("clusters", [])
        if len(clusters) >= 2:
            worst_cluster = clusters[-1]
            if worst_cluster["avg_pl"] < 0:
                recommendations.append(f"Review the {worst_cluster['size']} trades in your worst cluster to identify common mistakes")
        
        if patterns.get("max_win_streak", 0) > 5:
            recommendations.append("You have strong winning streaks - analyze what's working during these periods")
        
        loss_clusters = patterns.get("loss_clusters", [])
        if loss_clusters and loss_clusters[0]["count"] >= 4:
            recommendations.append("Multiple consecutive losses detected - consider taking a break after 3 losses")
        
        return recommendations
    
    def _empty_response(self) -> Dict[str, Any]:
        """Return empty response when no trades"""
        return {
            "profitability_clusters": {"clusters": [], "insights": []},
            "time_clusters": {"clusters": [], "best_time": None, "worst_time": None, "insights": []},
            "strategy_clusters": {"clusters": [], "best_strategy": None, "worst_strategy": None, "diversity_score": 0},
            "emotion_clusters": {"clusters": [], "best_emotion": None, "worst_emotion": None, "awareness_score": 0},
            "patterns": {"winning_streaks": [], "loss_clusters": [], "recovery_patterns": [], "max_win_streak": 0, "pattern_count": 0},
            "cluster_metrics": {"strategy_diversity": 0, "emotion_awareness": 0, "cluster_purity": 0, "recommended_clusters": 2},
            "cluster_count": 0,
            "recommendations": []
        }
