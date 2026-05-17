"""
AI-Powered Manufacturing IoT Alert Prioritization System
Specialized for Predictive Maintenance and Supply Chain Management
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.data_loader import EmailDataLoader
from src.gemini_client import GeminiClient
from src.sentiment_analyzer import SentimentAnalyzer
from src.downtime_calculator import DowntimeCalculator
from src.supply_chain_analyzer import SupplyChainAnalyzer
from src.response_optimizer import ResponseOptimizer


def main():
    """Main processing function for manufacturing alerts"""
    
    print("="*80)
    print("🏭 AI-Powered Manufacturing IoT Alert Prioritization System")
    print("   Predictive Maintenance | Supply Chain Intelligence | Downtime Prevention")
    print("="*80)
    
    # 1. Initialize components
    print("\n[1] Initializing system components...")
    data_loader = EmailDataLoader()
    downtime_calculator = DowntimeCalculator()
    
    # 2. Load historical alert data
    print("\n[2] Loading historical manufacturing alerts...")
    historical_alerts = data_loader.load_json('data/manufacturing_alerts.json')
    
    if not historical_alerts:
        print("⚠️  Historical alert data not found.")
        print("   Please check data/manufacturing_alerts.json")
        return
    
    # Display statistics
    summary = data_loader.get_email_summary(historical_alerts)
    print(f"\n📊 Historical Alert Statistics:")
    print(f"   Total Alerts: {summary['total']}")
    print(f"   Critical Alerts: {summary['starred']} ({summary['star_rate']}%)")
    print(f"   Standard Alerts: {summary['unstarred']}")
    
    # 3. Load new alerts
    print("\n[3] Loading new manufacturing alerts...")
    new_alerts = data_loader.load_json('data/new_manufacturing_alerts.json')
    
    if not new_alerts:
        print("⚠️  New alert data not found.")
        print("   Please check data/new_manufacturing_alerts.json")
        return
    
    print(f"   New Alerts: {len(new_alerts)}")
    
    # 4. Initialize AI components
    print("\n[4] Initializing AI analysis engines...")
    try:
        gemini_client = GeminiClient(model_id="gemini-2.0-flash-exp")
        
        print("   Testing API connection...")
        if not gemini_client.test_connection():
            print("✗ API connection failed.")
            return
        
        sentiment_analyzer = SentimentAnalyzer(gemini_client)
        supply_chain_analyzer = SupplyChainAnalyzer(gemini_client)
        response_optimizer = ResponseOptimizer()
        
        print("   ✓ Sentiment Analyzer ready")
        print("   ✓ Downtime Calculator ready")
        print("   ✓ Supply Chain Analyzer ready")
        print("   ✓ Response Optimizer ready")
            
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("   Please check if GEMINI_API_KEY is set in .env file.")
        return
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return
    
    # 5. Analyze alerts
    print("\n[5] Starting comprehensive manufacturing alert analysis...")
    print(f"\n{'='*80}")
    
    results = []
    total_financial_impact = 0
    total_units_lost = 0
    critical_alerts = 0
    
    for i, alert in enumerate(new_alerts, 1):
        print(f"\n🏭 Analyzing Alert [{i}/{len(new_alerts)}]")
        print(f"{'─'*80}")
        print(f"📋 Subject: {alert.get('subject', 'N/A')[:70]}...")
        print(f"🏢 Facility: {alert.get('facility_name', 'N/A')}")
        print(f"🏭 Industry: {alert.get('industry', 'N/A').capitalize()}")
        print(f"⚠️  Severity: {alert.get('severity', 'N/A').replace('_', ' ').title()}")
        
        # Calculate downtime impact
        print(f"\n   💰 Calculating financial impact...")
        downtime_data = downtime_calculator.calculate_downtime_impact(alert)
        
        financial_impact = downtime_data['financial_impact']['total_cost']
        units_lost = downtime_data['production_impact']['units_lost']
        total_financial_impact += financial_impact
        total_units_lost += units_lost
        
        # Sentiment analysis
        print(f"   😠 Analyzing urgency and sentiment...")
        sentiment_data = sentiment_analyzer.analyze_sentiment(alert)
        
        # Supply chain impact
        print(f"   🔗 Analyzing supply chain impact...")
        supply_chain_data = supply_chain_analyzer.analyze_supply_chain_impact(
            alert=alert,
            downtime_data=downtime_data
        )
        
        # Response optimization
        print(f"   ⏰ Optimizing response strategy...")
        
        # Adapt alert data for response optimizer
        alert_for_response = {
            **alert,
            'customer_tier': 'enterprise' if financial_impact > 1000000 else 'premium',
            'customer_ltv': financial_impact * 10  # Estimate customer value
        }
        
        response_data = response_optimizer.calculate_optimal_response_time(
            email=alert_for_response,
            sentiment_data=sentiment_data,
            churn_data={'risk_level': supply_chain_data.get('downstream_impact', 'medium'), 'risk_score': 70}
        )
        
        if response_data['response_category'] in ['immediate', 'urgent']:
            critical_alerts += 1
        
        # Compile results
        result = {
            'alert': alert,
            'downtime': downtime_data,
            'sentiment': sentiment_data,
            'supply_chain': supply_chain_data,
            'response': response_data
        }
        results.append(result)
        
        # Display key metrics
        print(f"\n   📊 Impact Summary:")
        print(f"   {downtime_calculator.get_severity_emoji(alert.get('severity', 'unknown'))} Severity: {alert.get('severity', 'N/A').replace('_', ' ').upper()}")
        print(f"   💵 Financial Impact: {downtime_calculator.format_currency(financial_impact)}")
        print(f"   📦 Units Lost: {units_lost:,}")
        print(f"   ⏱️  Downtime: {downtime_data['estimated_duration_hours']:.1f} hours")
        print(f"   🔄 Recovery: {downtime_data['recovery']['estimated_recovery_hours']:.1f} hours")
        print(f"   🔗 Supply Chain: {supply_chain_data.get('downstream_impact', 'unknown').upper()} impact")
        print(f"   ⚡ Response: {response_data['response_category'].upper()} ({response_optimizer.format_response_time(response_data['recommended_hours'])})")
        print(f"   ⏰ Deadline: {response_data['deadline']}")
        
        print(f"\n   {'─'*76}")
    
    # 6. Display comprehensive summary
    print(f"\n{'='*80}")
    print("📊 MANUFACTURING OPERATIONS SUMMARY")
    print(f"{'='*80}")
    
    print(f"\n🚨 Alert Priority Distribution:")
    immediate = sum(1 for r in results if r['response']['response_category'] == 'immediate')
    urgent = sum(1 for r in results if r['response']['response_category'] == 'urgent')
    high = sum(1 for r in results if r['response']['response_category'] == 'high')
    normal = sum(1 for r in results if r['response']['response_category'] == 'normal')
    
    print(f"   🚨 IMMEDIATE: {immediate} alerts (< 30 min response required)")
    print(f"   ⚡ URGENT: {urgent} alerts (< 2 hour response required)")
    print(f"   ⏰ HIGH: {high} alerts (< 4 hour response required)")
    print(f"   📅 NORMAL: {normal} alerts (< 24 hour response required)")
    
    print(f"\n💰 Financial Impact Analysis:")
    print(f"   Total Production Loss: {downtime_calculator.format_currency(total_financial_impact)}")
    print(f"   Average per Alert: {downtime_calculator.format_currency(total_financial_impact / len(results))}")
    print(f"   Highest Impact: {downtime_calculator.format_currency(max(r['downtime']['financial_impact']['total_cost'] for r in results))}")
    
    print(f"\n📦 Production Impact:")
    print(f"   Total Units Lost: {total_units_lost:,}")
    print(f"   Average per Alert: {int(total_units_lost / len(results)):,}")
    
    print(f"\n🔗 Supply Chain Impact:")
    critical_sc = sum(1 for r in results if r['supply_chain'].get('downstream_impact') == 'critical')
    high_sc = sum(1 for r in results if r['supply_chain'].get('downstream_impact') == 'high')
    print(f"   Critical Supply Chain Impact: {critical_sc} alerts")
    print(f"   High Supply Chain Impact: {high_sc} alerts")
    
    total_companies = sum(r['supply_chain'].get('metrics', {}).get('estimated_total_companies_impacted', 0) for r in results)
    print(f"   Estimated Companies Affected: {int(total_companies)}")
    
    # 7. Detailed alert analysis
    print(f"\n{'='*80}")
    print("📝 DETAILED ALERT ANALYSIS (Sorted by Financial Impact)")
    print(f"{'='*80}")
    
    # Sort by financial impact
    sorted_results = sorted(results, key=lambda x: x['downtime']['financial_impact']['total_cost'], reverse=True)
    
    for i, result in enumerate(sorted_results, 1):
        alert = result['alert']
        downtime = result['downtime']
        sentiment = result['sentiment']
        supply_chain = result['supply_chain']
        response = result['response']
        
        print(f"\n{'─'*80}")
        print(f"Alert #{i} - Priority Score: {response['priority_score']}/100")
        print(f"{'─'*80}")
        
        print(f"\n🏭 FACILITY INFORMATION:")
        print(f"   Facility: {alert.get('facility_name', 'N/A')}")
        print(f"   Industry: {alert.get('industry', 'N/A').capitalize()}")
        print(f"   Type: {alert.get('facility_type', 'N/A').replace('_', ' ').title()}")
        print(f"   Issue: {alert.get('issue_type', 'N/A').replace('_', ' ').title()}")
        
        print(f"\n📧 ALERT DETAILS:")
        print(f"   Subject: {alert.get('subject', 'N/A')}")
        print(f"   Severity: {alert.get('severity', 'N/A').replace('_', ' ').upper()}")
        print(f"   Affected Lines: {alert.get('affected_production_lines', 0)}")
        print(f"   Idle Workers: {alert.get('shift_workers', 0)}")
        
        print(f"\n💰 FINANCIAL IMPACT:")
        print(f"   Total Cost: {downtime_calculator.format_currency(downtime['financial_impact']['total_cost'])}")
        print(f"   Production Loss: {downtime_calculator.format_currency(downtime['financial_impact']['production_loss'])}")
        print(f"   Labor Cost: {downtime_calculator.format_currency(downtime['financial_impact']['labor_cost'])}")
        print(f"   Equipment Damage: {downtime_calculator.format_currency(downtime['financial_impact']['equipment_damage'])}")
        print(f"   Cost per Hour: {downtime_calculator.format_currency(downtime['financial_impact']['cost_per_hour'])}/hr")
        
        print(f"\n📦 PRODUCTION IMPACT:")
        print(f"   Units Lost: {downtime['production_impact']['units_lost']:,}")
        print(f"   Capacity Loss: {downtime['production_impact']['capacity_utilization_loss']}")
        print(f"   Downtime: {downtime['estimated_duration_hours']:.1f} hours")
        print(f"   Recovery Time: {downtime['recovery']['estimated_recovery_hours']:.1f} hours")
        print(f"   Full Capacity ETA: {downtime['recovery']['full_capacity_eta']}")
        
        print(f"\n🔗 SUPPLY CHAIN IMPACT:")
        print(f"   Downstream Impact: {supply_chain.get('downstream_impact', 'unknown').upper()}")
        print(f"   Upstream Impact: {supply_chain.get('upstream_impact', 'unknown').upper()}")
        
        if supply_chain.get('affected_customers'):
            print(f"   Key Affected Customers:")
            for customer in supply_chain.get('affected_customers', [])[:3]:
                print(f"      • {customer}")
        
        sc_metrics = supply_chain.get('metrics', {})
        if sc_metrics:
            print(f"   Companies Impacted: ~{sc_metrics.get('estimated_total_companies_impacted', 0)}")
            if 'hours_until_customer_shortage' in sc_metrics:
                print(f"   Customer Shortage In: {supply_chain_analyzer.format_timeline(sc_metrics['hours_until_customer_shortage'])}")
        
        print(f"\n⏰ RESPONSE STRATEGY:")
        print(f"   Category: {response['response_category'].upper()}")
        print(f"   Response Time: {response_optimizer.format_response_time(response['recommended_hours'])}")
        print(f"   Deadline: {response['deadline']}")
        print(f"   Reasoning: {response['reasoning']}")
        
        if supply_chain.get('mitigation_strategies'):
            print(f"\n💡 MITIGATION STRATEGIES:")
            for strategy in supply_chain.get('mitigation_strategies', [])[:4]:
                print(f"      • {strategy}")
    
    # 8. Executive summary
    print(f"\n{'='*80}")
    print("🎯 EXECUTIVE SUMMARY")
    print(f"{'='*80}")
    
    print(f"\n📊 Key Metrics:")
    print(f"   • {critical_alerts} alerts require immediate/urgent response")
    print(f"   • {downtime_calculator.format_currency(total_financial_impact)} total financial exposure")
    print(f"   • {total_units_lost:,} production units at risk")
    print(f"   • ~{int(total_companies)} companies in supply chain affected")
    
    print(f"\n⚠️  Critical Actions Required:")
    critical_results = [r for r in results if r['response']['response_category'] in ['immediate', 'urgent']]
    for r in critical_results:
        alert = r['alert']
        response = r['response']
        print(f"   • {alert.get('facility_name', 'Unknown')}: {response['response_category'].upper()} response needed")
        print(f"     Deadline: {response['deadline']} | Impact: {downtime_calculator.format_currency(r['downtime']['financial_impact']['total_cost'])}")
    
    print(f"\n{'='*80}")
    print("✅ Analysis Complete - Manufacturing Operations Intelligence Ready")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

# Made with Bob
