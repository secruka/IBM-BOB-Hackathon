"""
Response Time Optimization Module
Recommends optimal response times based on urgency, customer value, and sentiment
"""

from typing import Dict, Any
from datetime import datetime, timedelta


class ResponseOptimizer:
    """Optimizes response time recommendations for customer emails"""
    
    # Response time targets (in hours)
    RESPONSE_TIMES = {
        'immediate': 0.5,    # 30 minutes
        'urgent': 2,         # 2 hours
        'high': 4,           # 4 hours
        'normal': 24,        # 24 hours
        'low': 48            # 48 hours
    }
    
    # Customer tier multipliers
    TIER_MULTIPLIERS = {
        'enterprise': 0.5,   # 50% faster response
        'premium': 0.75,     # 25% faster response
        'standard': 1.0,     # Standard response time
        'basic': 1.5         # 50% slower response acceptable
    }
    
    def __init__(self):
        """Initialize response optimizer"""
        pass
    
    def calculate_optimal_response_time(
        self,
        email: Dict[str, Any],
        sentiment_data: Dict[str, Any] = None,
        churn_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate optimal response time for an email
        
        Args:
            email: Email data
            sentiment_data: Sentiment analysis results
            churn_data: Churn risk prediction results
            
        Returns:
            Response time recommendation
        """
        # Base priority calculation
        priority_score = self._calculate_priority_score(
            email, sentiment_data, churn_data
        )
        
        # Determine response category
        response_category = self._get_response_category(priority_score)
        
        # Get base response time
        base_hours = self.RESPONSE_TIMES[response_category]
        
        # Apply customer tier adjustment
        customer_tier = email.get('customer_tier', 'standard')
        tier_multiplier = self.TIER_MULTIPLIERS.get(customer_tier, 1.0)
        
        adjusted_hours = base_hours * tier_multiplier
        
        # Calculate deadline
        deadline = datetime.now() + timedelta(hours=adjusted_hours)
        
        return {
            'response_category': response_category,
            'recommended_hours': round(adjusted_hours, 1),
            'deadline': deadline.strftime('%Y-%m-%d %H:%M'),
            'priority_score': priority_score,
            'customer_tier': customer_tier,
            'reasoning': self._generate_reasoning(
                response_category, priority_score, customer_tier,
                sentiment_data, churn_data
            )
        }
    
    def _calculate_priority_score(
        self,
        email: Dict[str, Any],
        sentiment_data: Dict[str, Any] = None,
        churn_data: Dict[str, Any] = None
    ) -> int:
        """
        Calculate priority score (0-100)
        
        Args:
            email: Email data
            sentiment_data: Sentiment analysis
            churn_data: Churn risk data
            
        Returns:
            Priority score
        """
        score = 50  # Base score
        
        # Sentiment impact (0-25 points)
        if sentiment_data:
            urgency = sentiment_data.get('urgency_level', 'medium')
            sentiment = sentiment_data.get('sentiment', 'neutral')
            intensity = sentiment_data.get('intensity', 50)
            
            if urgency == 'critical':
                score += 25
            elif urgency == 'high':
                score += 15
            elif urgency == 'medium':
                score += 5
            
            if sentiment == 'angry':
                score += intensity * 0.2  # Up to 20 points
            elif sentiment == 'urgent':
                score += 15
        
        # Churn risk impact (0-25 points)
        if churn_data:
            risk_score = churn_data.get('risk_score', 50)
            score += (risk_score / 100) * 25
        
        # Customer value impact (0-20 points)
        customer_ltv = email.get('customer_ltv', 0)
        if customer_ltv >= 100000:
            score += 20
        elif customer_ltv >= 50000:
            score += 15
        elif customer_ltv >= 10000:
            score += 10
        elif customer_ltv >= 5000:
            score += 5
        
        # Customer tier impact (0-10 points)
        tier = email.get('customer_tier', 'standard')
        tier_points = {
            'enterprise': 10,
            'premium': 7,
            'standard': 3,
            'basic': 0
        }
        score += tier_points.get(tier, 0)
        
        return min(100, max(0, int(score)))
    
    def _get_response_category(self, priority_score: int) -> str:
        """
        Determine response category from priority score
        
        Args:
            priority_score: Priority score (0-100)
            
        Returns:
            Response category
        """
        if priority_score >= 90:
            return 'immediate'
        elif priority_score >= 75:
            return 'urgent'
        elif priority_score >= 60:
            return 'high'
        elif priority_score >= 40:
            return 'normal'
        else:
            return 'low'
    
    def _generate_reasoning(
        self,
        response_category: str,
        priority_score: int,
        customer_tier: str,
        sentiment_data: Dict[str, Any] = None,
        churn_data: Dict[str, Any] = None
    ) -> str:
        """
        Generate reasoning for response time recommendation
        
        Args:
            response_category: Response category
            priority_score: Priority score
            customer_tier: Customer tier
            sentiment_data: Sentiment analysis
            churn_data: Churn risk data
            
        Returns:
            Reasoning text
        """
        reasons = []
        
        # Priority level
        if priority_score >= 90:
            reasons.append("Critical priority requiring immediate attention")
        elif priority_score >= 75:
            reasons.append("High priority requiring urgent response")
        elif priority_score >= 60:
            reasons.append("Elevated priority requiring prompt response")
        else:
            reasons.append("Standard priority with normal response time")
        
        # Customer tier
        if customer_tier in ['enterprise', 'premium']:
            reasons.append(f"{customer_tier.capitalize()} customer with expedited SLA")
        
        # Sentiment factors
        if sentiment_data:
            sentiment = sentiment_data.get('sentiment', 'neutral')
            urgency = sentiment_data.get('urgency_level', 'medium')
            
            if sentiment == 'angry':
                reasons.append("Customer expressing frustration - quick response needed")
            elif urgency == 'critical':
                reasons.append("Time-sensitive issue requiring immediate action")
        
        # Churn risk factors
        if churn_data:
            risk_level = churn_data.get('risk_level', 'medium')
            if risk_level in ['critical', 'high']:
                reasons.append(f"{risk_level.capitalize()} churn risk - retention priority")
        
        return "; ".join(reasons)
    
    def get_response_emoji(self, response_category: str) -> str:
        """
        Get emoji for response category
        
        Args:
            response_category: Response category
            
        Returns:
            Emoji string
        """
        emoji_map = {
            'immediate': '🚨',
            'urgent': '⚡',
            'high': '⏰',
            'normal': '📅',
            'low': '📝'
        }
        return emoji_map.get(response_category, '📅')
    
    def format_response_time(self, hours: float) -> str:
        """
        Format response time in human-readable format
        
        Args:
            hours: Response time in hours
            
        Returns:
            Formatted string
        """
        if hours < 1:
            minutes = int(hours * 60)
            return f"{minutes} minutes"
        elif hours < 24:
            return f"{hours:.1f} hours"
        else:
            days = hours / 24
            return f"{days:.1f} days"

# Made with Bob
