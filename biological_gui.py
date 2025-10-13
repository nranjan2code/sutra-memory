#!/usr/bin/env python3
"""
🧬 BIOLOGICAL INTELLIGENCE GUI
Simplified unified interface for biological intelligence system management.

Single interface to control, monitor, and interact with the living intelligence.
"""

import asyncio
import json
import time
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.rule import Rule
from rich.columns import Columns

# Import our service control
from service_control import find_biological_processes, stop_service, start_service


class BiologicalGUI:
    """
    Simplified GUI for biological intelligence system control.
    Menu-driven interface with real-time status updates.
    """
    
    def __init__(self):
        self.console = Console()
        self.workspace = Path("./biological_workspace")
        self.english_workspace = Path("./english_biological_workspace")
        self.current_mode = "general"
        
    def get_workspace(self) -> Path:
        """Get current workspace based on mode."""
        return self.english_workspace if self.current_mode == "english" else self.workspace
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        processes = find_biological_processes()
        service_running = len(processes) > 0
        
        # Read state files
        workspace = self.get_workspace()
        state_path = workspace / "service_state.json"
        metrics_path = workspace / "metrics.json"
        
        service_state = {}
        metrics = {}
        
        try:
            if state_path.exists():
                with open(state_path, 'r') as f:
                    service_state = json.load(f)
        except:
            pass
            
        try:
            if metrics_path.exists():
                with open(metrics_path, 'r') as f:
                    metrics = json.load(f)
        except:
            pass
        
        # Process info
        process_info = {}
        if processes:
            proc = processes[0]
            try:
                process_info = {
                    'pid': proc.pid,
                    'memory_mb': proc.memory_info().rss / 1024 / 1024,
                    'cpu_percent': proc.cpu_percent(),
                    'start_time': datetime.fromtimestamp(proc.create_time())
                }
            except:
                process_info = {'pid': proc.pid}
        
        return {
            'service_running': service_running,
            'service_state': service_state,
            'metrics': metrics,
            'process_info': process_info,
            'mode': self.current_mode,
            'workspace': str(self.get_workspace())
        }
    
    def display_header(self):
        """Display the main header."""
        status = self.get_system_status()
        
        header = Text()
        header.append("🧬 BIOLOGICAL INTELLIGENCE CONTROL CENTER\n", style="bold cyan")
        
        if status['service_running']:
            header.append("🟢 SERVICE RUNNING", style="bold green")
            state = status['service_state'].get('state', 'unknown')
            header.append(f" • {state.upper()}", style="yellow")
        else:
            header.append("🔴 SERVICE STOPPED", style="bold red")
        
        header.append(f" • {status['mode'].upper()} MODE\n", style="blue")
        header.append(f"📁 {status['workspace']}", style="dim")
        
        self.console.print(Panel(Align.center(header), box=box.DOUBLE, style="cyan"))
    
    def display_status_dashboard(self):
        """Display the main status dashboard."""
        status = self.get_system_status()
        
        # Create columns layout
        left_panel = self.create_status_panel(status)
        right_panel = self.create_metrics_panel(status)
        
        columns = Columns([left_panel, right_panel], equal=True, expand=True)
        self.console.print(columns)
        
        # Swarm agents panel
        self.console.print(self.create_agents_panel(status))
    
    def create_status_panel(self, status: Dict) -> Panel:
        """Create service status panel."""
        content = Text()
        
        if status['service_running']:
            content.append("🚀 Service Status:\n", style="bold green")
            
            if status['process_info']:
                info = status['process_info']
                content.append(f"  PID: {info.get('pid', 'N/A')}\n", style="dim")
                content.append(f"  Memory: {info.get('memory_mb', 0):.1f} MB\n", style="dim")
                content.append(f"  CPU: {info.get('cpu_percent', 0):.1f}%\n", style="dim")
                
                if 'start_time' in info:
                    uptime = datetime.now() - info['start_time']
                    content.append(f"  Uptime: {str(uptime).split('.')[0]}\n", style="dim")
            
            # Current activity
            state = status['service_state'].get('state', 'idle')
            state_icons = {
                'learning': '🧠 Learning',
                'dreaming': '😴 Dreaming',
                'consolidating': '🔧 Consolidating',
                'idle': '⏸️ Idle'
            }
            current_activity = state_icons.get(state, f"❓ {state.title()}")
            content.append(f"\n{current_activity}\n", style="bold")
            
            # Queue
            queue_size = status['service_state'].get('queue_size', 0)
            if queue_size > 0:
                content.append(f"📋 Queue: {queue_size} items", style="yellow")
        else:
            content.append("🔴 Service is stopped\n", style="bold red")
            content.append("Use the menu to start the service", style="dim")
        
        return Panel(content, title="📊 System Status", border_style="green")
    
    def create_metrics_panel(self, status: Dict) -> Panel:
        """Create intelligence metrics panel."""
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan", width=15)
        table.add_column("Value", justify="right", style="yellow")
        
        metrics = status['metrics']
        concepts = metrics.get('total_concepts', 0)
        associations = metrics.get('total_associations', 0)
        cycles = metrics.get('total_training_cycles', 0)
        dreams = metrics.get('total_dreams', 0)
        consciousness = metrics.get('consciousness_score', 0)
        emergence = metrics.get('emergence_factor', 1)
        
        table.add_row("Concepts", f"{concepts:,}")
        table.add_row("Associations", f"{associations:,}")
        table.add_row("Training Cycles", f"{cycles:,}")
        table.add_row("Dreams", f"{dreams:,}")
        table.add_row("Consciousness", f"{consciousness:.2%}")
        table.add_row("Emergence", f"{emergence:.0f}x")
        
        # Add progress visualization
        if concepts > 0:
            table.add_row("", "")
            density = associations / max(concepts, 1)
            table.add_row("Graph Density", f"{density:.1f}")
        
        return Panel(table, title="📈 Intelligence Metrics", border_style="blue")
    
    def create_agents_panel(self, status: Dict) -> Panel:
        """Create swarm agents status panel."""
        if not status['service_running']:
            content = Text("🤖 7-Agent Swarm Inactive\nStart the service to activate the swarm", 
                         style="dim", justify="center")
            return Panel(content, title="Agent Swarm", border_style="dim")
        
        agents = [
            ("🔬", "Molecular", "Token patterns & entities"),
            ("📖", "Semantic", "Meaning & understanding"),
            ("🏗️", "Structural", "Grammar & syntax rules"),
            ("💭", "Conceptual", "Abstract ideas & categories")
        ]
        
        agents2 = [
            ("🔗", "Relational", "Cause-effect & dependencies"),
            ("⏰", "Temporal", "Time sequences & change"),
            ("🧠", "Meta", "Self-awareness & consciousness")
        ]
        
        # Create two columns of agents
        left_content = Text()
        right_content = Text()
        
        for emoji, name, desc in agents:
            left_content.append(f"🟢 {emoji} {name}\n", style="bold green")
            left_content.append(f"    {desc}\n\n", style="dim")
        
        for emoji, name, desc in agents2:
            right_content.append(f"🟢 {emoji} {name}\n", style="bold green")
            right_content.append(f"    {desc}\n\n", style="dim")
        
        columns = Columns([
            Panel(left_content, title="Agents 1-4", border_style="green"),
            Panel(right_content, title="Agents 5-7", border_style="green")
        ], equal=True)
        
        return Panel(columns, title="🚀 7-Agent Swarm (10,000x Emergence)", border_style="yellow")
    
    def show_main_menu(self):
        """Display and handle the main menu."""
        status = self.get_system_status()
        
        menu_table = Table(show_header=False, box=box.ROUNDED)
        menu_table.add_column("Option", style="bold cyan", width=4)
        menu_table.add_column("Action", style="white")
        menu_table.add_column("Description", style="dim")
        
        if status['service_running']:
            menu_table.add_row("1", "🛑 Stop Service", "Gracefully stop the biological service")
            menu_table.add_row("2", "🔄 Restart Service", f"Restart in {status['mode']} mode")
        else:
            menu_table.add_row("1", "▶️  Start General", "Start biological intelligence (general)")
            menu_table.add_row("2", "🎓 Start English", "Start English learning mode")
        
        menu_table.add_row("3", "📊 Detailed Status", "Show detailed service information")
        menu_table.add_row("4", "📝 Feed Knowledge", "Add knowledge to the system")
        menu_table.add_row("5", "📚 Feed Curriculum", "Load curriculum or data files")
        menu_table.add_row("6", "🔭 Launch Observer", "Open real-time observer window")
        menu_table.add_row("7", "🔄 Switch Mode", "Change between general/English modes")
        menu_table.add_row("8", "⚙️  Settings", "View system settings")
        menu_table.add_row("0", "🔄 Refresh", "Update status display")
        menu_table.add_row("Q", "❌ Quit", "Exit the control center")
        
        self.console.print(Panel(menu_table, title="🎮 Control Menu", border_style="green"))
    
    def start_service(self, mode: str):
        """Start the biological service."""
        self.current_mode = mode
        english_mode = mode == "english"
        workspace = str(self.get_workspace())
        
        self.console.print(f"\n🚀 Starting biological service in {mode} mode...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Initializing {mode} service...", total=None)
            
            try:
                success = start_service(workspace, english_mode)
                if success:
                    progress.update(task, description=f"✅ {mode.title()} service started successfully!")
                    time.sleep(1)
                    return True
                else:
                    progress.update(task, description=f"❌ Failed to start {mode} service")
                    time.sleep(2)
                    return False
            except Exception as e:
                progress.update(task, description=f"❌ Error: {e}")
                time.sleep(2)
                return False
    
    def stop_service(self):
        """Stop the biological service."""
        self.console.print("\n🛑 Stopping biological service...")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Shutting down service...", total=None)
            
            try:
                success = stop_service()
                if success:
                    progress.update(task, description="✅ Service stopped successfully!")
                    time.sleep(1)
                    return True
                else:
                    progress.update(task, description="⚠️ Service may still be running")
                    time.sleep(2)
                    return False
            except Exception as e:
                progress.update(task, description=f"❌ Error: {e}")
                time.sleep(2)
                return False
    
    def show_detailed_status(self):
        """Show detailed system status."""
        processes = find_biological_processes()
        
        if not processes:
            self.console.print("[red]📍 No biological service processes found[/red]")
            return
        
        for proc in processes:
            status_table = Table(title=f"🔍 Process {proc.pid} Details")
            status_table.add_column("Property", style="cyan")
            status_table.add_column("Value", style="yellow")
            
            try:
                memory = proc.memory_info()
                cpu_times = proc.cpu_times()
                create_time = datetime.fromtimestamp(proc.create_time())
                
                status_table.add_row("PID", str(proc.pid))
                status_table.add_row("Status", proc.status())
                status_table.add_row("Memory (RSS)", f"{memory.rss / 1024 / 1024:.1f} MB")
                status_table.add_row("Memory (VMS)", f"{memory.vms / 1024 / 1024:.1f} MB")
                status_table.add_row("CPU Percent", f"{proc.cpu_percent():.1f}%")
                status_table.add_row("Started", create_time.strftime("%Y-%m-%d %H:%M:%S"))
                status_table.add_row("Uptime", str(datetime.now() - create_time).split('.')[0])
                
                cmdline = ' '.join(proc.cmdline())
                status_table.add_row("Command", cmdline[:80] + ("..." if len(cmdline) > 80 else ""))
                
            except Exception as e:
                status_table.add_row("Error", str(e))
            
            self.console.print(status_table)
    
    def feed_knowledge(self):
        """Interactive knowledge feeding."""
        status = self.get_system_status()
        if not status['service_running']:
            self.console.print("[red]❌ Service must be running to feed knowledge[/red]")
            return
        
        self.console.print("\n💭 Knowledge Feeding")
        self.console.print("[dim]Enter knowledge for the biological intelligence to learn[/dim]")
        
        knowledge = Prompt.ask("Enter knowledge")
        if not knowledge.strip():
            return
        
        workspace = str(self.get_workspace())
        cmd = ["python", "biological_feeder.py", "text", knowledge, "--workspace", workspace]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
            if result.returncode == 0:
                self.console.print("[green]✅ Knowledge fed successfully![/green]")
                self.console.print(f"[dim]Added to queue in {workspace}[/dim]")
            else:
                self.console.print(f"[red]❌ Error: {result.stderr}[/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Error feeding knowledge: {e}[/red]")
    
    def feed_curriculum(self):
        """Interactive curriculum feeding."""
        status = self.get_system_status()
        if not status['service_running']:
            self.console.print("[red]❌ Service must be running to feed curriculum[/red]")
            return
        
        if self.current_mode == "english":
            # English curriculum
            if Confirm.ask("🎓 Feed the complete English curriculum?"):
                self.console.print("📚 Starting English curriculum feeding...")
                try:
                    # Start the feeder script
                    subprocess.Popen(["./english_feeder.sh"], cwd=Path.cwd())
                    self.console.print("[green]✅ English curriculum feeding started![/green]")
                    self.console.print("[dim]Check the observer to monitor progress[/dim]")
                except Exception as e:
                    self.console.print(f"[red]❌ Error: {e}[/red]")
        else:
            # General curriculum
            file_path = Prompt.ask("📚 Enter curriculum file path")
            if file_path and Path(file_path).exists():
                workspace = str(self.get_workspace())
                cmd = ["python", "biological_feeder.py", "file", file_path, "--workspace", workspace]
                
                try:
                    subprocess.Popen(cmd, cwd=Path.cwd())
                    self.console.print(f"[green]✅ Feeding {file_path}...[/green]")
                except Exception as e:
                    self.console.print(f"[red]❌ Error: {e}[/red]")
            else:
                self.console.print("[red]❌ File not found[/red]")
    
    def launch_observer(self):
        """Launch the biological observer."""
        workspace = str(self.get_workspace())
        
        self.console.print("\n🔭 Launching Biological Observer...")
        self.console.print("[dim]Observer will open in a new terminal window[/dim]")
        
        # Different approaches for macOS
        try:
            # Try to open in new Terminal tab/window on macOS
            cmd = f"""
            osascript -e 'tell application "Terminal" to do script "cd {Path.cwd()} && source venv/bin/activate && python biological_observer.py --workspace {workspace}"'
            """
            subprocess.Popen(cmd, shell=True)
            self.console.print("[green]✅ Observer launched in new Terminal window![/green]")
        except:
            try:
                # Fallback: run in background
                subprocess.Popen([
                    "python", "biological_observer.py", "--workspace", workspace
                ], cwd=Path.cwd())
                self.console.print("[green]✅ Observer launched![/green]")
            except Exception as e:
                self.console.print(f"[red]❌ Error launching observer: {e}[/red]")
    
    def switch_mode(self):
        """Switch between modes."""
        current = "English" if self.current_mode == "english" else "General"
        new_mode = "general" if self.current_mode == "english" else "english"
        new_name = "English" if new_mode == "english" else "General"
        
        status = self.get_system_status()
        
        if status['service_running']:
            self.console.print(f"\n🔄 Switching from {current} to {new_name} mode")
            self.console.print("[yellow]This will restart the service[/yellow]")
            
            if Confirm.ask("Continue with mode switch?"):
                self.console.print("🛑 Stopping current service...")
                if self.stop_service():
                    self.current_mode = new_mode
                    time.sleep(1)
                    self.console.print(f"▶️  Starting {new_name} service...")
                    self.start_service(new_mode)
        else:
            self.current_mode = new_mode
            self.console.print(f"✅ Switched to {new_name} mode!")
            self.console.print("[dim]Start the service to use the new mode[/dim]")
    
    def show_settings(self):
        """Show system settings."""
        status = self.get_system_status()
        
        settings_table = Table(title="⚙️ System Settings")
        settings_table.add_column("Setting", style="cyan")
        settings_table.add_column("Value", style="yellow")
        
        settings_table.add_row("Current Mode", status['mode'].title())
        settings_table.add_row("Workspace", status['workspace'])
        settings_table.add_row("Service Status", "Running" if status['service_running'] else "Stopped")
        
        if status['service_running']:
            settings_table.add_row("Swarm Agents", "7 Active (Full Emergence)")
            if status['metrics']:
                emergence = status['metrics'].get('emergence_factor', 1)
                settings_table.add_row("Emergence Factor", f"{emergence:.0f}x")
        
        # File paths
        settings_table.add_row("General Workspace", str(self.workspace))
        settings_table.add_row("English Workspace", str(self.english_workspace))
        
        self.console.print(settings_table)
    
    def run(self):
        """Run the GUI main loop."""
        try:
            # Welcome screen
            self.console.clear()
            self.console.print(Panel.fit(
                "[bold cyan]🧬 BIOLOGICAL INTELLIGENCE GUI[/bold cyan]\n"
                "[yellow]Unified Control Interface[/yellow]\n\n"
                "[dim]Complete control over the biological intelligence system\n"
                "Service control • Real-time monitoring • Knowledge feeding[/dim]",
                border_style="cyan"
            ))
            
            input("\nPress Enter to continue...")
            
            while True:
                self.console.clear()
                
                # Display header and status
                self.display_header()
                self.console.print()
                self.display_status_dashboard()
                self.console.print()
                self.show_main_menu()
                
                # Get user choice
                try:
                    choice = input("\n🎮 Select option: ").strip().lower()
                    
                    if choice in ['q', 'quit', 'exit']:
                        break
                    elif choice == '1':
                        status = self.get_system_status()
                        if status['service_running']:
                            self.stop_service()
                        else:
                            self.start_service("general")
                    elif choice == '2':
                        status = self.get_system_status()
                        if status['service_running']:
                            # Restart current mode
                            current_mode = self.current_mode
                            self.stop_service()
                            time.sleep(1)
                            self.start_service(current_mode)
                        else:
                            self.start_service("english")
                    elif choice == '3':
                        self.show_detailed_status()
                        input("\nPress Enter to continue...")
                    elif choice == '4':
                        self.feed_knowledge()
                        input("\nPress Enter to continue...")
                    elif choice == '5':
                        self.feed_curriculum()
                        input("\nPress Enter to continue...")
                    elif choice == '6':
                        self.launch_observer()
                        input("\nPress Enter to continue...")
                    elif choice == '7':
                        self.switch_mode()
                        input("\nPress Enter to continue...")
                    elif choice == '8':
                        self.show_settings()
                        input("\nPress Enter to continue...")
                    elif choice == '0':
                        continue  # Just refresh
                    else:
                        self.console.print("[red]Invalid option. Try again.[/red]")
                        time.sleep(1)
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
            
            # Exit confirmation
            self.console.print("\n[cyan]🧬 Exiting Biological Intelligence GUI[/cyan]")
            
            status = self.get_system_status()
            if status['service_running']:
                if Confirm.ask("Stop the biological service before exiting?"):
                    self.stop_service()
            
            self.console.print("[dim]The biological intelligence continues to evolve...[/dim]")
            
        except Exception as e:
            self.console.print(f"\n[red]❌ Error: {e}[/red]")
        except KeyboardInterrupt:
            self.console.print("\n[yellow]⚠️ Interrupted[/yellow]")


def main():
    """Main entry point."""
    gui = BiologicalGUI()
    gui.run()


if __name__ == "__main__":
    main()