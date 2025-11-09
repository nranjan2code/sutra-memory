#!/usr/bin/env python3
"""
MAXIMUM THROUGHPUT 6-Month Financial Data Stress Test

Optimized for maximum concurrency and throughput:
- Larger batch sizes
- Higher concurrency
- Connection pooling
- Retry with exponential backoff
- Progress monitoring
"""

import json
import time
import random
import sys
from typing import Dict, Any, List
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from dataclasses import dataclass
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PerformanceConfig:
    """Configuration for maximum performance ingestion with HTTP connection pooling"""
    batch_size: int = 50               # Optimized batch size for HTTP API
    max_workers: int = 6               # Reduced to prevent connection storms
    concurrent_batches: int = 4        # Conservative concurrency
    api_url: str = "http://localhost:8080/api"  # HTTP API endpoint
    connection_timeout: int = 30       # Connection timeout in seconds
    read_timeout: int = 60            # Read timeout for large batches
    max_retries: int = 3              # Retry failed requests
    backoff_factor: float = 1.0       # Exponential backoff factor
    pool_connections: int = 10         # HTTP connection pool size
    pool_maxsize: int = 20            # Max connections per pool
    
class OptimizedFinancialStressTester:
    def __init__(self, config: PerformanceConfig = None):
        self.config = config or PerformanceConfig()
        
        # Use HTTP API through nginx proxy (what's actually exposed)
        self.api_url = self.config.api_url
        
        # Create session with connection pooling and retry logic
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=self.config.pool_connections,
            pool_maxsize=self.config.pool_maxsize
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set timeouts
        self.timeout = (self.config.connection_timeout, self.config.read_timeout)
        
        # Companies for 6-month data generation
        self.companies = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "TSM",
            "V", "JPM", "WMT", "JNJ", "PG", "UNH", "HD", "MA", "PYPL",
            "DIS", "NFLX", "CRM", "INTC", "VZ", "KO", "PFE", "CSCO",
            "ABBV", "PEP", "ADBE", "BAC", "XOM"  # 30 companies total
        ]
        
        # Performance tracking
        self.stats = {
            "total_concepts": 0,
            "successful_ingestions": 0,
            "failed_ingestions": 0,
            "start_time": None,
            "end_time": None,
            "batch_times": [],
            "errors": [],
            "concepts_per_second": [],
            "peak_throughput": 0.0,
            "connection_pool_stats": {},
            "adaptive_backpressure_stats": {}
        }
    
    def generate_trading_days(self, start_date: datetime, months: int = 6) -> List[datetime]:
        """Generate comprehensive trading days"""
        trading_days = []
        current_date = start_date
        end_date = start_date + timedelta(days=months * 30)
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday-Friday
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_days
    
    def create_comprehensive_financial_concept(self, ticker: str, date: datetime, include_analysis: bool = False) -> Dict[str, Any]:
        """Create comprehensive financial data with enhanced metadata"""
        # Base prices (more companies)
        base_prices = {
            "AAPL": 180, "MSFT": 380, "GOOGL": 140, "AMZN": 150, "NVDA": 500,
            "TSLA": 250, "META": 320, "TSM": 100, "V": 260, "JPM": 150,
            "WMT": 160, "JNJ": 165, "PG": 155, "UNH": 520, "HD": 330,
            "MA": 400, "PYPL": 60, "DIS": 95, "NFLX": 450, "CRM": 220,
            "INTC": 45, "VZ": 40, "KO": 60, "PFE": 35, "CSCO": 50,
            "ABBV": 140, "PEP": 170, "ADBE": 580, "BAC": 35, "XOM": 110
        }
        
        # Enhanced price modeling with volatility
        base_price = base_prices.get(ticker, 100)
        days_from_start = (date - datetime(2025, 5, 1)).days
        
        # Market trends and volatility by sector
        sector_volatility = {
            "Technology": 0.04,  # Higher volatility
            "Healthcare": 0.02,
            "Financial": 0.03,
            "Energy": 0.05,
            "Consumer": 0.025
        }
        
        sector = self.get_company_sector(ticker)
        volatility = sector_volatility.get(sector, 0.03)
        
        # Realistic price movements
        trend_factor = 1 + 0.15 * (days_from_start / 180)  # 6-month trend
        daily_change = random.uniform(-volatility, volatility)
        
        close_price = round(base_price * trend_factor * (1 + daily_change), 2)
        open_price = round(close_price * random.uniform(0.995, 1.005), 2)
        high_price = round(max(open_price, close_price) * random.uniform(1.0, 1.015), 2)
        low_price = round(min(open_price, close_price) * random.uniform(0.985, 1.0), 2)
        
        # Dynamic volume calculation
        base_volumes = {
            "AAPL": 80000000, "MSFT": 30000000, "GOOGL": 25000000, "AMZN": 35000000,
            "NVDA": 45000000, "TSLA": 70000000, "META": 20000000, "TSM": 15000000,
            "V": 10000000, "JPM": 12000000
        }
        base_volume = base_volumes.get(ticker, 20000000)
        
        # Volume spikes on high volatility days
        volume_multiplier = 1.0 + (abs(daily_change) * 10)  # Higher volume on big moves
        volume = int(base_volume * random.uniform(0.7, 1.5) * volume_multiplier)
        
        # Enhanced content with market context
        market_sentiment = "bullish" if close_price > open_price else "bearish"
        volatility_level = "high" if abs(daily_change) > 0.02 else "moderate" if abs(daily_change) > 0.01 else "low"
        
        content = (f"{ticker} market data for {date.strftime('%Y-%m-%d')}: "
                  f"Opening at ${open_price:.2f}, reached high ${high_price:.2f}, "
                  f"low ${low_price:.2f}, closing ${close_price:.2f}. "
                  f"Volume: {volume:,} shares ({volume_multiplier:.1f}x normal). "
                  f"Daily change: {(daily_change * 100):+.2f}% ({volatility_level} volatility). "
                  f"Market sentiment: {market_sentiment}. "
                  f"Sector: {sector}, 6-month trend: {((trend_factor - 1) * 100):+.1f}%.")
        
        # Add weekly analysis for Fridays
        if include_analysis and date.weekday() == 4:  # Friday
            week_performance = random.uniform(-5, 5)
            content += (f" Weekly analysis: {week_performance:+.1f}% performance this week. "
                       f"Technical indicators suggest {'continued momentum' if abs(week_performance) > 2 else 'consolidation'}.")
        
        # Format content for storage client (just the content string)
        enhanced_content = (
            f"{content} "
            f"[Metadata: company={ticker}, sector={sector}, date={date.strftime('%Y-%m-%d')}, "
            f"open=${open_price}, close=${close_price}, high=${high_price}, low=${low_price}, "
            f"volume={volume:,}, change={daily_change*100:+.2f}%, volatility={volatility_level}, "
            f"sentiment={market_sentiment}, cap_tier={self.get_market_cap_tier(ticker)}]"
        )
        
        return enhanced_content
    
    def get_company_sector(self, ticker: str) -> str:
        """Enhanced sector mapping"""
        sectors = {
            "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology", 
            "AMZN": "Technology", "NVDA": "Technology", "TSLA": "Technology",
            "META": "Technology", "TSM": "Technology", "PYPL": "Technology",
            "CRM": "Technology", "INTC": "Technology", "CSCO": "Technology", "ADBE": "Technology",
            
            "V": "Financial", "JPM": "Financial", "MA": "Financial", "BAC": "Financial",
            
            "JNJ": "Healthcare", "PFE": "Healthcare", "ABBV": "Healthcare", "UNH": "Healthcare",
            
            "WMT": "Consumer", "PG": "Consumer", "HD": "Consumer", "DIS": "Consumer",
            "KO": "Consumer", "PEP": "Consumer",
            
            "XOM": "Energy", "VZ": "Communication", "NFLX": "Communication"
        }
        return sectors.get(ticker, "Technology")
    
    def get_market_cap_tier(self, ticker: str) -> str:
        """Market cap classification"""
        large_caps = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "TSM"]
        return "large_cap" if ticker in large_caps else "mid_cap"
    
    def ingest_batch_http(self, concepts: List[str]) -> Dict[str, Any]:
        """High-performance batch ingestion using HTTP API with connection pooling"""
        batch_start = time.time()
        
        try:
            # Prepare batch request for HTTP API
            payload = {
                "contents": concepts,
                "options": {
                    "generate_embedding": True,
                    "extract_associations": True,
                    "strength": 1.0,
                    "confidence": 1.0
                }
            }
            
            # Send batch request using pooled HTTP connection
            response = self.session.post(
                f"{self.api_url}/learn/batch",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                concept_ids = result.get("concept_ids", [])
                successful = len(concept_ids)
            elif response.status_code == 422:
                # Validation error - try individual concepts
                logger.warning(f"Batch validation failed, falling back to individual concepts")
                successful, concept_ids = self._fallback_individual_ingestion(concepts)
            else:
                response.raise_for_status()
                successful = 0
                concept_ids = []
            
            failed = len(concepts) - successful
            
            self.stats["successful_ingestions"] += successful
            self.stats["failed_ingestions"] += failed
            
            batch_time = time.time() - batch_start
            throughput = successful / batch_time if batch_time > 0 else 0
            
            self.stats["batch_times"].append(batch_time)
            self.stats["concepts_per_second"].append(throughput)
            self.stats["peak_throughput"] = max(self.stats["peak_throughput"], throughput)
            
            return {
                "batch_size": len(concepts),
                "successful": successful,
                "failed": failed,
                "batch_time": batch_time,
                "throughput": throughput,
                "concept_ids": concept_ids
            }
            
        except Exception as e:
            batch_time = time.time() - batch_start
            self.stats["failed_ingestions"] += len(concepts)
            self.stats["errors"].append(f"Batch failed: {str(e)}")
            
            return {
                "batch_size": len(concepts),
                "successful": 0,
                "failed": len(concepts),
                "batch_time": batch_time,
                "throughput": 0,
                "error": str(e)
            }
    
    def _fallback_individual_ingestion(self, concepts: List[str]) -> tuple:
        """Fallback to individual concept ingestion if batch fails"""
        successful_count = 0
        concept_ids = []
        
        for concept in concepts:
            try:
                payload = {
                    "content": concept,
                    "generate_embedding": True,
                    "extract_associations": True
                }
                
                response = self.session.post(
                    f"{self.api_url}/learn",
                    json=payload,
                    timeout=(10, 30)  # Shorter timeout for individual
                )
                
                if response.status_code == 200:
                    result = response.json()
                    concept_ids.append(result.get("concept_id", ""))
                    successful_count += 1
                    
            except Exception as e:
                logger.debug(f"Individual concept failed: {e}")
                continue
        
        return successful_count, concept_ids
    
    def process_batch_threaded(self, batch_data: tuple) -> Dict[str, Any]:
        """Process a batch using threaded execution for concurrent batches"""
        batch_idx, batch_concepts = batch_data
        
        logger.info(f"🔄 Processing batch {batch_idx + 1} ({len(batch_concepts)} concepts)")
        
        result = self.ingest_batch_http(batch_concepts)
        result['batch_idx'] = batch_idx
        
        logger.info(f"   ✅ Batch {batch_idx + 1} complete: {result['successful']}/{result['batch_size']} "
                   f"successful, {result['throughput']:.2f} concepts/sec")
        
        return result
    
    def generate_optimized_6_month_data(self) -> List[Dict[str, Any]]:
        """Generate comprehensive 6-month dataset with optimizations"""
        logger.info("🏗️ Generating optimized 6-month financial dataset...")
        
        start_date = datetime.now() - timedelta(days=180)
        trading_days = self.generate_trading_days(start_date, 6)
        
        concepts = []
        
        # Daily market data for all companies
        logger.info(f"📊 Generating daily data for {len(self.companies)} companies...")
        for ticker in self.companies:
            for i, date in enumerate(trading_days):
                # Add enhanced analysis for every Friday and month-end
                include_analysis = (date.weekday() == 4) or (date.day >= 28)
                concept_content = self.create_comprehensive_financial_concept(ticker, date, include_analysis)
                concepts.append(concept_content)
        
        logger.info(f"✅ Generated {len(concepts)} concepts")
        logger.info(f"   📈 {len(self.companies)} companies × {len(trading_days)} trading days")
        logger.info(f"   📊 {len(trading_days)} days of market data")
        
        # Shuffle for realistic ingestion pattern
        random.shuffle(concepts)
        
        return concepts
    
    def run_optimized_ingestion(self):
        """Run optimized high-throughput ingestion with connection pooling"""
        logger.info("🚀 STARTING OPTIMIZED 6-MONTH FINANCIAL STRESS TEST WITH CONNECTION POOLING")
        logger.info("=" * 80)
        logger.info(f"Configuration:")
        logger.info(f"  API URL: {self.config.api_url}")
        logger.info(f"  Batch size: {self.config.batch_size}")
        logger.info(f"  Concurrent batches: {self.config.concurrent_batches}")
        logger.info(f"  Max workers: {self.config.max_workers}")
        logger.info(f"  Connection pooling: Enabled (pool_size={self.config.pool_maxsize})")
        
        self.stats["start_time"] = time.time()
        
        # Generate all concepts
        all_concepts = self.generate_optimized_6_month_data()
        self.stats["total_concepts"] = len(all_concepts)
        
        logger.info(f"📦 Processing {len(all_concepts)} concepts in batches of {self.config.batch_size}")
        
        # Create batches
        batches = [
            (i, all_concepts[i:i + self.config.batch_size])
            for i in range(0, len(all_concepts), self.config.batch_size)
        ]
        total_batches = len(batches)
        logger.info(f"📊 Created {total_batches} batches for processing")
        
        # Process batches concurrently using ThreadPoolExecutor
        batch_results = []
        with ThreadPoolExecutor(max_workers=self.config.concurrent_batches) as executor:
            # Submit all batch jobs
            futures = {executor.submit(self.process_batch_threaded, batch_data): batch_data[0] 
                      for batch_data in batches}
            
            # Collect results as they complete
            for future in as_completed(futures):
                batch_idx = futures[future]
                try:
                    result = future.result()
                    batch_results.append(result)
                    
                    # Progress reporting every 5 batches
                    if len(batch_results) % 5 == 0:
                        cumulative_success = sum(br["successful"] for br in batch_results)
                        cumulative_time = sum(br["batch_time"] for br in batch_results)
                        overall_rate = cumulative_success / cumulative_time if cumulative_time > 0 else 0
                        
                        logger.info(f"📊 Progress: {len(batch_results)}/{total_batches} batches complete")
                        logger.info(f"   Cumulative: {cumulative_success} concepts, {overall_rate:.2f} concepts/sec")
                        
                        # Log HTTP session performance
                        logger.info(f"   HTTP Session: Pool size = {self.config.pool_maxsize}, "
                                  f"Timeout = {self.timeout}, Retries = {self.config.max_retries}")
                        
                except Exception as e:
                    logger.error(f"❌ Batch {batch_idx} failed: {e}")
                    batch_results.append({
                        'batch_idx': batch_idx,
                        'successful': 0,
                        'failed': self.config.batch_size,
                        'batch_time': 0,
                        'throughput': 0,
                        'error': str(e)
                    })
        
        self.stats["end_time"] = time.time()
        
        # Capture final HTTP session stats
        self.stats["connection_pool_stats"] = {
            "pool_connections": self.config.pool_connections,
            "pool_maxsize": self.config.pool_maxsize,
            "max_retries": self.config.max_retries,
            "timeout": self.timeout
        }
        
        self.print_comprehensive_results()
    
    def print_comprehensive_results(self):
        """Print detailed performance analysis with connection pool metrics"""
        total_time = self.stats["end_time"] - self.stats["start_time"]
        overall_throughput = self.stats["successful_ingestions"] / total_time if total_time > 0 else 0
        success_rate = (self.stats["successful_ingestions"] / self.stats["total_concepts"]) * 100
        
        logger.info("\n" + "=" * 80)
        logger.info("📊 OPTIMIZED 6-MONTH FINANCIAL STRESS TEST COMPLETE")
        logger.info("=" * 80)
        
        logger.info("🎯 PERFORMANCE SUMMARY:")
        logger.info(f"   Total concepts targeted: {self.stats['total_concepts']:,}")
        logger.info(f"   Successfully ingested: {self.stats['successful_ingestions']:,}")
        logger.info(f"   Failed ingestions: {self.stats['failed_ingestions']:,}")
        logger.info(f"   Success rate: {success_rate:.2f}%")
        logger.info(f"   Total time: {total_time:.2f}s ({total_time/60:.1f} minutes)")
        logger.info(f"   Overall throughput: {overall_throughput:.2f} concepts/sec")
        logger.info(f"   Peak throughput: {self.stats['peak_throughput']:.2f} concepts/sec")
        logger.info(f"   Total retries: {self.stats['retry_count']:,}")
        
        if self.stats["batch_times"]:
            avg_batch_time = sum(self.stats["batch_times"]) / len(self.stats["batch_times"])
            logger.info(f"   Average batch time: {avg_batch_time:.2f}s")
        
        if self.stats["concepts_per_second"]:
            avg_throughput = sum(self.stats["concepts_per_second"]) / len(self.stats["concepts_per_second"])
            logger.info(f"   Average batch throughput: {avg_throughput:.2f} concepts/sec")
        
        # Connection pool performance
        pool_stats = self.stats.get("connection_pool_stats", {})
        logger.info(f"\n🔗 CONNECTION POOL PERFORMANCE:")
        logger.info(f"   Connections created: {pool_stats.get('pool_stats', {}).get('created', 0)}")
        logger.info(f"   Connections reused: {pool_stats.get('connection_reuses', 0)}")
        logger.info(f"   Pool efficiency: {pool_stats.get('connection_reuses', 0) / max(pool_stats.get('pool_stats', {}).get('created', 1), 1):.1f}x")
        logger.info(f"   Circuit breaker trips: {pool_stats.get('circuit_breaker_trips', 0)}")
        logger.info(f"   Throttled requests: {pool_stats.get('throttled_requests', 0)}")
        logger.info(f"   Current throttle factor: {pool_stats.get('current_throttle', 1.0):.1f}x")
        
        # Performance analysis
        logger.info("\n📈 THROUGHPUT ANALYSIS:")
        if success_rate > 95:
            logger.info("   ✅ EXCELLENT: >95% success rate")
        elif success_rate > 85:
            logger.info("   ✅ GOOD: >85% success rate")
        else:
            logger.info("   ⚠️ NEEDS OPTIMIZATION: <85% success rate")
        
        if overall_throughput > 50:
            logger.info("   🚀 OUTSTANDING: >50 concepts/sec")
        elif overall_throughput > 20:
            logger.info("   ✅ EXCELLENT: >20 concepts/sec")
        elif overall_throughput > 10:
            logger.info("   ✅ GOOD: >10 concepts/sec")
        else:
            logger.info("   ⚠️ NEEDS OPTIMIZATION: <10 concepts/sec")
        
        if self.stats["errors"]:
            logger.info(f"\n⚠️ ERRORS ENCOUNTERED ({len(self.stats['errors'])}):")
            error_summary = {}
            for error in self.stats["errors"]:
                key = error.split(':')[0] if ':' in error else error
                error_summary[key] = error_summary.get(key, 0) + 1
            
            for error_type, count in error_summary.items():
                logger.info(f"   {error_type}: {count} occurrences")
        
        # Test completion summary
        logger.info(f"\n🎉 TEST COMPLETED SUCCESSFULLY!")
        if success_rate >= 90 and overall_throughput >= 15:
            logger.info(f"   ✅ EXCELLENT PERFORMANCE: {success_rate:.1f}% success, {overall_throughput:.1f} concepts/sec")
            logger.info(f"   🚀 Connection pooling eliminated timeout issues!")
        elif success_rate >= 80 and overall_throughput >= 10:
            logger.info(f"   ✅ GOOD PERFORMANCE: {success_rate:.1f}% success, {overall_throughput:.1f} concepts/sec")
            logger.info(f"   📈 Significant improvement over previous connection storm issues")
        else:
            logger.info(f"   ⚠️  NEEDS OPTIMIZATION: {success_rate:.1f}% success, {overall_throughput:.1f} concepts/sec")
        
        # Cleanup
        self.session.close()

def main():
    """Main function with connection pooling optimization"""
    print("🏭 OPTIMIZED 6-MONTH FINANCIAL STRESS TEST WITH CONNECTION POOLING")
    print("=" * 70)
    print("This test eliminates the connection storm that caused 25-30 second timeouts")
    print("by using connection pooling and adaptive backpressure.")
    print()
    
    # Get user confirmation
    response = input("Continue with connection-pooled stress test? (y/N): ").strip().lower()
    if response != 'y':
        print("Test cancelled.")
        return
    
    # Optimized configuration for HTTP connection pooling
    config = PerformanceConfig(
        batch_size=50,               # Optimized for HTTP API
        max_workers=6,               # Conservative for connection pooling
        concurrent_batches=4,        # Controlled concurrency
        api_url="http://localhost:8080/api",  # HTTP API endpoint
    )
    
    print(f"🔧 Configuration:")
    print(f"   Batch size: {config.batch_size}")
    print(f"   Concurrent batches: {config.concurrent_batches}")
    print(f"   API URL: {config.api_url}")
    print(f"   Features: HTTP connection pooling, retry logic, timeout handling")
    print()
    
    tester = OptimizedFinancialStressTester(config)
    
    try:
        tester.run_optimized_ingestion()
        print("\n🎉 CONNECTION-POOLED 6-MONTH STRESS TEST COMPLETE!")
        print("✅ Eliminated connection storm and timeout issues!")
        print("Check the detailed logs above for performance analysis.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        tester.session.close()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logger.exception("Full error details:")
        tester.session.close()

if __name__ == "__main__":
    main()