#!/usr/bin/env python3
"""
🧪 REAL LEARNING VERIFICATION

Actually queries the biological intelligence to verify it learned English.
No assumptions - real questions, real answers.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.biological_trainer import BiologicalTrainer
except ImportError:
    from biological_trainer import BiologicalTrainer

def test_actual_learning(workspace: str = "./english_biological_workspace"):
    """Actually test if the system learned by asking it questions."""
    print("🧪 REAL LEARNING VERIFICATION")
    print("=" * 60)
    print("Testing actual knowledge by querying the trained system...")
    print()
    
    # Load the trained system
    try:
        from src.workspace_manager import get_workspace_manager
        
        # Use centralized workspace management with automatic migration
        manager = get_workspace_manager()
        manager.auto_migrate_if_needed("english")  # Auto-migrate if needed
        
        # Get trainer config for English workspace
        config = manager.get_trainer_config("english", environment="desktop")
        config['base_path'] = workspace  # Override with provided workspace path
        
        from src.biological_trainer import BiologicalTrainer
        trainer = BiologicalTrainer(**config)
        
        workspace_id = config['workspace_id']
        print(f"🔄 Loading memory from {workspace} (workspace: {workspace_id})")
        trainer.load_memory(workspace)
        print(f"✅ Memory loaded successfully")
        print(f"   Concepts: {len(trainer.memory_system.concepts)}")
        print(f"   Associations: {len(trainer.memory_system.associations)}")
    except Exception as e:
        print(f"❌ Failed to load memory: {e}")
        print(f"   Workspace: {workspace}")
        print(f"   Workspace ID: {workspace_id if 'workspace_id' in locals() else 'unknown'}")
        # Check if workspace exists and has memory files
        from pathlib import Path
        ws_path = Path(workspace)
        if ws_path.exists():
            print(f"   Directory exists: ✅")
            nodes_dir = ws_path / "nodes"
            if nodes_dir.exists():
                node_files = list(nodes_dir.glob("*.pb"))
                print(f"   Memory nodes found: {len(node_files)}")
            else:
                print(f"   No 'nodes' directory found")
        else:
            print(f"   Workspace directory does not exist")
        return False
    
    if len(trainer.memory_system.concepts) == 0:
        print("❌ No concepts found in memory - system didn't learn")
        return False
    
    print("\n🔍 KNOWLEDGE TESTS")
    print("-" * 40)
    
    # Define test questions that should work based on curriculum
    test_questions = [
        {
            "question": "What are vowels in English?",
            "query": "vowels English",
            "expected_content": ["vowel", "A", "E", "I", "O", "U"]
        },
        {
            "question": "What is a cat?", 
            "query": "cat animal",
            "expected_content": ["cat", "animal", "domestic", "fur"]
        },
        {
            "question": "What is Subject-Verb-Object order?",
            "query": "Subject Verb Object",
            "expected_content": ["subject", "verb", "object", "SVO", "sentence"]
        },
        {
            "question": "How do you form past tense?",
            "query": "past tense",
            "expected_content": ["past", "tense", "ed", "verb"]
        },
        {
            "question": "What are synonyms?",
            "query": "synonyms meaning",
            "expected_content": ["synonym", "similar", "meaning"]
        }
    ]
    
    total_tests = len(test_questions)
    successful_tests = 0
    
    for i, test in enumerate(test_questions, 1):
        print(f"\nTest {i}: {test['question']}")
        
        try:
            # Query the system
            results = trainer.query_knowledge(test['query'], max_results=5)
            
            if not results:
                print("   ❌ No results found")
                continue
            
            print(f"   ✅ Found {len(results)} results:")
            
            # Check if results contain expected content
            found_expected = 0
            all_content = " ".join([r.get('content', '').lower() for r in results])
            
            for expected in test['expected_content']:
                if expected.lower() in all_content:
                    found_expected += 1
            
            # Show top results
            for j, result in enumerate(results[:3], 1):
                content = result.get('content', '')[:80] + "..."
                relevance = result.get('relevance', 0.0)
                print(f"      {j}. {content} (score: {relevance:.3f})")
            
            # Evaluate success
            expected_ratio = found_expected / len(test['expected_content'])
            if expected_ratio >= 0.5:  # At least 50% of expected content found
                print(f"   🟢 SUCCESS: Found {found_expected}/{len(test['expected_content'])} expected concepts")
                successful_tests += 1
            else:
                print(f"   🟡 PARTIAL: Found {found_expected}/{len(test['expected_content'])} expected concepts")
            
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 VERIFICATION RESULTS")
    print("=" * 60)
    
    success_rate = (successful_tests / total_tests) * 100
    
    print(f"Tests Passed: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🟢 VERIFIED: System demonstrates strong learning")
        conclusion = "LEARNING VERIFIED"
    elif success_rate >= 60:
        print("🟡 PARTIAL: System shows some learning")  
        conclusion = "PARTIAL LEARNING"
    elif success_rate >= 40:
        print("🟠 WEAK: System has minimal learning")
        conclusion = "WEAK LEARNING"
    else:
        print("🔴 FAILED: System shows little to no learning")
        conclusion = "LEARNING FAILED"
    
    print(f"\n🧠 CONCLUSION: {conclusion}")
    print(f"   The biological intelligence {'DID' if success_rate >= 60 else 'DID NOT'} learn English effectively")
    
    return success_rate >= 60

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify actual learning")
    parser.add_argument("--workspace", default="./english_biological_workspace",
                       help="Workspace directory")
    
    args = parser.parse_args()
    
    success = test_actual_learning(args.workspace)
    sys.exit(0 if success else 1)