#!/usr/bin/env python3
"""
Production-level Wikipedia dataset ingestion using validated production fixes.

This script processes the pre-downloaded Wikipedia dataset file and ingests it
into the Sutra AI knowledge system using our production-level batch learning
with comprehensive error handling and monitoring.
"""

import json
import logging
import time
import gc
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Any
import re

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/nisheethranjan/Projects/sutra-models/wikipedia_ingestion.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def parse_wikipedia_text_file(file_path: str, max_articles: int = None) -> List[Tuple[str, str, str]]:
    """
    Parse the Wikipedia text file into structured articles.
    
    Args:
        file_path: Path to the Wikipedia text file
        max_articles: Maximum number of articles to process (for testing)
        
    Returns:
        List of (content, source, category) tuples
    """
    logger.info(f"📚 Parsing Wikipedia dataset from {file_path}")
    
    articles = []
    current_title = None
    current_content = []
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line:
                    # Empty line might indicate article boundary
                    if current_title and current_content:
                        # Process completed article
                        content = ' '.join(current_content).strip()
                        if len(content) > 50:  # Minimum content length
                            articles.append((
                                content,
                                f"Wikipedia: {current_title}",
                                "encyclopedia"
                            ))
                            
                            if max_articles and len(articles) >= max_articles:
                                break
                        
                        # Reset for next article
                        current_title = None
                        current_content = []
                    continue
                
                # Check if this line looks like a title (short line, often capitalized)
                if (len(line) < 100 and 
                    not line.startswith((' ', '\t')) and 
                    not current_content and
                    not line.endswith('.') and
                    len(line.split()) <= 8):
                    current_title = line
                    logger.debug(f"Found article title: {current_title}")
                else:
                    # This is content
                    if current_title:
                        current_content.append(line)
                
                # Progress logging
                if line_num % 50000 == 0:
                    logger.info(f"📖 Processed {line_num:,} lines, found {len(articles):,} articles")
        
        # Handle the last article
        if current_title and current_content:
            content = ' '.join(current_content).strip()
            if len(content) > 50:
                articles.append((
                    content,
                    f"Wikipedia: {current_title}",
                    "encyclopedia"
                ))
    
    except Exception as e:
        logger.error(f"Error parsing Wikipedia file: {e}")
        raise
    
    logger.info(f"✅ Parsed {len(articles):,} articles from Wikipedia dataset")
    return articles

def clean_and_filter_articles(articles: List[Tuple[str, str, str]], 
                            min_length: int = 100,
                            max_length: int = 5000) -> List[Tuple[str, str, str]]:
    """
    Clean and filter articles for quality.
    
    Args:
        articles: Raw articles list
        min_length: Minimum content length
        max_length: Maximum content length
        
    Returns:
        Filtered and cleaned articles
    """
    logger.info(f"🧹 Cleaning and filtering {len(articles):,} articles")
    
    cleaned = []
    
    for content, source, category in articles:
        # Clean content
        content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
        content = re.sub(r'[^\w\s\.,;:!?\-()"\']', '', content)  # Remove special chars
        content = content.strip()
        
        # Filter by length and quality
        if (min_length <= len(content) <= max_length and 
            len(content.split()) >= 20 and  # At least 20 words
            content.count('.') >= 1):  # At least one sentence
            cleaned.append((content, source, category))
    
    logger.info(f"✅ Kept {len(cleaned):,} high-quality articles ({len(cleaned)/len(articles)*100:.1f}%)")
    return cleaned

