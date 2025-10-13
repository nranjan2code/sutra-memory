#!/usr/bin/env python3
"""
📚 BIOLOGICAL INTELLIGENCE FEEDER
Feed knowledge to the living biological intelligence system.

This client adds data to the training queue without direct connection.
The biological service will process it when ready.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse


class BiologicalFeeder:
    """
    Feeder for the biological intelligence service.
    Adds data to the training queue via file system.
    """
    
    def __init__(self, workspace_path: str = "./biological_workspace"):
        self.workspace = Path(workspace_path)
        self.training_queue_path = self.workspace / "training_queue.json"
        
        # Ensure workspace exists
        self.workspace.mkdir(exist_ok=True)
    
    def load_queue(self) -> list:
        """Load existing training queue."""
        if self.training_queue_path.exists():
            try:
                with open(self.training_queue_path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_queue(self, queue: list):
        """Save training queue."""
        with open(self.training_queue_path, 'w') as f:
            json.dump(queue, f, indent=2)
    
    def feed_text(self, text: str) -> bool:
        """Feed a single text to the biological system."""
        try:
            queue = self.load_queue()
            queue.append(text)
            self.save_queue(queue)
            print(f"✅ Added to training queue (now {len(queue)} items)")
            return True
        except Exception as e:
            print(f"❌ Failed to add to queue: {e}")
            return False
    
    def feed_file(self, filepath: str) -> bool:
        """Feed contents of a file to the biological system."""
        try:
            path = Path(filepath)
            if not path.exists():
                print(f"❌ File not found: {filepath}")
                return False
            
            with open(path, 'r') as f:
                content = f.read()
            
            # Split into paragraphs
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            queue = self.load_queue()
            initial_size = len(queue)
            queue.extend(paragraphs)
            self.save_queue(queue)
            
            added = len(paragraphs)
            print(f"✅ Added {added} paragraphs from {filepath}")
            print(f"   Queue: {initial_size} → {len(queue)} items")
            return True
            
        except Exception as e:
            print(f"❌ Failed to feed file: {e}")
            return False
    
    def feed_json(self, filepath: str) -> bool:
        """Feed JSON data to the biological system."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            texts = []
            if isinstance(data, list):
                texts = [str(item) for item in data]
            elif isinstance(data, dict):
                if 'texts' in data:
                    texts = data['texts']
                elif 'data' in data:
                    texts = [str(item) for item in data['data']]
                else:
                    # Convert dict to readable format
                    texts = [f"{k}: {v}" for k, v in data.items()]
            else:
                texts = [str(data)]
            
            queue = self.load_queue()
            initial_size = len(queue)
            queue.extend(texts)
            self.save_queue(queue)
            
            print(f"✅ Added {len(texts)} items from JSON")
            print(f"   Queue: {initial_size} → {len(queue)} items")
            return True
            
        except Exception as e:
            print(f"❌ Failed to feed JSON: {e}")
            return False
    
    def show_status(self):
        """Show current queue status."""
        queue = self.load_queue()
        print(f"\n📊 Training Queue Status:")
        print(f"   Items waiting: {len(queue)}")
        
        if queue:
            print(f"   First item: {queue[0][:50]}...")
            print(f"   Last item: {queue[-1][:50]}...")
        
        # Check if service is running
        state_path = self.workspace / "service_state.json"
        if state_path.exists():
            try:
                with open(state_path, 'r') as f:
                    state = json.load(f)
                print(f"\n🧬 Service Status:")
                print(f"   State: {state.get('state', 'unknown')}")
                print(f"   Started: {state.get('start_time', 'unknown')}")
            except:
                pass
        else:
            print("\n⚠️ Service state not found - service may not be running")
    
    def clear_queue(self):
        """Clear the training queue."""
        self.save_queue([])
        print("🗑️ Training queue cleared")


def main():
    parser = argparse.ArgumentParser(
        description='Feed knowledge to the Biological Intelligence System'
    )
    
    parser.add_argument(
        'action',
        choices=['text', 'file', 'json', 'status', 'clear'],
        help='Action to perform'
    )
    
    parser.add_argument(
        'data',
        nargs='?',
        help='Text to feed or path to file'
    )
    
    parser.add_argument(
        '--workspace',
        default='./biological_workspace',
        help='Path to biological workspace (default: ./biological_workspace)'
    )
    
    args = parser.parse_args()
    
    feeder = BiologicalFeeder(args.workspace)
    
    if args.action == 'text':
        if not args.data:
            print("❌ Please provide text to feed")
            sys.exit(1)
        feeder.feed_text(args.data)
        
    elif args.action == 'file':
        if not args.data:
            print("❌ Please provide file path")
            sys.exit(1)
        feeder.feed_file(args.data)
        
    elif args.action == 'json':
        if not args.data:
            print("❌ Please provide JSON file path")
            sys.exit(1)
        feeder.feed_json(args.data)
        
    elif args.action == 'status':
        feeder.show_status()
        
    elif args.action == 'clear':
        confirm = input("Are you sure you want to clear the queue? (y/N): ")
        if confirm.lower() == 'y':
            feeder.clear_queue()
        else:
            print("Cancelled")


if __name__ == "__main__":
    main()