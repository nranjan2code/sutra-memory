#!/usr/bin/env python3
"""
Continuous Learning Benchmark with Ollama-Generated Dataset

This script demonstrates Sutra's continuous learning capabilities by:
1. Generating realistic knowledge using local Ollama (granite4)
2. Feeding knowledge incrementally to Sutra
3. Testing retrieval and reasoning on learned knowledge
4. Benchmarking at scale (10K-1M concepts)

Usage:
    python continuous_learning_benchmark.py --scale 10000 --batch-size 100
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# Add sutra-core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sutra-core"))

try:
    import requests
    from sutra_core.reasoning.engine import ReasoningEngine
except ImportError as e:
    print(f"❌ Error importing dependencies: {e}")
    print("Install with: pip install requests")
    sys.exit(1)


class OllamaKnowledgeGenerator:
    """Generate realistic knowledge using local Ollama."""
    
    def __init__(self, model: str = "granite4:latest", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.session = requests.Session()
        self._verify_ollama()
    
    def _verify_ollama(self):
        """Verify Ollama is running and model is available."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            
            if not any(m["name"] == self.model for m in models):
                print(f"⚠️  Model {self.model} not found. Available models:")
                for m in models:
                    print(f"   - {m['name']}")
                sys.exit(1)
            
            print(f"✅ Connected to Ollama - Model: {self.model}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to Ollama at {self.base_url}")
            print(f"   Error: {e}")
            print("\nMake sure Ollama is running:")
            print("   ollama serve")
            sys.exit(1)
    
    def generate_knowledge_batch(self, topic: str, count: int = 10) -> List[str]:
        """
        Generate a batch of knowledge statements about a topic.
        
        Args:
            topic: Subject area (e.g., "science", "history", "technology")
            count: Number of statements to generate
            
        Returns:
            List of knowledge statements
        """
        prompt = f"""Generate {count} distinct, factual statements about {topic}.
Each statement should be:
- A single, clear fact or concept
- 1-2 sentences long
- Educational and informative
- Diverse (cover different aspects)

Format: One statement per line, numbered 1-{count}.

Example for "artificial intelligence":
1. Machine learning is a subset of AI that enables systems to learn from data without explicit programming.
2. Neural networks are inspired by biological neurons and consist of interconnected layers of nodes.
3. Natural language processing allows computers to understand and generate human language.

Now generate {count} statements about {topic}:"""

        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            
            # Parse response
            text = response.json()["response"]
            
            # Extract numbered statements
            statements = []
            for line in text.split("\n"):
                line = line.strip()
                # Remove numbering (1., 2., etc.)
                if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                    # Remove leading number/bullet and clean
                    cleaned = line.lstrip("0123456789.-*) ").strip()
                    if len(cleaned) > 20:  # Filter out noise
                        statements.append(cleaned)
            
            return statements[:count]  # Ensure we don't exceed count
            
        except Exception as e:
            print(f"⚠️  Error generating knowledge: {e}")
            return []
    
    def generate_diverse_dataset(self, target_size: int, batch_size: int = 10) -> List[Dict[str, str]]:
        """
        Generate a diverse dataset covering multiple topics.
        
        Args:
            target_size: Total number of concepts to generate
            batch_size: Concepts per Ollama call
            
        Returns:
            List of {topic, content} dicts
        """
        topics = [
            "artificial intelligence", "machine learning", "quantum physics",
            "molecular biology", "climate science", "astronomy",
            "ancient history", "world war 2", "renaissance art",
            "economics", "psychology", "philosophy",
            "computer science", "mathematics", "chemistry",
            "neuroscience", "genetics", "ecology",
            "political science", "sociology", "linguistics",
            "architecture", "music theory", "literature"
        ]
        
        dataset = []
        concepts_per_topic = max(1, target_size // len(topics))
        
        print(f"\n🎨 Generating diverse dataset:")
        print(f"   Topics: {len(topics)}")
        print(f"   Concepts per topic: ~{concepts_per_topic}")
        print(f"   Target total: {target_size}\n")
        
        for topic in topics:
            if len(dataset) >= target_size:
                break
            
            print(f"📚 Generating knowledge about {topic}...", end=" ", flush=True)
            
            # Generate multiple batches for this topic
            topic_concepts = []
            while len(topic_concepts) < concepts_per_topic:
                batch = self.generate_knowledge_batch(topic, min(batch_size, concepts_per_topic - len(topic_concepts)))
                topic_concepts.extend(batch)
                
                if not batch:  # Failed to generate
                    break
            
            # Add to dataset with metadata
            for content in topic_concepts:
                dataset.append({
                    "topic": topic,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
            
            print(f"✅ {len(topic_concepts)} concepts")
            
            if len(dataset) >= target_size:
                break
        
        print(f"\n✅ Generated {len(dataset)} total concepts\n")
        return dataset[:target_size]


class ContinuousLearningBenchmark:
    """Benchmark continuous learning with real knowledge."""
    
    def __init__(self, storage_path: str = "./continuous_learning_db"):
        self.storage_path = storage_path
        self.engine = None
        self.metrics = {
            "learning": [],
            "queries": [],
            "batch_times": []
        }
    
    def initialize_engine(self):
        """Initialize Sutra reasoning engine with batch processing."""
        print("🔧 Initializing Sutra ReasoningEngine with MPS batch support...")
        start = time.time()
        
        self.engine = ReasoningEngine(
            storage_path=self.storage_path,
            use_rust_storage=True,
            enable_caching=True,
            enable_vector_index=True,
            enable_batch_embeddings=True,  # NEW: Enable batch embeddings with MPS
            embedding_model="all-MiniLM-L6-v2",
            mps_batch_threshold=64,  # Use MPS for batches >= 64
        )
        
        init_time = time.time() - start
        print(f"✅ Engine ready in {init_time:.2f}s")
        
        # Report if MPS is being used
        if self.engine.embedding_batch_processor:
            print(f"   🚀 Batch embedding processor active (MPS threshold: 64)")
        
        print()
        return init_time
    
    def learn_batch(self, concepts: List[Dict[str, str]], batch_num: int = 0) -> Dict:
        """Learn a batch of concepts using new batch API for better performance."""
        start = time.time()
        
        # Prepare batch data for new API
        batch_data = [
            (concept["content"], concept["topic"], concept["topic"])
            for concept in concepts
        ]
        
        try:
            # Use new batch learning API (3-10x faster!)
            concept_ids = self.engine.learn_batch(batch_data)
            successful = len(concept_ids)
            errors = len(concepts) - successful
        except Exception as e:
            print(f"⚠️  Batch learning error: {e}")
            # Fallback to sequential learning if batch fails
            successful = 0
            errors = 0
            for concept in concepts:
                try:
                    self.engine.learn(
                        concept["content"],
                        source=concept["topic"],
                        category=concept["topic"]
                    )
                    successful += 1
                except Exception as e2:
                    errors += 1
                    if errors <= 3:
                        print(f"⚠️  Error learning concept: {e2}")
        
        elapsed = time.time() - start
        throughput = successful / elapsed if elapsed > 0 else 0
        
        metrics = {
            "batch_num": batch_num,
            "count": len(concepts),
            "successful": successful,
            "errors": errors,
            "time": elapsed,
            "throughput": throughput,
            "avg_latency_ms": (elapsed / successful * 1000) if successful > 0 else 0
        }
        
        self.metrics["learning"].append(metrics)
        return metrics
    
    def test_retrieval(self, test_queries: List[str]) -> Dict:
        """Test knowledge retrieval on learned concepts."""
        print("\n🔍 Testing knowledge retrieval...")
        
        results = {
            "total_queries": len(test_queries),
            "successful": 0,
            "empty_results": 0,
            "avg_results_per_query": 0,
            "total_time": 0,
            "throughput": 0
        }
        
        start = time.time()
        total_results = 0
        
        for query in test_queries:
            try:
                # Use ask() method which returns ConsensusResult
                query_result = self.engine.ask(query, num_reasoning_paths=3)
                if query_result and query_result.primary_answer:
                    results["successful"] += 1
                    total_results += len(query_result.supporting_paths) if query_result.supporting_paths else 1
                else:
                    results["empty_results"] += 1
            except Exception as e:
                print(f"⚠️  Query error: {e}")
        
        elapsed = time.time() - start
        results["total_time"] = elapsed
        results["throughput"] = len(test_queries) / elapsed if elapsed > 0 else 0
        results["avg_results_per_query"] = total_results / len(test_queries) if test_queries else 0
        
        return results
    
    def run_continuous_learning_benchmark(
        self, 
        dataset: List[Dict[str, str]], 
        batch_size: int = 100,
        test_every: int = 1000
    ):
        """
        Run continuous learning benchmark with incremental batches.
        
        Args:
            dataset: List of concepts to learn
            batch_size: Concepts per batch
            test_every: Test retrieval every N concepts
        """
        total_concepts = len(dataset)
        num_batches = (total_concepts + batch_size - 1) // batch_size
        
        print("="*80)
        print("🚀 CONTINUOUS LEARNING BENCHMARK")
        print("="*80)
        print(f"Dataset size: {total_concepts:,} concepts")
        print(f"Batch size: {batch_size}")
        print(f"Number of batches: {num_batches}")
        print(f"Test frequency: every {test_every:,} concepts")
        print("="*80 + "\n")
        
        # Initialize engine
        self.initialize_engine()
        
        # Learn in batches
        learned_count = 0
        overall_start = time.time()
        
        for batch_num in range(num_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, total_concepts)
            batch = dataset[start_idx:end_idx]
            
            # Learn batch
            print(f"📖 Batch {batch_num + 1}/{num_batches} "
                  f"({start_idx+1}-{end_idx}/{total_concepts}): ", end="", flush=True)
            
            metrics = self.learn_batch(batch, batch_num + 1)
            learned_count += metrics["successful"]
            
            print(f"✅ {metrics['throughput']:.1f} concepts/sec "
                  f"({metrics['avg_latency_ms']:.1f}ms avg latency)")
            
            # Test retrieval periodically
            if learned_count % test_every < batch_size or learned_count == total_concepts:
                test_queries = [
                    "What is artificial intelligence?",
                    "Explain quantum physics",
                    "Tell me about climate change",
                    "What happened in World War 2?",
                    "How does machine learning work?"
                ]
                retrieval_metrics = self.test_retrieval(test_queries)
                print(f"   📊 Retrieval test: {retrieval_metrics['successful']}/{retrieval_metrics['total_queries']} "
                      f"queries successful, {retrieval_metrics['avg_results_per_query']:.1f} results/query\n")
        
        overall_elapsed = time.time() - overall_start
        
        # Final summary
        print("\n" + "="*80)
        print("📊 BENCHMARK RESULTS SUMMARY")
        print("="*80)
        print(f"Total concepts learned: {learned_count:,}")
        print(f"Total time: {overall_elapsed:.2f}s ({overall_elapsed/60:.1f} minutes)")
        print(f"Overall throughput: {learned_count/overall_elapsed:.1f} concepts/sec")
        print(f"Average latency: {(overall_elapsed/learned_count)*1000:.1f}ms per concept")
        
        # Embedding processor statistics
        if self.engine.embedding_batch_processor:
            print("\n" + "="*80)
            print("🚀 BATCH EMBEDDING PROCESSOR STATS")
            print("="*80)
            stats = self.engine.embedding_batch_processor.get_stats()
            print(f"Total embeddings generated: {stats['total_embeddings']:,}")
            print(f"Embedding generation time: {stats['total_time']:.2f}s")
            print(f"Batch count: {stats['batch_count']}")
            print(f"Average throughput: {stats['avg_throughput']:.1f} texts/sec")
            print(f"Cache hits: {stats['cache_hits']:,}")
            print(f"Cache misses: {stats['cache_misses']:,}")
            print(f"Cache hit rate: {stats['cache_hit_rate']:.1f}%")
            print(f"Cache size: {stats['cache_size']:,} embeddings")
        
        # Save detailed metrics
        self.save_results(learned_count, overall_elapsed)
        
        return {
            "total_learned": learned_count,
            "total_time": overall_elapsed,
            "throughput": learned_count / overall_elapsed,
            "batches": self.metrics["learning"]
        }
    
    def save_results(self, total_concepts: int, total_time: float):
        """Save benchmark results to JSON."""
        results_dir = Path(__file__).parent.parent / "performance_results"
        results_dir.mkdir(exist_ok=True)
        
        timestamp = int(time.time())
        filename = results_dir / f"continuous_learning_{total_concepts}_{timestamp}.json"
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_concepts": total_concepts,
            "total_time_seconds": total_time,
            "overall_throughput": total_concepts / total_time,
            "batches": self.metrics["learning"]
        }
        
        with open(filename, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="Continuous Learning Benchmark with Ollama-Generated Dataset"
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=10000,
        help="Number of concepts to generate and learn (default: 10000)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Concepts per batch (default: 100)"
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama API URL (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="granite4:latest",
        help="Ollama model to use (default: granite4:latest)"
    )
    parser.add_argument(
        "--use-cached",
        action="store_true",
        help="Use cached dataset if available"
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("🧠 SUTRA CONTINUOUS LEARNING BENCHMARK")
    print("="*80)
    print(f"Scale: {args.scale:,} concepts")
    print(f"Batch size: {args.batch_size}")
    print(f"Model: {args.model}")
    print("="*80 + "\n")
    
    # Check for cached dataset
    cache_file = Path(__file__).parent.parent / f"dataset_cache_{args.scale}.json"
    
    if args.use_cached and cache_file.exists():
        print(f"📦 Loading cached dataset from {cache_file}...")
        with open(cache_file) as f:
            dataset = json.load(f)
        print(f"✅ Loaded {len(dataset)} concepts from cache\n")
    else:
        # Generate dataset using Ollama
        generator = OllamaKnowledgeGenerator(model=args.model, base_url=args.ollama_url)
        dataset = generator.generate_diverse_dataset(args.scale, batch_size=10)
        
        # Cache for future use
        print(f"💾 Caching dataset to {cache_file}...")
        with open(cache_file, "w") as f:
            json.dump(dataset, f, indent=2)
        print("✅ Dataset cached\n")
    
    # Run benchmark
    benchmark = ContinuousLearningBenchmark(
        storage_path=f"./continuous_learning_{args.scale}"
    )
    
    results = benchmark.run_continuous_learning_benchmark(
        dataset,
        batch_size=args.batch_size,
        test_every=1000
    )
    
    print("\n✨ Benchmark complete!")
    print(f"   Learned: {results['total_learned']:,} concepts")
    print(f"   Throughput: {results['throughput']:.1f} concepts/sec")
    print(f"   Time: {results['total_time']/60:.1f} minutes\n")


if __name__ == "__main__":
    main()
