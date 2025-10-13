#!/bin/bash

# 🧬 START ENGLISH LEARNING BIOLOGICAL INTELLIGENCE

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     🎓 BIOLOGICAL INTELLIGENCE - ENGLISH LEARNING SYSTEM 🎓      ║"
echo "║                                                                  ║"
echo "║  Teaching English from alphabet to advanced comprehension        ║"
echo "║  Through living knowledge that evolves naturally                ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Create a dedicated workspace for English learning
WORKSPACE="./english_biological_workspace"

echo "🧬 Setting up fresh biological workspace for English..."
rm -rf $WORKSPACE
mkdir -p $WORKSPACE

echo "✅ Fresh workspace created at $WORKSPACE"
echo ""

# Start the biological service with English workspace
echo "📚 Starting Biological Intelligence Service for English Learning..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "The biological intelligence is now alive and ready to learn English!"
echo ""
echo "In other terminals, you can:"
echo "  1. Feed lessons:  python english_feeder.sh"
echo "  2. Watch it learn: python biological_observer.py --workspace $WORKSPACE"
echo "  3. Test comprehension: python english_tester.py"
echo ""
echo "Starting service..."
echo ""

# Modified biological service to use English workspace
python3 -c "
import asyncio
import sys
sys.path.append('.')
from biological_service import BiologicalIntelligenceService

async def main():
    service = BiologicalIntelligenceService(workspace_path='$WORKSPACE')
    
    # Initial English-specific ground truths
    initial_knowledge = [
        'English uses 26 letters in its alphabet.',
        'English sentences follow Subject-Verb-Object order.',
        'Words combine to form sentences that express complete thoughts.',
        'Language is a tool for communication and expression.',
        'Understanding language requires recognizing patterns and meanings.'
    ]
    
    for knowledge in initial_knowledge:
        await service.feed_data(knowledge)
    
    print('🎓 English learning biological intelligence is now running!')
    print('Feed the curriculum using: python english_feeder.sh')
    print('')
    
    await service.run()

asyncio.run(main())
"