"""
Churn Risk Prediction Module
Predicts customer churn risk based on email content and customer data
"""

from typing import Dict, Any, List
from .gemini_client import GeminiClient


class ChurnPredictor:
    """Predicts customer churn risk from email interactions"""
    
    # Churn risk thresholds
    RISK_THRESHOLDS = {
        'critical': 80,  # 80%+ = Critical risk
        'high': 60,      # 60-79% = High risk
        'medium': 40,    # 40-59% = Medium risk
        'low': 0         # 0-39% = Low risk
    }
    
    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize churn predictor
        
        Args:
            gemini_client: Gemini API client instance
        """
        self.gemini_client = gemini_client
    
    def predict_churn_risk(
        self,
        email: Dict[str, Any],
        sentiment_data: Dict[str, Any] = None,
        historical_context: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict churn risk for a customer
        
        Args:
            email: Current email data
            sentiment_data: Sentiment analysis results (optional)
            historical_context: Past interactions (optional)
            
        Returns:
            Churn risk prediction results
        """
        prompt = self._build_churn_prompt(email, sentiment_data, historical_context)
        
        try:
            response = self.gemini_client.generate_content(
                prompt=prompt,
                temperature=0.2,
                max_tokens=600
            )
            
            result = self._parse_churn_response(response)
            result['risk_level'] = self._calculate_risk_level(result['risk_score'])
            
            return result
            
        except Exception as e:
            print(f"✗ Churn prediction error: {e}")
            return {
                'risk_score': 50,
                'risk_level': 'medium',
                'risk_factors': [],
                'mitigation_actions': [],
                'confidence': 'low',
                'error': str(e)
            }
    
    def _build_churn_prompt(
        self,
        email: Dict[str, Any],
        sentiment_data: Dict[str, Any] = None,
        historical_context: List[Dict[str, Any]] = None
    ) -> str:
        """
        Build prompt for churn risk prediction
        
        Args:
            email: Email data
            sentiment_data: Sentiment analysis results
            historical_context: Past interactions
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze the churn risk for this customer based on their email.

**Current Email:**
Subject: {email.get('subject', 'N/A')}
Sender: {email.get('sender', 'N/A')}
Body: {email.get('body', 'N/A')}

**Customer Information:**
Customer Tier: {email.get('customer_tier', 'standard')}
Lifetime Value: ${email.get('customer_ltv', 0):,}
"""

        if sentiment_data:
            prompt += f"""
**Sentiment Analysis:**
Sentiment: {sentiment_data.get('sentiment_label', 'N/A')}
Intensity: {sentiment_data.get('intensity', 50)}/100
Emotions: {', '.join(sentiment_data.get('emotions', []))}
Urgency: {sentiment_data.get('urgency_level', 'medium')}
"""

        if historical_context:
            prompt += f"""
**Historical Context:**
Previous interactions: {len(historical_context)} emails
"""

        prompt += """
**Churn Risk Analysis Required:**

1. **Churn Risk Score**: Provide a score from 0-100
   - 0-39: Low risk (customer is satisfied, no churn indicators)
   - 40-59: Medium risk (some concerns, needs attention)
   - 60-79: High risk (significant dissatisfaction, likely to churn)
   - 80-100: Critical risk (immediate action required, churn imminent)

2. **Risk Factors**: List specific indicators that suggest churn risk
   - Dissatisfaction expressions
   - Competitor mentions
   - Cancellation threats
   - Unresolved issues
   - Decreased engagement
   - Payment/pricing concerns

3. **Mitigation Actions**: Recommend specific actions to prevent churn
   - Immediate response requirements
   - Escalation needs
   - Compensation/credits
   - Feature requests
   - Account review

4. **Confidence Level**: How confident are you in this assessment?
   - high (clear indicators present)
   - medium (some indicators, needs verification)
   - low (limited information)

**Response Format:**

Churn Risk Score: [0-100]

Risk Factors:
- [factor 1]
- [factor 2]
- [factor 3]

Mitigation Actions:
- [action 1]
- [action 2]
- [action 3]

Confidence: [high/medium/low]

Reasoning: [Brief explanation of the assessment]

Base your analysis on actual content and customer data, not assumptions.
"""
        return prompt
    
    def _parse_churn_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse churn prediction response
        
        Args:
            response_text: Raw response from API
            
        Returns:
            Parsed churn risk data
        """
        result = {
            'risk_score': 50,
            'risk_factors': [],
            'mitigation_actions': [],
            'confidence': 'medium',
            'reasoning': ''
        }
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Parse risk score
            if line.startswith('Churn Risk Score:'):
                try:
                    score_str = line.split(':', 1)[1].strip()
                    score = int(''.join(filter(str.isdigit, score_str)))
                    result['risk_score'] = min(100, max(0, score))
                except:
                    pass
            
            # Identify sections
            elif line.startswith('Risk Factors:'):
                current_section = 'factors'
            elif line.startswith('Mitigation Actions:'):
                current_section = 'actions'
            elif line.startswith('Confidence:'):
                confidence = line.split(':', 1)[1].strip().lower()
                if confidence in ['high', 'medium', 'low']:
                    result['confidence'] = confidence
                current_section = None
            elif line.startswith('Reasoning:'):
                result['reasoning'] = line.split(':', 1)[1].strip()
                current_section = 'reasoning'
            
            # Parse list items
            elif line.startswith('-') and current_section:
                item = line.lstrip('-').strip()
                if item:
                    if current_section == 'factors':
                        result['risk_factors'].append(item)
                    elif current_section == 'actions':
                        result['mitigation_actions'].append(item)
            
            # Continue reasoning
            elif current_section == 'reasoning' and line:
                result['reasoning'] += ' ' + line
        
        return result
    
    def _calculate_risk_level(self, risk_score: int) -> str:
        """
        Calculate risk level from score
        
        Args:
            risk_score: Risk score (0-100)
            
        Returns:
            Risk level string
        """
        if risk_score >= self.RISK_THRESHOLDS['critical']:
            return 'critical'
        elif risk_score >= self.RISK_THRESHOLDS['high']:
            return 'high'
        elif risk_score >= self.RISK_THRESHOLDS['medium']:
            return 'medium'
        else:
            return 'low'
    
    def get_risk_emoji(self, risk_level: str) -> str:
        """
        Get emoji representation of risk level
        
        Args:
            risk_level: Risk level
            
        Returns:
            Emoji string
        """
        emoji_map = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '⚡',
            'low': '✅'
        }
        return emoji_map.get(risk_level, '⚡')
    
    def get_risk_color(self, risk_level: str) -> str:
        """
        Get color code for risk level
        
        Args:
            risk_level: Risk level
            
        Returns:
            Color name
        """
        color_map = {
            'critical': 'red',
            'high': 'orange',
            'medium': 'yellow',
            'low': 'green'
        }
        return color_map.get(risk_level, 'yellow')

# Made with Bob
