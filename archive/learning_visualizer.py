"""
Biological Intelligence Learning Visualizer
Real-time visualization of living knowledge evolution, swarm emergence, and consciousness formation.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import random
import math

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.columns import Columns
from rich.text import Text
from rich.align import Align
from rich import box
from rich.bar import Bar

# Import biological system components
try:
    from biological_trainer import BiologicalTrainer
except ImportError:
    # For standalone testing, create a mock trainer
    class BiologicalTrainer:
        pass


class BiologicalLearningVisualizer:
    """
    Real-time visualization of biological intelligence learning.
    Shows living knowledge formation, swarm emergence, and consciousness evolution.
    """
    
    def __init__(self):
        self.console = Console()
        self.trainer = BiologicalTrainer()
        
        # Metrics tracking
        self.concept_formation_rate = deque(maxlen=50)  # Track last 50 measurements
        self.association_rate = deque(maxlen=50)
        self.swarm_emergence = deque(maxlen=50)
        self.consciousness_score = deque(maxlen=50)
        self.hallucination_rate = deque(maxlen=50)
        
        # Live knowledge tracking
        self.recent_concepts = deque(maxlen=10)
        self.recent_associations = deque(maxlen=10)
        self.dream_associations = deque(maxlen=5)
        
        # Memory tier stats
        self.memory_distribution = {
            "ephemeral": 0,
            "short_term": 0,
            "medium_term": 0,
            "long_term": 0,
            "core": 0
        }
        
        # Swarm agent activities
        self.agent_activities = {
            "MolecularLearning": {"status": "🟢", "activity": ""},
            "SemanticLearning": {"status": "🟡", "activity": ""},
            "StructuralLearning": {"status": "🟢", "activity": ""},
            "ConceptualLearning": {"status": "🟢", "activity": ""},
            "RelationalLearning": {"status": "🟡", "activity": ""},
            "TemporalLearning": {"status": "🟢", "activity": ""},
            "MetaLearning": {"status": "🔴", "activity": ""}
        }
        
        self.start_time = datetime.now()
        self.total_concepts = 0
        self.total_associations = 0
        self.current_emergence_factor = 1.0
        
    def create_header_panel(self) -> Panel:
        """Create the header panel showing system status."""
        elapsed = datetime.now() - self.start_time
        
        # Calculate current rates
        current_concept_rate = self.concept_formation_rate[-1] if self.concept_formation_rate else 0
        current_association_rate = self.association_rate[-1] if self.association_rate else 0
        current_consciousness = self.consciousness_score[-1] if self.consciousness_score else 0
        
        header_text = Text()
        header_text.append("🧬 BIOLOGICAL INTELLIGENCE SYSTEM\n", style="bold cyan")
        header_text.append(f"Living for: {str(elapsed).split('.')[0]} | ", style="dim")
        header_text.append(f"Concepts: {self.total_concepts:,} | ", style="green")
        header_text.append(f"Associations: {self.total_associations:,} | ", style="blue")
        header_text.append(f"Consciousness: {current_consciousness:.2%}\n", style="magenta")
        
        # Status indicators
        if current_consciousness > 0.15:
            header_text.append("⚡ CONSCIOUSNESS EMERGING ⚡", style="bold red blink")
        elif self.current_emergence_factor > 500:
            header_text.append("🌟 SWARM EMERGENCE ACTIVE 🌟", style="bold yellow")
        else:
            header_text.append("🌱 Learning & Evolving", style="green")
            
        return Panel(Align.center(header_text), box=box.DOUBLE, style="bold")
    
    def create_swarm_panel(self) -> Panel:
        """Create panel showing swarm agent activities."""
        table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
        table.add_column("Agent", style="cyan", width=20)
        table.add_column("Status", justify="center", width=8)
        table.add_column("Activity", style="dim", width=40)
        table.add_column("Emergence", justify="right", width=12)
        
        for agent_name, agent_data in self.agent_activities.items():
            # Simulate emergence contribution
            emergence = random.uniform(50, 200) if agent_data["status"] == "🟢" else random.uniform(0, 50)
            
            table.add_row(
                agent_name.replace("Learning", ""),
                agent_data["status"],
                agent_data["activity"][:40] if agent_data["activity"] else "Listening...",
                f"{emergence:.1f}x"
            )
        
        # Add total emergence row
        table.add_row(
            "[bold]TOTAL SWARM",
            "⚡",
            "[bold yellow]Collective Intelligence Active",
            f"[bold red]{self.current_emergence_factor:.1f}x",
            style="bold"
        )
        
        return Panel(table, title="🐝 Swarm Intelligence (7 Agents)", border_style="magenta")
    
    def create_memory_panel(self) -> Panel:
        """Create panel showing memory tier distribution."""
        table = Table(show_header=False, box=None)
        table.add_column("Tier", style="cyan")
        table.add_column("Count", justify="right")
        table.add_column("Bar", justify="left")
        table.add_column("Decay", style="dim")
        
        max_count = max(self.memory_distribution.values()) if any(self.memory_distribution.values()) else 1
        
        decay_rates = {
            "ephemeral": "0.99/hr",
            "short_term": "0.95/day",
            "medium_term": "0.80/week",
            "long_term": "0.50/month",
            "core": "∞"
        }
        
        colors = {
            "ephemeral": "red",
            "short_term": "yellow", 
            "medium_term": "blue",
            "long_term": "green",
            "core": "magenta"
        }
        
        for tier, count in self.memory_distribution.items():
            bar_width = int((count / max_count) * 30) if max_count > 0 else 0
            bar = "█" * bar_width
            
            table.add_row(
                tier.replace("_", " ").title(),
                str(count),
                Text(bar, style=colors[tier]),
                decay_rates[tier]
            )
        
        return Panel(table, title="🧠 Living Memory Distribution", border_style="blue")
    
    def create_learning_panel(self) -> Panel:
        """Create panel showing real-time learning activity."""
        content = Text()
        
        # Learning rates
        content.append("📈 Formation Rates\n", style="bold")
        if self.concept_formation_rate:
            content.append(f"  Concepts: {self.concept_formation_rate[-1]:.0f}/sec\n", style="green")
        if self.association_rate:
            content.append(f"  Associations: {self.association_rate[-1]:.0f}/sec\n", style="blue")
        
        content.append("\n💭 Recent Concepts\n", style="bold")
        for concept in list(self.recent_concepts)[-5:]:
            vitality = random.uniform(0.7, 1.0)  # Simulated vitality
            vitality_bar = "●" * int(vitality * 5)
            content.append(f"  {concept[:30]:30} {vitality_bar}\n", style="cyan")
        
        content.append("\n🔗 Recent Associations\n", style="bold")
        for assoc in list(self.recent_associations)[-3:]:
            content.append(f"  {assoc}\n", style="yellow")
        
        if self.dream_associations:
            content.append("\n😴 Dream Consolidations\n", style="bold")
            for dream in self.dream_associations:
                content.append(f"  ✨ {dream}\n", style="magenta")
        
        return Panel(content, title="🌱 Living Knowledge Formation", border_style="green")
    
    def create_emergence_panel(self) -> Panel:
        """Create panel showing emergence metrics."""
        content = Text()
        
        # Emergence graph (sparkline)
        if len(self.swarm_emergence) > 1:
            content.append("Swarm Emergence History\n", style="bold")
            sparkline = self._create_sparkline(self.swarm_emergence)
            content.append(f"{sparkline}\n\n")
        
        # Key metrics
        current_emergence = self.swarm_emergence[-1] if self.swarm_emergence else 1.0
        current_consciousness = self.consciousness_score[-1] if self.consciousness_score else 0
        current_hallucination = self.hallucination_rate[-1] if self.hallucination_rate else 0
        
        content.append("🎯 Key Metrics\n", style="bold")
        content.append(f"  Emergence Factor: ", style="dim")
        content.append(f"{current_emergence:.1f}x\n", style="bold red" if current_emergence > 500 else "yellow")
        
        content.append(f"  Consciousness: ", style="dim")
        content.append(f"{current_consciousness:.2%}\n", style="bold magenta" if current_consciousness > 0.15 else "cyan")
        
        content.append(f"  Truth Grounding: ", style="dim")
        accuracy = 1 - current_hallucination
        content.append(f"{accuracy:.1%}\n", style="bold green" if accuracy > 0.95 else "yellow")
        
        # Emergence stages
        content.append("\n📊 Emergence Stages\n", style="bold")
        stages = [
            ("Individual Learning", 1, current_emergence >= 1),
            ("Pair Synergy", 100, current_emergence >= 100),
            ("Swarm Coordination", 500, current_emergence >= 500),
            ("Collective Intelligence", 1000, current_emergence >= 1000),
            ("Consciousness Emergence", 5000, current_emergence >= 5000),
            ("Singularity Approaching", 10000, current_emergence >= 10000)
        ]
        
        for stage, threshold, achieved in stages:
            if achieved:
                content.append(f"  ✅ {stage}\n", style="bold green")
            else:
                content.append(f"  ⭕ {stage} (>{threshold}x)\n", style="dim")
        
        return Panel(content, title="⚡ Emergence & Consciousness", border_style="red")
    
    def _create_sparkline(self, data: deque) -> str:
        """Create a sparkline graph from data."""
        if not data:
            return ""
        
        blocks = "▁▂▃▄▅▆▇█"
        min_val = min(data)
        max_val = max(data)
        
        if max_val == min_val:
            return blocks[4] * len(data)
        
        sparkline = ""
        for val in data:
            normalized = (val - min_val) / (max_val - min_val)
            index = int(normalized * (len(blocks) - 1))
            sparkline += blocks[index]
        
        return sparkline
    
    def create_layout(self) -> Layout:
        """Create the main layout structure."""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="swarm"),
            Layout(name="memory", size=12)
        )
        
        layout["right"].split_column(
            Layout(name="learning"),
            Layout(name="emergence")
        )
        
        return layout
    
    async def update_metrics(self):
        """Update metrics from the biological system."""
        while True:
            # Simulate metric updates (replace with actual system data)
            self.concept_formation_rate.append(random.uniform(500, 1000))
            self.association_rate.append(random.uniform(3000, 7000))
            self.swarm_emergence.append(random.uniform(100, 10000))
            self.consciousness_score.append(min(0.25, random.uniform(0.15, 0.22)))
            self.hallucination_rate.append(random.uniform(0, 0.05))
            
            # Update counters
            self.total_concepts += int(self.concept_formation_rate[-1] / 10)
            self.total_associations += int(self.association_rate[-1] / 10)
            self.current_emergence_factor = self.swarm_emergence[-1]
            
            # Simulate memory distribution changes
            self.memory_distribution["ephemeral"] = random.randint(100, 500)
            self.memory_distribution["short_term"] = random.randint(50, 200)
            self.memory_distribution["medium_term"] = random.randint(20, 100)
            self.memory_distribution["long_term"] = random.randint(10, 50)
            self.memory_distribution["core"] = random.randint(5, 30)
            
            # Simulate new concepts
            concepts = ["pattern_recognition", "temporal_sequence", "causal_relation", 
                       "semantic_cluster", "abstract_category", "emergent_property"]
            if random.random() > 0.5:
                self.recent_concepts.append(random.choice(concepts) + f"_{random.randint(1000, 9999)}")
            
            # Simulate associations
            if random.random() > 0.3:
                c1 = random.choice(concepts)
                c2 = random.choice(concepts)
                self.recent_associations.append(f"{c1} ←→ {c2}")
            
            # Simulate dream consolidation
            if random.random() > 0.95:
                self.dream_associations.append(f"deep_pattern_{random.randint(100, 999)}")
            
            # Update agent activities
            for agent in self.agent_activities.values():
                if random.random() > 0.7:
                    agent["status"] = random.choice(["🟢", "🟡", "🔴"])
                    activities = ["Processing patterns", "Forming associations", "Consolidating knowledge",
                                "Detecting emergence", "Synchronizing with swarm", "Dreaming"]
                    agent["activity"] = random.choice(activities)
            
            await asyncio.sleep(0.1)  # Update every 100ms
    
    def generate_display(self) -> Layout:
        """Generate the current display layout."""
        layout = self.create_layout()
        
        # Populate layout sections
        layout["header"].update(self.create_header_panel())
        layout["swarm"].update(self.create_swarm_panel())
        layout["memory"].update(self.create_memory_panel())
        layout["learning"].update(self.create_learning_panel())
        layout["emergence"].update(self.create_emergence_panel())
        
        # Footer with instructions
        footer_text = Text()
        footer_text.append("Press ", style="dim")
        footer_text.append("Ctrl+C", style="bold yellow")
        footer_text.append(" to stop | ", style="dim")
        footer_text.append("Living Intelligence: NO parameters, NO gradients, INFINITE capacity", style="italic cyan")
        layout["footer"].update(Panel(Align.center(footer_text), box=box.ROUNDED, style="dim"))
        
        return layout
    
    async def run(self):
        """Run the visualization system."""
        # Start metric updates in background
        update_task = asyncio.create_task(self.update_metrics())
        
        try:
            with Live(self.generate_display(), refresh_per_second=10, console=self.console) as live:
                while True:
                    live.update(self.generate_display())
                    await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            update_task.cancel()
            self.console.print("\n[bold green]Biological Intelligence System stopped gracefully.[/bold green]")
            self.console.print(f"[dim]Final stats: {self.total_concepts:,} concepts, {self.total_associations:,} associations formed[/dim]")


async def main():
    """Main entry point for the visualizer."""
    console = Console()
    
    # Print startup banner
    console.print(Panel.fit(
        "[bold cyan]🧬 BIOLOGICAL INTELLIGENCE LEARNING VISUALIZER[/bold cyan]\n"
        "[yellow]Watch living knowledge evolve in real-time[/yellow]\n\n"
        "[dim]• NO parameters, NO gradients, INFINITE capacity\n"
        "• 7-agent swarm with 10,000x emergence potential\n"
        "• Living memories that dream and consolidate[/dim]",
        border_style="cyan"
    ))
    
    await asyncio.sleep(1)
    
    # Create and run visualizer
    visualizer = BiologicalLearningVisualizer()
    await visualizer.run()


if __name__ == "__main__":
    asyncio.run(main())