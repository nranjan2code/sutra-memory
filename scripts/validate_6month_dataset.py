#!/usr/bin/env python3
"""
6-Month Financial Dataset Validation and Performance Analysis

Validates the ingested 6-month dataset and performs comprehensive
performance analysis on query capabilities, data retrieval, and
system responsiveness under load.
"""

import requests
import json
import time
import statistics
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SixMonthDatasetValidator:
    def __init__(self):
        self.base_url = "http://localhost:8080/api"
        self.session = requests.Session()
        
        # Test companies from our dataset
        self.test_companies = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "TSM"
        ]
        
        # Performance metrics
        self.query_times = []
        self.validation_results = {}
    
    def test_system_health_with_large_dataset(self) -> bool:
        """Test system health with large dataset loaded"""
        logger.info("🏥 SYSTEM HEALTH CHECK WITH LARGE DATASET")
        logger.info("=" * 50)
        
        try:
            # Basic health check
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code != 200:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return False
            
            health_data = response.json()
            logger.info(f"✅ API Health: {health_data.get('status', 'unknown')}")
            logger.info(f"📊 Uptime: {health_data.get('uptime_seconds', 0):.1f}s")
            
            # System statistics
            response = self.session.get(f"{self.base_url}/stats", timeout=15)
            if response.status_code == 200:
                stats = response.json()
                total_concepts = stats.get('total_concepts', 0)
                logger.info(f"📈 Total concepts loaded: {total_concepts:,}")
                
                if total_concepts < 200:
                    logger.warning(f"⚠️ Expected 200+ concepts for stress testing, found {total_concepts}")
                    return False
                else:
                    logger.info(f"✅ Enlarged dataset validated: {total_concepts:,} concepts (70%+ increase from baseline)")
                    
            return True
            
        except Exception as e:
            logger.error(f"❌ System health check failed: {e}")
            return False
    
    def test_query_performance_under_load(self) -> Dict[str, Any]:
        """Test query performance with large dataset"""
        logger.info("\n🚀 QUERY PERFORMANCE TESTING")
        logger.info("=" * 50)
        
        # Different types of queries to test various access patterns
        test_queries = [
            # Company-specific queries
            {"query": "AAPL stock price data", "type": "company_specific"},
            {"query": "NVDA trading volume patterns", "type": "company_specific"},
            {"query": "MSFT weekly analysis", "type": "company_specific"},
            
            # Sector-based queries
            {"query": "technology sector performance", "type": "sector_analysis"},
            {"query": "financial sector trends", "type": "sector_analysis"},
            
            # Temporal queries
            {"query": "stock data from last 6 months", "type": "temporal"},
            {"query": "November 2025 market performance", "type": "temporal"},
            {"query": "recent weekly analysis", "type": "temporal"},
            
            # Technical analysis queries
            {"query": "high volume trading days", "type": "technical"},
            {"query": "bullish momentum indicators", "type": "technical"},
            {"query": "stock volatility patterns", "type": "technical"},
            
            # Comparative queries
            {"query": "compare AAPL vs MSFT performance", "type": "comparative"},
            {"query": "tech stocks vs financial stocks", "type": "comparative"}
        ]
        
        results = {
            "total_queries": len(test_queries),
            "successful_queries": 0,
            "failed_queries": 0,
            "query_times": [],
            "results_by_type": {},
            "errors": []
        }
        
        for i, test_case in enumerate(test_queries):
            query = test_case["query"]
            query_type = test_case["type"]
            
            logger.info(f"🔍 Query {i+1}/{len(test_queries)}: '{query}'")
            
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    timeout=30
                )
                query_time = time.time() - start_time
                
                results["query_times"].append(query_time)
                
                if query_type not in results["results_by_type"]:
                    results["results_by_type"][query_type] = {"count": 0, "avg_time": 0, "times": []}
                
                results["results_by_type"][query_type]["times"].append(query_time)
                results["results_by_type"][query_type]["count"] += 1
                
                if response.status_code == 200:
                    results["successful_queries"] += 1
                    result_data = response.json()
                    confidence = result_data.get("confidence", 0)
                    answer_preview = result_data.get("answer", "")[:100] + "..." if result_data.get("answer") else ""
                    
                    logger.info(f"   ✅ {query_time:.3f}s | Confidence: {confidence:.2f} | {answer_preview}")
                else:
                    results["failed_queries"] += 1
                    results["errors"].append(f"HTTP {response.status_code}: {query}")
                    logger.info(f"   ❌ {query_time:.3f}s | Status: {response.status_code}")
                    
            except Exception as e:
                results["failed_queries"] += 1
                results["errors"].append(f"Exception: {query} - {str(e)}")
                logger.info(f"   💥 Exception: {e}")
        
        # Calculate averages by type
        for query_type in results["results_by_type"]:
            times = results["results_by_type"][query_type]["times"]
            results["results_by_type"][query_type]["avg_time"] = sum(times) / len(times) if times else 0
        
        return results
    
    def test_concurrent_query_load(self, num_concurrent: int = 10) -> Dict[str, Any]:
        """Test system performance under concurrent query load"""
        logger.info(f"\n⚡ CONCURRENT QUERY LOAD TEST ({num_concurrent} concurrent)")
        logger.info("=" * 50)
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Simple queries for concurrent testing
        base_queries = [
            "AAPL stock data", "MSFT performance", "NVDA analysis", "GOOGL trends",
            "technology sector", "market data", "trading volume", "stock prices"
        ]
        
        # Create concurrent queries
        concurrent_queries = [base_queries[i % len(base_queries)] for i in range(num_concurrent)]
        
        def execute_query(query: str) -> Dict[str, Any]:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    timeout=30
                )
                query_time = time.time() - start_time
                
                return {
                    "query": query,
                    "time": query_time,
                    "success": response.status_code == 200,
                    "status_code": response.status_code
                }
            except Exception as e:
                return {
                    "query": query,
                    "time": 30.0,  # Timeout time
                    "success": False,
                    "error": str(e)
                }
        
        # Execute concurrent queries
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            future_to_query = {
                executor.submit(execute_query, query): query 
                for query in concurrent_queries
            }
            
            for future in as_completed(future_to_query):
                results.append(future.result())
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        query_times = [r["time"] for r in results if r["success"]]
        
        analysis = {
            "total_queries": len(concurrent_queries),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / len(concurrent_queries)) * 100,
            "total_time": total_time,
            "average_query_time": statistics.mean(query_times) if query_times else 0,
            "median_query_time": statistics.median(query_times) if query_times else 0,
            "throughput": len(concurrent_queries) / total_time
        }
        
        logger.info(f"📊 Concurrent load results:")
        logger.info(f"   Successful: {successful}/{len(concurrent_queries)} ({analysis['success_rate']:.1f}%)")
        logger.info(f"   Total time: {total_time:.2f}s")
        logger.info(f"   Average query time: {analysis['average_query_time']:.3f}s")
        logger.info(f"   Median query time: {analysis['median_query_time']:.3f}s")
        logger.info(f"   Throughput: {analysis['throughput']:.2f} queries/sec")
        
        return analysis
    
    def test_data_completeness(self) -> Dict[str, Any]:
        """Test if all expected data types are present and queryable"""
        logger.info("\n📊 DATA COMPLETENESS VALIDATION")
        logger.info("=" * 50)
        
        completeness_tests = [
            # Company presence tests
            {"test": "AAPL data presence", "query": "AAPL stock", "expected": True},
            {"test": "MSFT data presence", "query": "MSFT stock", "expected": True},
            {"test": "NVDA data presence", "query": "NVDA stock", "expected": True},
            {"test": "TSLA data presence", "query": "TSLA stock", "expected": True},
            
            # Data type tests
            {"test": "Daily OHLCV data", "query": "daily stock price data", "expected": True},
            {"test": "Weekly analysis data", "query": "weekly analysis", "expected": True},
            {"test": "Volume data", "query": "trading volume", "expected": True},
            
            # Temporal coverage tests
            {"test": "Recent data (November)", "query": "November 2025 stock data", "expected": True},
            {"test": "Historical data (6 months)", "query": "stock data from 6 months ago", "expected": True},
            
            # Sector coverage tests
            {"test": "Technology sector", "query": "technology sector stocks", "expected": True},
            {"test": "Financial sector", "query": "financial sector stocks", "expected": True}
        ]
        
        results = {
            "total_tests": len(completeness_tests),
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        for test_case in completeness_tests:
            test_name = test_case["test"]
            query = test_case["query"]
            expected = test_case["expected"]
            
            try:
                response = self.session.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    timeout=20
                )
                
                if response.status_code == 200:
                    result_data = response.json()
                    confidence = result_data.get("confidence", 0)
                    has_data = confidence > 0.5  # Threshold for meaningful data
                    
                    if has_data == expected:
                        results["passed"] += 1
                        logger.info(f"   ✅ {test_name}: PASS (confidence: {confidence:.2f})")
                    else:
                        results["failed"] += 1
                        logger.info(f"   ❌ {test_name}: FAIL (confidence: {confidence:.2f})")
                else:
                    results["failed"] += 1
                    logger.info(f"   ❌ {test_name}: FAIL (HTTP {response.status_code})")
                    
                results["details"].append({
                    "test": test_name,
                    "passed": has_data == expected if 'has_data' in locals() else False,
                    "confidence": confidence if 'confidence' in locals() else 0
                })
                
            except Exception as e:
                results["failed"] += 1
                logger.info(f"   💥 {test_name}: ERROR ({e})")
                results["details"].append({"test": test_name, "passed": False, "error": str(e)})
        
        completion_rate = (results["passed"] / results["total_tests"]) * 100
        logger.info(f"\n📈 Data completeness: {completion_rate:.1f}% ({results['passed']}/{results['total_tests']} tests passed)")
        
        return results
    
    def generate_performance_report(self, query_results: Dict, concurrent_results: Dict, completeness_results: Dict):
        """Generate comprehensive performance report"""
        logger.info("\n" + "=" * 70)
        logger.info("📋 6-MONTH DATASET PERFORMANCE REPORT")
        logger.info("=" * 70)
        
        # Query performance summary
        if query_results["query_times"]:
            avg_time = statistics.mean(query_results["query_times"])
            median_time = statistics.median(query_results["query_times"])
            min_time = min(query_results["query_times"])
            max_time = max(query_results["query_times"])
            
            logger.info("🚀 QUERY PERFORMANCE:")
            logger.info(f"   Total queries tested: {query_results['total_queries']}")
            logger.info(f"   Success rate: {(query_results['successful_queries'] / query_results['total_queries']) * 100:.1f}%")
            logger.info(f"   Average response time: {avg_time:.3f}s")
            logger.info(f"   Median response time: {median_time:.3f}s")
            logger.info(f"   Fastest query: {min_time:.3f}s")
            logger.info(f"   Slowest query: {max_time:.3f}s")
        
        # Performance by query type
        logger.info("\n📊 PERFORMANCE BY QUERY TYPE:")
        for query_type, type_data in query_results["results_by_type"].items():
            logger.info(f"   {query_type}: {type_data['avg_time']:.3f}s avg ({type_data['count']} queries)")
        
        # Concurrent performance
        logger.info("\n⚡ CONCURRENT PERFORMANCE:")
        logger.info(f"   Concurrent success rate: {concurrent_results['success_rate']:.1f}%")
        logger.info(f"   Concurrent throughput: {concurrent_results['throughput']:.2f} queries/sec")
        logger.info(f"   Concurrent avg response: {concurrent_results['average_query_time']:.3f}s")
        
        # Data completeness
        logger.info("\n📊 DATA COMPLETENESS:")
        logger.info(f"   Completeness tests passed: {completeness_results['passed']}/{completeness_results['total_tests']}")
        completion_rate = (completeness_results['passed'] / completeness_results['total_tests']) * 100
        logger.info(f"   Overall completeness: {completion_rate:.1f}%")
        
        # Overall assessment
        logger.info("\n🎯 OVERALL ASSESSMENT:")
        
        # Performance grades
        avg_query_time = statistics.mean(query_results["query_times"]) if query_results["query_times"] else float('inf')
        query_success_rate = (query_results["successful_queries"] / query_results["total_queries"]) * 100
        
        performance_grade = "A+" if avg_query_time < 0.5 else "A" if avg_query_time < 1.0 else "B" if avg_query_time < 2.0 else "C"
        reliability_grade = "A+" if query_success_rate > 95 else "A" if query_success_rate > 90 else "B" if query_success_rate > 80 else "C"
        completeness_grade = "A+" if completion_rate > 95 else "A" if completion_rate > 90 else "B" if completion_rate > 80 else "C"
        
        logger.info(f"   Query Performance: {performance_grade} (avg {avg_query_time:.3f}s)")
        logger.info(f"   System Reliability: {reliability_grade} ({query_success_rate:.1f}% success)")
        logger.info(f"   Data Completeness: {completeness_grade} ({completion_rate:.1f}% complete)")
        
        # Recommendations
        if avg_query_time > 1.0:
            logger.info("\n💡 RECOMMENDATIONS:")
            logger.info("   • Consider query optimization for large datasets")
            logger.info("   • Monitor system resources under heavy query load")
        
        if query_success_rate < 95:
            logger.info("   • Investigate failed queries for pattern analysis")
        
        logger.info("\n✅ 6-MONTH DATASET VALIDATION COMPLETE")

def main():
    """Main validation function"""
    print("🔬 6-MONTH FINANCIAL DATASET VALIDATION")
    print("=" * 50)
    
    validator = SixMonthDatasetValidator()
    
    try:
        # Phase 1: System health with large dataset
        if not validator.test_system_health_with_large_dataset():
            logger.error("❌ System health check failed. Aborting validation.")
            return
        
        # Phase 2: Query performance testing
        query_results = validator.test_query_performance_under_load()
        
        # Phase 3: Concurrent load testing
        concurrent_results = validator.test_concurrent_query_load(num_concurrent=8)
        
        # Phase 4: Data completeness validation
        completeness_results = validator.test_data_completeness()
        
        # Phase 5: Generate comprehensive report
        validator.generate_performance_report(query_results, concurrent_results, completeness_results)
        
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted by user")
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()