#!/usr/bin/env python3
"""
Run the Entity Extraction Service as an independent background process.

Usage:
    python run_entity_service.py [storage_path]

Example:
    export OLLAMA_API_KEY=your_key_here
    python run_entity_service.py ./knowledge
"""

import sys
from pathlib import Path

# Add sutra-core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "sutra-core"))

from sutra_core.services import EntityExtractionService


if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get storage path
    storage_path = sys.argv[1] if len(sys.argv) > 1 else "./knowledge"
    
    print("="*70)
    print("SUTRA ENTITY EXTRACTION SERVICE")
    print("="*70)
    print(f"Storage path: {storage_path}")
    print(f"Model: gpt-oss:120b-cloud")
    print(f"Press Ctrl+C to stop")
    print("="*70)
    print()
    
    # Create and run service
    service = EntityExtractionService(
        storage_path=storage_path,
        batch_size=10,
        poll_interval=5.0
    )
    
    service.run_forever()
