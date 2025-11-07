#!/usr/bin/env python3
"""
Live Demo: Google Finance to Sutra Integration

This script demonstrates the complete end-to-end process of:
1. Fetching financial data from Google Sheets
2. Processing it into semantic concepts  
3. Ingesting into Sutra via the API
4. Querying the learned data

Usage:
    python demo_integration.py --api-key YOUR_API_KEY
"""

import asyncio
import json
import logging
import argparse
import aiohttp
from datetime import datetime
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LiveFinancialDemo:
    """Live demonstration of Google Finance → Sutra integration"""
    
    def __init__(self, api_key: str, sutra_url: str = "http://localhost:8080"):
        self.api_key = api_key
        self.sutra_url = sutra_url
        self.session = None
        
        # Demo configuration
        self.demo_config = {
            "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",  # Public demo sheet
            "sheet_name": "Sheet1",
            "range": "A1:D10",  # Small demo range
            "companies": ["NVDA", "GOOGL", "MSFT"]
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def step1_check_sutra_health(self) -> bool:
        """Step 1: Verify Sutra is running and accessible"""
        logger.info("🔍 Step 1: Checking Sutra platform health...")
        
        try:
            async with self.session.get(f"{self.sutra_url}/health") as response:
                if response.status == 200:
                    # Health endpoint returns plain text, not JSON
                    data = await response.text()
                    logger.info(f"✅ Sutra is healthy: {data.strip()}")
                    return True
                else:
                    logger.error(f"❌ Sutra health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to Sutra: {e}")
            logger.info("💡 Make sure Sutra is running: SUTRA_EDITION=simple sutra deploy")
            return False
            
    async def step2_fetch_demo_data(self) -> List[Dict]:
        """Step 2: Fetch sample financial data (simulated for demo)"""
        logger.info("📊 Step 2: Fetching financial data...")
        
        # For demo purposes, we'll create sample data
        # In real usage, this would fetch from Google Sheets
        demo_data = [
            {
                "Date": "2025-11-07",
                "Ticker": "NVDA", 
                "Price": "142.50",
                "Volume": "45000000",
                "Market Cap": "3500000000000",
                "P/E Ratio": "68.5"
            },
            {
                "Date": "2025-11-07",
                "Ticker": "GOOGL",
                "Price": "175.25", 
                "Volume": "28000000",
                "Market Cap": "2100000000000",
                "P/E Ratio": "24.8"
            },
            {
                "Date": "2025-11-07", 
                "Ticker": "MSFT",
                "Price": "420.85",
                "Volume": "22000000", 
                "Market Cap": "3100000000000",
                "P/E Ratio": "35.2"
            }
        ]
        
        logger.info(f"✅ Fetched {len(demo_data)} financial data points")
        for item in demo_data:
            logger.info(f"   📈 {item['Ticker']}: ${item['Price']} (Volume: {item['Volume']})")
            
        return demo_data
        
    def step3_create_semantic_concepts(self, raw_data: List[Dict]) -> List[Dict]:
        """Step 3: Convert raw data to semantic concepts for Sutra"""
        logger.info("🧠 Step 3: Creating semantic concepts...")
        
        concepts = []
        for row in raw_data:
            ticker = row['Ticker']
            date = row['Date'] 
            price = float(row['Price'])
            volume = int(row['Volume'])
            market_cap = float(row['Market Cap'])
            pe_ratio = float(row['P/E Ratio'])
            
            # Create rich semantic content
            content = f"""On {date}, {ticker} stock traded at ${price:.2f} with a volume of {volume:,} shares. 
The company has a market capitalization of ${market_cap/1e9:.1f}B and a P/E ratio of {pe_ratio:.1f}. 
This represents current market data for {ticker}, showing {'high' if volume > 30000000 else 'normal'} trading activity.
{ticker} is classified as a {'large-cap' if market_cap > 1e12 else 'mid-cap'} technology stock with 
{'high' if pe_ratio > 50 else 'moderate' if pe_ratio > 25 else 'low'} valuation metrics."""
            
            # Create concept with metadata for enhanced learning
            concept = {
                "content": content,
                "metadata": {
                    "ticker": ticker,
                    "date": date,
                    "price": price,
                    "volume": volume,
                    "market_cap": market_cap,
                    "pe_ratio": pe_ratio,
                    "domain": "finance",
                    "entity_type": "stock_data",
                    "data_source": "demo_integration",
                    
                    # Semantic classification for Sutra
                    "concept_type": "quantitative",
                    "temporal_type": "point_in_time",
                    "causal_relevance": "market_data"
                }
            }
            
            concepts.append(concept)
            
        logger.info(f"✅ Created {len(concepts)} semantic concepts")
        logger.info(f"   📝 Sample concept: {concepts[0]['content'][:100]}...")
        
        return concepts
        
    async def step4_ingest_to_sutra(self, concepts: List[Dict]) -> bool:
        """Step 4: Ingest semantic concepts into Sutra"""
        logger.info("🚀 Step 4: Ingesting concepts into Sutra...")
        
        try:
            # Use individual learn calls since batch might not be available
            concept_ids = []
            
            for i, concept in enumerate(concepts):
                async with self.session.post(
                    f"{self.sutra_url}/api/learn",
                    json={
                        "content": concept["content"],
                        "metadata": concept["metadata"]
                    }
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        concept_id = result.get("concept_id")
                        if concept_id:
                            concept_ids.append(concept_id)
                            logger.info(f"   ✅ Concept {i+1}: {concept_id}")
                    else:
                        error_text = await response.text()
                        logger.error(f"   ❌ Failed concept {i+1}: {response.status} - {error_text}")
            
            logger.info(f"✅ Successfully ingested {len(concept_ids)} concepts")
            return len(concept_ids) > 0
                    
        except Exception as e:
            logger.error(f"❌ Ingestion error: {e}")
            return False
            
    async def step5_query_learned_data(self) -> bool:
        """Step 5: Query the learned financial data"""
        logger.info("🔍 Step 5: Querying learned financial data...")
        
        test_queries = [
            "What is NVDA's stock price?",
            "Which company has the highest market cap?", 
            "Compare the P/E ratios of tech companies",
            "Which stocks have high trading volume?",
            "What financial data do you know about GOOGL?"
        ]
        
        all_passed = True
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"   📋 Query {i}: {query}")
            
            try:
                async with self.session.post(
                    f"{self.sutra_url}/api/query",
                    json={"query": query}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        answer = result.get("response", "No response")
                        confidence = result.get("confidence", 0)
                        
                        logger.info(f"   ✅ Answer: {answer[:100]}...")
                        logger.info(f"   📊 Confidence: {confidence:.2f}")
                    else:
                        logger.error(f"   ❌ Query failed: {response.status}")
                        all_passed = False
                        
            except Exception as e:
                logger.error(f"   ❌ Query error: {e}")
                all_passed = False
                
        return all_passed
        
    async def run_complete_demo(self) -> Dict[str, Any]:
        """Run the complete integration demo"""
        logger.info("🎯 Starting Google Finance → Sutra Integration Demo")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        results = {
            "demo_status": "started",
            "steps_completed": 0,
            "steps_failed": 0,
            "total_steps": 5
        }
        
        try:
            # Step 1: Health Check
            if await self.step1_check_sutra_health():
                results["steps_completed"] += 1
            else:
                results["steps_failed"] += 1
                results["demo_status"] = "failed_health_check"
                return results
                
            # Step 2: Fetch Data
            raw_data = await self.step2_fetch_demo_data()
            if raw_data:
                results["steps_completed"] += 1
                results["data_points"] = len(raw_data)
            else:
                results["steps_failed"] += 1
                
            # Step 3: Create Concepts
            concepts = self.step3_create_semantic_concepts(raw_data)
            if concepts:
                results["steps_completed"] += 1
                results["concepts_created"] = len(concepts)
            else:
                results["steps_failed"] += 1
                
            # Step 4: Ingest
            if await self.step4_ingest_to_sutra(concepts):
                results["steps_completed"] += 1
            else:
                results["steps_failed"] += 1
                
            # Step 5: Query
            if await self.step5_query_learned_data():
                results["steps_completed"] += 1
            else:
                results["steps_failed"] += 1
                
            # Final status
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            if results["steps_completed"] == results["total_steps"]:
                results["demo_status"] = "success"
                logger.info("🎉 Demo completed successfully!")
            else:
                results["demo_status"] = "partial_success"
                logger.info("⚠️  Demo completed with some issues")
                
            results["processing_time_seconds"] = processing_time
            
            logger.info("=" * 60)
            logger.info("📊 DEMO SUMMARY:")
            logger.info(f"   Status: {results['demo_status']}")
            logger.info(f"   Steps completed: {results['steps_completed']}/{results['total_steps']}")
            logger.info(f"   Processing time: {processing_time:.1f}s")
            logger.info(f"   Data points: {results.get('data_points', 0)}")
            logger.info(f"   Concepts created: {results.get('concepts_created', 0)}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Demo failed with exception: {e}")
            results["demo_status"] = "error"
            results["error"] = str(e)
            return results

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Live Demo: Google Finance → Sutra Integration")
    parser.add_argument("--api-key", type=str, default="DEMO_MODE", help="Google API key (optional for demo)")
    parser.add_argument("--sutra-url", type=str, default="http://localhost:8080", help="Sutra API URL")
    parser.add_argument("--output", type=str, help="Output file for results")
    
    args = parser.parse_args()
    
    print("""
🚀 Google Finance → Sutra AI Integration Demo
============================================

This demo shows the complete process:
1. Health check Sutra platform
2. Fetch financial data (demo data)
3. Create semantic concepts
4. Ingest into Sutra knowledge graph  
5. Query learned financial knowledge

Starting demo...
    """)
    
    async with LiveFinancialDemo(args.api_key, args.sutra_url) as demo:
        results = await demo.run_complete_demo()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n📄 Results saved to: {args.output}")
        else:
            print(f"\n📊 Final Results:")
            print(json.dumps(results, indent=2))
            
        print("\n🎯 Next Steps:")
        if results["demo_status"] == "success":
            print("✅ Demo successful! You can now:")
            print("   • Try the setup script: ./scripts/setup-google-finance.sh") 
            print("   • Use real Google Sheets data with your API key")
            print("   • Query financial data through the web UI: http://localhost:3000")
            print("   • Explore temporal and causal reasoning capabilities")
        else:
            print("⚠️  Demo had issues. Check:")
            print("   • Sutra platform is running: sutra status")
            print("   • API endpoints are accessible")
            print("   • Configuration is correct")

if __name__ == "__main__":
    asyncio.run(main())