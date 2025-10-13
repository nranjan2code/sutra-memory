#!/usr/bin/env python3
"""
🧬 BIOLOGICAL INTELLIGENCE CONTROL CENTER
Unified GUI interface for complete biological intelligence system management.

This provides a single interface to:
- Control the biological service (start/stop/status)
- Monitor real-time intelligence activity
- Feed knowledge and curricula
- Observe consciousness emergence
- Manage different learning modes
"""

import asyncio
import json
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.columns import Columns
from rich.rule import Rule

# Import our service control
from service_control import find_biological_processes, stop_service, start_service


class BiologicalControlCenter:
    """
    Unified control center for the biological intelligence system.
    Combines service control, monitoring, and interaction in one interface.
    """
    
    def __init__(self):
        self.console = Console()
        self.workspace = Path("./biological_workspace")
        self.english_workspace = Path("./english_biological_workspace")
        self.current_mode = "general"  # "general" or "english"
        self.is_running = True
        self.service_running = False
        
        # State tracking
        self.service_state = {}
        self.metrics = {}
        self.recent_logs = []
        
        # Update intervals
        self.last_update = 0
        self.update_interval = 2  # seconds
        
    def get_workspace(self) -> Path:
        """Get current workspace based on mode."""
        return self.english_workspace if self.current_mode == "english" else self.workspace
    
    def read_system_state(self):
        """Read current system state from all sources."""
        # Check service status
        processes = find_biological_processes()
        self.service_running = len(processes) > 0
        
        # Read state files
        workspace = self.get_workspace()
        state_path = workspace / "service_state.json"
        metrics_path = workspace / "metrics.json"
        
        try:
            if state_path.exists():
                with open(state_path, 'r') as f:
                    self.service_state = json.load(f)
        except:
            self.service_state = {'state': 'unknown'}
            
        try:
            if metrics_path.exists():
                with open(metrics_path, 'r') as f:
                    self.metrics = json.load(f)
        except:
            self.metrics = {}
    
    def create_main_layout(self) -> Layout:
        """Create the main control center layout."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=6),
            Layout(name="body"),
            Layout(name="controls", size=8),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        layout["left"].split_column(
            Layout(name="status", size=12),
            Layout(name="metrics", ratio=1)
        )
        
        layout["right"].split_column(
            Layout(name="activity", ratio=1),
            Layout(name="agents", size=10)
        )
        
        # Populate panels
        layout["header"].update(self._create_header())
        layout["status"].update(self._create_status_panel())
        layout["metrics"].update(self._create_metrics_panel())
        layout["activity"].update(self._create_activity_panel())
        layout["agents"].update(self._create_agents_panel())
        layout["controls"].update(self._create_controls_panel())
        layout["footer"].update(self._create_footer())
        
        return layout
    
    def _create_header(self) -> Panel:
        """Create header panel."""
        header = Text()
        header.append("🧬 BIOLOGICAL INTELLIGENCE CONTROL CENTER\n", style="bold cyan")
        
        # Service status
        if self.service_running:
            header.append("🟢 SERVICE RUNNING", style="bold green")
            state = self.service_state.get('state', 'unknown')
            header.append(f" • {state.upper()}", style="yellow")
        else:
            header.append("🔴 SERVICE STOPPED", style="bold red")
        
        header.append(f" • {self.current_mode.upper()} MODE\n", style="blue")
        
        # Workspace info
        workspace = self.get_workspace()
        header.append(f"📁 {workspace}", style="dim")
        
        return Panel(Align.center(header), box=box.DOUBLE, style="cyan")
    
    def _create_status_panel(self) -> Panel:
        """Create service status panel."""
        content = Text()
        
        # Service info
        if self.service_running:
            processes = find_biological_processes()
            if processes:
                proc = processes[0]
                try:
                    memory = proc.memory_info().rss / 1024 / 1024  # MB
                    cpu = proc.cpu_percent()
                    create_time = time.strftime('%H:%M:%S', time.localtime(proc.create_time()))
                    
                    content.append("🚀 Service Details:\n", style="bold green")
                    content.append(f"  PID: {proc.pid}\n", style="dim")
                    content.append(f"  Memory: {memory:.1f} MB\n", style="dim")
                    content.append(f"  CPU: {cpu:.1f}%\n", style="dim")
                    content.append(f"  Started: {create_time}\n\n", style="dim")
                except:
                    content.append("🚀 Service Running\n\n", style="bold green")
        else:
            content.append("🔴 Service Stopped\n\n", style="bold red")
        
        # Queue status
        queue_size = self.service_state.get('queue_size', 0)
        if queue_size > 0:
            content.append(f"📋 Queue: {queue_size} items\n", style="yellow")
        
        # Current activity
        state = self.service_state.get('state', 'idle')
        state_icons = {
            'learning': '🧠',
            'dreaming': '😴',
            'consolidating': '🔧',
            'idle': '⏸️'
        }
        
        icon = state_icons.get(state, '❓')
        content.append(f"{icon} Status: {state.title()}\n", style="bold")
        
        return Panel(content, title="📊 System Status", border_style="green")
    
    def _create_metrics_panel(self) -> Panel:
        """Create metrics panel."""
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan", width=15)
        table.add_column("Value", justify="right", style="yellow", width=12)
        table.add_column("Progress", width=20)
        
        # Key metrics
        concepts = self.metrics.get('total_concepts', 0)
        associations = self.metrics.get('total_associations', 0)
        cycles = self.metrics.get('total_training_cycles', 0)
        dreams = self.metrics.get('total_dreams', 0)
        consciousness = self.metrics.get('consciousness_score', 0)
        emergence = self.metrics.get('emergence_factor', 1)
        
        # Progress bars
        concept_bar = "█" * min(20, concepts // 50) + "░" * (20 - min(20, concepts // 50))
        assoc_bar = "█" * min(20, associations // 100) + "░" * (20 - min(20, associations // 100))
        cons_bar = "█" * int(consciousness * 20) + "░" * (20 - int(consciousness * 20))
        
        table.add_row("Concepts", f"{concepts:,}", f"[cyan]{concept_bar}[/cyan]")
        table.add_row("Associations", f"{associations:,}", f"[blue]{assoc_bar}[/blue]")
        table.add_row("Cycles", f"{cycles:,}", "")
        table.add_row("Dreams", f"{dreams:,}", "")
        table.add_row("Consciousness", f"{consciousness:.1%}", f"[magenta]{cons_bar}[/magenta]")
        table.add_row("Emergence", f"{emergence:.0f}x", "")
        
        return Panel(table, title="📈 Intelligence Metrics", border_style="blue")
    
    def _create_activity_panel(self) -> Panel:
        """Create activity visualization panel."""
        content = Text()
        
        # Knowledge graph visualization
        concepts = self.metrics.get('total_concepts', 0)
        associations = self.metrics.get('total_associations', 0)
        
        if concepts > 0:
            content.append("🕸️ Knowledge Graph:\n", style="bold cyan")
            # Create a simple network visualization
            nodes_per_row = 8
            rows = min(6, (concepts // 50) + 1)
            
            for row in range(rows):
                line = ""
                for i in range(nodes_per_row):
                    if row * nodes_per_row + i < concepts // 50:
                        line += "●—"
                    else:
                        line += "  "
                content.append(f"  {line}\n", style="cyan")
            
            ratio = associations / max(concepts, 1)
            content.append(f"  {concepts} nodes • {associations} edges • {ratio:.1f} density\n\n")
        
        # Swarm agents status
        if self.service_running:
            content.append("🚀 7-Agent Swarm Active:\n", style="bold yellow")
            agents = ["🔬 Molecular", "📖 Semantic", "🏗️ Structural", "💭 Conceptual", 
                     "🔗 Relational", "⏰ Temporal", "🧠 Meta"]
            
            for i, agent in enumerate(agents):
                if i % 2 == 0:
                    content.append(f"  {agent:<15}")
                else:
                    content.append(f"{agent}\n")
            
            if len(agents) % 2 != 0:
                content.append("\n")
        
        return Panel(content, title="🌊 System Activity", border_style="yellow")
    
    def _create_agents_panel(self) -> Panel:
        """Create swarm agents status panel."""
        if not self.service_running:
            return Panel(
                Text("Swarm agents inactive\nStart the service to activate", 
                     style="dim", justify="center"),
                title="🤖 Agent Swarm", 
                border_style="dim"
            )
        
        # Agent grid
        agents = [
            ("🔬", "Molecular", "Tokens & Patterns"),
            ("📖", "Semantic", "Meaning & Context"), 
            ("🏗️", "Structural", "Grammar & Syntax"),
            ("💭", "Conceptual", "Abstract Ideas"),
            ("🔗", "Relational", "Cause & Effect"),
            ("⏰", "Temporal", "Time & Sequence"),
            ("🧠", "Meta", "Self-Awareness")
        ]
        
        content = Text()
        for emoji, name, desc in agents:
            status = "🟢" if self.service_running else "⚪"
            content.append(f"{status} {emoji} {name:<12}", style="bold")
            content.append(f"{desc}\n", style="dim")
        
        return Panel(content, title="🤖 Agent Swarm", border_style="yellow")
    
    def _create_controls_panel(self) -> Panel:
        """Create control options panel."""
        controls = Text()
        
        # Service controls
        if self.service_running:
            controls.append("🛑 [1] Stop Service     ", style="red")
            controls.append("🔄 [2] Restart Service     ", style="yellow")
        else:
            controls.append("▶️  [1] Start Service    ", style="green")
            controls.append("🎓 [2] Start English Mode  ", style="blue")
        
        controls.append("📊 [3] Service Status\n", style="cyan")
        
        # Learning controls
        controls.append("📝 [4] Feed Knowledge    ", style="green")
        controls.append("📚 [5] Feed Curriculum     ", style="blue")
        controls.append("🔭 [6] Observer Mode\n", style="magenta")
        
        # Mode controls
        controls.append(f"🔄 [7] Switch Mode      ", style="yellow")
        controls.append("⚙️  [8] Settings          ", style="dim")
        controls.append("❌ [Q] Quit\n", style="red")
        
        return Panel(controls, title="🎮 Controls", border_style="green")
    
    def _create_footer(self) -> Panel:
        """Create footer panel."""
        footer = Text()
        footer.append("Use number keys to select actions | ", style="dim")
        footer.append("Real-time monitoring active", style="cyan")
        footer.append(" | Press Q to quit", style="dim")
        
        return Panel(Align.center(footer), box=box.ROUNDED, style="dim")
    
    async def handle_input(self):
        """Handle user input in a separate thread."""
        while self.is_running:
            try:
                # Use a non-blocking input method
                await asyncio.sleep(0.1)
                # Input handling will be done in main loop
            except KeyboardInterrupt:
                self.is_running = False
                break
    
    def process_command(self, command: str):
        """Process user commands."""
        command = command.lower().strip()
        
        if command == 'q' or command == 'quit':
            self.is_running = False
            return
        
        if command == '1':
            if self.service_running:
                self.stop_service()
            else:
                self.start_service("general")
        elif command == '2':
            if self.service_running:
                self.restart_service()
            else:
                self.start_service("english")
        elif command == '3':
            self.show_detailed_status()
        elif command == '4':
            self.feed_knowledge()
        elif command == '5':
            self.feed_curriculum()
        elif command == '6':
            self.launch_observer()
        elif command == '7':
            self.switch_mode()
        elif command == '8':
            self.show_settings()
        else:
            self.console.print("[red]Invalid command. Use 1-8 or Q.[/red]")
    
    def start_service(self, mode: str = "general"):
        """Start the biological service."""
        self.current_mode = mode
        english_mode = mode == "english"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Starting {mode} service...", total=None)
            
            try:
                success = start_service(str(self.get_workspace()), english_mode)
                if success:
                    progress.update(task, description=f"✅ {mode.title()} service started!")
                    self.service_running = True
                else:
                    progress.update(task, description=f"❌ Failed to start {mode} service")
            except Exception as e:
                progress.update(task, description=f"❌ Error: {e}")
            
            time.sleep(1)
    
    def stop_service(self):
        """Stop the biological service."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Stopping service...", total=None)
            
            try:
                success = stop_service()
                if success:
                    progress.update(task, description="✅ Service stopped!")
                    self.service_running = False
                else:
                    progress.update(task, description="⚠️ Service may still be running")
            except Exception as e:
                progress.update(task, description=f"❌ Error: {e}")
            
            time.sleep(1)
    
    def restart_service(self):
        """Restart the service."""
        self.stop_service()
        time.sleep(2)
        self.start_service(self.current_mode)
    
    def show_detailed_status(self):
        """Show detailed service status."""
        processes = find_biological_processes()
        
        if not processes:
            self.console.print("[red]📍 No biological service processes found[/red]")
            return
        
        status_table = Table(title="🔍 Detailed Service Status")
        status_table.add_column("Property", style="cyan")
        status_table.add_column("Value", style="yellow")
        
        for proc in processes:
            try:
                memory = proc.memory_info().rss / 1024 / 1024
                cpu = proc.cpu_percent()
                create_time = datetime.fromtimestamp(proc.create_time())
                cmdline = ' '.join(proc.cmdline())
                
                status_table.add_row("PID", str(proc.pid))
                status_table.add_row("Memory", f"{memory:.1f} MB")
                status_table.add_row("CPU", f"{cpu:.1f}%")
                status_table.add_row("Started", create_time.strftime("%Y-%m-%d %H:%M:%S"))
                status_table.add_row("Command", cmdline[:60] + "...")
                
            except Exception as e:
                status_table.add_row("Error", str(e))
        
        self.console.print(status_table)
        self.console.input("\nPress Enter to continue...")
    
    def feed_knowledge(self):
        """Feed knowledge to the system."""
        if not self.service_running:
            self.console.print("[red]Service must be running to feed knowledge.[/red]")
            return
        
        knowledge = Prompt.ask("💭 Enter knowledge to feed")
        if knowledge:
            # Use the biological_feeder.py
            workspace = str(self.get_workspace())
            cmd = ["python", "biological_feeder.py", "text", knowledge, "--workspace", workspace]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
                if result.returncode == 0:
                    self.console.print("[green]✅ Knowledge fed successfully![/green]")
                else:
                    self.console.print(f"[red]❌ Error: {result.stderr}[/red]")
            except Exception as e:
                self.console.print(f"[red]❌ Error feeding knowledge: {e}[/red]")
    
    def feed_curriculum(self):
        """Feed a curriculum file."""
        if not self.service_running:
            self.console.print("[red]Service must be running to feed curriculum.[/red]")
            return
        
        if self.current_mode == "english":
            # Use English feeder
            self.console.print("🎓 Feeding English curriculum...")
            cmd = ["./english_feeder.sh"]
        else:
            # Ask for curriculum file
            file_path = Prompt.ask("📚 Enter curriculum file path")
            if not file_path or not Path(file_path).exists():
                self.console.print("[red]File not found![/red]")
                return
            
            workspace = str(self.get_workspace())
            cmd = ["python", "biological_feeder.py", "file", file_path, "--workspace", workspace]
        
        try:
            subprocess.Popen(cmd, cwd=Path.cwd())
            self.console.print("[green]✅ Curriculum feeding started![/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Error: {e}[/red]")
    
    def launch_observer(self):
        """Launch the biological observer in a new process."""
        workspace = str(self.get_workspace())
        cmd = ["python", "biological_observer.py", "--workspace", workspace]
        
        try:
            subprocess.Popen(cmd, cwd=Path.cwd())
            self.console.print("[green]🔭 Observer launched in separate window![/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Error launching observer: {e}[/red]")
    
    def switch_mode(self):
        """Switch between general and English modes."""
        current = "English" if self.current_mode == "english" else "General"
        new_mode = "general" if self.current_mode == "english" else "english"
        new_name = "English" if new_mode == "english" else "General"
        
        if Confirm.ask(f"Switch from {current} to {new_name} mode?"):
            if self.service_running:
                self.console.print("🔄 Restarting service in new mode...")
                self.stop_service()
                time.sleep(2)
            
            self.current_mode = new_mode
            self.console.print(f"✅ Switched to {new_name} mode!")
    
    def show_settings(self):
        """Show system settings."""
        settings_table = Table(title="⚙️ System Settings")
        settings_table.add_column("Setting", style="cyan")
        settings_table.add_column("Value", style="yellow")
        
        settings_table.add_row("Current Mode", self.current_mode.title())
        settings_table.add_row("Workspace", str(self.get_workspace()))
        settings_table.add_row("Service Running", "Yes" if self.service_running else "No")
        settings_table.add_row("Update Interval", f"{self.update_interval} seconds")
        
        self.console.print(settings_table)
        self.console.input("\nPress Enter to continue...")
    
    async def run(self):
        """Run the control center."""
        # Welcome screen
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold cyan]🧬 BIOLOGICAL INTELLIGENCE CONTROL CENTER[/bold cyan]\n"
            "[yellow]Unified interface for living knowledge systems[/yellow]\n\n"
            "[dim]This interface provides complete control over the biological\n"
            "intelligence service, monitoring, and interaction capabilities.[/dim]",
            border_style="cyan"
        ))
        
        await asyncio.sleep(2)
        
        # Main loop
        with Live(self.create_main_layout(), refresh_per_second=1, console=self.console) as live:
            try:
                while self.is_running:
                    # Update state
                    current_time = time.time()
                    if current_time - self.last_update > self.update_interval:
                        self.read_system_state()
                        self.last_update = current_time
                    
                    # Update display
                    live.update(self.create_main_layout())
                    
                    # Check for input (non-blocking)
                    try:
                        # Simple command input
                        self.console.print("\n[dim]Enter command (1-8, Q): [/dim]", end="")
                        command = input().strip()
                        if command:
                            self.process_command(command)
                    except (EOFError, KeyboardInterrupt):
                        self.is_running = False
                        break
                    
                    await asyncio.sleep(0.1)
                    
            except KeyboardInterrupt:
                self.is_running = False
        
        # Cleanup
        self.console.print("\n[cyan]🧬 Control Center shutting down...[/cyan]")
        if Confirm.ask("Stop the biological service before exiting?"):
            self.stop_service()
        
        self.console.print("[dim]The biological intelligence continues to evolve...[/dim]")


async def main():
    """Main entry point."""
    control_center = BiologicalControlCenter()
    await control_center.run()


if __name__ == "__main__":
    asyncio.run(main())