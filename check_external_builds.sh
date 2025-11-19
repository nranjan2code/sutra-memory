#!/bin/bash

echo "🔍 External Docker Image Status Check"
echo "===================================="
echo "$(date)"
echo

# Check both images
echo "📦 sutra-embedder:v1.0.1"
if docker pull ghcr.io/nranjan2code/sutra-embedder:v1.0.1 >/dev/null 2>&1; then
    echo "   ✅ AVAILABLE"
    embedder_ready=true
else
    echo "   ⏳ Still building..."
    embedder_ready=false
fi

echo
echo "📦 sutraworks-model:v1.0.0"
if docker pull ghcr.io/nranjan2code/sutraworks-model:v1.0.0 >/dev/null 2>&1; then
    echo "   ✅ AVAILABLE"
    model_ready=true
else
    echo "   ⏳ Still building..."
    model_ready=false
fi

echo
echo "📊 Summary:"
if [ "$embedder_ready" = true ] && [ "$model_ready" = true ]; then
    echo "   🎉 Both images ready! Deploy with: SUTRA_EDITION=simple ./sutra deploy"
    exit 0
else
    echo "   ⏳ Waiting for GitHub Actions to complete..."
    echo "   🔗 Monitor: https://github.com/nranjan2code/sutra-embedder/actions"
    echo "   🔗 Monitor: https://github.com/nranjan2code/sutraworks-model/actions"
    exit 1
fi