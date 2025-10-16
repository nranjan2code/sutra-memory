"""
🌍 Wikipedia Full Dataset Downloader and Performance Tester

Downloads the entire Wikipedia EN dataset and creates random samples for testing.
This script optimizes for comprehensive knowledge while using efficient testing samples.
"""

import gc
import json
import logging
import os
import sys
import time
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import psutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sutra_core.reasoning.engine import ReasoningEngine

# Optional: Hugging Face datasets
try:
    from datasets import load_dataset
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠️  Hugging Face datasets not installed. Run: pip install datasets")

# Suppress warnings for clean output
logging.basicConfig(level=logging.ERROR)

# Beautiful colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


@dataclass
class WikiResult:
    """Result from Wikipedia performance test."""
    operation: str
    num_articles: int
    total_time: float
    throughput: float
    avg_article_length: int
    total_concepts: int
    total_associations: int
    memory_mb: float
    disk_mb: float
    success_count: int
    error_count: int
    sample_queries: Optional[List[dict]] = None


class WikipediaFullDatasetTester:
    """
    Performance tester using the full Wikipedia dataset with intelligent sampling.
    
    Strategy:
    1. Download and learn from as many Wikipedia articles as possible
    2. Generate high-quality Q&A pairs from the learned content
    3. Test with random samples of 100 Q&A pairs for efficient evaluation
    """
    
    def __init__(self, output_dir: str = "./performance_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[WikiResult] = []
        self.start_time = time.time()
        
        # Check if HF token is set
        self.hf_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_TOKEN')
        if not self.hf_token and HF_AVAILABLE:
            print(f"{Colors.YELLOW}⚠️  No Hugging Face token found in environment.{Colors.END}")
            print(f"{Colors.YELLOW}   Set HF_TOKEN or HUGGING_FACE_TOKEN to avoid rate limits.{Colors.END}\n")
    
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
        print(f"  {color}▸{Colors.END} {label:25s}: {Colors.BOLD}{value}{Colors.END}")
    
    def animated_progress(self, current: int, total: int, prefix: str = ""):
        """Show animated progress bar."""
        percent = 100 * (current / float(total))
        filled = int(50 * current // total)
        bar = '█' * filled + '░' * (50 - filled)
        
        elapsed = time.time() - self.start_time
        rate = current / elapsed if elapsed > 0 else 0
        eta = (total - current) / rate if rate > 0 else 0
        
        if eta < 60:
            eta_str = f"{eta:.0f}s"
        elif eta < 3600:
            eta_str = f"{eta/60:.1f}m"
        else:
            eta_str = f"{eta/3600:.1f}h"
        
        print(f'\r{Colors.CYAN}{prefix}{Colors.END} '
              f'{Colors.GREEN}|{bar}|{Colors.END} '
              f'{Colors.BOLD}{percent:>5.1f}%{Colors.END} '
              f'({Colors.YELLOW}{current:,}/{total:,}{Colors.END}) '
              f'{Colors.BLUE}{rate:>6,.1f}/s{Colors.END} '
              f'ETA: {Colors.YELLOW}{eta_str:>6s}{Colors.END}', 
              end='', flush=True)
        
        if current >= total:
            print()
    
    def get_memory_mb(self) -> float:
        """Get current memory usage in MB."""
        return psutil.Process().memory_info().rss / (1024 * 1024)
    
    def get_disk_mb(self, path: Path) -> float:
        """Get disk usage in MB."""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except:
            pass
        return total / (1024 * 1024)
    
    def load_full_wikipedia_dataset(self, max_articles: int = 100000) -> List[Dict[str, str]]:
        """
        Load as many Wikipedia articles as possible from the full dataset.
        
        Uses streaming to avoid memory issues and processes articles in batches.
        """
        print(f"\n📥 Downloading Wikipedia articles (up to {max_articles:,})...")
        
        try:
            # Use the latest wikimedia/wikipedia dataset (November 2023)
            print("Loading wikimedia/wikipedia dataset (20231101.en) in streaming mode...")
            dataset = load_dataset(
                "wikimedia/wikipedia",
                "20231101.en",
                split="train",
                streaming=True,  # Essential for large datasets
                token=self.hf_token if self.hf_token else None
            )
            
            # Process articles in batches to manage memory
            articles = []
            print("Processing Wikipedia articles...")
            count = 0
            batch_size = 1000
            
            for item in dataset:
                if len(articles) >= max_articles:
                    break
                
                count += 1
                
                # Show progress every batch
                if count % batch_size == 0:
                    print(f"  Processed {count:,} articles, collected {len(articles):,} suitable articles...")
                    # Force garbage collection to manage memory
                    gc.collect()
                
                # Filter for articles with substantial content
                text = item.get("text", "")
                title = item.get("title", "Unknown")
                
                # Quality filters
                if (len(text) > 1000 and  # At least 1000 characters
                    len(text) < 50000 and  # Not too long (likely list articles)
                    not title.startswith("List of") and  # Skip list articles
                    not title.startswith("Category:") and  # Skip category pages
                    "disambiguation" not in title.lower() and  # Skip disambiguation
                    len(title.split()) > 1):  # Multi-word titles tend to be better
                    
                    articles.append({
                        "title": title,
                        "text": text[:10000],  # First 10k chars for each article
                        "original_length": len(text)
                    })
            
            print(f"✓ Collected {len(articles):,} high-quality articles from {count:,} total articles")
            
            # Sort by original length to prioritize substantial articles
            articles.sort(key=lambda x: x['original_length'], reverse=True)
            
            return articles
            
        except Exception as e:
            print(f"❌ Failed to load Wikipedia: {e}")
            print(f"📌 Error type: {type(e).__name__}")
            raise
    
    def generate_qa_samples(self, articles: List[Dict[str, str]], num_samples: int = 100) -> List[Dict[str, str]]:
        """
        Generate high-quality Q&A pairs from the learned articles.
        
        Creates diverse questions that test different aspects of the knowledge.
        """
        print(f"\n🤔 Generating {num_samples} Q&A samples from {len(articles)} articles...")
        
        qa_pairs = []
        random.seed(42)  # For reproducible results
        
        # Sample articles to generate questions from
        sample_articles = random.sample(articles, min(num_samples * 2, len(articles)))
        
        question_templates = [
            "What is {title}?",
            "Tell me about {title}",
            "What do you know about {title}?",
            "Explain {title}",
            "Describe {title}",
            "What are the key facts about {title}?",
            "What is the main topic of {title}?",
            "Can you summarize {title}?",
        ]
        
        for i, article in enumerate(sample_articles):
            if len(qa_pairs) >= num_samples:
                break
                
            title = article['title']
            text = article['text']
            
            # Generate different types of questions
            template = random.choice(question_templates)
            question = template.format(title=title)
            
            # Create expected answer from the first paragraph
            first_paragraph = text.split('\n')[0] if '\n' in text else text[:500]
            
            qa_pairs.append({
                'question': question,
                'expected_context': first_paragraph,
                'source_article': title,
                'article_length': len(text)
            })
            
            # Add some content-based questions
            if 'is a' in text.lower() or 'was a' in text.lower():
                content_question = f"What type of thing is {title}?"
                qa_pairs.append({
                    'question': content_question,
                    'expected_context': first_paragraph,
                    'source_article': title,
                    'article_length': len(text)
                })
            
            if len(qa_pairs) >= num_samples:
                break
        
        # Randomize the final set
        random.shuffle(qa_pairs)
        qa_pairs = qa_pairs[:num_samples]
        
        print(f"✓ Generated {len(qa_pairs)} Q&A pairs")
        
        # Show sample questions
        print(f"\n{Colors.CYAN}📋 Sample questions:{Colors.END}")
        for i, qa in enumerate(qa_pairs[:5], 1):
            print(f"  {i}. {qa['question']}")
            print(f"     Source: {qa['source_article']}")
        if len(qa_pairs) > 5:
            print(f"  ... and {len(qa_pairs) - 5} more questions")
        
        return qa_pairs
    
    def benchmark_full_wikipedia_learning(
        self, 
        max_articles: int = 100000,
        storage_path: str = "./wiki_knowledge"
    ) -> Tuple[WikiResult, ReasoningEngine, List[Dict[str, str]]]:
        """
        Benchmark learning from the full Wikipedia dataset.
        """
        self.print_section(f"📚 DOWNLOADING & LEARNING FROM WIKIPEDIA (up to {max_articles:,} articles)")
        
        # Load articles from full dataset
        articles = self.load_full_wikipedia_dataset(max_articles)
        
        # Calculate statistics
        avg_length = int(np.mean([len(a['text']) for a in articles]))
        total_chars = sum(len(a['text']) for a in articles)
        self.print_metric("Articles collected", f"{len(articles):,}")
        self.print_metric("Average article length", f"{avg_length:,} chars")
        self.print_metric("Total content", f"{total_chars:,} chars ({total_chars/1024/1024:.1f} MB)")
        
        # Initialize engine (clean start)
        self.print_status("🔧", "Initializing ReasoningEngine...")
        storage = Path(storage_path)
        if storage.exists():
            import shutil
            shutil.rmtree(storage)
            print(f"  Cleaned existing knowledge base at {storage_path}")
        
        engine = ReasoningEngine(
            storage_path=storage_path,
            use_rust_storage=True,
            enable_vector_index=True,
            enable_caching=False
        )
        self.print_status("✅", "Engine ready!", Colors.GREEN)
        
        # Learn from articles in batches
        print(f"\n{Colors.YELLOW}📖 Learning from Wikipedia articles...{Colors.END}")
        memory_before = self.get_memory_mb()
        errors = 0
        batch_size = 100
        self.start_time = time.time()
        total_start = time.time()
        
        for i, article in enumerate(articles):
            try:
                engine.learn(
                    content=article['text'],
                    source=f"wikipedia:{article['title']}",
                    category="encyclopedia"
                )
                
                # Periodic memory management
                if (i + 1) % batch_size == 0:
                    gc.collect()  # Force garbage collection
                    
            except Exception as e:
                errors += 1
                if errors < 10:  # Show first 10 errors
                    self.print_status("⚠️", f"Error learning '{article['title'][:50]}...': {str(e)[:100]}", Colors.RED)
            
            # Update progress
            if (i + 1) % 50 == 0 or i == len(articles) - 1:
                self.animated_progress(i + 1, len(articles), "Learning")
        
        total_time = time.time() - total_start
        memory_after = self.get_memory_mb()
        
        # Get final stats
        stats = engine.get_system_stats()
        system_info = stats.get('system_info', stats)
        
        # Save knowledge base
        print(f"\n{Colors.CYAN}💾 Saving comprehensive knowledge base...{Colors.END}")
        save_start = time.time()
        engine.save()
        save_time = time.time() - save_start
        disk_usage = self.get_disk_mb(storage)
        self.print_status("✅", f"Saved in {save_time:.2f}s ({disk_usage:.2f} MB)", Colors.GREEN)
        
        # Create result
        result = WikiResult(
            operation="wikipedia_full_learn",
            num_articles=len(articles),
            total_time=total_time,
            throughput=len(articles) / total_time,
            avg_article_length=avg_length,
            total_concepts=system_info.get('total_concepts', len(engine.concepts)),
            total_associations=system_info.get('total_associations', len(engine.associations)),
            memory_mb=memory_after - memory_before,
            disk_mb=disk_usage,
            success_count=len(articles) - errors,
            error_count=errors
        )
        
        self._print_wiki_result(result)
        self.results.append(result)
        
        return result, engine, articles
    
    def benchmark_qa_sampling(
        self, 
        engine: ReasoningEngine,
        articles: List[Dict[str, str]],
        num_qa_samples: int = 100
    ) -> WikiResult:
        """
        Benchmark question answering using random samples from the learned knowledge.
        """
        self.print_section(f"🎯 TESTING WITH {num_qa_samples} RANDOM Q&A SAMPLES")
        
        # Generate Q&A samples
        qa_samples = self.generate_qa_samples(articles, num_qa_samples)
        
        # Get engine stats
        stats = engine.get_system_stats()
        system_info = stats.get('system_info', stats)
        self.print_metric("Knowledge base size", f"{system_info.get('total_concepts', 0):,} concepts")
        self.print_metric("Total associations", f"{system_info.get('total_associations', 0):,}")
        
        # Run Q&A tests
        print(f"\n{Colors.YELLOW}🚀 Running Q&A tests...{Colors.END}")
        results_list = []
        self.start_time = time.time()
        total_start = time.time()
        
        for i, qa in enumerate(qa_samples):
            try:
                query_start = time.time()
                result = engine.ask(qa['question'], num_reasoning_paths=3)
                query_time = (time.time() - query_start) * 1000
                
                results_list.append({
                    'question': qa['question'],
                    'answer': result.primary_answer,
                    'confidence': result.confidence,
                    'time_ms': query_time,
                    'num_sources': len(result.supporting_paths),
                    'source_article': qa['source_article'],
                    'expected_context': qa['expected_context'][:200] + "..."
                })
                
            except Exception as e:
                results_list.append({
                    'question': qa['question'],
                    'answer': f"Error: {e}",
                    'confidence': 0.0,
                    'time_ms': 0,
                    'num_sources': 0,
                    'source_article': qa['source_article'],
                    'expected_context': qa['expected_context'][:200] + "..."
                })
            
            self.animated_progress(i + 1, len(qa_samples), "Testing")
        
        total_time = time.time() - total_start
        
        # Calculate performance metrics
        successful_queries = [r for r in results_list if r['confidence'] > 0]
        avg_confidence = np.mean([r['confidence'] for r in successful_queries]) if successful_queries else 0
        avg_query_time = np.mean([r['time_ms'] for r in results_list])
        high_confidence_count = sum(1 for r in results_list if r['confidence'] > 0.7)
        
        # Print detailed sample results
        print(f"\n{Colors.GREEN}📊 Sample Q&A Results:{Colors.END}\n")
        for i, r in enumerate(results_list[:3], 1):
            print(f"{Colors.CYAN}Q{i}:{Colors.END} {r['question']}")
            print(f"{Colors.GREEN}A{i}:{Colors.END} {r['answer'][:300]}...")
            print(f"{Colors.YELLOW}Source:{Colors.END} {r['source_article']}")
            print(f"{Colors.BLUE}Stats:{Colors.END} Confidence: {r['confidence']:.2f}, "
                  f"Time: {r['time_ms']:.1f}ms, Sources: {r['num_sources']}\n")
        
        # Create result
        result = WikiResult(
            operation="wikipedia_qa_sampling",
            num_articles=len(qa_samples),
            total_time=total_time,
            throughput=len(qa_samples) / total_time,
            avg_article_length=0,
            total_concepts=system_info.get('total_concepts', 0),
            total_associations=system_info.get('total_associations', 0),
            memory_mb=0,
            disk_mb=0,
            success_count=len(successful_queries),
            error_count=len(qa_samples) - len(successful_queries),
            sample_queries=results_list
        )
        
        # Print performance summary
        self.print_metric("Average confidence", f"{avg_confidence:.3f}")
        self.print_metric("Average query time", f"{avg_query_time:.1f} ms")
        self.print_metric("Success rate", f"{result.success_count}/{len(qa_samples)} ({result.success_count/len(qa_samples)*100:.1f}%)")
        self.print_metric("High confidence (>0.7)", f"{high_confidence_count}/{len(qa_samples)} ({high_confidence_count/len(qa_samples)*100:.1f}%)")
        
        self.results.append(result)
        return result
    
    def _print_wiki_result(self, result: WikiResult):
        """Print formatted result."""
        print(f"\n{Colors.GREEN}┌{'─'*78}┐{Colors.END}")
        print(f"{Colors.GREEN}│{Colors.END} {result.operation.upper().center(76)} {Colors.GREEN}│{Colors.END}")
        print(f"{Colors.GREEN}├{'─'*78}┤{Colors.END}")
        
        self.print_metric("Articles processed", f"{result.num_articles:,}")
        self.print_metric("Total time", f"{result.total_time:.2f}s")
        self.print_metric("Throughput", f"{result.throughput:.1f} articles/sec")
        
        if result.avg_article_length > 0:
            self.print_metric("Avg article length", f"{result.avg_article_length:,} chars")
        
        self.print_metric("Total concepts", f"{result.total_concepts:,}")
        self.print_metric("Total associations", f"{result.total_associations:,}")
        
        if result.memory_mb > 0:
            self.print_metric("Memory used", f"{result.memory_mb:.1f} MB")
        if result.disk_mb > 0:
            self.print_metric("Disk used", f"{result.disk_mb:.1f} MB")
        
        success_rate = (result.success_count / result.num_articles * 100) if result.num_articles > 0 else 0
        self.print_metric("Success rate", f"{success_rate:.1f}% ({result.error_count} errors)")
        
        print(f"{Colors.GREEN}└{'─'*78}┘{Colors.END}\n")
    
    def save_results(self, max_articles: int):
        """Save results to JSON file."""
        results_dict = {
            "test_type": "wikipedia_full_dataset",
            "timestamp": time.time(),
            "max_articles": max_articles,
            "system_info": {
                "platform": os.uname().sysname,
                "cpus": psutil.cpu_count(),
                "memory_gb": psutil.virtual_memory().total / (1024**3)
            },
            "results": [asdict(r) for r in self.results]
        }
        
        filename = self.output_dir / f"wikipedia_full_{max_articles}_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        self.print_status("💾", f"Results saved to: {filename}", Colors.CYAN)


def main():
    """Run the full Wikipedia dataset test."""
    tester = WikipediaFullDatasetTester()
    
    # Get parameters from command line
    max_articles = 10000  # Default: 10k articles
    qa_samples = 100     # Default: 100 Q&A samples
    
    if len(sys.argv) > 1:
        max_articles = int(sys.argv[1])
    if len(sys.argv) > 2:
        qa_samples = int(sys.argv[2])
    
    # Print header
    tester.print_header("🌍 WIKIPEDIA FULL DATASET PERFORMANCE TEST 🌍")
    
    print(f"{Colors.CYAN}Configuration:{Colors.END}")
    tester.print_metric("Platform", os.uname().sysname)
    tester.print_metric("CPU Cores", str(psutil.cpu_count()))
    tester.print_metric("Total Memory", f"{psutil.virtual_memory().total / (1024**3):.1f} GB")
    tester.print_metric("Max Articles", f"{max_articles:,}")
    tester.print_metric("Q&A Samples", f"{qa_samples}")
    tester.print_metric("Storage Path", "./wiki_knowledge")
    
    if not HF_AVAILABLE:
        print(f"\n{Colors.RED}❌ Hugging Face datasets not installed!{Colors.END}")
        print(f"{Colors.YELLOW}Install with: pip install datasets{Colors.END}\n")
        return 1
    
    # Check for HF token
    if tester.hf_token:
        tester.print_status("🔑", "Hugging Face token found", Colors.GREEN)
    else:
        print(f"\n{Colors.YELLOW}⚠️  No Hugging Face token found!{Colors.END}")
        print(f"{Colors.YELLOW}   Large dataset downloads may fail without authentication.{Colors.END}")
        print(f"{Colors.YELLOW}   Set HF_TOKEN environment variable with your token.{Colors.END}\n")
        return 1
    
    try:
        # Step 1: Download and learn from full Wikipedia dataset
        learning_result, learned_engine, articles = tester.benchmark_full_wikipedia_learning(
            max_articles=max_articles,
            storage_path="./wiki_knowledge"
        )
        
        # Step 2: Test with random Q&A samples
        qa_result = tester.benchmark_qa_sampling(
            engine=learned_engine,
            articles=articles,
            num_qa_samples=qa_samples
        )
        
        # Save results
        tester.save_results(max_articles)
        
        # Final summary
        tester.print_header("✨ WIKIPEDIA FULL DATASET TEST COMPLETE! ✨")
        print(f"{Colors.GREEN}📊 Final Summary:{Colors.END}\n")
        tester.print_metric("Articles processed", f"{learning_result.num_articles:,}")
        tester.print_metric("Total concepts", f"{learning_result.total_concepts:,}")
        tester.print_metric("Total associations", f"{learning_result.total_associations:,}")
        tester.print_metric("Knowledge base size", f"{learning_result.disk_mb:.1f} MB")
        tester.print_metric("Learning time", f"{learning_result.total_time:.1f}s")
        tester.print_metric("Q&A samples tested", f"{qa_result.num_articles}")
        tester.print_metric("Q&A success rate", f"{qa_result.success_count}/{qa_result.num_articles}")
        tester.print_metric("Avg confidence", f"{np.mean([q['confidence'] for q in qa_result.sample_queries if q['confidence'] > 0]):.3f}")
        
        print(f"\n{Colors.GREEN}🎉 Knowledge base ready in ./wiki_knowledge/{Colors.END}")
        print(f"{Colors.GREEN}🎉 Test with: python -c \"from sutra_core.reasoning.engine import ReasoningEngine; engine = ReasoningEngine('./wiki_knowledge'); print(engine.ask('What is artificial intelligence?'))\"  {Colors.END}\n")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⏸️  Process interrupted by user{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test failed: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())