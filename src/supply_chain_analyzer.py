"""
Supply Chain Impact Analyzer
Analyzes downstream and upstream supply chain impacts of production issues
"""

from typing import Dict, Any, List
from .gemini_client import GeminiClient


class SupplyChainAnalyzer:
    """Analyzes supply chain impacts and dependencies"""
    
    # Supply chain tier definitions
    TIER_DEFINITIONS = {
        'tier1': 'Direct customers/suppliers',
        'tier2': 'Customers of customers / Suppliers of suppliers',
        'tier3': 'Extended supply chain network'
    }
    
    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize supply chain analyzer
        
        Args:
            gemini_client: Gemini API client instance
        """
        self.gemini_client = gemini_client
    
    def analyze_supply_chain_impact(
        self,
        alert: Dict[str, Any],
        downtime_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze supply chain impact of production issue
        
        Args:
            alert: Production alert data
            downtime_data: Downtime calculation results
            
        Returns:
            Supply chain impact analysis
        """
        prompt = self._build_supply_chain_prompt(alert, downtime_data)
        
        try:
            response = self.gemini_client.generate_content(
                prompt=prompt,
                temperature=0.2,
                max_tokens=800
            )
            
            result = self._parse_supply_chain_response(response)
            
            # Add quantitative metrics
            result['metrics'] = self._calculate_supply_chain_metrics(alert, downtime_data)
            
            return result
            
        except Exception as e:
            print(f"✗ Supply chain analysis error: {e}")
            return {
                'downstream_impact': 'unknown',
                'upstream_impact': 'unknown',
                'affected_customers': [],
                'affected_suppliers': [],
                'mitigation_strategies': [],
                'metrics': {},
                'error': str(e)
            }
    
    def _build_supply_chain_prompt(
        self,
        alert: Dict[str, Any],
        downtime_data: Dict[str, Any] = None
    ) -> str:
        """
        Build prompt for supply chain analysis
        
        Args:
            alert: Alert data
            downtime_data: Downtime impact data
            
        Returns:
            Formatted prompt
        """
        prompt = f"""Analyze the supply chain impact of this manufacturing production issue.

**Production Issue:**
Facility: {alert.get('facility_name', 'N/A')}
Industry: {alert.get('industry', 'N/A')}
Issue Type: {alert.get('issue_type', 'N/A')}
Severity: {alert.get('severity', 'N/A')}
Affected Product Lines: {alert.get('product_lines', 'N/A')}
Production Capacity: {alert.get('daily_capacity_units', 'N/A')} units/day
"""

        if downtime_data:
            prompt += f"""
**Downtime Impact:**
Estimated Duration: {downtime_data.get('estimated_duration_hours', 0)} hours
Units Lost: {downtime_data.get('production_impact', {}).get('units_lost', 0)}
Financial Impact: ${downtime_data.get('financial_impact', {}).get('total_cost', 0):,}
"""

        prompt += f"""
**Customer Information:**
Key Customers: {', '.join(alert.get('key_customers', ['Unknown']))}
Customer Industries: {', '.join(alert.get('customer_industries', ['Unknown']))}
Just-in-Time Delivery: {alert.get('jit_delivery', False)}

**Supply Chain Analysis Required:**

1. **Downstream Impact** (Impact on customers):
   - Which customers will be affected?
   - What is the severity of impact for each customer?
   - Will this cause customer production delays?
   - Risk of customer switching to competitors?
   - Contractual penalties or SLA violations?

2. **Upstream Impact** (Impact on suppliers):
   - Which suppliers will be affected by reduced orders?
   - Will this cause supplier inventory buildup?
   - Impact on supplier relationships?

3. **Ripple Effects**:
   - How far will the impact propagate through the supply chain?
   - Which industries will be affected?
   - Estimated number of companies impacted?

4. **Mitigation Strategies**:
   - Alternative sourcing options
   - Inventory reallocation
   - Production rescheduling
   - Customer communication plan
   - Supplier coordination needs

5. **Timeline**:
   - When will customers start experiencing shortages?
   - Critical decision points
   - Point of no return for mitigation

**Response Format:**

Downstream Impact Severity: [critical/high/medium/low]

Affected Customers:
- [Customer 1]: [Impact description]
- [Customer 2]: [Impact description]

Upstream Impact Severity: [critical/high/medium/low]

Affected Suppliers:
- [Supplier 1]: [Impact description]

Ripple Effects:
- [Effect 1]
- [Effect 2]

Mitigation Strategies:
- [Strategy 1]
- [Strategy 2]
- [Strategy 3]

Critical Timeline:
- [Hour X]: [Event]
- [Hour Y]: [Event]

Provide specific, actionable analysis based on the manufacturing context.
"""
        return prompt
    
    def _parse_supply_chain_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse supply chain analysis response
        
        Args:
            response_text: Raw response from API
            
        Returns:
            Parsed supply chain data
        """
        result = {
            'downstream_impact': 'medium',
            'upstream_impact': 'low',
            'affected_customers': [],
            'affected_suppliers': [],
            'ripple_effects': [],
            'mitigation_strategies': [],
            'critical_timeline': []
        }
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Parse impact severity
            if 'Downstream Impact Severity:' in line:
                severity = line.split(':', 1)[1].strip().lower()
                if severity in ['critical', 'high', 'medium', 'low']:
                    result['downstream_impact'] = severity
            
            elif 'Upstream Impact Severity:' in line:
                severity = line.split(':', 1)[1].strip().lower()
                if severity in ['critical', 'high', 'medium', 'low']:
                    result['upstream_impact'] = severity
            
            # Identify sections
            elif line.startswith('Affected Customers:'):
                current_section = 'customers'
            elif line.startswith('Affected Suppliers:'):
                current_section = 'suppliers'
            elif line.startswith('Ripple Effects:'):
                current_section = 'ripple'
            elif line.startswith('Mitigation Strategies:'):
                current_section = 'mitigation'
            elif line.startswith('Critical Timeline:'):
                current_section = 'timeline'
            
            # Parse list items
            elif line.startswith('-') and current_section:
                item = line.lstrip('-').strip()
                if item:
                    if current_section == 'customers':
                        result['affected_customers'].append(item)
                    elif current_section == 'suppliers':
                        result['affected_suppliers'].append(item)
                    elif current_section == 'ripple':
                        result['ripple_effects'].append(item)
                    elif current_section == 'mitigation':
                        result['mitigation_strategies'].append(item)
                    elif current_section == 'timeline':
                        result['critical_timeline'].append(item)
        
        return result
    
    def _calculate_supply_chain_metrics(
        self,
        alert: Dict[str, Any],
        downtime_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate quantitative supply chain metrics
        
        Args:
            alert: Alert data
            downtime_data: Downtime impact data
            
        Returns:
            Supply chain metrics
        """
        metrics = {}
        
        # Customer impact metrics
        num_customers = len(alert.get('key_customers', []))
        if num_customers == 0:
            num_customers = alert.get('estimated_customer_count', 10)
        
        metrics['affected_customer_count'] = num_customers
        
        # Calculate shortage timeline
        if downtime_data:
            units_lost = downtime_data.get('production_impact', {}).get('units_lost', 0)
            daily_capacity = alert.get('daily_capacity_units', 1000)
            
            # Days of production lost
            days_lost = units_lost / daily_capacity if daily_capacity > 0 else 0
            metrics['production_days_lost'] = round(days_lost, 2)
            
            # Customer inventory depletion
            customer_inventory_days = alert.get('customer_inventory_days', 3)
            hours_until_shortage = customer_inventory_days * 24
            metrics['hours_until_customer_shortage'] = hours_until_shortage
            
            # Supplier impact
            supplier_count = len(alert.get('key_suppliers', []))
            if supplier_count == 0:
                supplier_count = alert.get('estimated_supplier_count', 5)
            metrics['affected_supplier_count'] = supplier_count
        
        # Supply chain depth
        jit_delivery = alert.get('jit_delivery', False)
        if jit_delivery:
            metrics['supply_chain_vulnerability'] = 'high'
            metrics['buffer_inventory_days'] = 0
        else:
            metrics['supply_chain_vulnerability'] = 'medium'
            metrics['buffer_inventory_days'] = alert.get('customer_inventory_days', 7)
        
        # Estimated companies impacted (tier 1 + tier 2)
        tier1_impact = num_customers + metrics.get('affected_supplier_count', 0)
        tier2_multiplier = 3  # Each tier 1 company affects ~3 tier 2 companies
        metrics['estimated_total_companies_impacted'] = tier1_impact * (1 + tier2_multiplier)
        
        return metrics
    
    def get_impact_emoji(self, impact_level: str) -> str:
        """
        Get emoji for impact level
        
        Args:
            impact_level: Impact severity level
            
        Returns:
            Emoji string
        """
        emoji_map = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '📊',
            'low': '✅'
        }
        return emoji_map.get(impact_level, '📊')
    
    def format_timeline(self, hours: float) -> str:
        """
        Format timeline in human-readable format
        
        Args:
            hours: Hours until event
            
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
