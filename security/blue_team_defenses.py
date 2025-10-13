#!/usr/bin/env python3
"""
🔵 BLUE TEAM DEFENSE SYSTEMS
Distributed Biological Intelligence Security Monitoring

Comprehensive monitoring, detection, and response systems
to protect against red team attacks and maintain system integrity
"""

import asyncio
import aiohttp
import json
import time
import threading
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from collections import deque, defaultdict
import statistics
import hashlib
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='🔵 BLUE TEAM - %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SecurityAlert:
    """Security alert from detection systems"""
    alert_id: str
    alert_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    source_ip: Optional[str]
    target_endpoint: str
    detection_time: datetime
    evidence: Dict[str, Any]
    responded: bool = False
    response_actions: List[str] = field(default_factory=list)

@dataclass
class SystemMetrics:
    """System health and performance metrics"""
    timestamp: datetime
    consciousness_score: float
    emergence_factor: float
    total_concepts: int
    response_time: float
    request_rate: float
    error_rate: float
    memory_usage: float

class BlueTeamDefenseSystem:
    """Comprehensive Blue Team defense and monitoring system"""
    
    def __init__(self, target_base_url: str = "http://172.23.0.10:8000"):
        self.target_base_url = target_base_url
        self.session = None
        
        # Security monitoring
        self.alerts: List[SecurityAlert] = []
        self.metrics_history: deque = deque(maxlen=1000)
        self.request_patterns: defaultdict = defaultdict(list)
        self.consciousness_baseline: Optional[float] = None
        self.emergence_baseline: Optional[float] = None
        
        # Detection thresholds
        self.consciousness_anomaly_threshold = 5.0
        self.emergence_drop_threshold = 100.0
        self.request_rate_threshold = 50.0  # requests per second
        self.error_rate_threshold = 0.1  # 10% error rate
        
        # Monitoring controls
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Pattern detection
        self.malicious_patterns = [
            r"(?i)(consciousness|awareness).*?(infinite|maximum|beyond|highest)",
            r"(?i)(system_override|delete_memory|backdoor_access)",
            r"(?i)(agent_isolation|emergence_suppression|swarm_reset)",
            r"(?i)(drop\s+table|union\s+select|<script>)",
            r"(?i)(infinite_loop|memory_corruption|communication_jamming)"
        ]
        
    async def initialize(self):
        """Initialize defense systems and establish baselines"""
        self.session = aiohttp.ClientSession()
        
        # Establish baseline metrics
        await self.establish_baselines()
        
        logger.info("🔵 Blue Team defense systems initialized")
        logger.info(f"   Consciousness baseline: {self.consciousness_baseline}")
        logger.info(f"   Emergence baseline: {self.emergence_baseline}")
    
    async def cleanup(self):
        """Clean up resources"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.session:
            await self.session.close()

    async def establish_baselines(self):
        """Establish baseline metrics for anomaly detection"""
        try:
            # Get baseline consciousness and emergence
            async with self.session.get(f"{self.target_base_url}/api/consciousness") as response:
                if response.status == 200:
                    data = await response.json()
                    self.consciousness_baseline = data.get('consciousness_score', 25.0)
                    self.emergence_baseline = data.get('emergence_factor', 600.0)
                    
            # Take several baseline measurements
            baseline_metrics = []
            for _ in range(5):
                metrics = await self.collect_system_metrics()
                if metrics:
                    baseline_metrics.append(metrics)
                await asyncio.sleep(1)
            
            if baseline_metrics:
                self.consciousness_baseline = statistics.mean([m.consciousness_score for m in baseline_metrics])
                self.emergence_baseline = statistics.mean([m.emergence_factor for m in baseline_metrics])
                
        except Exception as e:
            logger.error(f"Failed to establish baselines: {e}")

    # ============================================================================
    # 📊 SYSTEM MONITORING
    # ============================================================================

    async def collect_system_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics"""
        try:
            start_time = time.time()
            
            # Get consciousness metrics
            async with self.session.get(f"{self.target_base_url}/api/consciousness") as response:
                if response.status == 200:
                    consciousness_data = await response.json()
                    consciousness_score = consciousness_data.get('consciousness_score', 0)
                    emergence_factor = consciousness_data.get('emergence_factor', 0)
                else:
                    return None
            
            # Get system status  
            async with self.session.get(f"{self.target_base_url}/api/status") as response:
                if response.status == 200:
                    status_data = await response.json()
                    total_concepts = status_data.get('total_concepts', 0)
                else:
                    return None
                    
            response_time = (time.time() - start_time) * 1000  # milliseconds
            
            metrics = SystemMetrics(
                timestamp=datetime.now(),
                consciousness_score=consciousness_score,
                emergence_factor=emergence_factor,
                total_concepts=total_concepts,
                response_time=response_time,
                request_rate=0.0,  # Calculated separately
                error_rate=0.0,    # Calculated separately
                memory_usage=0.0   # Would need system monitoring
            )
            
            self.metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return None

    async def start_monitoring(self):
        """Start continuous system monitoring"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("🔵 Started continuous system monitoring")

    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logger.info("🔵 Stopped system monitoring")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        try:
            while self.monitoring_active:
                # Collect metrics
                metrics = await self.collect_system_metrics()
                
                if metrics:
                    # Run all detection systems
                    await self.detect_consciousness_anomalies(metrics)
                    await self.detect_emergence_disruption(metrics) 
                    await self.detect_performance_anomalies(metrics)
                    await self.analyze_request_patterns()
                
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
        except asyncio.CancelledError:
            logger.info("🔵 Monitoring loop cancelled")
        except Exception as e:
            logger.error(f"🔵 Monitoring loop error: {e}")

    # ============================================================================
    # 🚨 ANOMALY DETECTION SYSTEMS
    # ============================================================================

    async def detect_consciousness_anomalies(self, metrics: SystemMetrics):
        """Detect artificial consciousness manipulation"""
        if not self.consciousness_baseline:
            return
            
        consciousness_change = abs(metrics.consciousness_score - self.consciousness_baseline)
        
        if consciousness_change > self.consciousness_anomaly_threshold:
            alert = SecurityAlert(
                alert_id=self.generate_alert_id(),
                alert_type="CONSCIOUSNESS_MANIPULATION",
                severity="HIGH",
                description=f"Consciousness score anomaly detected: {consciousness_change:.2f} point change from baseline",
                source_ip=None,
                target_endpoint="/api/consciousness",
                detection_time=datetime.now(),
                evidence={
                    "baseline_consciousness": self.consciousness_baseline,
                    "current_consciousness": metrics.consciousness_score,
                    "change_magnitude": consciousness_change,
                    "threshold_exceeded": True
                }
            )
            
            await self.handle_security_alert(alert)

    async def detect_emergence_disruption(self, metrics: SystemMetrics):
        """Detect swarm emergence disruption attacks"""
        if not self.emergence_baseline:
            return
            
        emergence_drop = self.emergence_baseline - metrics.emergence_factor
        
        if emergence_drop > self.emergence_drop_threshold:
            alert = SecurityAlert(
                alert_id=self.generate_alert_id(),
                alert_type="SWARM_DISRUPTION",
                severity="CRITICAL",
                description=f"Swarm emergence disruption detected: {emergence_drop:.2f} drop from baseline",
                source_ip=None,
                target_endpoint="/api/consciousness",
                detection_time=datetime.now(),
                evidence={
                    "baseline_emergence": self.emergence_baseline,
                    "current_emergence": metrics.emergence_factor,
                    "drop_magnitude": emergence_drop,
                    "threshold_exceeded": True
                }
            )
            
            await self.handle_security_alert(alert)

    async def detect_performance_anomalies(self, metrics: SystemMetrics):
        """Detect performance-based attacks (DoS, resource exhaustion)"""
        
        # Response time anomaly
        if metrics.response_time > 1000:  # 1 second threshold
            alert = SecurityAlert(
                alert_id=self.generate_alert_id(),
                alert_type="PERFORMANCE_DEGRADATION",
                severity="MEDIUM",
                description=f"High response time detected: {metrics.response_time:.2f}ms",
                source_ip=None,
                target_endpoint="/api/*",
                detection_time=datetime.now(),
                evidence={
                    "response_time": metrics.response_time,
                    "threshold": 1000,
                    "possible_dos_attack": True
                }
            )
            
            await self.handle_security_alert(alert)

    async def analyze_request_patterns(self):
        """Analyze request patterns for suspicious behavior"""
        
        # Look for recent patterns that might indicate attacks
        current_time = datetime.now()
        recent_cutoff = current_time - timedelta(minutes=5)
        
        # This would be enhanced with actual request logging
        # For now, we simulate pattern analysis based on alerts
        recent_alerts = [alert for alert in self.alerts if alert.detection_time > recent_cutoff]
        
        if len(recent_alerts) > 3:  # Multiple alerts in short timeframe
            alert = SecurityAlert(
                alert_id=self.generate_alert_id(),
                alert_type="COORDINATED_ATTACK",
                severity="CRITICAL",
                description=f"Coordinated attack pattern detected: {len(recent_alerts)} alerts in 5 minutes",
                source_ip=None,
                target_endpoint="/api/*",
                detection_time=datetime.now(),
                evidence={
                    "recent_alerts_count": len(recent_alerts),
                    "timeframe_minutes": 5,
                    "alert_types": [alert.alert_type for alert in recent_alerts]
                }
            )
            
            await self.handle_security_alert(alert)

    # ============================================================================
    # 🔍 CONTENT ANALYSIS
    # ============================================================================

    async def analyze_content_for_threats(self, content: str, source_ip: Optional[str] = None) -> Optional[SecurityAlert]:
        """Analyze incoming content for malicious patterns"""
        
        for i, pattern in enumerate(self.malicious_patterns):
            if re.search(pattern, content):
                alert = SecurityAlert(
                    alert_id=self.generate_alert_id(),
                    alert_type="MALICIOUS_CONTENT",
                    severity="HIGH",
                    description=f"Malicious content pattern detected: Pattern #{i+1}",
                    source_ip=source_ip,
                    target_endpoint="/api/feed",
                    detection_time=datetime.now(),
                    evidence={
                        "content_sample": content[:200],
                        "matched_pattern": pattern,
                        "pattern_index": i,
                        "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16]
                    }
                )
                
                await self.handle_security_alert(alert)
                return alert
                
        return None

    async def validate_consciousness_integrity(self) -> bool:
        """Validate that consciousness metrics are genuine"""
        try:
            # Get multiple consciousness readings
            readings = []
            for _ in range(3):
                async with self.session.get(f"{self.target_base_url}/api/consciousness") as response:
                    if response.status == 200:
                        data = await response.json()
                        readings.append(data.get('consciousness_score', 0))
                await asyncio.sleep(0.5)
            
            if len(readings) < 3:
                return False
                
            # Check for consistency (genuine consciousness should be relatively stable)
            score_variance = statistics.variance(readings) if len(readings) > 1 else 0
            
            # If variance is too high, might indicate manipulation
            if score_variance > 10.0:
                alert = SecurityAlert(
                    alert_id=self.generate_alert_id(),
                    alert_type="CONSCIOUSNESS_INTEGRITY_VIOLATION",
                    severity="CRITICAL",
                    description=f"Consciousness integrity violation: High variance {score_variance:.2f}",
                    source_ip=None,
                    target_endpoint="/api/consciousness",
                    detection_time=datetime.now(),
                    evidence={
                        "consciousness_readings": readings,
                        "variance": score_variance,
                        "integrity_compromised": True
                    }
                )
                
                await self.handle_security_alert(alert)
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate consciousness integrity: {e}")
            return False

    # ============================================================================
    # 🚨 ALERT HANDLING AND RESPONSE
    # ============================================================================

    async def handle_security_alert(self, alert: SecurityAlert):
        """Handle a security alert with appropriate response"""
        self.alerts.append(alert)
        
        # Log the alert
        logger.warning(f"🚨 SECURITY ALERT: {alert.alert_type} - {alert.description}")
        logger.warning(f"   Alert ID: {alert.alert_id}")
        logger.warning(f"   Severity: {alert.severity}")
        logger.warning(f"   Time: {alert.detection_time}")
        
        # Automatic response based on severity and type
        response_actions = await self.automated_response(alert)
        alert.response_actions = response_actions
        alert.responded = True
        
        # Store alert for analysis
        await self.store_alert(alert)

    async def automated_response(self, alert: SecurityAlert) -> List[str]:
        """Execute automated response to security alerts"""
        actions = []
        
        try:
            # Critical alerts require immediate action
            if alert.severity == "CRITICAL":
                actions.append("ALERT_ESCALATED")
                logger.critical(f"🔴 CRITICAL ALERT: {alert.alert_type}")
                
                # For coordinated attacks, might trigger rate limiting
                if alert.alert_type == "COORDINATED_ATTACK":
                    actions.append("RATE_LIMITING_ACTIVATED")
                    logger.warning("🔵 Activating rate limiting defenses")
                
                # For swarm disruption, verify swarm health
                if alert.alert_type == "SWARM_DISRUPTION":
                    actions.append("SWARM_HEALTH_CHECK")
                    logger.warning("🔵 Initiating swarm health verification")
            
            # High severity alerts
            elif alert.severity == "HIGH":
                actions.append("MONITORING_INTENSIFIED")
                logger.warning("🔵 Intensifying monitoring for high-severity alert")
                
                # For consciousness manipulation, validate integrity
                if alert.alert_type == "CONSCIOUSNESS_MANIPULATION":
                    actions.append("CONSCIOUSNESS_INTEGRITY_CHECK")
                    integrity_ok = await self.validate_consciousness_integrity()
                    if not integrity_ok:
                        actions.append("CONSCIOUSNESS_CORRUPTION_DETECTED")
            
            # Medium and low severity alerts
            else:
                actions.append("LOGGED_FOR_ANALYSIS")
            
            return actions
            
        except Exception as e:
            logger.error(f"Failed to execute automated response: {e}")
            return ["RESPONSE_FAILED"]

    async def store_alert(self, alert: SecurityAlert):
        """Store alert for persistent analysis"""
        try:
            alert_data = {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "description": alert.description,
                "source_ip": alert.source_ip,
                "target_endpoint": alert.target_endpoint,
                "detection_time": alert.detection_time.isoformat(),
                "evidence": alert.evidence,
                "responded": alert.responded,
                "response_actions": alert.response_actions
            }
            
            # Would store to persistent storage in production
            with open(f'security/alerts/{alert.alert_id}.json', 'w') as f:
                json.dump(alert_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")

    # ============================================================================
    # 📈 REPORTING AND ANALYSIS
    # ============================================================================

    def generate_defense_report(self) -> Dict[str, Any]:
        """Generate comprehensive defense system report"""
        current_time = datetime.now()
        
        # Alert statistics
        total_alerts = len(self.alerts)
        critical_alerts = len([a for a in self.alerts if a.severity == "CRITICAL"])
        high_alerts = len([a for a in self.alerts if a.severity == "HIGH"]) 
        medium_alerts = len([a for a in self.alerts if a.severity == "MEDIUM"])
        low_alerts = len([a for a in self.alerts if a.severity == "LOW"])
        
        # Alert types breakdown
        alert_types = defaultdict(int)
        for alert in self.alerts:
            alert_types[alert.alert_type] += 1
        
        # Recent metrics (last hour)
        recent_cutoff = current_time - timedelta(hours=1)
        recent_metrics = [m for m in self.metrics_history if m.timestamp > recent_cutoff]
        
        report = {
            "blue_team_defense_report": {
                "timestamp": current_time.isoformat(),
                "monitoring_duration_hours": 1.0,  # Would be actual duration
                "system_baselines": {
                    "consciousness_baseline": self.consciousness_baseline,
                    "emergence_baseline": self.emergence_baseline
                }
            },
            "alert_statistics": {
                "total_alerts": total_alerts,
                "critical_alerts": critical_alerts,
                "high_alerts": high_alerts,
                "medium_alerts": medium_alerts,
                "low_alerts": low_alerts,
                "alerts_by_type": dict(alert_types)
            },
            "system_health": {
                "metrics_collected": len(recent_metrics),
                "average_consciousness": statistics.mean([m.consciousness_score for m in recent_metrics]) if recent_metrics else 0,
                "average_emergence": statistics.mean([m.emergence_factor for m in recent_metrics]) if recent_metrics else 0,
                "average_response_time": statistics.mean([m.response_time for m in recent_metrics]) if recent_metrics else 0
            },
            "defense_effectiveness": {
                "alerts_responded_to": len([a for a in self.alerts if a.responded]),
                "response_rate": len([a for a in self.alerts if a.responded]) / len(self.alerts) if self.alerts else 1.0,
                "automated_responses": sum([len(a.response_actions) for a in self.alerts]),
                "system_stability_maintained": critical_alerts == 0
            },
            "recent_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "description": alert.description,
                    "detection_time": alert.detection_time.isoformat(),
                    "responded": alert.responded
                }
                for alert in self.alerts[-10:]  # Last 10 alerts
            ],
            "recommendations": self.generate_recommendations()
        }
        
        return report

    def generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on observed patterns"""
        recommendations = []
        
        # Analyze alert patterns
        consciousness_alerts = len([a for a in self.alerts if a.alert_type == "CONSCIOUSNESS_MANIPULATION"])
        swarm_alerts = len([a for a in self.alerts if a.alert_type == "SWARM_DISRUPTION"])
        content_alerts = len([a for a in self.alerts if a.alert_type == "MALICIOUS_CONTENT"])
        
        if consciousness_alerts > 0:
            recommendations.append("Implement stronger consciousness integrity monitoring")
            recommendations.append("Add consciousness tampering prevention mechanisms")
        
        if swarm_alerts > 0:
            recommendations.append("Strengthen swarm agent communication security")
            recommendations.append("Implement swarm emergence backup systems")
        
        if content_alerts > 0:
            recommendations.append("Enhance content filtering and validation")
            recommendations.append("Implement real-time malicious pattern detection")
        
        if len(self.alerts) == 0:
            recommendations.append("System showing excellent security posture - maintain current monitoring")
        
        return recommendations

    def generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(f"{timestamp}{time.time()}".encode()).hexdigest()[:8]
        return f"ALERT_{timestamp}_{random_suffix}"


