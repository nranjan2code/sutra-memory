#!/bin/bash

# 📚 ENGLISH CURRICULUM FEEDER
# Progressively feeds English lessons to the biological intelligence

WORKSPACE="./english_biological_workspace"

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║           📚 ENGLISH CURRICULUM FEEDER                           ║"
echo "║                                                                  ║"
echo "║  Feeding structured English lessons to biological intelligence   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check current status
echo "📊 Checking current status..."
python biological_feeder.py status --workspace $WORKSPACE
echo ""

# Feed lessons progressively
echo "🎓 Starting progressive English curriculum feeding..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Level 1: Alphabet (Foundation)
echo "📝 Level 1: Teaching the alphabet and phonetics..."
python biological_feeder.py json english_curriculum/level_1_alphabet.json --workspace $WORKSPACE
sleep 2

# Level 2: Basic Words  
echo ""
echo "📝 Level 2: Teaching basic vocabulary..."
python biological_feeder.py json english_curriculum/level_2_words.json --workspace $WORKSPACE
sleep 2

# Level 3: Grammar
echo ""
echo "📝 Level 3: Teaching grammar structures..."
python biological_feeder.py json english_curriculum/level_3_grammar.json --workspace $WORKSPACE
sleep 2

# Level 4: Sentences
echo ""
echo "📝 Level 4: Teaching sentence formation..."
python biological_feeder.py json english_curriculum/level_4_sentences.json --workspace $WORKSPACE
sleep 2

# Level 5: Semantics
echo ""
echo "📝 Level 5: Teaching semantic relationships..."
python biological_feeder.py json english_curriculum/level_5_semantics.json --workspace $WORKSPACE
sleep 2

# Level 6: Advanced
echo ""
echo "📝 Level 6: Teaching advanced language concepts..."
python biological_feeder.py json english_curriculum/level_6_advanced.json --workspace $WORKSPACE
sleep 2

# Practice texts
echo ""
echo "📖 Adding practice texts for comprehension..."
python biological_feeder.py json english_curriculum/practice_texts.json --workspace $WORKSPACE

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Complete English curriculum fed to biological intelligence!"
echo ""
echo "📊 Final queue status:"
python biological_feeder.py status --workspace $WORKSPACE
echo ""
echo "The biological intelligence will now process and learn this knowledge."
echo "Watch the learning progress with: python biological_observer.py --workspace $WORKSPACE"