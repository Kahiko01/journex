from typing import List, Dict, Any
from datetime import datetime, timedelta
import uuid
import hashlib

class CertificationService:
    
    def __init__(self):
        self.levels = {
            'bronze': {
                'min_discipline_score': 60,
                'min_risk_consistency': 55,
                'min_avg_r_multiple': 0.3,
                'max_drawdown_percent': 25,
                'min_quiz_score': 60,
                'max_rule_violations': 10,
                'min_trades_analyzed': 20,
                'consecutive_weeks_required': 2
            },
            'silver': {
                'min_discipline_score': 70,
                'min_risk_consistency': 65,
                'min_avg_r_multiple': 0.5,
                'max_drawdown_percent': 20,
                'min_quiz_score': 70,
                'max_rule_violations': 7,
                'min_trades_analyzed': 40,
                'consecutive_weeks_required': 3
            },
            'gold': {
                'min_discipline_score': 80,
                'min_risk_consistency': 75,
                'min_avg_r_multiple': 0.8,
                'max_drawdown_percent': 15,
                'min_quiz_score': 80,
                'max_rule_violations': 5,
                'min_trades_analyzed': 60,
                'consecutive_weeks_required': 4
            },
            'elite': {
                'min_discipline_score': 90,
                'min_risk_consistency': 85,
                'min_avg_r_multiple': 1.2,
                'max_drawdown_percent': 10,
                'min_quiz_score': 90,
                'max_rule_violations': 2,
                'min_trades_analyzed': 100,
                'consecutive_weeks_required': 6
            }
        }
    
    def check_certification_eligibility(self, user_stats: Dict, level: str) -> Dict:
        """Check if user is eligible for a certification level"""
        if level not in self.levels:
            return {'eligible': False, 'error': 'Invalid level'}
        
        requirements = self.levels[level]
        results = {
            'level': level,
            'eligible': True,
            'requirements_met': {},
            'requirements_missing': []
        }
        
        # Check discipline score
        discipline = user_stats.get('discipline_score', 0)
        required = requirements['min_discipline_score']
        met = discipline >= required
        results['requirements_met']['discipline_score'] = {
            'current': discipline,
            'required': required,
            'met': met
        }
        if not met:
            results['requirements_missing'].append('discipline_score')
        
        # Check risk consistency
        risk = user_stats.get('risk_consistency', 0)
        required = requirements['min_risk_consistency']
        met = risk >= required
        results['requirements_met']['risk_consistency'] = {
            'current': risk,
            'required': required,
            'met': met
        }
        if not met:
            results['requirements_missing'].append('risk_consistency')
        
        # Check average R multiple
        avg_r = user_stats.get('avg_r_multiple', 0)
        required = requirements['min_avg_r_multiple']
        met = avg_r >= required
        results['requirements_met']['avg_r_multiple'] = {
            'current': avg_r,
            'required': required,
            'met': met
        }
        if not met:
            results['requirements_missing'].append('avg_r_multiple')
        
        # Check max drawdown
        dd = user_stats.get('max_drawdown_percent', 100)
        required = requirements['max_drawdown_percent']
        met = dd <= required
        results['requirements_met']['max_drawdown'] = {
            'current': dd,
            'required': required,
            'met': met
        }
        if not met:
            results['requirements_missing'].append('max_drawdown')
        
        # Check quiz score
        quiz = user_stats.get('average_quiz_score', 0)
        required = requirements['min_quiz_score']
        met = quiz >= required
        results['requirements_met']['quiz_score'] = {
            'current': quiz,
            'required': required,
            'met': met
        }
        if not met:
            results['requirements_missing'].append('quiz_score')
        
        # Check rule violations
        violations = user_stats.get('rule_violations', 0)
        required = requirements['max_rule_violations']
        met = violations <= required
        results['requirements_met']['rule_violations'] = {
            'current': violations,
            'required': required,
            'met': met
        }
        if not met:
            results['requirements_missing'].append('rule_violations')
        
        # Check trades analyzed
        trades = user_stats.get('trades_analyzed', 0)
        required = requirements['min_trades_analyzed']
        met = trades >= required
        results['requirements_met']['trades_analyzed'] = {
            'current': trades,
            'required': required,
            'met': met
        }
        if not met:
            results['requirements_missing'].append('trades_analyzed')
        
        # Check consecutive weeks
        weeks = user_stats.get('weeks_above_threshold', 0)
        required = requirements['consecutive_weeks_required']
        met = weeks >= required
        results['requirements_met']['consecutive_weeks'] = {
            'current': weeks,
            'required': required,
            'met': met
        }
        if not met:
            results['requirements_missing'].append('consecutive_weeks')
        
        results['eligible'] = len(results['requirements_missing']) == 0
        
        return results
    
    def generate_certificate_number(self, user_id: str, level: str) -> str:
        """Generate unique certificate number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_string = f"{user_id}{level}{timestamp}{uuid.uuid4()}"
        hash_obj = hashlib.sha256(unique_string.encode())
        cert_hash = hash_obj.hexdigest()[:16].upper()
        
        return f"JNX-{level.upper()}-{cert_hash}"
    
    def generate_verification_url(self, certificate_number: str) -> str:
        """Generate public verification URL"""
        return f"/verify/{certificate_number}"
    
    def evaluate_for_highest_certification(self, user_stats: Dict) -> Dict:
        """Find the highest certification level user qualifies for"""
        levels = ['elite', 'gold', 'silver', 'bronze']
        
        for level in levels:
            result = self.check_certification_eligibility(user_stats, level)
            if result['eligible']:
                return {
                    'level': level,
                    'eligible': True,
                    'details': result
                }
        
        return {
            'level': None,
            'eligible': False,
            'details': None
        }
    
    def check_revocation(self, user_stats: Dict, current_level: str) -> bool:
        """Check if certification should be revoked"""
        # If discipline drops below threshold for current level
        level_reqs = self.levels.get(current_level, self.levels['bronze'])
        
        # More lenient revocation thresholds (80% of original)
        discipline_threshold = level_reqs['min_discipline_score'] * 0.8
        
        if user_stats.get('discipline_score', 100) < discipline_threshold:
            return True
        
        # If rule violations spike
        if user_stats.get('rule_violations_30d', 0) > level_reqs['max_rule_violations'] * 2:
            return True
        
        # If overtrading detected consistently
        if user_stats.get('overtrading_days_30d', 0) > 10:
            return True
        
        return False
