#!/usr/bin/env python3
"""
Financial Learning Validation Script for Sutra AI

This script validates that Sutra can learn and reason about financial data
by testing temporal, causal, and semantic understanding capabilities.

Usage:
    python test_financial_learning.py --config basic_config.json
    python test_financial_learning.py --quick-test
"""

import asyncio
import json
import logging
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import aiohttp

# Add sutra packages to path  
sys.path.append(str(Path(__file__).parent.parent.parent / "packages/sutra-core"))
sys.path.append(str(Path(__file__).parent.parent.parent / "packages/sutra-client"))

try:
    from sutra_client.client import SutraClient
except ImportError as e:
    print(f"Warning: Could not import Sutra modules: {e}")
    SutraClient = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialLearningValidator:
    """Validates Sutra's financial data learning capabilities"""
    
    def __init__(self, sutra_api_url: str = "http://localhost:8000"):
        self.sutra_api_url = sutra_api_url
        self.sutra_client = None
        self.test_results = []
        
    async def __aenter__(self):
        """Async context manager entry"""
        if SutraClient:
            self.sutra_client = SutraClient(api_url=self.sutra_api_url)
            try:
                await self.sutra_client.health_check()
                logger.info("Connected to Sutra successfully")
            except Exception as e:
                logger.warning(f"Could not connect to Sutra: {e}")
                self.sutra_client = None
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass
        
    async def test_temporal_reasoning(self) -> Dict[str, Any]:
        """Test Sutra's ability to understand temporal relationships in financial data"""
        logger.info("Testing temporal reasoning capabilities...")
        
        test_queries = [
            {
                "query": "What was NVDA's price trend from January to October 2024?",
                "expected_concepts": ["NVDA", "price", "trend", "2024", "January", "October"],
                "reasoning_type": "temporal_sequence"
            },
            {
                "query": "Which companies had high trading volume on Fridays in 2024?", 
                "expected_concepts": ["trading volume", "Friday", "2024"],
                "reasoning_type": "temporal_pattern"
            },
            {
                "query": "Show me quarterly performance patterns for tech stocks",
                "expected_concepts": ["quarterly", "performance", "pattern", "tech stocks"],
                "reasoning_type": "temporal_aggregation"
            },
            {
                "query": "What happened to tech stock prices after earnings announcements?",
                "expected_concepts": ["tech stock", "prices", "after", "earnings"],
                "reasoning_type": "temporal_causality"
            }
        ]
        
        results = []
        for test_case in test_queries:
            result = await self._run_query_test(test_case)
            results.append(result)
            
        passed = sum(1 for r in results if r["status"] == "passed")
        
        return {
            "test_type": "temporal_reasoning",
            "total_tests": len(test_queries),
            "passed": passed,
            "failed": len(test_queries) - passed,
            "success_rate": passed / len(test_queries),
            "details": results
        }
        
    async def test_causal_analysis(self) -> Dict[str, Any]:
        """Test Sutra's ability to understand causal relationships"""
        logger.info("Testing causal analysis capabilities...")
        
        test_queries = [
            {
                "query": "What factors caused NVDA's price surge in 2024?",
                "expected_concepts": ["factors", "caused", "NVDA", "price surge", "2024"],
                "reasoning_type": "causal_identification"
            },
            {
                "query": "How does high trading volume correlate with price movements?",
                "expected_concepts": ["trading volume", "correlate", "price movements"],
                "reasoning_type": "causal_correlation"
            },
            {
                "query": "What market conditions led to tech stock volatility?",
                "expected_concepts": ["market conditions", "led to", "tech stock", "volatility"],
                "reasoning_type": "causal_chain"
            },
            {
                "query": "Why do stock prices typically drop on bad earnings news?",
                "expected_concepts": ["stock prices", "drop", "bad earnings", "news"],
                "reasoning_type": "causal_mechanism"
            }
        ]
        
        results = []
        for test_case in test_queries:
            result = await self._run_query_test(test_case)
            results.append(result)
            
        passed = sum(1 for r in results if r["status"] == "passed")
        
        return {
            "test_type": "causal_analysis", 
            "total_tests": len(test_queries),
            "passed": passed,
            "failed": len(test_queries) - passed,
            "success_rate": passed / len(test_queries),
            "details": results
        }
        
    async def test_comparative_analysis(self) -> Dict[str, Any]:
        """Test Sutra's ability to compare financial entities"""
        logger.info("Testing comparative analysis capabilities...")
        
        test_queries = [
            {
                "query": "Compare the P/E ratios of AI companies vs traditional tech",
                "expected_concepts": ["compare", "P/E ratios", "AI companies", "traditional tech"],
                "reasoning_type": "comparative_metrics"
            },
            {
                "query": "Which companies have the most stable beta coefficients?",
                "expected_concepts": ["companies", "most stable", "beta coefficients"],
                "reasoning_type": "comparative_ranking"
            },
            {
                "query": "Show me dividend yield trends across the tech sector",
                "expected_concepts": ["dividend yield", "trends", "tech sector"],
                "reasoning_type": "comparative_trends"
            },
            {
                "query": "How does TSLA's volatility compare to other EV companies?",
                "expected_concepts": ["TSLA", "volatility", "compare", "EV companies"],
                "reasoning_type": "comparative_analysis"
            }
        ]
        
        results = []
        for test_case in test_queries:
            result = await self._run_query_test(test_case)
            results.append(result)
            
        passed = sum(1 for r in results if r["status"] == "passed")
        
        return {
            "test_type": "comparative_analysis",
            "total_tests": len(test_queries),
            "passed": passed, 
            "failed": len(test_queries) - passed,
            "success_rate": passed / len(test_queries),
            "details": results
        }
        
    async def test_semantic_classification(self) -> Dict[str, Any]:
        """Test Sutra's semantic understanding of financial concepts"""
        logger.info("Testing semantic classification capabilities...")
        
        # Test Sutra's 9 semantic types with financial data
        test_queries = [
            {
                "query": "What entities are mentioned in NVDA financial data?",
                "expected_concepts": ["NVDA", "entities"],
                "reasoning_type": "entity_extraction",
                "semantic_type": "Entity"
            },
            {
                "query": "What events affected tech stock prices this year?",
                "expected_concepts": ["events", "affected", "tech stock prices"],
                "reasoning_type": "event_identification", 
                "semantic_type": "Event"
            },
            {
                "query": "What rules govern stock price movements?",
                "expected_concepts": ["rules", "govern", "stock price movements"],
                "reasoning_type": "rule_identification",
                "semantic_type": "Rule"
            },
            {
                "query": "When do quarterly earnings typically get announced?",
                "expected_concepts": ["when", "quarterly earnings", "announced"],
                "reasoning_type": "temporal_pattern",
                "semantic_type": "Temporal"
            },
            {
                "query": "What quantitative metrics define a stock's performance?",
                "expected_concepts": ["quantitative metrics", "stock performance"],
                "reasoning_type": "quantitative_analysis",
                "semantic_type": "Quantitative"
            }
        ]
        
        results = []
        for test_case in test_queries:
            result = await self._run_query_test(test_case)
            results.append(result)
            
        passed = sum(1 for r in results if r["status"] == "passed")
        
        return {
            "test_type": "semantic_classification",
            "total_tests": len(test_queries),
            "passed": passed,
            "failed": len(test_queries) - passed, 
            "success_rate": passed / len(test_queries),
            "details": results
        }
        
    async def _run_query_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run individual query test"""
        query = test_case["query"]
        logger.info(f"Testing query: {query}")
        
        if not self.sutra_client:
            return {
                "query": query,
                "status": "skipped",
                "reason": "No Sutra client available",
                "response": None,
                "reasoning_type": test_case.get("reasoning_type"),
                "expected_concepts": test_case.get("expected_concepts")
            }
            
        try:
            # Query Sutra
            response = await self.sutra_client.query(query)
            
            # Analyze response for expected concepts
            response_text = response.get("response", "").lower()
            expected = test_case.get("expected_concepts", [])
            found_concepts = []
            
            for concept in expected:
                if concept.lower() in response_text:
                    found_concepts.append(concept)
                    
            concept_coverage = len(found_concepts) / len(expected) if expected else 1.0
            
            # Determine pass/fail based on concept coverage and response quality
            has_substantive_response = len(response_text.split()) > 10
            status = "passed" if concept_coverage >= 0.5 and has_substantive_response else "failed"
            
            return {
                "query": query,
                "status": status,
                "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                "concept_coverage": concept_coverage,
                "found_concepts": found_concepts,
                "expected_concepts": expected,
                "reasoning_type": test_case.get("reasoning_type"),
                "semantic_type": test_case.get("semantic_type")
            }
            
        except Exception as e:
            logger.error(f"Query test failed: {e}")
            return {
                "query": query,
                "status": "error",
                "reason": str(e),
                "response": None,
                "reasoning_type": test_case.get("reasoning_type"),
                "expected_concepts": test_case.get("expected_concepts")
            }
            
    async def test_knowledge_retrieval(self) -> Dict[str, Any]:
        """Test basic knowledge retrieval of ingested financial data"""
        logger.info("Testing knowledge retrieval capabilities...")
        
        basic_queries = [
            "What is NVDA?",
            "Show me recent stock prices",
            "What companies are in the database?",
            "What financial metrics are available?",
            "Show me some trading volume data"
        ]
        
        results = []
        for query in basic_queries:
            result = await self._run_query_test({"query": query, "expected_concepts": []})
            results.append(result)
            
        passed = sum(1 for r in results if r["status"] == "passed")
        
        return {
            "test_type": "knowledge_retrieval",
            "total_tests": len(basic_queries),
            "passed": passed,
            "failed": len(basic_queries) - passed,
            "success_rate": passed / len(basic_queries),
            "details": results
        }
        
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        logger.info("Starting comprehensive financial learning validation...")
        start_time = datetime.now()
        
        # Run all test suites
        test_suites = [
            self.test_knowledge_retrieval(),
            self.test_temporal_reasoning(),
            self.test_causal_analysis(),
            self.test_comparative_analysis(),
            self.test_semantic_classification()
        ]
        
        results = await asyncio.gather(*test_suites, return_exceptions=True)
        
        # Process results
        total_tests = 0
        total_passed = 0
        suite_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Test suite {i} failed: {result}")
                suite_results.append({
                    "test_type": f"suite_{i}",
                    "status": "error", 
                    "error": str(result)
                })
            else:
                total_tests += result["total_tests"]
                total_passed += result["passed"]
                suite_results.append(result)
                
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        overall_score = total_passed / total_tests if total_tests > 0 else 0
        
        # Generate final assessment
        assessment = self._generate_assessment(overall_score, suite_results)
        
        return {
            "validation_summary": {
                "status": "completed",
                "overall_score": overall_score,
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_tests - total_passed,
                "processing_time_seconds": processing_time,
                "assessment": assessment
            },
            "test_suites": suite_results,
            "recommendations": self._generate_recommendations(suite_results),
            "timestamp": datetime.now().isoformat()
        }
        
    def _generate_assessment(self, score: float, results: List[Dict]) -> str:
        """Generate assessment of Sutra's financial learning capabilities"""
        if score >= 0.9:
            return "Excellent: Sutra demonstrates strong financial reasoning capabilities"
        elif score >= 0.7:
            return "Good: Sutra shows solid financial understanding with minor gaps"
        elif score >= 0.5:
            return "Fair: Sutra has basic financial knowledge but needs improvement"
        elif score >= 0.3:
            return "Poor: Sutra shows limited financial reasoning capabilities"
        else:
            return "Critical: Sutra appears to lack fundamental financial understanding"
            
    def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        for result in results:
            if result.get("success_rate", 0) < 0.7:
                test_type = result.get("test_type", "unknown")
                
                if test_type == "temporal_reasoning":
                    recommendations.append(
                        "Improve temporal reasoning by ingesting more time-series data with explicit date relationships"
                    )
                elif test_type == "causal_analysis":
                    recommendations.append(
                        "Enhance causal understanding by adding more cause-effect relationships in financial concepts"
                    )
                elif test_type == "comparative_analysis":
                    recommendations.append(
                        "Strengthen comparative analysis by ingesting cross-company comparison data"
                    )
                elif test_type == "semantic_classification":
                    recommendations.append(
                        "Improve semantic classification by adding more metadata and entity type information"
                    )
                elif test_type == "knowledge_retrieval":
                    recommendations.append(
                        "Increase data ingestion volume and improve concept quality for better knowledge retrieval"
                    )
                    
        if not recommendations:
            recommendations.append("Performance is strong across all areas. Consider expanding to more complex financial scenarios.")
            
        return recommendations

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Financial Learning Validation for Sutra AI")
    parser.add_argument("--sutra-url", type=str, default="http://localhost:8000", help="Sutra API URL")
    parser.add_argument("--quick-test", action="store_true", help="Run quick validation test")
    parser.add_argument("--output", type=str, help="Output file for results")
    
    args = parser.parse_args()
    
    async with FinancialLearningValidator(args.sutra_url) as validator:
        if args.quick_test:
            # Quick test - just knowledge retrieval
            result = await validator.test_knowledge_retrieval()
            print(json.dumps(result, indent=2))
        else:
            # Comprehensive validation
            result = await validator.run_comprehensive_validation()
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                logger.info(f"Results saved to {args.output}")
            else:
                print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())