#!/bin/bash
# Simple change detection for smart builds
# Only builds packages that actually changed

set -euo pipefail

# Get changed files since last commit (or specified ref)
BASE_REF="${1:-HEAD~1}"
CHANGED_FILES=$(git diff --name-only "$BASE_REF" 2>/dev/null || echo "")

# If no git changes, check for uncommitted changes
if [ -z "$CHANGED_FILES" ]; then
    CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null || echo "")
fi

# If still nothing, assume everything changed (first run)
if [ -z "$CHANGED_FILES" ]; then
    echo "No git repository or no changes detected"
    exit 0
fi

# Track which packages changed
CHANGED_PACKAGES=()

# Check each package directory
while IFS= read -r file; do
    case "$file" in
        packages/sutra-api/*)
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " sutra-api " ]] && CHANGED_PACKAGES+=("sutra-api")
            ;;
        packages/sutra-hybrid/*)
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " sutra-hybrid " ]] && CHANGED_PACKAGES+=("sutra-hybrid")
            ;;
        packages/sutra-storage/*)
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " storage-server " ]] && CHANGED_PACKAGES+=("storage-server")
            ;;
        packages/sutra-client/*)
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " sutra-client " ]] && CHANGED_PACKAGES+=("sutra-client")
            ;;
        packages/sutra-embedding-service/*)
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " embedding-single " ]] && CHANGED_PACKAGES+=("embedding-single")
            ;;
        packages/sutra-grid-master/*)
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " grid-master " ]] && CHANGED_PACKAGES+=("grid-master")
            ;;
        packages/sutra-grid-agent/*)
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " grid-agent " ]] && CHANGED_PACKAGES+=("grid-agent")
            ;;
        packages/sutra-protocol/*)
            # Protocol changes affect all Rust services
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " storage-server " ]] && CHANGED_PACKAGES+=("storage-server")
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " grid-master " ]] && CHANGED_PACKAGES+=("grid-master")
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " grid-agent " ]] && CHANGED_PACKAGES+=("grid-agent")
            ;;
        packages/sutra-storage-client-tcp/*)
            # Storage client changes affect all Python services
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " sutra-api " ]] && CHANGED_PACKAGES+=("sutra-api")
            [[ ! " ${CHANGED_PACKAGES[@]} " =~ " sutra-hybrid " ]] && CHANGED_PACKAGES+=("sutra-hybrid")
            ;;
    esac
done <<< "$CHANGED_FILES"

# Output results
if [ ${#CHANGED_PACKAGES[@]} -eq 0 ]; then
    echo "No package changes detected (only docs/config changes)"
else
    echo "Changed packages:"
    for pkg in "${CHANGED_PACKAGES[@]}"; do
        echo "  - $pkg"
    done
fi

# Export for use in scripts
export CHANGED_PACKAGES_LIST="${CHANGED_PACKAGES[*]}"