def ingest_wikipedia_with_production_fixes():
    """
    Main Wikipedia ingestion using production-level fixes.
    """
    
    logger.info("🚀 WIKIPEDIA INGESTION WITH PRODUCTION FIXES")
    logger.info("=" * 70)
    
    # Configuration
    WIKIPEDIA_FILE = "/Users/nisheethranjan/Projects/sutra-models/dataset/wikipedia.txt"
    KNOWLEDGE_BASE_PATH = "/Users/nisheethranjan/Projects/sutra-models/wikipedia_knowledge_production"
    BATCH_SIZE = 100  # Optimized batch size for production
    MEMORY_CLEANUP_INTERVAL = 5  # Clean memory every 5 batches
    MAX_ARTICLES = None  # None = process all articles
    
    # Import after logging setup
    from sutra_core.reasoning.engine import ReasoningEngine
    
    # Initialize reasoning engine with production settings
    logger.info("🔧 Initializing Sutra AI Reasoning Engine...")
    
    engine = ReasoningEngine(
        storage_path=KNOWLEDGE_BASE_PATH,
        enable_vector_index=True,
        enable_caching=True,
        use_rust_storage=True,
        enable_batch_embeddings=True,
        enable_parallel_associations=True,
        association_workers=4,
        # Production optimizations
        max_cache_size=10000,  # Large cache for production
        embedding_model="all-MiniLM-L6-v2",
        mps_batch_threshold=32  # Use Apple Silicon GPU for efficiency
    )
    
    logger.info("✅ Reasoning engine initialized")
    
    # Step 1: Parse Wikipedia dataset
    logger.info("\n📚 STEP 1: Parsing Wikipedia Dataset")
    start_time = time.time()
    
    try:
        articles = parse_wikipedia_text_file(WIKIPEDIA_FILE, MAX_ARTICLES)
        parse_duration = time.time() - start_time
        logger.info(f"✅ Parsing completed in {parse_duration:.2f}s")
        
    except Exception as e:
        logger.error(f"❌ Failed to parse Wikipedia dataset: {e}")
        return False
    
    # Step 2: Clean and filter articles
    logger.info("\n🧹 STEP 2: Cleaning and Filtering Articles")
    start_time = time.time()
    
    try:
        filtered_articles = clean_and_filter_articles(articles)
        filter_duration = time.time() - start_time
        logger.info(f"✅ Filtering completed in {filter_duration:.2f}s")
        
        if len(filtered_articles) == 0:
            logger.error("❌ No articles remaining after filtering")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to filter articles: {e}")
        return False
    
    # Step 3: Production-level batch ingestion
    logger.info("\n🏭 STEP 3: Production Batch Learning")
    logger.info(f"📊 Processing {len(filtered_articles):,} articles in batches of {BATCH_SIZE}")
    
    ingestion_start = time.time()
    
    try:
        learned_concepts = engine.learn_batch(
            contents=filtered_articles,
            batch_size=BATCH_SIZE,
            memory_cleanup_interval=MEMORY_CLEANUP_INTERVAL,
            fail_on_error=False  # Continue on individual failures but log them
        )
        
        ingestion_duration = time.time() - ingestion_start
        
        # Calculate statistics
        success_rate = len(learned_concepts) / len(filtered_articles) * 100
        ingestion_rate = len(learned_concepts) / ingestion_duration
        
        logger.info(f"\n🎯 INGESTION COMPLETE!")
        logger.info(f"📊 Statistics:")
        logger.info(f"   • Total articles processed: {len(filtered_articles):,}")
        logger.info(f"   • Successfully learned: {len(learned_concepts):,}")
        logger.info(f"   • Success rate: {success_rate:.1f}%")
        logger.info(f"   • Processing time: {ingestion_duration:.2f}s")
        logger.info(f"   • Ingestion rate: {ingestion_rate:.1f} articles/sec")
        
        if success_rate < 90:
            logger.warning(f"⚠️ Success rate below 90%: {success_rate:.1f}%")
        else:
            logger.info(f"✅ Excellent success rate: {success_rate:.1f}%")
        
    except Exception as e:
        logger.error(f"❌ Batch learning failed: {e}")
        return False
    
    # Step 4: System validation
    logger.info("\n🔍 STEP 4: System Validation")
    
    try:
        # Get system statistics
        stats = engine.get_system_stats()
        
        logger.info(f"📈 Final System Statistics:")
        logger.info(f"   • Total concepts: {stats.get('total_concepts', 0):,}")
        logger.info(f"   • Total associations: {stats.get('total_associations', 0):,}")
        logger.info(f"   • Vector index size: {stats.get('vector_index_size', 0):,}")
        
        # Test a sample query
        logger.info("\n🧪 Testing sample queries...")
        test_queries = [
            "What is April?",
            "Tell me about the fourth month",
            "How many days does April have?"
        ]
        
        for query in test_queries:
            try:
                result = engine.ask(query)
                if result and hasattr(result, 'answer') and result.answer:
                    logger.info(f"✅ Query '{query}' → Answer found")
                else:
                    logger.warning(f"⚠️ Query '{query}' → No answer")
            except Exception as e:
                logger.warning(f"⚠️ Query '{query}' → Error: {e}")
        
        # Memory cleanup
        gc.collect()
        
        # Storage validation
        storage_path = Path(KNOWLEDGE_BASE_PATH)
        if storage_path.exists():
            storage_size = sum(f.stat().st_size for f in storage_path.rglob('*') if f.is_file())
            storage_mb = storage_size / 1024 / 1024
            logger.info(f"💾 Knowledge base storage: {storage_mb:.1f} MB")
        
        logger.info("\n🎉 WIKIPEDIA INGESTION SUCCESSFUL!")
        logger.info(f"🚀 Knowledge base ready at: {KNOWLEDGE_BASE_PATH}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ System validation failed: {e}")
        return False

def main():
    """Main execution function."""
    
    try:
        success = ingest_wikipedia_with_production_fixes()
        
        if success:
            print("\n🎉 SUCCESS: Wikipedia dataset ingested successfully!")
            print("The production-level Sutra AI knowledge base is ready.")
            sys.exit(0)
        else:
            print("\n❌ FAILURE: Wikipedia ingestion failed.")
            print("Check the logs for detailed error information.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        print(f"\n💥 CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()