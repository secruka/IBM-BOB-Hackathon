"""
Sentiment Analysis Module
Analyzes customer emotions and sentiment from email content
"""

from typing import Dict, Any
from .gemini_client import GeminiClient


class SentimentAnalyzer:
    """Analyzes sentiment and emotions in customer emails"""
    
    # Sentiment categories
    SENTIMENTS = {
        'angry': 'Angry/Frustrated',
        'dissatisfied': 'Dissatisfied',
        'neutral': 'Neutral',
        'satisfied': 'Satisfied',
        'urgent': 'Urgent/Concerned'
    }
    
    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize sentiment analyzer
        
        Args:
            gemini_client: Gemini API client instance
        """
        self.gemini_client = gemini_client
    
    def analyze_sentiment(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment of an email
        
        Args:
            email: Email data dictionary
            
        Returns:
            Sentiment analysis results
        """
        prompt = self._build_sentiment_prompt(email)
        
        try:
            response = self.gemini_client.generate_content(
                prompt=prompt,
                temperature=0.2,  # Lower temperature for more consistent analysis
                max_tokens=500
            )
            
            result = self._parse_sentiment_response(response)
            return result
            
        except Exception as e:
            print(f"✗ Sentiment analysis error: {e}")
            return {
                'sentiment': 'neutral',
                'sentiment_label': 'Neutral',
                'intensity': 50,
                'emotions': [],
                'urgency_level': 'medium',
                'error': str(e)
            }
    
    def _build_sentiment_prompt(self, email: Dict[str, Any]) -> str:
        """
        Build prompt for sentiment analysis
        
        Args:
            email: Email data
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze the sentiment and emotions in this customer email.

**Email Details:**
Subject: {email.get('subject', 'N/A')}
Sender: {email.get('sender', 'N/A')}
Body: {email.get('body', 'N/A')}

**Analysis Required:**

1. **Primary Sentiment**: Choose ONE from:
   - angry (customer is frustrated, upset, or angry)
   - dissatisfied (customer is unhappy but not angry)
   - neutral (no strong emotion)
   - satisfied (customer is happy or content)
   - urgent (customer needs immediate help, time-sensitive)

2. **Sentiment Intensity**: Rate from 0-100
   - 0-20: Very mild
   - 21-40: Mild
   - 41-60: Moderate
   - 61-80: Strong
   - 81-100: Very strong

3. **Detected Emotions**: List specific emotions (e.g., frustration, anxiety, disappointment, gratitude)

4. **Urgency Level**: Choose ONE from:
   - critical (immediate action required, business impact)
   - high (needs quick response, customer waiting)
   - medium (normal priority)
   - low (informational, no rush)

5. **Key Indicators**: List specific words/phrases that indicate the sentiment

**Response Format:**

Primary Sentiment: [sentiment]
Intensity: [0-100]
Emotions: [emotion1, emotion2, emotion3]
Urgency Level: [level]
Key Indicators:
- [indicator 1]
- [indicator 2]
- [indicator 3]

Be objective and base your analysis on the actual content, not assumptions.
"""
        return prompt
    
    def _parse_sentiment_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse sentiment analysis response
        
        Args:
            response_text: Raw response from API
            
        Returns:
            Parsed sentiment data
        """
        result = {
            'sentiment': 'neutral',
            'sentiment_label': 'Neutral',
            'intensity': 50,
            'emotions': [],
            'urgency_level': 'medium',
            'key_indicators': []
        }
        
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Parse primary sentiment
            if line.startswith('Primary Sentiment:'):
                sentiment = line.split(':', 1)[1].strip().lower()
                for key in self.SENTIMENTS.keys():
                    if key in sentiment:
                        result['sentiment'] = key
                        result['sentiment_label'] = self.SENTIMENTS[key]
                        break
            
            # Parse intensity
            elif line.startswith('Intensity:'):
                try:
                    intensity_str = line.split(':', 1)[1].strip()
                    # Extract number from string
                    intensity = int(''.join(filter(str.isdigit, intensity_str)))
                    result['intensity'] = min(100, max(0, intensity))
                except:
                    pass
            
            # Parse emotions
            elif line.startswith('Emotions:'):
                emotions_str = line.split(':', 1)[1].strip()
                emotions = [e.strip() for e in emotions_str.split(',')]
                result['emotions'] = [e for e in emotions if e and e != 'N/A']
            
            # Parse urgency level
            elif line.startswith('Urgency Level:'):
                urgency = line.split(':', 1)[1].strip().lower()
                if urgency in ['critical', 'high', 'medium', 'low']:
                    result['urgency_level'] = urgency
            
            # Parse key indicators
            elif line.startswith('-') and 'Key Indicators' in response_text[:response_text.index(line)]:
                indicator = line.lstrip('-').strip()
                if indicator:
                    result['key_indicators'].append(indicator)
        
        return result
    
    def get_sentiment_emoji(self, sentiment: str) -> str:
        """
        Get emoji representation of sentiment
        
        Args:
            sentiment: Sentiment category
            
        Returns:
            Emoji string
        """
        emoji_map = {
            'angry': '😠',
            'dissatisfied': '😞',
            'neutral': '😐',
            'satisfied': '😊',
            'urgent': '⚠️'
        }
        return emoji_map.get(sentiment, '😐')
    
    def get_urgency_emoji(self, urgency: str) -> str:
        """
        Get emoji representation of urgency
        
        Args:
            urgency: Urgency level
            
        Returns:
            Emoji string
        """
        emoji_map = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '📋',
            'low': '📝'
        }
        return emoji_map.get(urgency, '📋')

# Made with Bob
