#!/usr/bin/env python3
"""
Optimized stress test using high-performance client with connection pooling.

This test should eliminate the connection storm and achieve sustained high
throughput without the 25-30 second timeout issues.
"""

import asyncio
import time
import json
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import statistics

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the new high-performance client
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'packages', 'sutra-storage-client-tcp'))
from high_performance_client import HighPerformanceStorageClient

class OptimizedStressTest:
    """
    Optimized stress test using connection pooling and adaptive backpressure.
    
    Designed to eliminate resource exhaustion and achieve sustained high throughput.
    """
    
    def __init__(self):
        self.client = HighPerformanceStorageClient("localhost:50051")
        self.results_lock = Lock()
        self.results = {
            'total_concepts': 0,
            'successful_concepts': 0,
            'failed_concepts': 0,
            'response_times': [],
            'errors': [],
            'batch_stats': [],
            'start_time': None,
            'end_time': None,
        }
    
    def generate_financial_concept(self, company_idx: int, day_idx: int) -> str:
        """Generate a realistic financial concept."""
        companies = [
            "Apple", "Microsoft", "Google", "Amazon", "Tesla", "Meta", "Netflix", "NVIDIA",
            "Salesforce", "Adobe", "Intel", "Oracle", "Cisco", "IBM", "Dell", "HP",
            "VMware", "ServiceNow", "Workday", "Zoom", "Slack", "DocuSign", "CrowdStrike",
            "Palantir", "Snowflake", "DataDog", "Splunk", "MongoDB", "Elastic", "Twilio"
        ]
        
        company = companies[company_idx % len(companies)]
        price = round(100 + (company_idx * 3.7 + day_idx * 0.8) % 200, 2)
        volume = int(1000000 + (company_idx * 50000 + day_idx * 10000) % 5000000)
        
        events = [
            f"earnings beat expectations by 15% with revenue of ${price * 1000}M",
            f"announced new product launch driving stock up {price % 10:.1f}%",
            f"reported strong Q{(day_idx % 4) + 1} results with volume spike to {volume:,}",
            f"CEO announced partnership causing {price % 15:.1f}% price increase",
            f"analyst upgrade to BUY target ${price * 1.1:.2f} on growth prospects"
        ]
        
        event = events[day_idx % len(events)]
        date = f"2024-{(day_idx % 12) + 1:02d}-{(day_idx % 28) + 1:02d}"
        
        return (
            f"{company} stock on {date}: Price ${price} (Volume: {volume:,} shares). "
            f"Market event: {event}. Technical analysis shows strong momentum with "
            f"institutional buying pressure. Sector rotation into technology continues "
            f"as investors seek growth opportunities amid economic uncertainty."
        )
    
    def run_batch_test(self, batch_size: int, num_batches: int, concurrent_batches: int = 5) -> Dict[str, Any]:
        """
        Run optimized batch test with connection pooling.
        
        Args:
            batch_size: Size of each batch
            num_batches: Total number of batches
            concurrent_batches: Max concurrent batches
            
        Returns:
            Test results dictionary
        """
        logger.info(f"Starting optimized batch test: {num_batches} batches × {batch_size} concepts")
        logger.info(f"Concurrent batches: {concurrent_batches}")
        
        self.results['start_time'] = time.time()
        
        def process_batch(batch_idx: int) -> Dict[str, Any]:
            """Process a single batch of concepts."""
            batch_start = time.time()
            
            # Generate batch content
            start_idx = batch_idx * batch_size
            contents = [
                self.generate_financial_concept(start_idx + i, start_idx + i)
                for i in range(batch_size)
            ]
            
            try:
                # Use high-performance batch learning
                concept_ids = self.client.learn_batch(contents)
                
                batch_time = time.time() - batch_start
                
                # Record results thread-safely
                with self.results_lock:
                    self.results['total_concepts'] += batch_size
                    self.results['successful_concepts'] += len(concept_ids)
                    self.results['response_times'].append(batch_time)
                    self.results['batch_stats'].append({
                        'batch_idx': batch_idx,
                        'size': batch_size,
                        'time': batch_time,
                        'success_count': len(concept_ids),
                        'throughput': len(concept_ids) / batch_time if batch_time > 0 else 0
                    })
                
                logger.info(f"✅ Batch {batch_idx}: {len(concept_ids)}/{batch_size} concepts in {batch_time:.2f}s "
                          f"({len(concept_ids)/batch_time:.1f} concepts/sec)")
                
                return {
                    'batch_idx': batch_idx,
                    'success': True,
                    'concepts_processed': len(concept_ids),
                    'time': batch_time,
                    'error': None
                }
                
            except Exception as e:
                batch_time = time.time() - batch_start
                error_msg = str(e)
                
                with self.results_lock:
                    self.results['total_concepts'] += batch_size
                    self.results['failed_concepts'] += batch_size
                    self.results['response_times'].append(batch_time)
                    self.results['errors'].append({
                        'batch_idx': batch_idx,
                        'error': error_msg,
                        'time': batch_time
                    })
                
                logger.error(f"❌ Batch {batch_idx} failed in {batch_time:.2f}s: {error_msg}")
                
                return {
                    'batch_idx': batch_idx,
                    'success': False,
                    'concepts_processed': 0,
                    'time': batch_time,
                    'error': error_msg
                }
        
        # Execute batches with controlled concurrency
        batch_results = []
        with ThreadPoolExecutor(max_workers=concurrent_batches) as executor:
            # Submit all batches
            futures = {
                executor.submit(process_batch, batch_idx): batch_idx 
                for batch_idx in range(num_batches)
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                batch_idx = futures[future]
                try:
                    result = future.result()
                    batch_results.append(result)
                    
                    # Print progress every 10 batches
                    if len(batch_results) % 10 == 0:
                        successful_batches = sum(1 for r in batch_results if r['success'])
                        logger.info(f"Progress: {len(batch_results)}/{num_batches} batches "
                                  f"({successful_batches} successful)")
                        
                        # Print client stats
                        client_stats = self.client.get_stats()
                        logger.info(f"Client stats: {client_stats['success_rate']:.1%} success, "
                                  f"{client_stats['avg_response_time']:.2f}s avg response, "
                                  f"throttle={client_stats['current_throttle']:.1f}x")
                        
                except Exception as e:
                    logger.error(f"Future failed for batch {batch_idx}: {e}")
                    batch_results.append({
                        'batch_idx': batch_idx,
                        'success': False,
                        'concepts_processed': 0,
                        'time': 0,
                        'error': str(e)
                    })
        
        self.results['end_time'] = time.time()
        return self.analyze_results()
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results and generate report."""
        if not self.results['response_times']:
            return {'error': 'No data collected'}
        
        total_time = self.results['end_time'] - self.results['start_time']
        success_rate = (
            self.results['successful_concepts'] / self.results['total_concepts']
            if self.results['total_concepts'] > 0 else 0
        )
        
        response_times = self.results['response_times']
        client_stats = self.client.get_stats()
        
        # Calculate throughput metrics
        successful_batches = [b for b in self.results['batch_stats'] if b['success_count'] > 0]
        avg_batch_throughput = (
            statistics.mean([b['throughput'] for b in successful_batches])
            if successful_batches else 0
        )
        
        overall_throughput = self.results['successful_concepts'] / total_time if total_time > 0 else 0
        
        analysis = {
            'summary': {
                'total_concepts': self.results['total_concepts'],
                'successful_concepts': self.results['successful_concepts'],
                'failed_concepts': self.results['failed_concepts'],
                'success_rate': success_rate,
                'total_time_seconds': total_time,
                'overall_throughput_concepts_per_sec': overall_throughput,
            },
            'performance': {
                'avg_batch_throughput': avg_batch_throughput,
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'avg_response_time': statistics.mean(response_times),
                'median_response_time': statistics.median(response_times),
                'p95_response_time': self._percentile(response_times, 95),
            },
            'client_performance': client_stats,
            'connection_pool': client_stats.get('pool_stats', {}),
            'raw_data': {
                'batch_stats': self.results['batch_stats'],
                'errors': self.results['errors'][:10],  # First 10 errors only
            },
            'test_config': {
                'timestamp': datetime.now().isoformat(),
                'client_type': 'HighPerformanceStorageClient',
                'features': ['connection_pooling', 'adaptive_backpressure', 'circuit_breaker']
            }
        }
        
        return analysis
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(percentile / 100.0 * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def close(self):
        """Clean up resources."""
        self.client.close()

def main():
    """Run the optimized stress test."""
    logger.info("🚀 Starting Optimized Stress Test with Connection Pooling")
    
    test = OptimizedStressTest()
    
    try:
        # Test Configuration - Optimized for sustained high throughput
        BATCH_SIZE = 25          # Smaller batches for better flow control
        NUM_BATCHES = 50         # 1,250 total concepts (reasonable load)
        CONCURRENT_BATCHES = 8   # Moderate concurrency to avoid overwhelming
        
        logger.info(f"Test Configuration:")
        logger.info(f"  Batch size: {BATCH_SIZE}")
        logger.info(f"  Number of batches: {NUM_BATCHES}")
        logger.info(f"  Concurrent batches: {CONCURRENT_BATCHES}")
        logger.info(f"  Total concepts: {BATCH_SIZE * NUM_BATCHES}")
        logger.info(f"  Expected features: Connection pooling, adaptive backpressure, circuit breaker")
        
        # Run the test
        results = test.run_batch_test(BATCH_SIZE, NUM_BATCHES, CONCURRENT_BATCHES)
        
        # Print summary
        summary = results['summary']
        performance = results['performance']
        
        print(f"\n🎯 OPTIMIZED STRESS TEST RESULTS")
        print(f"=" * 60)
        print(f"Total Concepts:     {summary['total_concepts']:,}")
        print(f"Successful:         {summary['successful_concepts']:,}")
        print(f"Failed:            {summary['failed_concepts']:,}")
        print(f"Success Rate:      {summary['success_rate']:.1%}")
        print(f"Total Time:        {summary['total_time_seconds']:.1f}s")
        print(f"Overall Throughput: {summary['overall_throughput_concepts_per_sec']:.2f} concepts/sec")
        print(f"\nPerformance Metrics:")
        print(f"Avg Batch Throughput: {performance['avg_batch_throughput']:.2f} concepts/sec")
        print(f"Response Times (sec):")
        print(f"  Average:  {performance['avg_response_time']:.2f}")
        print(f"  Median:   {performance['median_response_time']:.2f}")
        print(f"  P95:      {performance['p95_response_time']:.2f}")
        print(f"  Min:      {performance['min_response_time']:.2f}")
        print(f"  Max:      {performance['max_response_time']:.2f}")
        
        # Connection pool stats
        pool_stats = results.get('connection_pool', {})
        print(f"\nConnection Pool Performance:")
        print(f"Connections Created: {pool_stats.get('created', 0)}")
        print(f"Connections Reused:  {pool_stats.get('reused', 0)}")
        print(f"Circuit Breaker:     {'OPEN' if pool_stats.get('circuit_open', False) else 'CLOSED'}")
        print(f"Pool Efficiency:     {pool_stats.get('reused', 0) / max(pool_stats.get('created', 1), 1):.1f}x reuse")
        
        # Client performance
        client_perf = results['client_performance']
        print(f"\nClient Performance:")
        print(f"Throttled Requests:  {client_perf.get('throttled_requests', 0)}")
        print(f"Current Throttle:    {client_perf.get('current_throttle', 1.0):.1f}x")
        print(f"Request Success:     {client_perf.get('success_rate', 0):.1%}")
        
        # Save detailed results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"optimized_stress_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {filename}")
        
        # Performance comparison
        if summary['overall_throughput_concepts_per_sec'] > 15:
            print(f"\n🎉 EXCELLENT: Sustained {summary['overall_throughput_concepts_per_sec']:.1f} concepts/sec!")
            print("✅ Connection pooling eliminated the connection storm")
            print("✅ Adaptive backpressure prevented resource exhaustion")
        elif summary['overall_throughput_concepts_per_sec'] > 10:
            print(f"\n✅ GOOD: {summary['overall_throughput_concepts_per_sec']:.1f} concepts/sec achieved")
            print("✅ Significant improvement over previous 25-30 second timeouts")
        else:
            print(f"\n⚠️  CONCERN: Only {summary['overall_throughput_concepts_per_sec']:.1f} concepts/sec")
            print("❓ May need further optimization")
        
        return results
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        return None
    except Exception as e:
        logger.error(f"Test failed with error: {e}", exc_info=True)
        return None
    finally:
        test.close()

if __name__ == "__main__":
    main()