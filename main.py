"""
AI-Powered Customer Success Email Prioritization System
Main Entry Point
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.data_loader import EmailDataLoader
from src.gemini_client import GeminiClient
from src.classifier import EmailClassifier
from src.sentiment_analyzer import SentimentAnalyzer
from src.churn_predictor import ChurnPredictor
from src.response_optimizer import ResponseOptimizer


def main():
    """Main processing function"""
    
    print("="*70)
    print("📧 AI-Powered Customer Success Email Prioritization System")
    print("="*70)
    
    # 1. Initialize data loader
    print("\n[1] Initializing data loader...")
    data_loader = EmailDataLoader()
    
    # 2. Load historical email data
    print("\n[2] Loading historical email data...")
    historical_emails = data_loader.load_json('data/historical_emails.json')
    
    if not historical_emails:
        print("⚠️  Historical email data not found.")
        print("   Please check data/historical_emails.json")
        return
    
    # Display data statistics
    summary = data_loader.get_email_summary(historical_emails)
    print(f"\n📊 Historical Email Statistics:")
    print(f"   Total: {summary['total']} emails")
    print(f"   High Priority: {summary['starred']} emails ({summary['star_rate']}%)")
    print(f"   Standard Priority: {summary['unstarred']} emails")
    
    # 3. Load new email data
    print("\n[3] Loading new emails...")
    new_emails = data_loader.load_json('data/new_emails.json')
    
    if not new_emails:
        print("⚠️  New email data not found.")
        print("   Please check data/new_emails.json")
        return
    
    print(f"   New emails: {len(new_emails)}")
    
    # 4. Initialize Gemini API client
    print("\n[4] Initializing Gemini API client...")
    try:
        gemini_client = GeminiClient(model_id="gemini-2.0-flash-exp")
        
        # Test connection
        print("   Testing API connection...")
        if not gemini_client.test_connection():
            print("✗ API connection failed.")
            return
            
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("   Please check if GEMINI_API_KEY is set in .env file.")
        return
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return
    
    # 5. Initialize analyzers
    print("\n[5] Initializing AI analyzers...")
    sentiment_analyzer = SentimentAnalyzer(gemini_client)
    churn_predictor = ChurnPredictor(gemini_client)
    response_optimizer = ResponseOptimizer()
    print("   ✓ Sentiment Analyzer ready")
    print("   ✓ Churn Risk Predictor ready")
    print("   ✓ Response Time Optimizer ready")
    
    # 6. Analyze emails
    print("\n[6] Starting comprehensive email analysis...")
    print(f"\n{'='*70}")
    
    results = []
    
    for i, email in enumerate(new_emails, 1):
        print(f"\n📧 Analyzing Email [{i}/{len(new_emails)}]")
        print(f"   Subject: {email.get('subject', 'N/A')[:60]}...")
        print(f"   From: {email.get('sender', 'N/A')}")
        print(f"   Customer: {email.get('customer_tier', 'N/A').capitalize()} (LTV: ${email.get('customer_ltv', 0):,})")
        
        # Sentiment analysis
        print("\n   🔍 Analyzing sentiment...")
        sentiment_data = sentiment_analyzer.analyze_sentiment(email)
        
        # Churn risk prediction
        print("   🔍 Predicting churn risk...")
        churn_data = churn_predictor.predict_churn_risk(
            email=email,
            sentiment_data=sentiment_data
        )
        
        # Response time optimization
        print("   🔍 Optimizing response time...")
        response_data = response_optimizer.calculate_optimal_response_time(
            email=email,
            sentiment_data=sentiment_data,
            churn_data=churn_data
        )
        
        # Compile results
        result = {
            'email': email,
            'sentiment': sentiment_data,
            'churn_risk': churn_data,
            'response': response_data
        }
        results.append(result)
        
        # Display analysis results
        print(f"\n   📊 Analysis Results:")
        print(f"   {sentiment_analyzer.get_sentiment_emoji(sentiment_data.get('sentiment', 'neutral'))} Sentiment: {sentiment_data.get('sentiment_label', 'N/A')} (Intensity: {sentiment_data.get('intensity', 0)}/100)")
        print(f"   {sentiment_analyzer.get_urgency_emoji(sentiment_data.get('urgency_level', 'medium'))} Urgency: {sentiment_data.get('urgency_level', 'N/A').capitalize()}")
        print(f"   {churn_predictor.get_risk_emoji(churn_data.get('risk_level', 'medium'))} Churn Risk: {churn_data.get('risk_level', 'N/A').upper()} ({churn_data.get('risk_score', 0)}%)")
        print(f"   {response_optimizer.get_response_emoji(response_data.get('response_category', 'normal'))} Response Time: {response_optimizer.format_response_time(response_data.get('recommended_hours', 24))}")
        print(f"   ⏰ Deadline: {response_data.get('deadline', 'N/A')}")
        
        print(f"\n   {'─'*66}")
    
    # 7. Display comprehensive summary
    print(f"\n{'='*70}")
    print("📊 COMPREHENSIVE ANALYSIS SUMMARY")
    print(f"{'='*70}")
    
    # Priority distribution
    immediate = sum(1 for r in results if r['response']['response_category'] == 'immediate')
    urgent = sum(1 for r in results if r['response']['response_category'] == 'urgent')
    high = sum(1 for r in results if r['response']['response_category'] == 'high')
    normal = sum(1 for r in results if r['response']['response_category'] == 'normal')
    low = sum(1 for r in results if r['response']['response_category'] == 'low')
    
    print(f"\n🎯 Priority Distribution:")
    print(f"   🚨 Immediate: {immediate} emails")
    print(f"   ⚡ Urgent: {urgent} emails")
    print(f"   ⏰ High: {high} emails")
    print(f"   📅 Normal: {normal} emails")
    print(f"   📝 Low: {low} emails")
    
    # Churn risk distribution
    critical_risk = sum(1 for r in results if r['churn_risk']['risk_level'] == 'critical')
    high_risk = sum(1 for r in results if r['churn_risk']['risk_level'] == 'high')
    medium_risk = sum(1 for r in results if r['churn_risk']['risk_level'] == 'medium')
    low_risk = sum(1 for r in results if r['churn_risk']['risk_level'] == 'low')
    
    print(f"\n⚠️  Churn Risk Distribution:")
    print(f"   🚨 Critical: {critical_risk} customers")
    print(f"   ⚠️  High: {high_risk} customers")
    print(f"   ⚡ Medium: {medium_risk} customers")
    print(f"   ✅ Low: {low_risk} customers")
    
    # Sentiment distribution
    angry = sum(1 for r in results if r['sentiment']['sentiment'] == 'angry')
    dissatisfied = sum(1 for r in results if r['sentiment']['sentiment'] == 'dissatisfied')
    neutral = sum(1 for r in results if r['sentiment']['sentiment'] == 'neutral')
    satisfied = sum(1 for r in results if r['sentiment']['sentiment'] == 'satisfied')
    urgent_sentiment = sum(1 for r in results if r['sentiment']['sentiment'] == 'urgent')
    
    print(f"\n😊 Sentiment Distribution:")
    print(f"   😠 Angry: {angry} emails")
    print(f"   😞 Dissatisfied: {dissatisfied} emails")
    print(f"   😐 Neutral: {neutral} emails")
    print(f"   😊 Satisfied: {satisfied} emails")
    print(f"   ⚠️  Urgent: {urgent_sentiment} emails")
    
    # 8. Display detailed results
    print(f"\n{'='*70}")
    print("📝 DETAILED EMAIL ANALYSIS")
    print(f"{'='*70}")
    
    # Sort by priority score (highest first)
    sorted_results = sorted(results, key=lambda x: x['response']['priority_score'], reverse=True)
    
    for i, result in enumerate(sorted_results, 1):
        email = result['email']
        sentiment = result['sentiment']
        churn = result['churn_risk']
        response = result['response']
        
        print(f"\n{'─'*70}")
        print(f"Email #{i} - Priority Score: {response['priority_score']}/100")
        print(f"{'─'*70}")
        print(f"📧 Subject: {email.get('subject', 'N/A')}")
        print(f"👤 From: {email.get('sender', 'N/A')}")
        print(f"💼 Customer: {email.get('customer_tier', 'N/A').capitalize()} (LTV: ${email.get('customer_ltv', 0):,})")
        
        print(f"\n📊 Analysis:")
        print(f"   Sentiment: {sentiment.get('sentiment_label', 'N/A')} ({sentiment.get('intensity', 0)}/100)")
        if sentiment.get('emotions'):
            print(f"   Emotions: {', '.join(sentiment.get('emotions', [])[:3])}")
        
        print(f"\n⚠️  Churn Risk: {churn.get('risk_level', 'N/A').upper()} ({churn.get('risk_score', 0)}%)")
        if churn.get('risk_factors'):
            print(f"   Risk Factors:")
            for factor in churn.get('risk_factors', [])[:3]:
                print(f"      • {factor}")
        
        print(f"\n⏰ Response Recommendation:")
        print(f"   Category: {response.get('response_category', 'N/A').upper()}")
        print(f"   Time: {response_optimizer.format_response_time(response.get('recommended_hours', 24))}")
        print(f"   Deadline: {response.get('deadline', 'N/A')}")
        print(f"   Reasoning: {response.get('reasoning', 'N/A')}")
        
        if churn.get('mitigation_actions'):
            print(f"\n💡 Recommended Actions:")
            for action in churn.get('mitigation_actions', [])[:3]:
                print(f"      • {action}")
    
    print(f"\n{'='*70}")
    print("✅ Analysis Complete!")
    print(f"{'='*70}")
    print(f"\n📈 Key Insights:")
    print(f"   • {immediate + urgent} emails require immediate/urgent attention")
    print(f"   • {critical_risk + high_risk} customers at high churn risk")
    print(f"   • {angry + dissatisfied} customers expressing negative sentiment")
    print(f"\n💼 Business Impact:")
    total_at_risk_ltv = sum(r['email'].get('customer_ltv', 0) for r in results if r['churn_risk']['risk_level'] in ['critical', 'high'])
    print(f"   • ${total_at_risk_ltv:,} in customer LTV at risk")
    print(f"   • Average response time: {sum(r['response']['recommended_hours'] for r in results) / len(results):.1f} hours")
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    main()

# Made with Bob
