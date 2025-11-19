#!/bin/bash

echo "🔍 Monitoring External Repository Builds..."
echo "==========================================="
echo

# Function to check if Docker image exists
check_image() {
    local image=$1
    docker pull "$image" &>/dev/null
    return $?
}

# Images to monitor
SUTRA_EMBEDDER="ghcr.io/nranjan2code/sutra-embedder:v1.0.1"
SUTRAWORKS_MODEL="ghcr.io/nranjan2code/sutraworks-model:v1.0.0"

# Track status
embedder_ready=false
model_ready=false

echo "⏳ Waiting for GitHub Actions to build and publish Docker images..."
echo "   - sutra-embedder: $SUTRA_EMBEDDER"
echo "   - sutraworks-model: $SUTRAWORKS_MODEL"
echo

attempt=1
max_attempts=30  # 15 minutes with 30-second intervals

while [ $attempt -le $max_attempts ]; do
    echo "🔄 Check #$attempt ($(date '+%H:%M:%S'))"
    
    # Check sutra-embedder
    if [ "$embedder_ready" = false ]; then
        if check_image "$SUTRA_EMBEDDER"; then
            echo "✅ sutra-embedder:v1.0.1 is now available!"
            embedder_ready=true
        else
            echo "⏳ sutra-embedder:v1.0.1 still building..."
        fi
    else
        echo "✅ sutra-embedder:v1.0.1 ready"
    fi
    
    # Check sutraworks-model
    if [ "$model_ready" = false ]; then
        if check_image "$SUTRAWORKS_MODEL"; then
            echo "✅ sutraworks-model:v1.0.0 is now available!"
            model_ready=true
        else
            echo "⏳ sutraworks-model:v1.0.0 still building..."
        fi
    else
        echo "✅ sutraworks-model:v1.0.0 ready"
    fi
    
    # Check if both are ready
    if [ "$embedder_ready" = true ] && [ "$model_ready" = true ]; then
        echo
        echo "🎉 SUCCESS: Both external images are now available!"
        echo "   ✅ sutra-embedder:v1.0.1"
        echo "   ✅ sutraworks-model:v1.0.0"
        echo
        echo "🚀 Ready to deploy with external services!"
        echo "   Next step: SUTRA_EDITION=simple ./sutra deploy"
        exit 0
    fi
    
    # Wait before next check
    if [ $attempt -lt $max_attempts ]; then
        echo "   Waiting 30 seconds before next check..."
        echo
        sleep 30
    fi
    
    ((attempt++))
done

echo
echo "⚠️  Timeout: Images not available after 15 minutes"
echo "   This is normal for first-time builds or complex compilation"
echo
echo "🔍 Check GitHub Actions status:"
echo "   - https://github.com/nranjan2code/sutra-embedder/actions"
echo "   - https://github.com/nranjan2code/sutraworks-model/actions"
echo
echo "💡 You can deploy with internal services while waiting:"
echo "   SUTRA_EDITION=simple ./sutra deploy --profile simple"

exit 1
