#!/usr/bin/env python3
"""
Financial Data Persistence Validation
Test if our 30 financial concepts are properly persisted and queryable
"""

import requests
import json
from typing import List, Dict, Any
import time

class FinancialDataValidator:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def query_sutra(self, query: str) -> Dict[str, Any]:
        """Query the Sutra system via the hybrid service"""
        try:
            response = self.session.post(
                f"{self.base_url}/sutra/query",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text[:200]}"}
                
        except Exception as e:
            return {"error": f"Query failed: {str(e)}"}
    
    def test_api_health(self) -> Dict[str, Any]:
        """Check API health and concept count"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Health check failed: {response.status_code}"}
        except Exception as e:
            return {"error": f"Health check error: {str(e)}"}
    
    def validate_company_data(self, companies: List[str]) -> Dict[str, Any]:
        """Validate financial data for specific companies"""
        results = {
            "companies_tested": len(companies),
            "companies_found": 0,
            "queries_successful": 0,
            "total_queries": 0,
            "company_results": {}
        }
        
        for company in companies:
            print(f"🔍 Testing {company} data...")
            
            queries = [
                f"{company} stock price",
                f"{company} financial data",
                f"{company} trading volume"
            ]
            
            company_found = False
            company_queries = 0
            
            for query in queries:
                results["total_queries"] += 1
                company_queries += 1
                
                print(f"  📊 Query: '{query}'")
                result = self.query_sutra(query)
                
                if "error" in result:
                    print(f"  ❌ Error: {result['error']}")
                    results["company_results"][f"{company}_{query}"] = {"status": "error", "error": result["error"]}
                else:
                    answer = result.get('answer', '')
                    confidence = result.get('confidence', 0)
                    
                    # Check if the answer contains relevant financial information
                    if (company.lower() in answer.lower() or 
                        any(keyword in answer.lower() for keyword in ['stock', 'price', 'financial', 'trading', '$'])):
                        print(f"  ✅ Found data! Confidence: {confidence}")
                        print(f"     Preview: {answer[:100]}...")
                        company_found = True
                        results["queries_successful"] += 1
                        results["company_results"][f"{company}_{query}"] = {
                            "status": "success", 
                            "confidence": confidence,
                            "answer_preview": answer[:150]
                        }
                    else:
                        print(f"  ⚠️  No relevant data found")
                        results["company_results"][f"{company}_{query}"] = {
                            "status": "no_data", 
                            "answer": answer[:100]
                        }
                
                time.sleep(0.5)  # Small delay between queries
            
            if company_found:
                results["companies_found"] += 1
                print(f"  🎯 {company}: Data found!\n")
            else:
                print(f"  🚫 {company}: No financial data found\n")
        
        return results
    
    def test_semantic_queries(self) -> Dict[str, Any]:
        """Test semantic understanding with complex queries"""
        semantic_queries = [
            "Which technology stocks performed well?",
            "Show me financial data from November 2025",
            "What was the trading volume for tech companies?",
            "Compare stock prices across different companies",
            "Which companies had the highest volatility?"
        ]
        
        results = {
            "semantic_queries_tested": len(semantic_queries),
            "semantic_successful": 0,
            "semantic_results": {}
        }
        
        print("🧠 Testing semantic understanding...")
        
        for query in semantic_queries:
            print(f"  🔮 Query: '{query}'")
            result = self.query_sutra(query)
            
            if "error" in result:
                print(f"  ❌ Error: {result['error']}")
                results["semantic_results"][query] = {"status": "error", "error": result["error"]}
            else:
                answer = result.get('answer', '')
                confidence = result.get('confidence', 0)
                
                # Check if answer contains financial insight
                if any(keyword in answer.lower() for keyword in ['stock', 'financial', 'trading', 'price', 'company']):
                    print(f"  ✅ Semantic understanding! Confidence: {confidence}")
                    print(f"     Answer: {answer[:150]}...")
                    results["semantic_successful"] += 1
                    results["semantic_results"][query] = {
                        "status": "success",
                        "confidence": confidence,
                        "answer": answer[:200]
                    }
                else:
                    print(f"  ⚠️  Limited semantic understanding")
                    results["semantic_results"][query] = {
                        "status": "limited",
                        "answer": answer[:100]
                    }
            
            time.sleep(1)  # Longer delay for complex queries
        
        return results
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of financial data persistence"""
        print("🔬 FINANCIAL DATA PERSISTENCE VALIDATION")
        print("=" * 60)
        
        # Test API health
        print("\n1️⃣ API Health Check")
        health = self.test_api_health()
        if "error" in health:
            print(f"❌ Health check failed: {health['error']}")
        else:
            print(f"✅ API Status: {health.get('status', 'unknown')}")
            print(f"📊 Concepts Loaded: {health.get('concepts_loaded', 'unknown')}")
        
        # Test company data (companies we ingested)
        print("\n2️⃣ Company Data Validation")
        companies = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "TSM", "V", "JPM"]
        company_results = self.validate_company_data(companies)
        
        # Test semantic understanding
        print("\n3️⃣ Semantic Query Testing")
        semantic_results = self.test_semantic_queries()
        
        # Generate summary
        print("\n📊 VALIDATION SUMMARY")
        print("=" * 60)
        
        total_success_rate = (company_results["queries_successful"] / company_results["total_queries"] * 100) if company_results["total_queries"] > 0 else 0
        semantic_success_rate = (semantic_results["semantic_successful"] / semantic_results["semantic_queries_tested"] * 100) if semantic_results["semantic_queries_tested"] > 0 else 0
        
        print(f"🏢 Companies with data: {company_results['companies_found']}/{company_results['companies_tested']} ({company_results['companies_found']/company_results['companies_tested']*100:.1f}%)")
        print(f"📊 Query success rate: {company_results['queries_successful']}/{company_results['total_queries']} ({total_success_rate:.1f}%)")
        print(f"🧠 Semantic understanding: {semantic_results['semantic_successful']}/{semantic_results['semantic_queries_tested']} ({semantic_success_rate:.1f}%)")
        
        # Overall assessment
        if company_results['companies_found'] >= 5 and total_success_rate >= 50:
            print("\n🎉 DATA PERSISTENCE: EXCELLENT")
            print("✅ Financial concepts are properly stored and retrievable")
        elif company_results['companies_found'] >= 3 and total_success_rate >= 30:
            print("\n👍 DATA PERSISTENCE: GOOD")
            print("✅ Most financial concepts are accessible")
        else:
            print("\n⚠️ DATA PERSISTENCE: NEEDS INVESTIGATION")
            print("🔧 Some concepts may not be properly persisted")
        
        return {
            "health": health,
            "company_validation": company_results,
            "semantic_validation": semantic_results,
            "summary": {
                "companies_found_rate": company_results['companies_found']/company_results['companies_tested']*100,
                "query_success_rate": total_success_rate,
                "semantic_success_rate": semantic_success_rate
            }
        }

def main():
    validator = FinancialDataValidator()
    results = validator.run_comprehensive_validation()
    
    # Save results
    with open("financial_data_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: financial_data_validation_results.json")

if __name__ == "__main__":
    main()