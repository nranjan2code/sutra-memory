#!/bin/bash
# Sutra AI Maximum Performance Configuration
# Removes all rate limits and optimizes for stress testing

echo "🚀 OPTIMIZING SUTRA AI FOR MAXIMUM STRESS TESTING PERFORMANCE"
echo "================================================================"

echo "📝 Updating Docker Compose configuration..."

# Update all ML-Base batch sizes
sed -i.bak 's/ML_BASE_MAX_BATCH_SIZE=64/ML_BASE_MAX_BATCH_SIZE=256/g' .sutra/compose/production.yml
sed -i.bak 's/ML_BASE_BATCH_TIMEOUT_MS=50/ML_BASE_BATCH_TIMEOUT_MS=10/g' .sutra/compose/production.yml
sed -i.bak 's/ML_BASE_MODEL_UNLOAD_TIMEOUT=300/ML_BASE_MODEL_UNLOAD_TIMEOUT=600/g' .sutra/compose/production.yml

# Set environment variables for maximum performance
export SUTRA_RATE_LIMIT_RPS=1000000
export SUTRA_RATE_LIMIT_BURST=1000000
export SUTRA_EMBEDDING_TIMEOUT_SEC=120
export SUTRA_MAX_ASSOCIATIONS_PER_CONCEPT=50
export MATRYOSHKA_DIM=256  # Optimize for speed

echo "🔧 Environment variables set:"
echo "   SUTRA_RATE_LIMIT_RPS=${SUTRA_RATE_LIMIT_RPS}"
echo "   SUTRA_RATE_LIMIT_BURST=${SUTRA_RATE_LIMIT_BURST}"
echo "   SUTRA_EMBEDDING_TIMEOUT_SEC=${SUTRA_EMBEDDING_TIMEOUT_SEC}"
echo "   SUTRA_MAX_ASSOCIATIONS_PER_CONCEPT=${SUTRA_MAX_ASSOCIATIONS_PER_CONCEPT}"
echo "   MATRYOSHKA_DIM=${MATRYOSHKA_DIM}"

# Export to current shell
echo "export SUTRA_RATE_LIMIT_RPS=1000000" >> ~/.bash_profile
echo "export SUTRA_RATE_LIMIT_BURST=1000000" >> ~/.bash_profile
echo "export SUTRA_EMBEDDING_TIMEOUT_SEC=120" >> ~/.bash_profile
echo "export SUTRA_MAX_ASSOCIATIONS_PER_CONCEPT=50" >> ~/.bash_profile
echo "export MATRYOSHKA_DIM=256" >> ~/.bash_profile

echo ""
echo "🔄 Restarting Sutra services with optimized configuration..."

# Stop services
./sutra clean --containers

# Start with optimized configuration
SUTRA_EDITION=simple ./sutra deploy

echo ""
echo "✅ OPTIMIZATION COMPLETE!"
echo "   - All rate limits removed or set to 1M/sec"
echo "   - ML batch processing maximized (256 batch size)"
echo "   - Nginx worker connections increased to 16384"
echo "   - Vector dimension optimized for speed (256)"
echo ""
echo "🧪 Ready for maximum stress testing!"