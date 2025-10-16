"""
🌍 Wikipedia Real-World Performance Test Suite

Tests the Sutra AI system with actual Wikipedia articles instead of synthetic data.
Measures real-world performance, answer quality, and knowledge graph formation.
"""

import gc
import json
import logging
import os
import sys
import time
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


class WikipediaPerformanceTester:
    """
    Performance tester using real Wikipedia articles.
    
    Tests:
    1. Learning from Wikipedia articles
    2. Query answering with real questions
    3. Knowledge graph quality metrics
    4. Scaling behavior with real-world data
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
    
    def load_wikipedia_articles(self, num_articles: int = 100) -> List[Dict[str, str]]:
        """
        Load Wikipedia articles from Hugging Face datasets.
        
        For comprehensive knowledge building, we load as many high-quality articles as possible
        up to the specified limit, with improved filtering for better content quality.
        """
        print(f"\n📥 Downloading up to {num_articles:,} Wikipedia articles...")
        
        try:
            # Use the latest wikimedia/wikipedia dataset (November 2023)
            print("Loading wikimedia/wikipedia dataset (20231101.en) in streaming mode...")
            dataset = load_dataset(
                "wikimedia/wikipedia",
                "20231101.en",
                split="train",
                streaming=True,  # Essential for large datasets to avoid memory issues
                token=self.hf_token if self.hf_token else None
            )
            
            # Process articles with improved quality filtering
            articles = []
            print("Processing articles with quality filtering...")
            count = 0
            batch_size = 1000
            
            for item in dataset:
                if len(articles) >= num_articles:
                    break
                
                count += 1
                
                # Show progress every batch
                if count % batch_size == 0:
                    print(f"  Processed {count:,} articles, collected {len(articles):,} high-quality articles...")
                    # Force garbage collection for memory management
                    import gc
                    gc.collect()
                
                # Improved quality filters
                text = item.get("text", "")
                title = item.get("title", "Unknown")
                
                # Quality criteria for better articles
                if (len(text) > 1000 and  # At least 1000 characters for substantial content
                    len(text) < 50000 and  # Not too long (likely list articles or dumps)
                    not title.startswith("List of") and  # Skip list articles
                    not title.startswith("Category:") and  # Skip category pages
                    "disambiguation" not in title.lower() and  # Skip disambiguation pages
                    len(title.split()) > 1 and  # Multi-word titles tend to be better
                    not title.endswith("(disambiguation)") and  # Another disambiguation check
                    ":" not in title[:50]):  # Skip most namespace pages
                    
                    articles.append({
                        "title": title,
                        "text": text[:10000],  # First 10k chars for comprehensive learning
                        "original_length": len(text)
                    })
            
            print(f"✓ Collected {len(articles):,} high-quality articles from {count:,} total articles processed")
            
            # Sort by original length to prioritize substantial articles
            articles.sort(key=lambda x: x.get('original_length', 0), reverse=True)
            
            # Calculate some stats
            if articles:
                avg_length = sum(len(a['text']) for a in articles) / len(articles)
                total_content = sum(len(a['text']) for a in articles)
                print(f"  Average article length: {avg_length:,.0f} characters")
                print(f"  Total content: {total_content:,} characters ({total_content/1024/1024:.1f} MB)")
            
            return articles
            
        except Exception as e:
            print(f"❌ Failed to load Wikipedia: {e}")
            print(f"📌 Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise
    
    def benchmark_wikipedia_learning(
        self, 
        num_articles: int = 1000,
        storage_path: str = "./wiki_knowledge"
    ) -> Tuple[WikiResult, ReasoningEngine, List[Dict[str, str]]]:
        """
        Benchmark learning from real Wikipedia articles.
        """
        self.print_section(f"📚 TEST 1: LEARNING FROM {num_articles:,} WIKIPEDIA ARTICLES")
        
        # Load articles
        articles = self.load_wikipedia_articles(num_articles)
        
        # Calculate average article length
        avg_length = int(np.mean([len(a['text']) for a in articles]))
        self.print_metric("Average article length", f"{avg_length:,} chars")
        
        # Initialize engine
        self.print_status("🔧", "Initializing ReasoningEngine...")
        storage = Path(storage_path)
        if storage.exists():
            import shutil
            shutil.rmtree(storage)
        
        engine = ReasoningEngine(
            storage_path=storage_path,
            use_rust_storage=True,
            enable_vector_index=True,
            enable_caching=False
        )
        self.print_status("✅", "Engine ready!", Colors.GREEN)
        
        # Show what articles we're learning from
        print(f"\n{Colors.CYAN}📋 Wikipedia articles to learn from:{Colors.END}")
        for i, article in enumerate(articles[:5]):  # Show first 5
            print(f"  {i+1}. {article['title']}")
            print(f"     {article['text'][:100]}...")
        if len(articles) > 5:
            print(f"  ... and {len(articles) - 5} more articles")
        
        # Learn from articles
        print(f"\n{Colors.YELLOW}📖 Learning from Wikipedia articles...{Colors.END}")
        memory_before = self.get_memory_mb()
        errors = 0
        self.start_time = time.time()
        total_start = time.time()
        
        for i, article in enumerate(articles):
            try:
                engine.learn(
                    content=article['text'],
                    source=f"wikipedia:{article['title']}",
                    category="encyclopedia"
                )
            except Exception as e:
                errors += 1
                if errors < 5:
                    self.print_status("⚠️", f"Error learning '{article['title']}': {e}", Colors.RED)
            
            # Update progress every 10 articles
            if (i + 1) % 10 == 0 or i == len(articles) - 1:
                self.animated_progress(i + 1, len(articles), "Progress")
        
        total_time = time.time() - total_start
        memory_after = self.get_memory_mb()
        
        # Get stats
        stats = engine.get_system_stats()
        
        # Save knowledge base
        print(f"\n{Colors.CYAN}💾 Saving knowledge base...{Colors.END}")
        save_start = time.time()
        engine.save()
        save_time = time.time() - save_start
        disk_usage = self.get_disk_mb(storage)
        self.print_status("✅", f"Saved in {save_time:.2f}s ({disk_usage:.2f} MB)", Colors.GREEN)
        
        # Create result (stats are nested under 'system_info')
        system_info = stats.get('system_info', stats)  # Handle both nested and flat formats
        result = WikiResult(
            operation="wikipedia_learn",
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
    
    def generate_questions_from_articles(self, articles: List[Dict[str, str]], num_questions: int = 100) -> List[str]:
        """
        Generate diverse, high-quality questions based on the Wikipedia articles we learned from.
        
        Uses random sampling to create exactly the requested number of questions
        with good variety and coverage of different topics.
        """
        import random
        random.seed(42)  # For reproducible results
        
        questions = []
        
        # Sample articles to generate questions from (use more articles for diversity)
        sample_size = min(num_questions * 2, len(articles))  # Sample more articles than questions needed
        sampled_articles = random.sample(articles, sample_size)
        
        # Question templates for variety
        question_templates = [
            "What is {title}?",
            "Tell me about {title}",
            "What do you know about {title}?",
            "Explain {title}",
            "Describe {title}",
            "What are the key facts about {title}?",
            "What is the main topic of {title}?",
            "Can you summarize {title}?",
            "What information do you have about {title}?",
            "How would you describe {title}?",
        ]
        
        print(f"Generating {num_questions} questions from {len(sampled_articles)} sampled articles...")
        
        for article in sampled_articles:
            if len(questions) >= num_questions:
                break
                
            title = article['title']
            text = article['text']
            
            # Generate primary question using random template
            template = random.choice(question_templates)
            questions.append(template.format(title=title))
            
            if len(questions) >= num_questions:
                break
            
            # Generate content-based questions for variety
            if 'is a' in text.lower() or 'was a' in text.lower():
                questions.append(f"What type of thing is {title}?")
            elif 'located' in text.lower() or 'situated' in text.lower():
                questions.append(f"Where is {title} located?")
            elif any(word in text.lower() for word in ['founded', 'established', 'created', 'invented']):
                questions.append(f"When was {title} founded or established?")
            elif any(word in text.lower() for word in ['born', 'died', 'lived']):
                questions.append(f"What do you know about the life of {title}?")
            else:
                # Fallback to another template
                if len(questions) < num_questions:
                    questions.append(f"What are the main characteristics of {title}?")
            
            if len(questions) >= num_questions:
                break
        
        # If we don't have enough questions, add some generic ones
        if len(questions) < num_questions:
            generic_questions = [
                "What information is available?",
                "Describe the main topics you know about",
                "What are some interesting facts?",
                "Tell me about something educational",
                "What knowledge do you have?",
                "Share some information",
                "What can you tell me?",
            ]
            questions.extend(generic_questions[:num_questions - len(questions)])
        
        # Randomize and trim to exact number requested
        random.shuffle(questions)
        questions = questions[:num_questions]
        
        print(f"✓ Generated {len(questions)} diverse questions")
        return questions
        
    def benchmark_question_answering(
        self, 
        engine: ReasoningEngine,  # Use existing engine instead of loading
        articles: List[Dict[str, str]],  # Pass articles to generate relevant questions
        test_questions: Optional[List[str]] = None
    ) -> WikiResult:
        """
        Benchmark question answering on learned Wikipedia knowledge.
        """
        self.print_section("🔍 TEST 2: QUESTION ANSWERING ON WIKIPEDIA KNOWLEDGE")
        
        # Use provided engine (already has learned knowledge and vectors)
        self.print_status("📂", "Loading knowledge base...")
        # No need to create new engine - reuse the learning engine
        stats = engine.get_system_stats()
        system_info = stats.get('system_info', stats)  # Handle both nested and flat formats
        self.print_metric("Concepts loaded", f"{system_info.get('total_concepts', len(engine.concepts)):,}")
        self.print_metric("Associations loaded", f"{system_info.get('total_associations', len(engine.associations)):,}")
        
        # Generate relevant test questions if none provided
        if test_questions is None:
            num_qa_samples = 100  # Default to 100 Q&A samples for efficient testing
            test_questions = self.generate_questions_from_articles(articles, num_qa_samples)
            print(f"\n{Colors.CYAN}🤔 Generated {len(test_questions)} questions from learned content:{Colors.END}")
            for i, question in enumerate(test_questions[:5], 1):  # Show first 5 as examples
                print(f"  {i}. {question}")
            if len(test_questions) > 5:
                print(f"  ... and {len(test_questions) - 5} more questions")
        else:
            print(f"\n{Colors.CYAN}🤔 Using provided test questions{Colors.END}")
        
        self.print_status("❓", f"Testing with {len(test_questions)} questions...")
        
        # Run queries
        print(f"\n{Colors.YELLOW}🚀 Running queries...{Colors.END}")
        results_list = []
        self.start_time = time.time()
        total_start = time.time()
        
        for i, question in enumerate(test_questions):
            try:
                query_start = time.time()
                result = engine.ask(question, num_reasoning_paths=3)
                query_time = (time.time() - query_start) * 1000
                
                results_list.append({
                    'question': question,
                    'answer': result.primary_answer,
                    'confidence': result.confidence,
                    'time_ms': query_time,
                    'num_sources': len(result.supporting_paths)
                })
                
            except Exception as e:
                results_list.append({
                    'question': question,
                    'answer': f"Error: {e}",
                    'confidence': 0.0,
                    'time_ms': 0,
                    'num_sources': 0
                })
            
            self.animated_progress(i + 1, len(test_questions), "Progress")
        
        total_time = time.time() - total_start
        
        # Calculate stats
        avg_confidence = np.mean([r['confidence'] for r in results_list])
        avg_query_time = np.mean([r['time_ms'] for r in results_list])
        
        # Print sample results
        print(f"\n{Colors.GREEN}📊 Sample Results:{Colors.END}\n")
        for r in results_list[:3]:
            print(f"{Colors.CYAN}Q:{Colors.END} {r['question']}")
            print(f"{Colors.GREEN}A:{Colors.END} {r['answer'][:200]}...")
            print(f"{Colors.YELLOW}Confidence:{Colors.END} {r['confidence']:.2f} | "
                  f"{Colors.BLUE}Time:{Colors.END} {r['time_ms']:.1f}ms | "
                  f"{Colors.CYAN}Sources:{Colors.END} {r['num_sources']}\n")
        
        result = WikiResult(
            operation="wikipedia_qa",
            num_articles=len(test_questions),
            total_time=total_time,
            throughput=len(test_questions) / total_time,
            avg_article_length=0,
            total_concepts=system_info.get('total_concepts', len(engine.concepts)),
            total_associations=system_info.get('total_associations', len(engine.associations)),
            memory_mb=0,
            disk_mb=0,
            success_count=sum(1 for r in results_list if r['confidence'] > 0),
            error_count=sum(1 for r in results_list if r['confidence'] == 0),
            sample_queries=results_list
        )
        
        self.print_metric("Average confidence", f"{avg_confidence:.2f}")
        self.print_metric("Average query time", f"{avg_query_time:.1f} ms")
        self.print_metric("Success rate", f"{result.success_count}/{len(test_questions)}")
        
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
    
    def save_results(self, num_articles: int):
        """Save results to JSON file."""
        results_dict = {
            "test_type": "wikipedia_real_world",
            "timestamp": time.time(),
            "num_articles": num_articles,
            "system_info": {
                "platform": os.uname().sysname,
                "cpus": psutil.cpu_count(),
                "memory_gb": psutil.virtual_memory().total / (1024**3)
            },
            "results": [asdict(r) for r in self.results]
        }
        
        filename = self.output_dir / f"wikipedia_{num_articles}_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        self.print_status("💾", f"Results saved to: {filename}", Colors.CYAN)


def main():
    """Run the Wikipedia performance test suite."""
    tester = WikipediaPerformanceTester()
    
    # Get number of articles from command line
    if len(sys.argv) > 1:
        num_articles = int(sys.argv[1])
    else:
        print(f"{Colors.CYAN}Usage: python wikipedia_performance_suite.py <num_articles>{Colors.END}")
        print(f"{Colors.CYAN}Examples:{Colors.END}")
        print(f"  python wikipedia_performance_suite.py 1000     # Quick test (1k articles)")
        print(f"  python wikipedia_performance_suite.py 10000    # Standard test (10k articles)")
        print(f"  python wikipedia_performance_suite.py 50000    # Large test (50k articles)")
        print(f"  python wikipedia_performance_suite.py 100000   # Comprehensive test (100k articles)")
        print(f"\n{Colors.YELLOW}Running with default: 10,000 articles for comprehensive knowledge{Colors.END}\n")
        num_articles = 10000  # Better default for comprehensive knowledge
    
    # Print header
    tester.print_header("🌍 WIKIPEDIA REAL-WORLD PERFORMANCE TEST 🌍")
    
    print(f"{Colors.CYAN}System Configuration:{Colors.END}")
    tester.print_metric("Platform", os.uname().sysname)
    tester.print_metric("CPU Cores", str(psutil.cpu_count()))
    tester.print_metric("Total Memory", f"{psutil.virtual_memory().total / (1024**3):.1f} GB")
    tester.print_metric("Test Scale", f"{num_articles:,} Wikipedia articles")
    
    if not HF_AVAILABLE:
        print(f"\n{Colors.RED}❌ Hugging Face datasets not installed!{Colors.END}")
        print(f"{Colors.YELLOW}Install with: pip install datasets{Colors.END}\n")
        return
    
    # Check for HF token
    if tester.hf_token:
        tester.print_status("🔑", "Hugging Face token found", Colors.GREEN)
    else:
        print(f"\n{Colors.YELLOW}💡 Tip: Set HF_TOKEN environment variable to avoid rate limits{Colors.END}")
        print(f"{Colors.YELLOW}   export HF_TOKEN='your_token_here'{Colors.END}\n")
    
    try:
        # Test 1: Learn from Wikipedia
        learning_result, learned_engine, articles = tester.benchmark_wikipedia_learning(
            num_articles=num_articles,
            storage_path="./wiki_knowledge"
        )
        
        # Test 2: Question Answering (reuse the same engine to preserve vectors)
        qa_result = tester.benchmark_question_answering(
            engine=learned_engine,
            articles=articles
        )
        
        # Save results
        tester.save_results(num_articles)
        
        # Final summary
        tester.print_header("✨ WIKIPEDIA TEST COMPLETE! ✨")
        print(f"{Colors.GREEN}📊 Summary:{Colors.END}\n")
        tester.print_metric("Articles learned", f"{learning_result.num_articles:,}")
        tester.print_metric("Concepts created", f"{learning_result.total_concepts:,}")
        tester.print_metric("Associations formed", f"{learning_result.total_associations:,}")
        tester.print_metric("Learning throughput", f"{learning_result.throughput:.1f} articles/sec")
        tester.print_metric("QA queries tested", f"{qa_result.num_articles}")
        tester.print_metric("QA throughput", f"{qa_result.throughput:.1f} queries/sec")
        
        print(f"\n{Colors.GREEN}🎉 All tests completed successfully!{Colors.END}\n")
        
    except Exception as e:
        print(f"\n{Colors.RED}❌ Test failed: {e}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
