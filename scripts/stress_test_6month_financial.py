#!/usr/bin/env python3
"""
6-Month Financial Data Stress Test

Ingests 6 months worth of financial data across multiple companies
and runs comprehensive stress tests to validate system performance at scale.

Expected Data Volume:
- 20 companies × 6 months × ~22 trading days = ~2,640 concepts
- Plus additional market events, earnings, news = ~3,000+ total concepts
"""

import requests
import json
import time
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SixMonthFinancialStressTester:
    def __init__(self):
        self.base_url = "http://localhost:8080/api"
        self.session = requests.Session()
        
        # Major companies for testing (20 companies)
        self.companies = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "TSM",
            "V", "JPM", "WMT", "JNJ", "PG", "UNH", "HD", "MA", "PYPL",
            "DIS", "NFLX", "CRM"
        ]
        
        # Performance tracking
        self.stats = {
            "total_concepts": 0,
            "successful_ingestions": 0,
            "failed_ingestions": 0,
            "start_time": None,
            "end_time": None,
            "batch_times": [],
            "errors": []
        }
    
    def generate_trading_days(self, start_date: datetime, months: int = 6) -> List[datetime]:
        """Generate list of trading days (Mon-Fri) for the specified period"""
        trading_days = []
        current_date = start_date
        end_date = start_date + timedelta(days=months * 30)  # Approximate 6 months
        
        while current_date <= end_date:
            # Only weekdays (Monday=0, Sunday=6)
            if current_date.weekday() < 5:  
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_days
    
    def create_daily_market_concept(self, ticker: str, date: datetime) -> Dict[str, Any]:
        """Create realistic daily market data concept"""
        # Base prices for different companies (realistic approximations)
        base_prices = {
            "AAPL": 180, "MSFT": 380, "GOOGL": 140, "AMZN": 150, "NVDA": 500,
            "TSLA": 250, "META": 320, "TSM": 100, "V": 260, "JPM": 150,
            "WMT": 160, "JNJ": 165, "PG": 155, "UNH": 520, "HD": 330,
            "MA": 400, "PYPL": 60, "DIS": 95, "NFLX": 450, "CRM": 220
        }
        
        # Generate realistic price movements
        base_price = base_prices.get(ticker, 100)
        
        # Add some seasonal trends and volatility
        days_from_start = (date - datetime(2025, 5, 1)).days
        seasonal_factor = 1 + 0.1 * (days_from_start / 180)  # 6-month trend
        daily_volatility = random.uniform(-0.03, 0.03)  # ±3% daily volatility
        
        close_price = round(base_price * seasonal_factor * (1 + daily_volatility), 2)
        open_price = round(close_price * random.uniform(0.99, 1.01), 2)
        high_price = round(max(open_price, close_price) * random.uniform(1.0, 1.02), 2)
        low_price = round(min(open_price, close_price) * random.uniform(0.98, 1.0), 2)
        
        # Volume varies by company size and day
        base_volumes = {
            "AAPL": 80000000, "MSFT": 30000000, "GOOGL": 25000000, "AMZN": 35000000,
            "NVDA": 45000000, "TSLA": 70000000, "META": 20000000, "TSM": 15000000,
        }
        base_volume = base_volumes.get(ticker, 20000000)
        volume = int(base_volume * random.uniform(0.7, 1.5))
        
        return {
            "content": f"{ticker} stock market data for {date.strftime('%Y-%m-%d')}: "
                      f"Opening at ${open_price:.2f}, the stock reached a high of ${high_price:.2f} "
                      f"and a low of ${low_price:.2f}, closing at ${close_price:.2f}. "
                      f"Trading volume was {volume:,} shares. "
                      f"Daily change: {((close_price - open_price) / open_price * 100):+.2f}%. "
                      f"Market sentiment: {'bullish' if close_price > open_price else 'bearish'} "
                      f"with {'high' if volume > base_volume else 'moderate'} trading activity.",
            "metadata": {
                "source": "financial_market_data_6month",
                "company": ticker,
                "date": date.strftime('%Y-%m-%d'),
                "data_type": "daily_ohlcv",
                "price_open": str(open_price),
                "price_close": str(close_price),
                "price_high": str(high_price),
                "price_low": str(low_price),
                "volume": str(volume),
                "daily_change_pct": f"{((close_price - open_price) / open_price * 100):+.2f}",
                "market_cap_tier": "large_cap" if ticker in ["AAPL", "MSFT", "GOOGL", "AMZN"] else "mid_cap",
                "sector": self.get_company_sector(ticker),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def get_company_sector(self, ticker: str) -> str:
        """Get the sector for a given ticker"""
        sectors = {
            "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology", 
            "AMZN": "Consumer_Discretionary", "NVDA": "Technology", "TSLA": "Consumer_Discretionary",
            "META": "Technology", "TSM": "Technology", "V": "Financial", "JPM": "Financial",
            "WMT": "Consumer_Staples", "JNJ": "Healthcare", "PG": "Consumer_Staples", 
            "UNH": "Healthcare", "HD": "Consumer_Discretionary", "MA": "Financial",
            "PYPL": "Technology", "DIS": "Communication", "NFLX": "Communication", "CRM": "Technology"
        }
        return sectors.get(ticker, "Technology")
    
    def create_weekly_analysis_concept(self, ticker: str, date: datetime) -> Dict[str, Any]:
        """Create weekly market analysis concept"""
        week_performance = random.uniform(-5, 5)  # ±5% weekly performance
        
        return {
            "content": f"Weekly analysis for {ticker} ending {date.strftime('%Y-%m-%d')}: "
                      f"Stock showed {week_performance:+.1f}% performance this week. "
                      f"Technical indicators suggest {'bullish' if week_performance > 0 else 'bearish'} momentum. "
                      f"Trading volume was {'above' if abs(week_performance) > 2 else 'near'} average. "
                      f"Key resistance levels identified around current price ranges.",
            "metadata": {
                "source": "weekly_technical_analysis",
                "company": ticker,
                "analysis_date": date.strftime('%Y-%m-%d'),
                "data_type": "technical_analysis",
                "week_performance": str(week_performance),
                "analysis_type": "weekly_summary",
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def ingest_single_concept(self, concept: Dict[str, Any]) -> bool:
        """Ingest a single concept with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    f"{self.base_url}/learn", 
                    json=concept, 
                    timeout=30
                )
                
                if response.status_code == 201:
                    self.stats["successful_ingestions"] += 1
                    return True
                else:
                    logger.warning(f"Attempt {attempt + 1} failed: {response.status_code}")
                    if attempt == max_retries - 1:
                        self.stats["failed_ingestions"] += 1
                        self.stats["errors"].append(f"HTTP {response.status_code}: {response.text[:100]}")
                        return False
                    time.sleep(1)  # Brief pause before retry
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} exception: {e}")
                if attempt == max_retries - 1:
                    self.stats["failed_ingestions"] += 1
                    self.stats["errors"].append(str(e))
                    return False
                time.sleep(1)
        
        return False
    
    def ingest_batch_concurrent(self, concepts: List[Dict[str, Any]], max_workers: int = 5) -> Dict[str, Any]:
        """Ingest a batch of concepts concurrently"""
        batch_start = time.time()
        successful = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all concepts
            future_to_concept = {
                executor.submit(self.ingest_single_concept, concept): concept 
                for concept in concepts
            }
            
            # Process results
            for future in as_completed(future_to_concept):
                if future.result():
                    successful += 1
                else:
                    failed += 1
        
        batch_time = time.time() - batch_start
        self.stats["batch_times"].append(batch_time)
        
        return {
            "batch_size": len(concepts),
            "successful": successful,
            "failed": failed,
            "batch_time": batch_time,
            "throughput": len(concepts) / batch_time if batch_time > 0 else 0
        }
    
    def generate_6_month_data(self) -> List[Dict[str, Any]]:
        """Generate 6 months worth of financial data"""
        logger.info("🏗️ Generating 6 months of financial data...")
        
        # Start from 6 months ago
        start_date = datetime.now() - timedelta(days=180)
        trading_days = self.generate_trading_days(start_date, 6)
        
        concepts = []
        
        # Daily market data for each company
        for ticker in self.companies:
            for date in trading_days:
                concepts.append(self.create_daily_market_concept(ticker, date))
        
        # Weekly analysis (every Friday or last trading day of week)
        weekly_dates = [d for d in trading_days if d.weekday() == 4]  # Fridays
        for ticker in self.companies:
            for date in weekly_dates[::1]:  # Every week
                concepts.append(self.create_weekly_analysis_concept(ticker, date))
        
        logger.info(f"✅ Generated {len(concepts)} concepts")
        logger.info(f"   📊 Daily data: {len(self.companies) * len(trading_days)} concepts")
        logger.info(f"   📊 Weekly analysis: {len(self.companies) * len(weekly_dates)} concepts")
        
        return concepts
    
    def run_large_scale_ingestion(self, batch_size: int = 50, max_workers: int = 5):
        """Run the complete 6-month data ingestion"""
        logger.info("🚀 STARTING 6-MONTH FINANCIAL DATA STRESS TEST")
        logger.info("=" * 70)
        
        self.stats["start_time"] = time.time()
        
        # Generate all concepts
        all_concepts = self.generate_6_month_data()
        self.stats["total_concepts"] = len(all_concepts)
        
        logger.info(f"📦 Processing {len(all_concepts)} concepts in batches of {batch_size}")
        
        # Process in batches
        for i in range(0, len(all_concepts), batch_size):
            batch = all_concepts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(all_concepts) + batch_size - 1) // batch_size
            
            logger.info(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} concepts)")
            
            batch_result = self.ingest_batch_concurrent(batch, max_workers)
            
            logger.info(f"   ✅ Batch complete: {batch_result['successful']}/{batch_result['batch_size']} "
                       f"successful, {batch_result['throughput']:.2f} concepts/sec")
            
            # Brief pause between batches to prevent overwhelming the system
            if i + batch_size < len(all_concepts):
                time.sleep(2)
        
        self.stats["end_time"] = time.time()
        self.print_ingestion_summary()
    
    def print_ingestion_summary(self):
        """Print comprehensive ingestion summary"""
        total_time = self.stats["end_time"] - self.stats["start_time"]
        overall_throughput = self.stats["successful_ingestions"] / total_time if total_time > 0 else 0
        success_rate = (self.stats["successful_ingestions"] / self.stats["total_concepts"]) * 100
        
        logger.info("\n" + "=" * 70)
        logger.info("📊 6-MONTH FINANCIAL DATA INGESTION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"📈 PERFORMANCE METRICS:")
        logger.info(f"   Total concepts: {self.stats['total_concepts']}")
        logger.info(f"   Successful: {self.stats['successful_ingestions']}")
        logger.info(f"   Failed: {self.stats['failed_ingestions']}")
        logger.info(f"   Success rate: {success_rate:.1f}%")
        logger.info(f"   Total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
        logger.info(f"   Overall throughput: {overall_throughput:.2f} concepts/sec")
        
        if self.stats["batch_times"]:
            avg_batch_time = sum(self.stats["batch_times"]) / len(self.stats["batch_times"])
            logger.info(f"   Average batch time: {avg_batch_time:.2f}s")
        
        if self.stats["errors"]:
            logger.info(f"\n⚠️ ERRORS ENCOUNTERED: {len(self.stats['errors'])}")
            for i, error in enumerate(self.stats["errors"][:5]):  # Show first 5 errors
                logger.info(f"   {i+1}. {error}")
            if len(self.stats["errors"]) > 5:
                logger.info(f"   ... and {len(self.stats['errors']) - 5} more")
    
    def run_post_ingestion_stress_tests(self):
        """Run comprehensive stress tests after data ingestion"""
        logger.info("\n🧪 RUNNING POST-INGESTION STRESS TESTS")
        logger.info("=" * 50)
        
        # Test 1: System health with large dataset
        try:
            response = self.session.get(f"{self.base_url}/stats", timeout=10)
            if response.status_code == 200:
                stats = response.json()
                logger.info(f"✅ System stats with large dataset:")
                logger.info(f"   Total concepts: {stats.get('total_concepts', 'unknown')}")
                logger.info(f"   System status: healthy")
            else:
                logger.error(f"❌ System stats failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ System health check failed: {e}")
        
        # Test 2: Query performance with large dataset
        test_queries = [
            "AAPL stock performance",
            "NVDA weekly analysis", 
            "technology sector trends",
            "financial market data November 2025",
            "high volume trading days"
        ]
        
        logger.info(f"\n🔍 Testing query performance with {len(test_queries)} sample queries:")
        query_times = []
        
        for query in test_queries:
            try:
                start_time = time.time()
                response = self.session.post(
                    f"{self.base_url}/query",
                    json={"query": query},
                    timeout=30
                )
                query_time = time.time() - start_time
                query_times.append(query_time)
                
                if response.status_code == 200:
                    logger.info(f"   ✅ '{query}': {query_time:.3f}s")
                else:
                    logger.info(f"   ⚠️ '{query}': {query_time:.3f}s (status: {response.status_code})")
            except Exception as e:
                logger.info(f"   ❌ '{query}': failed ({e})")
        
        if query_times:
            avg_query_time = sum(query_times) / len(query_times)
            logger.info(f"\n📊 Query performance summary:")
            logger.info(f"   Average query time: {avg_query_time:.3f}s")
            logger.info(f"   Fastest query: {min(query_times):.3f}s")
            logger.info(f"   Slowest query: {max(query_times):.3f}s")

def main():
    """Main function to run the 6-month financial stress test"""
    print("🏭 6-MONTH FINANCIAL DATA STRESS TEST")
    print("=" * 50)
    print("This test will ingest 6 months of financial data (~3000+ concepts)")
    print("across 20 major companies and run comprehensive stress tests.")
    print()
    
    # Confirm before proceeding
    response = input("Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("Test cancelled.")
        return
    
    tester = SixMonthFinancialStressTester()
    
    # Run the complete test
    try:
        # Phase 1: Large-scale data ingestion
        tester.run_large_scale_ingestion(batch_size=50, max_workers=3)
        
        # Phase 2: Post-ingestion stress tests
        tester.run_post_ingestion_stress_tests()
        
        print("\n🎉 6-MONTH FINANCIAL STRESS TEST COMPLETE!")
        print("Check the logs above for detailed performance metrics.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Full error details:")

if __name__ == "__main__":
    main()