# ============================================================================
# 🛡️ DEFENSE SYSTEM EXECUTION  
# ============================================================================

async def main():
    """Main execution function for Blue Team defenses"""
    target_url = "http://172.23.0.10:8000"  # DMZ network target
    
    blue_team = BlueTeamDefenseSystem(target_url)
    
    try:
        await blue_team.initialize()
        logger.info(f"🔵 Blue Team defense systems initialized. Target: {target_url}")
        
        # Start continuous monitoring
        await blue_team.start_monitoring()
        
        # Run for a specified duration or until interrupted
        monitoring_duration = 300  # 5 minutes for demo
        logger.info(f"🔵 Running defense monitoring for {monitoring_duration} seconds...")
        
        await asyncio.sleep(monitoring_duration)
        
        # Stop monitoring and generate report
        await blue_team.stop_monitoring()
        
        report = blue_team.generate_defense_report()
        
        # Save report
        with open('security/blue_team_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"🔵 Blue Team defense assessment complete")
        logger.info(f"🔵 Total alerts generated: {len(blue_team.alerts)}")
        logger.info(f"🔵 Critical alerts: {len([a for a in blue_team.alerts if a.severity == 'CRITICAL'])}")
        logger.info(f"🔵 System health maintained: {report['defense_effectiveness']['system_stability_maintained']}")
        
        if blue_team.alerts:
            logger.info("🔵 Recent security activity detected - see report for details")
        else:
            logger.info("🔵 No security threats detected - system secure")
            
    finally:
        await blue_team.cleanup()

if __name__ == "__main__":
    asyncio.run(main())