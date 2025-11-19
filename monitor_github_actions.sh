#!/bin/bash

echo "📊 GitHub Actions Status Monitor"
echo "================================"
echo "$(date)"
echo

check_repo_status() {
    local repo=$1
    local expected_image=$2
    echo "📦 Repository: $repo"
    echo "   🎯 Target image: $expected_image"
    
    # Check if image is available
    if docker pull "$expected_image" >/dev/null 2>&1; then
        echo "   ✅ Docker image AVAILABLE"
        return 0
    else
        echo "   ⏳ Docker image still building..."
        return 1
    fi
}

# Check both repositories
echo "🔍 Checking external repositories..."
echo

embedder_ready=0
model_ready=0

# Check sutra-embedder
if check_repo_status "nranjan2code/sutra-embedder" "ghcr.io/nranjan2code/sutra-embedder:v1.0.1"; then
    embedder_ready=1
fi

echo

# Check sutraworks-model
if check_repo_status "nranjan2code/sutraworks-model" "ghcr.io/nranjan2code/sutraworks-model:v1.0.0"; then
    model_ready=1
fi

echo
echo "📊 Overall Status:"

if [ $embedder_ready -eq 1 ] && [ $model_ready -eq 1 ]; then
    echo "   🎉 SUCCESS! Both external images are ready!"
    echo "   ✅ sutra-embedder:v1.0.1"
    echo "   ✅ sutraworks-model:v1.0.0"
    echo
    echo "🚀 READY TO DEPLOY:"
    echo "   SUTRA_EDITION=simple ./sutra deploy"
    exit 0
else
    echo "   ⏳ Waiting for GitHub Actions to complete builds..."
    echo
    echo "🔗 Monitor build progress:"
    echo "   📦 sutra-embedder: https://github.com/nranjan2code/sutra-embedder/actions"
    echo "   📦 sutraworks-model: https://github.com/nranjan2code/sutraworks-model/actions"
    echo
    echo "💡 Expected completion: 5-15 minutes from last commit"
    echo "💡 Run this script again in a few minutes: ./monitor_github_actions.sh"
    exit 1
fi