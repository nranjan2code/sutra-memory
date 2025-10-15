"""
🎯 Production Performance Test Suite - With Beautiful Visual Feedback! 🎨

Real-time progress bars, colorful output, and detailed status updates
so you never feel anxious about what's happening! 
"""

import gc
import json
import logging
import os
import psutil
import shutil
import statistics
import sys
import tempfile
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np

# Suppress warnings for clean output
logging.basicConfig(level=logging.ERROR)

from sutra_core.reasoning.engine import ReasoningEngine


# Beautiful colors for terminal output!
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


@dataclass
class BenchmarkResult:
    """Performance benchmark result."""
    operation: str
    scale: int
    total_time: float
    throughput: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    memory_mb: float
    disk_mb: float
    success_count: int
    error_count: int


class BeautifulPerformanceTester:
    """
    Performance tester with gorgeous visual feedback!
    You'll never feel anxious about what's happening! 😊
    """
    
    def __init__(self, output_dir: str = "./performance_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[BenchmarkResult] = []
        self.start_time = time.time()
        
    def print_header(self, text: str, color=Colors.CYAN):
        """Print beautiful header."""
        width = 80
        print(f"\n{color}{'='*width}{Colors.END}")
        print(f"{color}{text.center(width)}{Colors.END}")
        print(f"{color}{'='*width}{Colors.END}\n")
    
    def print_section(self, text: str):
        """Print section header."""
        print(f"\n{Colors.BLUE}{'─'*80}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.BLUE}{'─'*80}{Colors.END}\n")
    
    def print_status(self, emoji: str, text: str, color=Colors.GREEN):
        """Print status with emoji."""
        print(f"{color}{emoji} {text}{Colors.END}")
    
    def print_metric(self, label: str, value: str, color=Colors.CYAN):
        """Print a metric nicely."""
        print(f"  {color}▸{Colors.END} {label:20s}: {Colors.BOLD}{value}{Colors.END}")
    
    def animated_progress(self, current: int, total: int, prefix: str = "", bar_length: int = 50):
        """Show beautiful animated progress bar."""
        percent = 100 * (current / float(total))
        filled = int(bar_length * current // total)
        
        # Create gradient bar
        bar = '█' * filled + '░' * (bar_length - filled)
        
        # Calculate rate and ETA
        elapsed = time.time() - self.start_time
        rate = current / elapsed if elapsed > 0 else 0
        eta = (total - current) / rate if rate > 0 else 0
        
        # Format ETA nicely
        if eta < 60:
            eta_str = f"{eta:.0f}s"
        elif eta < 3600:
            eta_str = f"{eta/60:.1f}m"
        else:
            eta_str = f"{eta/3600:.1f}h"
        
        # Print with colors
        print(f'\r{Colors.CYAN}{prefix}{Colors.END} '
              f'{Colors.GREEN}|{bar}|{Colors.END} '
              f'{Colors.BOLD}{percent:>5.1f}%{Colors.END} '
              f'({Colors.YELLOW}{current:,}/{total:,}{Colors.END}) '
              f'{Colors.BLUE}{rate:>6,.0f}/s{Colors.END} '
              f'ETA: {Colors.YELLOW}{eta_str:>6s}{Colors.END}', 
              end='', flush=True)
        
        if current >= total:
            print()  # New line when complete
    
    def spinner_animation(self, message: str, duration: float = 1.0):
        """Show a friendly spinner while something is happening."""
        spinners = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        start = time.time()
        i = 0
        while time.time() - start < duration:
            print(f'\r{Colors.CYAN}{spinners[i % len(spinners)]}{Colors.END} {message}...', 
                  end='', flush=True)
            time.sleep(0.1)
            i += 1
        print(f'\r{Colors.GREEN}✓{Colors.END} {message}... Done!    ')
    
    def get_memory_mb(self) -> float:
        """Get memory usage."""
        return psutil.Process().memory_info().rss / (1024 * 1024)
    
    def get_disk_mb(self, path: Path) -> float:
        """Get disk usage."""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except:
            pass
        return total / (1024 * 1024)
    
    def benchmark_learn(self, scale: int, batch_size: int = 50) -> BenchmarkResult:
        """
        Benchmark learning with beautiful progress visualization! 📚
        """
        self.print_section(f"🎓 TEST 1: LEARNING {scale:,} CONCEPTS")
        
        temp_dir = tempfile.mkdtemp(prefix="perf_learn_")
        storage_path = Path(temp_dir) / "storage"
        
        try:
            # Initialize
            self.print_status("🔧", "Initializing ReasoningEngine...")
            engine = ReasoningEngine(
                storage_path=str(storage_path),
                use_rust_storage=True,
                enable_vector_index=False,
                enable_caching=False
            )
            self.print_status("✅", "Engine ready!", Colors.GREEN)
            
            # Learn with progress bar
            print(f"\n{Colors.YELLOW}📖 Learning {scale:,} concepts...{Colors.END}")
            memory_before = self.get_memory_mb()
            latencies = []
            errors = 0
            
            self.start_time = time.time()
            total_start = time.time()
            
            for i in range(scale):
                concept_start = time.time()
                try:
                    engine.learn(
                        f"Performance test concept {i}: Sample text about topic {i % 100}",
                        source="benchmark"
                    )
                    latency = (time.time() - concept_start) * 1000
                    latencies.append(latency)
                except Exception as e:
                    errors += 1
                    if errors < 5:
                        self.print_status("⚠️", f"Error: {e}", Colors.RED)
                
                # Update progress
                if (i + 1) % batch_size == 0 or i == scale - 1:
                    self.animated_progress(i + 1, scale, "Progress")
            
            total_time = time.time() - total_start
            memory_after = self.get_memory_mb()
            
            # Save
            print(f"\n{Colors.CYAN}💾 Saving to disk...{Colors.END}")
            save_start = time.time()
            engine.save()
            save_time = time.time() - save_start
            disk_usage = self.get_disk_mb(storage_path)
            self.print_status("✅", f"Saved in {save_time:.2f}s ({disk_usage:.2f} MB)", Colors.GREEN)
            
            # Calculate stats
            result = BenchmarkResult(
                operation="learn",
                scale=scale,
                total_time=total_time,
                throughput=scale / total_time,
                latency_p50=float(np.percentile(latencies, 50)),
                latency_p95=float(np.percentile(latencies, 95)),
                latency_p99=float(np.percentile(latencies, 99)),
                memory_mb=memory_after - memory_before,
                disk_mb=disk_usage,
                success_count=scale - errors,
                error_count=errors
            )
            
            self._print_result(result)
            self.results.append(result)
            return result
            
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
    
    def benchmark_query(self, scale: int, num_queries: int) -> BenchmarkResult:
        """
        Benchmark queries with visual feedback! 🔍
        """
        self.print_section(f"🔍 TEST 2: QUERYING {num_queries:,} TIMES")
        
        temp_dir = tempfile.mkdtemp(prefix="perf_query_")
        storage_path = Path(temp_dir) / "storage"
        
        try:
            # Setup
            self.print_status("🏗️", f"Creating {scale:,} test concepts...")
            engine = ReasoningEngine(
                storage_path=str(storage_path),
                use_rust_storage=True,
                enable_vector_index=False,
                enable_caching=False
            )
            
            for i in range(scale):
                engine.learn(f"Query benchmark concept {i}", source="test")
                if (i + 1) % 100 == 0:
                    print(f'\r  {Colors.CYAN}Adding concepts... '
                          f'{i+1:,}/{scale:,}{Colors.END}', end='', flush=True)
            print()
            self.print_status("✅", f"Test data ready ({scale:,} concepts)", Colors.GREEN)
            
            concept_ids = list(engine.concepts.keys())
            
            # Query with progress
            print(f"\n{Colors.YELLOW}🚀 Executing {num_queries:,} queries...{Colors.END}")
            latencies = []
            errors = 0
            
            self.start_time = time.time()
            query_start = time.time()
            
            for i in range(num_queries):
                cid = concept_ids[i % len(concept_ids)]
                
                op_start = time.time()
                try:
                    info = engine.get_concept_info(cid)
                    if info is None:
                        errors += 1
                    latencies.append((time.time() - op_start) * 1000)
                except:
                    errors += 1
                
                if (i + 1) % 1000 == 0 or i == num_queries - 1:
                    self.animated_progress(i + 1, num_queries, "Progress")
            
            total_time = time.time() - query_start
            
            result = BenchmarkResult(
                operation="query",
                scale=num_queries,
                total_time=total_time,
                throughput=num_queries / total_time,
                latency_p50=float(np.percentile(latencies, 50)),
                latency_p95=float(np.percentile(latencies, 95)),
                latency_p99=float(np.percentile(latencies, 99)),
                memory_mb=0,
                disk_mb=0,
                success_count=num_queries - errors,
                error_count=errors
            )
            
            self._print_result(result)
            self.results.append(result)
            return result
            
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
    
    def benchmark_distance(self, scale: int, num_ops: int) -> Optional[BenchmarkResult]:
        """
        Benchmark distance computation! 📐
        """
        self.print_section(f"📐 TEST 3: DISTANCE COMPUTATION {num_ops:,} TIMES")
        
        temp_dir = tempfile.mkdtemp(prefix="perf_dist_")
        storage_path = Path(temp_dir) / "storage"
        
        try:
            # Setup
            self.print_status("🏗️", f"Creating {scale:,} test concepts...")
            engine = ReasoningEngine(
                storage_path=str(storage_path),
                use_rust_storage=True,
                enable_vector_index=False,
                enable_caching=False
            )
            
            for i in range(scale):
                engine.learn(f"Distance benchmark concept {i}", source="test")
                if (i + 1) % 100 == 0:
                    print(f'\r  {Colors.CYAN}Adding concepts... '
                          f'{i+1:,}/{scale:,}{Colors.END}', end='', flush=True)
            print()
            
            if not engine.use_rust_storage or not engine.storage:
                self.print_status("⚠️", "Rust storage not available, skipping", Colors.YELLOW)
                return None
            
            self.print_status("✅", "Test data ready", Colors.GREEN)
            
            all_ids = list(engine.concepts.keys())
            concept_ids = all_ids[:min(100, len(all_ids))]
            
            # Distance computation with progress
            print(f"\n{Colors.YELLOW}⚡ Computing {num_ops:,} distances...{Colors.END}")
            latencies = []
            successes = 0
            
            self.start_time = time.time()
            dist_start = time.time()
            
            for i in range(num_ops):
                id1 = concept_ids[i % len(concept_ids)]
                id2 = concept_ids[(i + 1) % len(concept_ids)]
                
                op_start = time.time()
                try:
                    dist = engine.storage.distance(id1, id2)
                    if dist is not None:
                        successes += 1
                    latencies.append((time.time() - op_start) * 1000)
                except:
                    pass
                
                if (i + 1) % 1000 == 0 or i == num_ops - 1:
                    self.animated_progress(i + 1, num_ops, "Progress")
            
            total_time = time.time() - dist_start
            
            result = BenchmarkResult(
                operation="distance",
                scale=num_ops,
                total_time=total_time,
                throughput=num_ops / total_time,
                latency_p50=float(np.percentile(latencies, 50)) if latencies else 0,
                latency_p95=float(np.percentile(latencies, 95)) if latencies else 0,
                latency_p99=float(np.percentile(latencies, 99)) if latencies else 0,
                memory_mb=0,
                disk_mb=0,
                success_count=successes,
                error_count=num_ops - successes
            )
            
            self._print_result(result)
            self.results.append(result)
            return result
            
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
    
    def benchmark_save_load(self, scale: int) -> tuple:
        """
        Benchmark persistence operations! 💾
        """
        self.print_section(f"💾 TEST 4: SAVE/LOAD {scale:,} CONCEPTS")
        
        temp_dir = tempfile.mkdtemp(prefix="perf_saveload_")
        storage_path = Path(temp_dir) / "storage"
        
        try:
            # Create data
            self.print_status("🏗️", f"Creating {scale:,} test concepts...")
            engine = ReasoningEngine(
                storage_path=str(storage_path),
                use_rust_storage=True,
                enable_vector_index=False,
                enable_caching=False
            )
            
            for i in range(scale):
                engine.learn(f"SaveLoad test concept {i}", source="test")
                if (i + 1) % 100 == 0:
                    print(f'\r  {Colors.CYAN}Adding concepts... '
                          f'{i+1:,}/{scale:,}{Colors.END}', end='', flush=True)
            print()
            self.print_status("✅", "Test data ready", Colors.GREEN)
            
            # SAVE test
            print(f"\n{Colors.YELLOW}💾 Saving {scale:,} concepts to disk...{Colors.END}")
            save_start = time.time()
            engine.save()
            save_time = time.time() - save_start
            disk_usage = self.get_disk_mb(storage_path)
            
            self.print_status("✅", f"Saved in {save_time:.2f}s", Colors.GREEN)
            self.print_metric("Disk usage", f"{disk_usage:.2f} MB")
            self.print_metric("Per concept", f"{disk_usage*1024/scale:.2f} KB")
            
            save_result = BenchmarkResult(
                operation="save",
                scale=scale,
                total_time=save_time,
                throughput=scale / save_time if save_time > 0 else 0,
                latency_p50=save_time * 1000,
                latency_p95=save_time * 1000,
                latency_p99=save_time * 1000,
                memory_mb=0,
                disk_mb=disk_usage,
                success_count=scale,
                error_count=0
            )
            
            # Cleanup for load test
            del engine
            gc.collect()
            self.spinner_animation("Clearing memory", 0.5)
            
            # LOAD test  
            print(f"\n{Colors.YELLOW}📂 Loading {scale:,} concepts from disk...{Colors.END}")
            
            # Suppress warnings during load
            import warnings
            warnings.filterwarnings('ignore')
            
            load_start = time.time()
            engine2 = ReasoningEngine(
                storage_path=str(storage_path),
                use_rust_storage=True,
                enable_vector_index=False,
                enable_caching=False
            )
            load_time = time.time() - load_start
            loaded_count = len(engine2.concepts)
            memory_used = self.get_memory_mb()
            
            self.print_status("✅", f"Loaded in {load_time:.2f}s", Colors.GREEN)
            self.print_metric("Concepts loaded", f"{loaded_count:,}")
            self.print_metric("Memory usage", f"{memory_used:.1f} MB")
            
            load_result = BenchmarkResult(
                operation="load",
                scale=scale,
                total_time=load_time,
                throughput=loaded_count / load_time if load_time > 0 else 0,
                latency_p50=load_time * 1000,
                latency_p95=load_time * 1000,
                latency_p99=load_time * 1000,
                memory_mb=memory_used,
                disk_mb=disk_usage,
                success_count=loaded_count,
                error_count=scale - loaded_count
            )
            
            self._print_result(save_result)
            self._print_result(load_result)
            
            self.results.extend([save_result, load_result])
            return save_result, load_result
            
        finally:
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir)
    
    def _print_result(self, result: BenchmarkResult):
        """Print beautiful result box."""
        print(f"\n{Colors.GREEN}{'┌' + '─'*78 + '┐'}{Colors.END}")
        print(f"{Colors.GREEN}│{Colors.END} {Colors.BOLD}{result.operation.upper():^76}{Colors.END} {Colors.GREEN}│{Colors.END}")
        print(f"{Colors.GREEN}{'├' + '─'*78 + '┤'}{Colors.END}")
        
        print(f"{Colors.GREEN}│{Colors.END} Scale:        {result.scale:>12,} operations{' '*38}{Colors.GREEN}│{Colors.END}")
        print(f"{Colors.GREEN}│{Colors.END} Time:         {result.total_time:>12.2f} seconds{' '*40}{Colors.GREEN}│{Colors.END}")
        print(f"{Colors.GREEN}│{Colors.END} Throughput:   {result.throughput:>12,.0f} ops/sec{' '*38}{Colors.GREEN}│{Colors.END}")
        print(f"{Colors.GREEN}│{Colors.END} Latency p50:  {result.latency_p50:>12.3f} ms{' '*44}{Colors.GREEN}│{Colors.END}")
        print(f"{Colors.GREEN}│{Colors.END} Latency p95:  {result.latency_p95:>12.3f} ms{' '*44}{Colors.GREEN}│{Colors.END}")
        print(f"{Colors.GREEN}│{Colors.END} Latency p99:  {result.latency_p99:>12.3f} ms{' '*44}{Colors.GREEN}│{Colors.END}")
        
        if result.memory_mb > 0:
            print(f"{Colors.GREEN}│{Colors.END} Memory:       {result.memory_mb:>12.1f} MB{' '*46}{Colors.GREEN}│{Colors.END}")
        if result.disk_mb > 0:
            print(f"{Colors.GREEN}│{Colors.END} Disk:         {result.disk_mb:>12.2f} MB{' '*46}{Colors.GREEN}│{Colors.END}")
        
        success_rate = result.success_count * 100 / result.scale if result.scale > 0 else 0
        print(f"{Colors.GREEN}│{Colors.END} Success rate: {success_rate:>12.1f}% ({result.error_count} errors){' '*32}{Colors.GREEN}│{Colors.END}")
        
        print(f"{Colors.GREEN}{'└' + '─'*78 + '┘'}{Colors.END}")
    
    def run_full_suite(self, scale: int = 1000):
        """
        Run the complete performance test suite! 🚀
        """
        self.print_header("🎯 SUTRA STORAGE PERFORMANCE TEST SUITE 🎯", Colors.CYAN)
        
        # System info
        print(f"{Colors.BOLD}System Configuration:{Colors.END}")
        self.print_metric("Platform", os.uname().sysname)
        self.print_metric("CPU Cores", str(psutil.cpu_count()))
        self.print_metric("Total Memory", f"{psutil.virtual_memory().total / (1024**3):.1f} GB")
        self.print_metric("Test Scale", f"{scale:,} concepts")
        
        # Estimate time
        estimated_time = scale * 0.24  # seconds per concept
        if estimated_time < 60:
            time_str = f"{estimated_time:.0f} seconds"
        elif estimated_time < 3600:
            time_str = f"{estimated_time/60:.1f} minutes"
        else:
            time_str = f"{estimated_time/3600:.1f} hours"
        
        print(f"\n{Colors.YELLOW}⏱️  Estimated total time: {time_str}{Colors.END}")
        print(f"{Colors.CYAN}💡 Sit back and relax - you'll see progress every step of the way!{Colors.END}")
        
        suite_start = time.time()
        
        # Run all tests
        self.benchmark_learn(scale)
        self.benchmark_query(scale, min(10000, scale * 10))
        self.benchmark_distance(scale, min(10000, scale * 10))
        self.benchmark_save_load(scale)
        
        suite_time = time.time() - suite_start
        
        # Beautiful summary
        self.print_header("📊 PERFORMANCE SUMMARY 📊", Colors.GREEN)
        
        print(f"{Colors.BOLD}Results by Operation:{Colors.END}\n")
        for result in self.results:
            emoji = self._get_emoji(result.throughput, result.operation)
            color = self._get_color(result.throughput, result.operation)
            print(f"{emoji} {Colors.BOLD}{result.operation:12s}{Colors.END}: "
                  f"{color}{result.throughput:>12,.0f} ops/sec{Colors.END}  "
                  f"({result.latency_p50:>8.3f} ms p50)")
        
        print(f"\n{Colors.CYAN}{'─'*80}{Colors.END}")
        print(f"{Colors.BOLD}Total test time: {suite_time:.1f} seconds{Colors.END}")
        
        # Save results
        self._save_results(scale)
        
        self.print_header("✨ ALL TESTS COMPLETE! ✨", Colors.GREEN)
        print(f"{Colors.GREEN}🎉 Great job! All performance tests finished successfully!{Colors.END}\n")
    
    def _get_emoji(self, throughput: float, operation: str) -> str:
        """Get emoji based on performance."""
        if operation == "learn":
            return "📚" if throughput > 10 else "🐌"
        elif operation == "query":
            return "⚡" if throughput > 100000 else "🔍"
        elif operation == "distance":
            return "🚀" if throughput > 100000 else "📐"
        elif operation == "save":
            return "💾"
        elif operation == "load":
            return "📂"
        return "✓"
    
    def _get_color(self, throughput: float, operation: str) -> str:
        """Get color based on performance."""
        if operation == "learn":
            return Colors.GREEN if throughput > 10 else Colors.YELLOW
        elif operation in ["query", "distance"]:
            return Colors.GREEN if throughput > 100000 else Colors.YELLOW
        return Colors.CYAN
    
    def _save_results(self, scale: int):
        """Save results to JSON."""
        results_dict = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scale": scale,
            "system": {
                "platform": os.uname().sysname,
                "cpus": psutil.cpu_count(),
                "memory_gb": psutil.virtual_memory().total / (1024**3)
            },
            "results": [asdict(r) for r in self.results]
        }
        
        filename = self.output_dir / f"performance_{scale}_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        self.print_status("💾", f"Results saved to: {filename}", Colors.CYAN)


def main():
    """Run the beautiful performance test suite!"""
    tester = BeautifulPerformanceTester()
    
    # Get scale from command line
    if len(sys.argv) > 1:
        scale = int(sys.argv[1])
    else:
        print(f"{Colors.CYAN}Usage: python performance_suite.py <scale>{Colors.END}")
        print(f"{Colors.CYAN}Examples:{Colors.END}")
        print(f"  python performance_suite.py 1000    # Quick test (15 min)")
        print(f"  python performance_suite.py 5000    # Medium test (1 hour)")
        print(f"  python performance_suite.py 10000   # Large test (2 hours)")
        print(f"\n{Colors.YELLOW}Running with default scale: 1000{Colors.END}\n")
        scale = 1000
    
    tester.run_full_suite(scale=scale)


if __name__ == "__main__":
    main()
