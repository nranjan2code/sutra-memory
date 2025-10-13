#!/usr/bin/env python3
"""
🔍 WORKSPACE DIAGNOSTIC TOOL

This script analyzes workspace directory and memory nodes to diagnose
workspace ID mismatches that cause "0 concepts loaded" issues.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.pure_binary_storage import PureBinaryStorage
except ImportError:
    print("❌ Cannot import PureBinaryStorage - run from project root")
    sys.exit(1)

def analyze_workspace(workspace_path: str):
    """Analyze workspace directory and memory nodes."""
    print("🔍 WORKSPACE DIAGNOSTIC")
    print("=" * 60)
    print(f"Analyzing: {workspace_path}")
    print()
    
    ws_path = Path(workspace_path)
    if not ws_path.exists():
        print(f"❌ Workspace directory does not exist: {workspace_path}")
        return
    
    print("📁 WORKSPACE STRUCTURE")
    print("-" * 30)
    
    # Check key files
    key_files = {
        "metrics.json": "Service metrics and stats",
        "service_state.json": "Service state information", 
        "training_queue.json": "Pending training data",
        "memory.pbss": "Canonical memory file (legacy)",
        "nodes/": "Memory node storage directory"
    }
    
    for file_name, description in key_files.items():
        file_path = ws_path / file_name
        if file_path.exists():
            if file_path.is_dir():
                count = len(list(file_path.glob("*")))
                print(f"   ✅ {file_name:<20} {description} ({count} files)")
            else:
                size = file_path.stat().st_size
                print(f"   ✅ {file_name:<20} {description} ({size} bytes)")
        else:
            print(f"   ❌ {file_name:<20} {description} (missing)")
    
    print()
    
    # Analyze memory nodes
    nodes_dir = ws_path / "nodes"
    if not nodes_dir.exists():
        print("❌ No 'nodes' directory found - no persistent memory")
        return
    
    try:
        storage = PureBinaryStorage(str(nodes_dir))
        nodes = storage.list_all_nodes()
        
        print("🧠 MEMORY NODES ANALYSIS")
        print("-" * 30)
        print(f"Total nodes found: {len(nodes)}")
        
        if len(nodes) == 0:
            print("❌ No memory nodes found - system has no saved knowledge")
            return
        
        # Analyze by workspace_id
        workspace_counts = defaultdict(int)
        node_types = defaultdict(int)
        
        for node in nodes:
            metadata = node.get("metadata", {})
            workspace_id = metadata.get("workspace_id", "unknown")
            workspace_counts[workspace_id] += 1
            
            node_level = node.get("level", "unknown")
            node_types[node_level] += 1
        
        print(f"\n📊 BY WORKSPACE ID:")
        for workspace_id, count in workspace_counts.items():
            print(f"   {workspace_id:<20} {count} nodes")
        
        print(f"\n📊 BY NODE TYPE:")
        for node_type, count in node_types.items():
            print(f"   {node_type:<20} {count} nodes")
        
        # Check for mismatches
        print(f"\n🔍 WORKSPACE ID ANALYSIS:")
        unique_workspaces = list(workspace_counts.keys())
        
        if len(unique_workspaces) == 1:
            workspace_id = unique_workspaces[0]
            print(f"   ✅ Consistent workspace ID: '{workspace_id}'")
        else:
            print(f"   ⚠️ Multiple workspace IDs found: {unique_workspaces}")
            print(f"   This may cause loading issues if scripts use different IDs")
        
        # Expected workspace IDs
        expected_ids = ["core", "biological_service"]
        found_expected = [wid for wid in unique_workspaces if wid in expected_ids]
        
        if found_expected:
            print(f"   ✅ Found expected workspace IDs: {found_expected}")
        else:
            print(f"   ⚠️ No expected workspace IDs found (expected: {expected_ids})")
            print(f"   Found: {unique_workspaces}")
        
    except Exception as e:
        print(f"❌ Error analyzing memory nodes: {e}")
        import traceback
        traceback.print_exc()

def test_workspace_loading(workspace_path: str, workspace_id: str = "core"):
    """Test loading memory with specific workspace ID."""
    print(f"\n🧪 LOADING TEST")
    print("-" * 30)
    print(f"Testing memory load from: {workspace_path}")
    print(f"Using workspace ID: '{workspace_id}'")
    
    try:
        from src.biological_trainer import BiologicalTrainer
        
        print("🔄 Creating trainer...")
        trainer = BiologicalTrainer(
            base_path=workspace_path, 
            workspace_id=workspace_id, 
            use_full_swarm=True
        )
        
        print("🔄 Loading memory...")
        trainer.load_memory(workspace_path)
        
        concepts = len(trainer.memory_system.concepts)
        associations = len(trainer.memory_system.associations)
        
        print(f"✅ Memory loaded successfully:")
        print(f"   Concepts: {concepts}")
        print(f"   Associations: {associations}")
        
        if concepts == 0:
            print("⚠️ Zero concepts loaded - likely workspace ID mismatch")
            return False
        else:
            print("✅ Memory loading appears successful")
            return True
        
    except Exception as e:
        print(f"❌ Memory loading failed: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Diagnose workspace and memory issues")
    parser.add_argument("--workspace", default="./biological_workspace",
                       help="Workspace directory to analyze")
    parser.add_argument("--test-load", action="store_true",
                       help="Test loading memory from workspace")
    parser.add_argument("--workspace-id", default="core",
                       help="Workspace ID to use for loading test")
    
    args = parser.parse_args()
    
    # Analyze workspace structure
    analyze_workspace(args.workspace)
    
    # Test loading if requested
    if args.test_load:
        test_workspace_loading(args.workspace, args.workspace_id)

if __name__ == "__main__":
    main()