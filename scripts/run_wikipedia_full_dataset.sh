#!/bin/bash

# Wikipedia Full Dataset Download and Test Script
# This script downloads the entire Wikipedia EN dataset and tests with random 100 Q&A samples

echo "🌍 Wikipedia Full Dataset Download and Performance Test"
echo "=================================================="

# Set the Hugging Face token (make sure it's set in environment)
if [ -z "$HF_TOKEN" ]; then
    echo "❌ Error: HF_TOKEN environment variable is not set!"
    echo "Please set your Hugging Face token:"
    echo "export HF_TOKEN=\"your_token_here\""
    exit 1
fi

echo "✅ Hugging Face token is set"

# Remove existing knowledge base for fresh start
echo "🧹 Cleaning existing knowledge base..."
rm -rf wiki_knowledge 2>/dev/null
echo "✅ Cleaned wiki_knowledge directory"

# Determine number of articles to download
NUM_ARTICLES=${1:-10000}  # Default to 10k articles if not specified
echo "📥 Will download up to $NUM_ARTICLES Wikipedia articles"

# Run the Wikipedia performance suite
echo "🚀 Starting Wikipedia performance test..."
echo "This will:"
echo "  1. Download up to $NUM_ARTICLES high-quality Wikipedia articles"
echo "  2. Learn from all articles and build comprehensive knowledge base"
echo "  3. Test with 100 random Q&A samples"
echo "  4. Save results and performance metrics"
echo ""

# Run with proper Python environment
python scripts/wikipedia_performance_suite.py $NUM_ARTICLES

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Wikipedia test completed successfully!"
    echo ""
    echo "📊 Knowledge base created in: ./wiki_knowledge/"
    
    # Show knowledge base size
    if [ -d "wiki_knowledge" ]; then
        KB_SIZE=$(du -sh wiki_knowledge | cut -f1)
        echo "💾 Knowledge base size: $KB_SIZE"
    fi
    
    echo ""
    echo "🧪 Test the knowledge base:"
    echo "python -c \"from sutra_core.reasoning.engine import ReasoningEngine; engine = ReasoningEngine('./wiki_knowledge'); print(engine.ask('What is artificial intelligence?'))\""
    echo ""
else
    echo ""
    echo "❌ Wikipedia test failed!"
    echo "Check the output above for error details."
    exit 1
fi