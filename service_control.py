#!/usr/bin/env python3
"""
🛠️ BIOLOGICAL INTELLIGENCE SERVICE CONTROL

Utility for starting, stopping, and managing the biological intelligence service.
"""

import sys
import time
import signal
import subprocess
import psutil
from pathlib import Path
import argparse
import json


def find_biological_processes():
    """Find all running biological service processes."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline_list = proc.info['cmdline']
            if cmdline_list:
                cmdline = ' '.join(cmdline_list)
                if 'biological_service' in cmdline or 'BiologicalIntelligenceService' in cmdline:
                    processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
            continue
    return processes


def stop_service(force=False):
    """Stop all biological service processes."""
    processes = find_biological_processes()
    
    if not processes:
        print("📍 No biological service processes found")
        return True
    
    print(f"🔍 Found {len(processes)} biological service process(es)")
    
    for proc in processes:
        try:
            cmdline = ' '.join(proc.cmdline())
            print(f"🛑 Stopping process {proc.pid}: {cmdline[:100]}...")
            
            if force:
                proc.kill()  # SIGKILL
                print(f"💀 Force killed process {proc.pid}")
            else:
                proc.terminate()  # SIGTERM
                print(f"🔄 Sent termination signal to process {proc.pid}")
                
                # Wait for graceful shutdown (increased timeout for biological processes)
                try:
                    proc.wait(timeout=20)  # Increased from 10 to 20 seconds
                    print(f"✅ Process {proc.pid} stopped gracefully")
                except psutil.TimeoutExpired:
                    print(f"⏰ Process {proc.pid} didn't stop within 20s, force killing...")
                    proc.kill()
                    print(f"💀 Force killed process {proc.pid}")
                    
        except psutil.NoSuchProcess:
            print(f"⚠️ Process {proc.pid} already stopped")
        except Exception as e:
            print(f"❌ Error stopping process {proc.pid}: {e}")
    
    # Verify all processes are stopped
    time.sleep(1)
    remaining = find_biological_processes()
    if remaining:
        print(f"⚠️ {len(remaining)} processes still running")
        return False
    else:
        print("✅ All biological service processes stopped")
        return True


def start_service(workspace="./biological_workspace", english_mode=False):
    """Start the biological service."""
    # Stop any existing processes first
    print("🧹 Cleaning up any existing processes...")
    stop_service()
    
    if english_mode:
        workspace = "./english_biological_workspace"
        print("🎓 Starting English learning mode...")
        
        # Clean workspace
        import shutil
        if Path(workspace).exists():
            shutil.rmtree(workspace)
        Path(workspace).mkdir(exist_ok=True)
    
    print(f"🧬 Starting biological intelligence service...")
    print(f"📁 Workspace: {workspace}")
    
    # Use the biological_service.py directly with proper workspace
    cmd = [
        sys.executable, "biological_service.py", 
        "--workspace", workspace
    ]
    
    if english_mode:
        cmd.extend(["--english"])
    
    try:
        # Start the service as a background process
        proc = subprocess.Popen(cmd, cwd=Path.cwd())
        print(f"🚀 Service started with PID {proc.pid}")
        
        # Give it a moment to start
        time.sleep(3)
        
        # Check if it's still running
        if proc.poll() is None:
            print("✅ Service is running successfully")
            print("\nNext steps:")
            print(f"  Monitor: python biological_observer.py --workspace {workspace}")
            if english_mode:
                print("  Feed data: ./english_feeder.sh")
            else:
                print("  Feed data: python biological_feeder.py text 'Your knowledge here'")
            print("  Stop: python service_control.py stop")
            return True
        else:
            print("❌ Service failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start service: {e}")
        return False


def status():
    """Show service status."""
    processes = find_biological_processes()
    
    if not processes:
        print("📍 No biological service processes running")
        return
    
    print(f"🧬 Biological Intelligence Service Status")
    print(f"{'='*50}")
    print(f"Active processes: {len(processes)}")
    print()
    
    for proc in processes:
        try:
            cmdline = ' '.join(proc.cmdline())
            memory = proc.memory_info().rss / 1024 / 1024  # MB
            cpu = proc.cpu_percent()
            create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(proc.create_time()))
            
            print(f"PID: {proc.pid}")
            print(f"Command: {cmdline[:80]}...")
            print(f"Memory: {memory:.1f} MB")
            print(f"CPU: {cpu:.1f}%")
            print(f"Started: {create_time}")
            print("-" * 40)
            
        except psutil.NoSuchProcess:
            print(f"Process {proc.pid} no longer exists")
        except Exception as e:
            print(f"Error getting info for process {proc.pid}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Biological Intelligence Service Control")
    parser.add_argument("command", choices=["start", "stop", "restart", "status", "force-stop"],
                       help="Command to execute")
    parser.add_argument("--workspace", default="./biological_workspace",
                       help="Workspace directory")
    parser.add_argument("--english", action="store_true",
                       help="Start in English learning mode")
    
    args = parser.parse_args()
    
    if args.command == "start":
        success = start_service(args.workspace, args.english)
        sys.exit(0 if success else 1)
        
    elif args.command == "stop":
        success = stop_service()
        sys.exit(0 if success else 1)
        
    elif args.command == "force-stop":
        success = stop_service(force=True)
        sys.exit(0 if success else 1)
        
    elif args.command == "restart":
        print("🔄 Restarting biological intelligence service...")
        stop_service()
        time.sleep(2)
        success = start_service(args.workspace, args.english)
        sys.exit(0 if success else 1)
        
    elif args.command == "status":
        status()


if __name__ == "__main__":
    main()