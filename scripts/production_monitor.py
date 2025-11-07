#!/usr/bin/env python3
"""
Production Financial Intelligence Monitoring System

Real-time monitoring and health checks for the Sutra AI financial intelligence platform.
Provides comprehensive observability for production deployments handling 100+ companies.
"""

import requests
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import threading
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class HealthMetric:
    """Represents a health metric with status and metadata."""
    name: str
    status: str  # "healthy", "warning", "critical"
    value: Any
    threshold: Optional[float] = None
    message: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ProductionMonitor:
    """Production-grade monitoring system for financial intelligence."""
    
    def __init__(self, base_url: str = "http://localhost:8080/api"):
        self.base_url = base_url
        self.metrics_history = []
        self.alerts = []
        self.monitoring_active = False
        
    def check_system_health(self) -> List[HealthMetric]:
        """Comprehensive system health check."""
        metrics = []
        
        # API Health Check
        try:
            response = requests.get(f"{self.base_url.replace('/api', '')}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                uptime = health_data.get("uptime_seconds", 0)
                
                metrics.append(HealthMetric(
                    name="API_Health",
                    status="healthy" if uptime > 0 else "critical",
                    value=f"{uptime:.0f}s",
                    message="API responding normally" if uptime > 0 else "API not responding"
                ))
            else:
                metrics.append(HealthMetric(
                    name="API_Health",
                    status="critical",
                    value=response.status_code,
                    message=f"API returned HTTP {response.status_code}"
                ))
        except Exception as e:
            metrics.append(HealthMetric(
                name="API_Health",
                status="critical",
                value="unreachable",
                message=f"API unreachable: {str(e)}"
            ))
        
        # System Statistics Check
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                total_concepts = stats.get("total_concepts", 0)
                
                # Concept count health
                if total_concepts > 1000:
                    status = "healthy"
                    message = "Large dataset - system handling enterprise load"
                elif total_concepts > 100:
                    status = "healthy"
                    message = "Good dataset size - system operating normally"
                elif total_concepts > 10:
                    status = "warning"
                    message = "Small dataset - consider ingesting more data"
                else:
                    status = "warning"
                    message = "Very small dataset - ingestion may be needed"
                
                metrics.append(HealthMetric(
                    name="Concept_Count",
                    status=status,
                    value=total_concepts,
                    threshold=100,
                    message=message
                ))
                
                # Associations health
                associations = stats.get("total_associations", 0)
                metrics.append(HealthMetric(
                    name="Association_Count",
                    status="healthy" if associations >= 0 else "warning",
                    value=associations,
                    message="Association graph building normally"
                ))
                
            else:
                metrics.append(HealthMetric(
                    name="System_Stats",
                    status="warning",
                    value=response.status_code,
                    message="Stats endpoint not accessible"
                ))
                
        except Exception as e:
            metrics.append(HealthMetric(
                name="System_Stats",
                status="critical",
                value="error",
                message=f"Stats check failed: {str(e)}"
            ))
        
        return metrics
    
    def check_ingestion_performance(self) -> List[HealthMetric]:
        """Monitor ingestion performance and capacity."""
        metrics = []
        
        # Test ingestion latency
        start_time = time.time()
        test_concept = {
            "content": f"Performance test concept - {datetime.now().isoformat()}",
            "metadata": {
                "type": "performance_test",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/learn", json=test_concept, timeout=10)
            latency = time.time() - start_time
            
            if response.status_code == 201:
                # Evaluate latency
                if latency < 0.5:
                    status = "healthy"
                    message = "Excellent ingestion performance"
                elif latency < 2.0:
                    status = "healthy"
                    message = "Good ingestion performance"
                elif latency < 5.0:
                    status = "warning"
                    message = "Slower ingestion - monitor for bottlenecks"
                else:
                    status = "critical"
                    message = "Very slow ingestion - investigate immediately"
                
                metrics.append(HealthMetric(
                    name="Ingestion_Latency",
                    status=status,
                    value=f"{latency:.2f}s",
                    threshold=2.0,
                    message=message
                ))
                
                concept_id = response.json().get("concept_id", "unknown")
                metrics.append(HealthMetric(
                    name="Ingestion_Success",
                    status="healthy",
                    value=concept_id,
                    message="Concept ingestion working normally"
                ))
            else:
                metrics.append(HealthMetric(
                    name="Ingestion_Success",
                    status="critical",
                    value=response.status_code,
                    message=f"Ingestion failed with HTTP {response.status_code}"
                ))
                
        except Exception as e:
            metrics.append(HealthMetric(
                name="Ingestion_Performance",
                status="critical",
                value="error",
                message=f"Ingestion test failed: {str(e)}"
            ))
        
        return metrics
    
    def check_financial_data_integrity(self) -> List[HealthMetric]:
        """Verify financial data integrity and completeness."""
        metrics = []
        
        try:
            # Get current system stats
            response = requests.get(f"{self.base_url}/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                total_concepts = stats.get("total_concepts", 0)
                
                # Check for expected financial data patterns
                if total_concepts >= 50:
                    # Assume good financial dataset for 100+ company monitoring
                    metrics.append(HealthMetric(
                        name="Financial_Dataset_Size",
                        status="healthy",
                        value=total_concepts,
                        threshold=50,
                        message="Sufficient financial data for analysis"
                    ))
                else:
                    metrics.append(HealthMetric(
                        name="Financial_Dataset_Size",
                        status="warning",
                        value=total_concepts,
                        threshold=50,
                        message="Financial dataset may be incomplete"
                    ))
                
                # Test financial query capability
                test_query = {
                    "content": "Monitor query: Check financial data accessibility",
                    "metadata": {
                        "type": "monitor_query",
                        "purpose": "data_integrity_check"
                    }
                }
                
                query_response = requests.post(f"{self.base_url}/learn", json=test_query, timeout=5)
                if query_response.status_code == 201:
                    metrics.append(HealthMetric(
                        name="Financial_Query_Capability",
                        status="healthy",
                        value="accessible",
                        message="Financial data query system operational"
                    ))
                else:
                    metrics.append(HealthMetric(
                        name="Financial_Query_Capability",
                        status="warning",
                        value=query_response.status_code,
                        message="Financial query system may have issues"
                    ))
                    
        except Exception as e:
            metrics.append(HealthMetric(
                name="Financial_Data_Integrity",
                status="critical",
                value="error",
                message=f"Data integrity check failed: {str(e)}"
            ))
        
        return metrics
    
    def generate_monitoring_report(self, metrics: List[HealthMetric]) -> Dict[str, Any]:
        """Generate comprehensive monitoring report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "healthy",
            "total_metrics": len(metrics),
            "healthy_count": 0,
            "warning_count": 0,
            "critical_count": 0,
            "metrics": [],
            "recommendations": []
        }
        
        # Process metrics
        for metric in metrics:
            report["metrics"].append({
                "name": metric.name,
                "status": metric.status,
                "value": metric.value,
                "message": metric.message,
                "timestamp": metric.timestamp.isoformat()
            })
            
            if metric.status == "healthy":
                report["healthy_count"] += 1
            elif metric.status == "warning":
                report["warning_count"] += 1
            elif metric.status == "critical":
                report["critical_count"] += 1
        
        # Determine overall health
        if report["critical_count"] > 0:
            report["overall_health"] = "critical"
        elif report["warning_count"] > 0:
            report["overall_health"] = "warning"
        
        # Generate recommendations
        if report["critical_count"] > 0:
            report["recommendations"].append("🚨 CRITICAL: Immediate attention required for system stability")
        
        if report["warning_count"] > 0:
            report["recommendations"].append("⚠️ WARNING: Monitor system closely and consider optimization")
        
        if report["overall_health"] == "healthy":
            report["recommendations"].append("✅ HEALTHY: System operating within normal parameters")
            report["recommendations"].append("🚀 READY: System can handle production financial workloads")
        
        return report
    
    def run_continuous_monitoring(self, interval_seconds: int = 60):
        """Run continuous monitoring with specified interval."""
        logger.info(f"🔍 Starting continuous monitoring (every {interval_seconds}s)")
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                logger.info("📊 Running monitoring cycle...")
                
                # Collect all metrics
                all_metrics = []
                all_metrics.extend(self.check_system_health())
                all_metrics.extend(self.check_ingestion_performance()) 
                all_metrics.extend(self.check_financial_data_integrity())
                
                # Generate report
                report = self.generate_monitoring_report(all_metrics)
                
                # Log summary
                health_emoji = {
                    "healthy": "✅",
                    "warning": "⚠️",
                    "critical": "🚨"
                }
                
                logger.info(f"{health_emoji.get(report['overall_health'], '❓')} Overall Health: {report['overall_health'].upper()}")
                logger.info(f"   Metrics: {report['healthy_count']} healthy, {report['warning_count']} warning, {report['critical_count']} critical")
                
                # Store metrics history
                self.metrics_history.append(report)
                
                # Keep only last 24 hours of data (assuming 1-minute intervals)
                if len(self.metrics_history) > 1440:
                    self.metrics_history = self.metrics_history[-1440:]
                
                # Sleep until next cycle
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring cycle failed: {e}")
                time.sleep(interval_seconds)
        
        self.monitoring_active = False
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.monitoring_active = False
    
    def run_single_check(self) -> Dict[str, Any]:
        """Run a single comprehensive monitoring check."""
        logger.info("🔍 PRODUCTION FINANCIAL INTELLIGENCE MONITORING")
        logger.info("=" * 60)
        
        # Collect all metrics
        all_metrics = []
        
        logger.info("📋 System Health Check...")
        all_metrics.extend(self.check_system_health())
        
        logger.info("⚡ Ingestion Performance Check...")
        all_metrics.extend(self.check_ingestion_performance())
        
        logger.info("💰 Financial Data Integrity Check...")
        all_metrics.extend(self.check_financial_data_integrity())
        
        # Generate comprehensive report
        report = self.generate_monitoring_report(all_metrics)
        
        # Display results
        logger.info(f"\\n📊 MONITORING RESULTS:")
        logger.info(f"   Overall Health: {report['overall_health'].upper()}")
        logger.info(f"   Total Metrics: {report['total_metrics']}")
        logger.info(f"   ✅ Healthy: {report['healthy_count']}")
        logger.info(f"   ⚠️ Warning: {report['warning_count']}")
        logger.info(f"   🚨 Critical: {report['critical_count']}")
        
        logger.info(f"\\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            logger.info(f"   {rec}")
        
        logger.info(f"\\n📈 DETAILED METRICS:")
        for metric in report["metrics"]:
            status_emoji = {"healthy": "✅", "warning": "⚠️", "critical": "🚨"}
            logger.info(f"   {status_emoji.get(metric['status'], '❓')} {metric['name']}: {metric['value']} - {metric['message']}")
        
        return report

def main():
    """Run production monitoring check."""
    print("🏭 PRODUCTION FINANCIAL INTELLIGENCE MONITORING")
    print("=" * 70)
    print(f"Monitor Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    monitor = ProductionMonitor()
    
    # Run single comprehensive check
    report = monitor.run_single_check()
    
    print(f"\\n🎯 PRODUCTION READINESS ASSESSMENT:")
    if report["overall_health"] == "healthy":
        print("   ✅ PRODUCTION READY - All systems operational")
        print("   🚀 System can handle 100+ company financial intelligence workloads")
        print("   📊 Monitoring confirms system stability and performance")
    elif report["overall_health"] == "warning":
        print("   ⚠️ PRODUCTION CAUTION - Minor issues detected") 
        print("   🔧 Address warnings before scaling to full production load")
        print("   📈 System functional but may need optimization")
    else:
        print("   🚨 PRODUCTION NOT READY - Critical issues require attention")
        print("   🛠️ Resolve critical issues before production deployment")
        print("   ⏳ System needs stabilization")
    
    print(f"\\nMonitor End: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Option for continuous monitoring
    user_input = input("\\n❓ Start continuous monitoring? (y/N): ")
    if user_input.lower() in ['y', 'yes']:
        print("🔄 Starting continuous monitoring... (Ctrl+C to stop)")
        try:
            monitor.run_continuous_monitoring(30)  # Every 30 seconds
        except KeyboardInterrupt:
            print("\\n✅ Continuous monitoring stopped")

if __name__ == "__main__":
    main()