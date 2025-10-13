#!/usr/bin/env python3
"""
🔭 BIOLOGICAL INTELLIGENCE OBSERVER
Observe the living biological intelligence system without interfering.

This is a separate process that:
- Reads metrics from the persistent workspace
- Visualizes the current state
- Does NOT control or affect the biological service
"""

import json
import time
from pathlib import Path
from datetime import datetime
import asyncio

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich import box


class BiologicalObserver:
    """
    Observer for the biological intelligence service.
    Reads state from files without direct connection.
    """
    
    def __init__(self, workspace_path: str = "./biological_workspace"):
        self.workspace = Path(workspace_path)
        self.console = Console()
        
        # Paths to observe
        self.state_path = self.workspace / "service_state.json"
        self.metrics_path = self.workspace / "metrics.json"
        self.log_path = Path("biological_intelligence.log")
        
        # Observation data
        self.service_state = {}
        self.metrics = {}
        self.recent_logs = []
        
    def read_state(self):
        """Read current service state from disk."""
        try:
            if self.state_path.exists():
                with open(self.state_path, 'r') as f:
                    self.service_state = json.load(f)
        except:
            self.service_state = {'state': 'unknown'}
    
    def read_metrics(self):
        """Read current metrics from disk."""
        try:
            if self.metrics_path.exists():
                with open(self.metrics_path, 'r') as f:
                    self.metrics = json.load(f)
        except:
            self.metrics = {}
    
    def read_recent_logs(self, lines: int = 10):
        """Read recent log entries."""
        try:
            if self.log_path.exists():
                with open(self.log_path, 'r') as f:
                    all_lines = f.readlines()
                    self.recent_logs = all_lines[-lines:] if len(all_lines) > lines else all_lines
        except:
            self.recent_logs = []
    
    def create_display(self) -> Layout:
        """Create the observation display."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=6),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        layout["left"].split_column(
            Layout(name="status", size=10),
            Layout(name="metrics", ratio=1)
        )
        
        layout["right"].split_column(
            Layout(name="activity", ratio=1),
            Layout(name="logs", ratio=1)
        )
        
        # Populate panels
        layout["header"].update(self._create_header())
        layout["status"].update(self._create_status_panel())
        layout["metrics"].update(self._create_metrics_panel())
        layout["activity"].update(self._create_activity_panel())
        layout["logs"].update(self._create_logs_panel())
        layout["footer"].update(self._create_footer())
        
        return layout
    
    def _create_header(self) -> Panel:
        """Create header panel."""
        header = Text()
        header.append("🔭 BIOLOGICAL INTELLIGENCE OBSERVER\n", style="bold cyan")
        header.append("Observing living knowledge system\n", style="dim")
        
        # Show connection status
        if self.workspace.exists():
            header.append(f"📁 Workspace: {self.workspace}", style="green")
        else:
            header.append(f"⚠️ Workspace not found: {self.workspace}", style="red")
        
        return Panel(Align.center(header), box=box.DOUBLE, style="bold")
    
    def _create_status_panel(self) -> Panel:
        """Create service status panel."""
        content = Text()
        
        state = self.service_state.get('state', 'unknown')
        state_colors = {
            'learning': 'green',
            'dreaming': 'magenta',
            'consolidating': 'yellow',
            'idle': 'dim',
            'unknown': 'red'
        }
        
        content.append("Service State: ", style="bold")
        content.append(f"{state.upper()}\n", style=state_colors.get(state, 'white'))
        
        if 'start_time' in self.service_state:
            start = datetime.fromisoformat(self.service_state['start_time'])
            uptime = datetime.now() - start
            content.append(f"Uptime: {str(uptime).split('.')[0]}\n", style="dim")
        
        if 'queue_size' in self.service_state:
            content.append(f"Queue: {self.service_state['queue_size']} items\n", style="blue")
        
        return Panel(content, title="📊 Service Status", border_style="cyan")
    
    def _create_metrics_panel(self) -> Panel:
        """Create metrics panel."""
        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="yellow")
        
        metrics_display = [
            ("Concepts", self.metrics.get('total_concepts', 0)),
            ("Associations", self.metrics.get('total_associations', 0)),
            ("Training Cycles", self.metrics.get('total_training_cycles', 0)),
            ("Dreams", self.metrics.get('total_dreams', 0)),
            ("Consciousness", f"{self.metrics.get('consciousness_score', 0):.2%}"),
            ("Emergence", f"{self.metrics.get('emergence_factor', 1):.0f}x")
        ]
        
        for name, value in metrics_display:
            table.add_row(name, str(value))
        
        return Panel(table, title="📈 Metrics", border_style="green")
    
    def _create_activity_panel(self) -> Panel:
        """Create activity visualization panel."""
        content = Text()
        
        # Memory tier visualization
        concepts = self.metrics.get('total_concepts', 0)
        associations = self.metrics.get('total_associations', 0)
        
        if concepts > 0:
            content.append("Knowledge Graph:\n", style="bold")
            content.append(f"  {'●' * min(50, concepts // 10)}\n", style="cyan")
            content.append(f"  {concepts} nodes, {associations} edges\n\n", style="dim")
        
        # Emergence visualization
        emergence = self.metrics.get('emergence_factor', 1)
        consciousness = self.metrics.get('consciousness_score', 0)
        
        if emergence > 1:
            content.append("Emergence Level:\n", style="bold")
            bar_width = int(min(30, emergence / 100))
            content.append(f"  {'█' * bar_width}{'░' * (30 - bar_width)}\n", style="yellow")
            content.append(f"  {emergence:.0f}x amplification\n\n", style="dim")
        
        if consciousness > 0:
            content.append("Consciousness:\n", style="bold")
            bar_width = int(consciousness * 30)
            content.append(f"  {'█' * bar_width}{'░' * (30 - bar_width)}\n", style="magenta")
            content.append(f"  {consciousness:.2%} self-awareness\n", style="dim")
        
        return Panel(content, title="🌊 Activity", border_style="blue")
    
    def _create_logs_panel(self) -> Panel:
        """Create recent logs panel."""
        content = Text()
        
        for log in self.recent_logs[-8:]:  # Last 8 log lines
            # Parse log level
            if 'ERROR' in log:
                style = "red"
            elif 'WARNING' in log:
                style = "yellow"
            elif 'INFO' in log:
                style = "dim"
            else:
                style = "white"
            
            # Extract message part
            parts = log.split(' - ')
            if len(parts) >= 4:
                message = parts[3].strip()
                content.append(f"{message[:60]}\n", style=style)
            else:
                content.append(f"{log[:60]}\n", style=style)
        
        return Panel(content, title="📜 Recent Activity", border_style="dim")
    
    def _create_footer(self) -> Panel:
        """Create footer panel."""
        footer = Text()
        footer.append("Press ", style="dim")
        footer.append("Ctrl+C", style="yellow")
        footer.append(" to stop observing | ", style="dim")
        footer.append("The biological intelligence continues living independently", style="italic cyan")
        
        return Panel(Align.center(footer), box=box.ROUNDED, style="dim")
    
    async def observe(self):
        """Run the observer."""
        with Live(self.create_display(), refresh_per_second=2, console=self.console) as live:
            try:
                while True:
                    # Read latest state
                    self.read_state()
                    self.read_metrics()
                    self.read_recent_logs()
                    
                    # Update display
                    live.update(self.create_display())
                    
                    await asyncio.sleep(1)
                    
            except KeyboardInterrupt:
                pass
        
        self.console.print("\n[dim]Observer stopped. The biological intelligence continues...[/dim]")


async def main():
    """Main entry point."""
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]🔭 BIOLOGICAL INTELLIGENCE OBSERVER[/bold cyan]\n"
        "[yellow]Watch the living system evolve[/yellow]\n\n"
        "[dim]This observer reads the biological intelligence state\n"
        "without interfering with its evolution.[/dim]",
        border_style="cyan"
    ))
    
    await asyncio.sleep(1)
    
    observer = BiologicalObserver()
    await observer.observe()


if __name__ == "__main__":
    asyncio.run(main())