"""
Production Downtime Impact Calculator
Calculates financial and operational impact of manufacturing downtime
"""

from typing import Dict, Any
from datetime import datetime, timedelta


class DowntimeCalculator:
    """Calculates production downtime impact and costs"""
    
    # Industry-specific hourly production values (USD)
    INDUSTRY_HOURLY_VALUES = {
        'automotive': 150000,      # Automotive assembly line
        'semiconductor': 500000,   # Chip fabrication
        'pharmaceutical': 200000,  # Drug manufacturing
        'food_beverage': 50000,    # Food processing
        'electronics': 100000,     # Electronics assembly
        'aerospace': 300000,       # Aircraft manufacturing
        'chemical': 180000,        # Chemical processing
        'steel': 120000           # Steel production
    }
    
    # Downtime severity levels
    SEVERITY_MULTIPLIERS = {
        'complete_shutdown': 1.0,      # 100% production loss
        'partial_degradation': 0.5,    # 50% production loss
        'intermittent': 0.3,           # 30% production loss
        'minor_slowdown': 0.1          # 10% production loss
    }
    
    def __init__(self):
        """Initialize downtime calculator"""
        pass
    
    def calculate_downtime_impact(
        self,
        alert: Dict[str, Any],
        estimated_duration_hours: float = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive downtime impact
        
        Args:
            alert: Alert/incident data
            estimated_duration_hours: Estimated downtime duration
            
        Returns:
            Downtime impact analysis
        """
        # Extract alert details
        industry = alert.get('industry', 'automotive')
        facility_type = alert.get('facility_type', 'assembly_line')
        severity = alert.get('severity', 'complete_shutdown')
        affected_lines = alert.get('affected_production_lines', 1)
        shift_workers = alert.get('shift_workers', 200)
        
        # Estimate duration if not provided
        if estimated_duration_hours is None:
            estimated_duration_hours = self._estimate_duration(alert)
        
        # Calculate financial impact
        hourly_value = self.INDUSTRY_HOURLY_VALUES.get(industry, 100000)
        severity_multiplier = self.SEVERITY_MULTIPLIERS.get(severity, 1.0)
        
        # Base production loss
        production_loss_per_hour = hourly_value * severity_multiplier * affected_lines
        total_production_loss = production_loss_per_hour * estimated_duration_hours
        
        # Additional costs
        labor_cost = self._calculate_labor_cost(shift_workers, estimated_duration_hours)
        equipment_damage = self._estimate_equipment_damage(alert)
        quality_impact = self._estimate_quality_impact(alert, production_loss_per_hour)
        
        # Total financial impact
        total_cost = (
            total_production_loss +
            labor_cost +
            equipment_damage +
            quality_impact
        )
        
        # Calculate production units lost
        units_per_hour = alert.get('units_per_hour', 100)
        units_lost = int(units_per_hour * estimated_duration_hours * severity_multiplier * affected_lines)
        
        # Calculate recovery time
        recovery_hours = self._estimate_recovery_time(severity, estimated_duration_hours)
        
        return {
            'estimated_duration_hours': round(estimated_duration_hours, 2),
            'severity': severity,
            'affected_production_lines': affected_lines,
            'financial_impact': {
                'production_loss': int(total_production_loss),
                'labor_cost': int(labor_cost),
                'equipment_damage': int(equipment_damage),
                'quality_impact': int(quality_impact),
                'total_cost': int(total_cost),
                'cost_per_hour': int(production_loss_per_hour)
            },
            'production_impact': {
                'units_lost': units_lost,
                'units_per_hour': units_per_hour,
                'capacity_utilization_loss': f"{severity_multiplier * 100:.0f}%"
            },
            'recovery': {
                'estimated_recovery_hours': round(recovery_hours, 2),
                'full_capacity_eta': self._calculate_eta(estimated_duration_hours + recovery_hours)
            },
            'workforce_impact': {
                'idle_workers': shift_workers,
                'labor_cost_per_hour': int(labor_cost / estimated_duration_hours) if estimated_duration_hours > 0 else 0
            }
        }
    
    def _estimate_duration(self, alert: Dict[str, Any]) -> float:
        """
        Estimate downtime duration based on alert details
        
        Args:
            alert: Alert data
            
        Returns:
            Estimated hours
        """
        severity = alert.get('severity', 'complete_shutdown')
        issue_type = alert.get('issue_type', 'unknown')
        
        # Base estimates by issue type
        duration_map = {
            'sensor_failure': 2.0,
            'network_outage': 1.0,
            'mechanical_failure': 8.0,
            'software_crash': 0.5,
            'power_outage': 4.0,
            'supply_shortage': 24.0,
            'quality_issue': 6.0,
            'safety_incident': 12.0,
            'unknown': 4.0
        }
        
        base_duration = duration_map.get(issue_type, 4.0)
        
        # Adjust by severity
        if severity == 'minor_slowdown':
            return base_duration * 0.5
        elif severity == 'intermittent':
            return base_duration * 0.75
        elif severity == 'partial_degradation':
            return base_duration * 1.0
        else:  # complete_shutdown
            return base_duration * 1.5
    
    def _calculate_labor_cost(self, workers: int, hours: float) -> float:
        """
        Calculate idle labor cost
        
        Args:
            workers: Number of workers
            hours: Downtime hours
            
        Returns:
            Labor cost in USD
        """
        # Average manufacturing wage: $25/hour + benefits (40% overhead)
        hourly_cost_per_worker = 25 * 1.4
        return workers * hourly_cost_per_worker * hours
    
    def _estimate_equipment_damage(self, alert: Dict[str, Any]) -> float:
        """
        Estimate equipment damage/repair costs
        
        Args:
            alert: Alert data
            
        Returns:
            Estimated damage cost
        """
        issue_type = alert.get('issue_type', 'unknown')
        
        damage_estimates = {
            'mechanical_failure': 50000,
            'power_outage': 10000,
            'sensor_failure': 5000,
            'safety_incident': 100000,
            'quality_issue': 20000,
            'network_outage': 2000,
            'software_crash': 1000,
            'supply_shortage': 0,
            'unknown': 10000
        }
        
        return damage_estimates.get(issue_type, 10000)
    
    def _estimate_quality_impact(self, alert: Dict[str, Any], hourly_value: float) -> float:
        """
        Estimate quality/scrap costs
        
        Args:
            alert: Alert data
            hourly_value: Production value per hour
            
        Returns:
            Quality impact cost
        """
        issue_type = alert.get('issue_type', 'unknown')
        
        # Quality issues cause additional scrap/rework costs
        if issue_type in ['quality_issue', 'mechanical_failure']:
            return hourly_value * 0.3  # 30% of hourly value in scrap
        elif issue_type in ['sensor_failure', 'intermittent']:
            return hourly_value * 0.1  # 10% quality impact
        else:
            return 0
    
    def _estimate_recovery_time(self, severity: str, downtime_hours: float) -> float:
        """
        Estimate time to return to full capacity
        
        Args:
            severity: Downtime severity
            downtime_hours: Duration of downtime
            
        Returns:
            Recovery time in hours
        """
        recovery_factors = {
            'complete_shutdown': 0.5,      # 50% of downtime for recovery
            'partial_degradation': 0.3,    # 30% for recovery
            'intermittent': 0.2,           # 20% for recovery
            'minor_slowdown': 0.1          # 10% for recovery
        }
        
        factor = recovery_factors.get(severity, 0.3)
        return downtime_hours * factor
    
    def _calculate_eta(self, total_hours: float) -> str:
        """
        Calculate estimated time of arrival to full capacity
        
        Args:
            total_hours: Total hours (downtime + recovery)
            
        Returns:
            ETA timestamp
        """
        eta = datetime.now() + timedelta(hours=total_hours)
        return eta.strftime('%Y-%m-%d %H:%M')
    
    def get_severity_emoji(self, severity: str) -> str:
        """
        Get emoji for severity level
        
        Args:
            severity: Severity level
            
        Returns:
            Emoji string
        """
        emoji_map = {
            'complete_shutdown': '🚨',
            'partial_degradation': '⚠️',
            'intermittent': '⚡',
            'minor_slowdown': '📊'
        }
        return emoji_map.get(severity, '⚠️')
    
    def format_currency(self, amount: float) -> str:
        """
        Format currency with appropriate units
        
        Args:
            amount: Dollar amount
            
        Returns:
            Formatted string
        """
        if amount >= 1000000:
            return f"${amount/1000000:.2f}M"
        elif amount >= 1000:
            return f"${amount/1000:.1f}K"
        else:
            return f"${amount:.0f}"

# Made with Bob
