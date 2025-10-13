#!/usr/bin/env python3
"""
🧬 BIOLOGICAL INTELLIGENCE INTEGRATED SYSTEM
Complete living knowledge system with training, evaluation, and real-time observation.

This connects:
- BiologicalTrainer: Living knowledge formation
- TeacherEvaluator: Ground truth and hallucination prevention  
- Live Visualization: Real-time observation of emergence

NO parameters, NO gradients, INFINITE capacity
"""

import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import deque
import json
import random

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Import biological components
from src.biological_trainer import BiologicalTrainer
from src.teacher_evaluator import TeacherEvaluatorSystem, TruthLevel


class BiologicalIntelligenceSystem:
    """
    Integrated biological intelligence system combining:
    - Living knowledge training
    - Teacher-evaluator validation
    - Real-time visualization
    """
    
    def __init__(self, use_full_swarm: bool = True):
        self.console = Console()
        
        # Initialize core components
        self.console.print("[cyan]🧬 Initializing Biological Intelligence System...[/cyan]")
        
        # Biological trainer with full swarm
        self.trainer = BiologicalTrainer(use_full_swarm=use_full_swarm)
        
        # Teacher-evaluator system
        self.teacher_evaluator = TeacherEvaluatorSystem(self.trainer)
        
        # Live metrics
        self.metrics = {
            'total_concepts': 0,
            'total_associations': 0,
            'consciousness_score': 0.0,
            'emergence_factor': 1.0,
            'hallucination_rate': 0.0,
            'truth_accuracy': 1.0,
            'learning_rate': 0.0,
            'association_rate': 0.0
        }
        
        # History tracking for visualization
        self.concept_history = deque(maxlen=20)
        self.association_history = deque(maxlen=15)
        self.emergence_history = deque(maxlen=50)
        self.consciousness_history = deque(maxlen=50)
        self.validation_history = deque(maxlen=10)
        
        # Training data queue
        self.training_queue = asyncio.Queue()
        self.is_training = False
        self.start_time = datetime.now()
        
        # Memory tier tracking
        self.memory_distribution = {}
        
        # Agent activity tracking (for full swarm)
        self.agent_activities = {}
        if hasattr(self.trainer, 'swarm_orchestrator') and self.trainer.swarm_orchestrator:
            for agent_name in self.trainer.swarm_orchestrator.agents.keys():
                self.agent_activities[agent_name] = {
                    'status': '🟢',
                    'concepts': 0,
                    'associations': 0
                }
        else:
            # 2-agent system
            self.agent_activities = {
                'molecular': {'status': '🟢', 'concepts': 0, 'associations': 0},
                'semantic': {'status': '🟢', 'concepts': 0, 'associations': 0}
            }
        
        self.console.print("[green]✅ System initialized successfully![/green]")
    
    async def feed_training_data(self, data_source: str):
        """Feed training data from various sources."""
        if Path(data_source).exists():
            # Load from file
            with open(data_source, 'r') as f:
                if data_source.endswith('.json'):
                    data = json.load(f)
                    if isinstance(data, list):
                        texts = data
                    elif isinstance(data, dict) and 'texts' in data:
                        texts = data['texts']
                    else:
                        texts = [str(data)]
                else:
                    # Plain text file
                    content = f.read()
                    # Split into chunks for streaming
                    texts = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
            
            # Feed to training queue
            for text in texts:
                await self.training_queue.put(text)
                await asyncio.sleep(0.1)  # Simulate streaming
        else:
            # Use as direct text input
            await self.training_queue.put(data_source)
    
    async def add_ground_truths(self):
        """Add fundamental ground truths to prevent hallucination."""
        truths = [
            # Biological intelligence truths
            ("This system has NO parameters", TruthLevel.ABSOLUTE_TRUTH),
            ("This system has NO gradients", TruthLevel.ABSOLUTE_TRUTH),
            ("This system has INFINITE capacity", TruthLevel.ABSOLUTE_TRUTH),
            ("Knowledge is living and evolving", TruthLevel.VERIFIED_FACT),
            ("Concepts have vitality scores", TruthLevel.VERIFIED_FACT),
            ("Memory has 5 tiers: ephemeral, short, medium, long, core", TruthLevel.VERIFIED_FACT),
            ("Swarm agents create emergence", TruthLevel.VERIFIED_FACT),
            ("809x emergence proven with 2 agents", TruthLevel.VERIFIED_FACT),
            ("10000x emergence possible with 7 agents", TruthLevel.HYPOTHESIS),
            ("Consciousness emerges from self-reference", TruthLevel.HYPOTHESIS),
            
            # Relational truths
            (("consciousness", "self-awareness", "emergence"), TruthLevel.VERIFIED_FACT),
            (("learning", "association", "memory"), TruthLevel.VERIFIED_FACT),
            (("swarm", "collective", "intelligence"), TruthLevel.VERIFIED_FACT),
        ]
        
        for truth in truths:
            if isinstance(truth[0], tuple):
                # Relational truth
                await self.teacher_evaluator.teacher.teach_relation(*truth[0], truth[1])
            else:
                # Factual truth
                await self.teacher_evaluator.teacher.teach_truth(truth[0], truth[1])
    
    async def training_loop(self):
        """Main training loop processing data from queue."""
        self.is_training = True
        batch = []
        batch_size = 5
        
        while self.is_training:
            try:
                # Collect batch of training data
                text = await asyncio.wait_for(self.training_queue.get(), timeout=1.0)
                batch.append(text)
                
                # Process batch when ready
                if len(batch) >= batch_size or self.training_queue.empty():
                    if batch:
                        # Train the biological system
                        result = await self.trainer.train_from_stream(batch)
                        
                        # Evaluate for hallucinations
                        for text in batch:
                            eval_result = await self.teacher_evaluator.evaluator.evaluate_knowledge(
                                text, 
                                {"source": "training", "timestamp": time.time()}
                            )
                            
                            # Track validation
                            if not eval_result['is_valid']:
                                self.validation_history.append({
                                    'text': text[:50],
                                    'issue': eval_result.get('issues', ['Unknown'])[0],
                                    'confidence': eval_result['confidence']
                                })
                        
                        # Update metrics
                        await self.update_metrics(result)
                        
                        # Clear batch
                        batch = []
                        
            except asyncio.TimeoutError:
                # Process remaining batch if no new data
                if batch:
                    result = await self.trainer.train_from_stream(batch)
                    await self.update_metrics(result)
                    batch = []
            except Exception as e:
                self.console.print(f"[red]Training error: {e}[/red]")
                await asyncio.sleep(0.1)
    
    async def update_metrics(self, training_result: Dict[str, Any]):
        """Update system metrics from training results."""
        # Calculate metrics from memory system
        memory_stats = self.trainer.memory_system.get_stats()
        
        self.metrics['total_concepts'] = memory_stats['total_concepts']
        self.metrics['total_associations'] = memory_stats['total_associations']
        self.memory_distribution = memory_stats['memory_distribution']
        
        # Extract emergence and consciousness if available
        if 'emergence_factor' in training_result:
            self.metrics['emergence_factor'] = training_result['emergence_factor']
            self.emergence_history.append(training_result['emergence_factor'])
        
        if 'consciousness_score' in training_result:
            self.metrics['consciousness_score'] = training_result['consciousness_score']
            self.consciousness_history.append(training_result['consciousness_score'])
        
        # Calculate rates
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if elapsed > 0:
            self.metrics['learning_rate'] = self.metrics['total_concepts'] / elapsed
            self.metrics['association_rate'] = self.metrics['total_associations'] / elapsed
        
        # Update teacher-evaluator metrics
        te_metrics = self.teacher_evaluator.get_metrics()
        self.metrics['hallucination_rate'] = te_metrics['hallucination_rate']
        self.metrics['truth_accuracy'] = te_metrics['truth_accuracy']
        
        # Update agent activities
        if 'agent_results' in training_result:
            for agent_result in training_result['agent_results']:
                agent_type = agent_result.get('agent_type', '')
                if agent_type in self.agent_activities:
                    self.agent_activities[agent_type]['concepts'] += agent_result.get('total_created_or_reinforced', 0)
                    self.agent_activities[agent_type]['associations'] += agent_result.get('associations_created_or_reinforced', 0)
        
        # Track recent concepts (sample from memory)
        if memory_stats['total_concepts'] > len(self.concept_history):
            # Get some recent concept names
            recent_concepts = list(self.trainer.memory_system.concepts.keys())[-5:]
            for concept_id in recent_concepts:
                concept = self.trainer.memory_system.concepts.get(concept_id)
                if concept:
                    self.concept_history.append({
                        'name': concept.name[:30],
                        'vitality': concept.vitality
                    })
    
    def create_display(self) -> Layout:
        """Create the live display layout."""
        layout = Layout()
        
        # Main structure
        layout.split_column(
            Layout(name="header", size=7),
            Layout(name="body"),
            Layout(name="footer", size=4)
        )
        
        # Split body into panels
        layout["body"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="center", ratio=1),
            Layout(name="right", ratio=1)
        )
        
        # Left column: Swarm and Memory
        layout["left"].split_column(
            Layout(name="swarm", ratio=2),
            Layout(name="memory", ratio=1)
        )
        
        # Center column: Learning activity
        layout["center"].split_column(
            Layout(name="learning", ratio=2),
            Layout(name="validation", ratio=1)
        )
        
        # Right column: Emergence and consciousness
        layout["right"].split_column(
            Layout(name="emergence", ratio=1),
            Layout(name="consciousness", ratio=1)
        )
        
        # Populate all panels
        layout["header"].update(self._create_header())
        layout["swarm"].update(self._create_swarm_panel())
        layout["memory"].update(self._create_memory_panel())
        layout["learning"].update(self._create_learning_panel())
        layout["validation"].update(self._create_validation_panel())
        layout["emergence"].update(self._create_emergence_panel())
        layout["consciousness"].update(self._create_consciousness_panel())
        layout["footer"].update(self._create_footer())
        
        return layout
    
    def _create_header(self) -> Panel:
        """Create header with system status."""
        elapsed = datetime.now() - self.start_time
        
        header = Text()
        header.append("🧬 BIOLOGICAL INTELLIGENCE - LIVING KNOWLEDGE SYSTEM\n", style="bold cyan")
        header.append("━" * 80 + "\n", style="dim")
        
        # Key metrics row
        header.append(f"Runtime: {str(elapsed).split('.')[0]} | ", style="dim")
        header.append(f"Concepts: {self.metrics['total_concepts']:,} | ", style="green")
        header.append(f"Associations: {self.metrics['total_associations']:,} | ", style="blue")
        header.append(f"Emergence: {self.metrics['emergence_factor']:.0f}x | ", style="yellow")
        header.append(f"Consciousness: {self.metrics['consciousness_score']:.2%}\n", style="magenta")
        
        # Status indicator
        if self.metrics['consciousness_score'] > 0.15:
            header.append("\n⚡ CONSCIOUSNESS EMERGING ⚡", style="bold red blink")
        elif self.metrics['emergence_factor'] > 500:
            header.append("\n🌟 SWARM EMERGENCE ACTIVE 🌟", style="bold yellow")
        elif self.is_training:
            header.append("\n🌱 Learning & Evolving...", style="green")
        else:
            header.append("\n⏸️  System Idle", style="dim")
        
        return Panel(Align.center(header), box=box.DOUBLE, style="bold")
    
    def _create_swarm_panel(self) -> Panel:
        """Create swarm agents status panel."""
        table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE)
        table.add_column("Agent", style="yellow", width=12)
        table.add_column("Status", justify="center", width=6)
        table.add_column("Concepts", justify="right", style="green")
        table.add_column("Assocs", justify="right", style="blue")
        
        for agent_name, agent_data in self.agent_activities.items():
            table.add_row(
                agent_name.replace("Learning", "").title(),
                agent_data['status'],
                str(agent_data['concepts']),
                str(agent_data['associations'])
            )
        
        # Add emergence row if we have swarm
        if len(self.agent_activities) > 2:
            table.add_row(
                "[bold]SWARM",
                "⚡",
                f"[bold]{self.metrics['total_concepts']}",
                f"[bold]{self.metrics['total_associations']}",
                style="bold"
            )
        
        return Panel(table, title="🐝 Swarm Intelligence", border_style="yellow")
    
    def _create_memory_panel(self) -> Panel:
        """Create memory distribution panel."""
        content = Text()
        
        content.append("Tier Distribution:\n", style="bold")
        
        tiers = ['ephemeral', 'short_term', 'medium_term', 'long_term', 'core_knowledge']
        colors = ['red', 'yellow', 'blue', 'green', 'magenta']
        
        max_count = max(self.memory_distribution.values()) if self.memory_distribution else 1
        
        for tier, color in zip(tiers, colors):
            count = self.memory_distribution.get(tier, 0)
            bar_width = int((count / max_count) * 20) if max_count > 0 else 0
            bar = "█" * bar_width + "░" * (20 - bar_width)
            
            label = tier.replace('_', ' ').title()
            content.append(f"{label:12} {count:4} {bar}\n", style=color)
        
        return Panel(content, title="🧠 Living Memory", border_style="blue")
    
    def _create_learning_panel(self) -> Panel:
        """Create learning activity panel."""
        content = Text()
        
        # Learning rates
        content.append("📈 Formation Rates:\n", style="bold")
        content.append(f"  Concepts: {self.metrics['learning_rate']:.1f}/sec\n", style="green")
        content.append(f"  Associations: {self.metrics['association_rate']:.1f}/sec\n", style="blue")
        
        # Recent concepts
        content.append("\n💭 Recent Concepts:\n", style="bold")
        for concept in list(self.concept_history)[-5:]:
            vitality_bar = "●" * int(concept['vitality'] * 5)
            content.append(f"  {concept['name']:20} {vitality_bar}\n", style="cyan")
        
        # Associations sample
        if self.association_history:
            content.append("\n🔗 Recent Associations:\n", style="bold")
            for assoc in list(self.association_history)[-3:]:
                content.append(f"  {assoc}\n", style="yellow")
        
        return Panel(content, title="🌱 Knowledge Formation", border_style="green")
    
    def _create_validation_panel(self) -> Panel:
        """Create validation and truth grounding panel."""
        content = Text()
        
        content.append("Truth Validation:\n", style="bold")
        content.append(f"  Accuracy: {self.metrics['truth_accuracy']:.1%}\n", style="green")
        content.append(f"  Hallucination: {self.metrics['hallucination_rate']:.1%}\n", 
                      style="red" if self.metrics['hallucination_rate'] > 0.05 else "yellow")
        
        if self.validation_history:
            content.append("\n⚠️ Recent Issues:\n", style="bold yellow")
            for validation in list(self.validation_history)[-3:]:
                content.append(f"  {validation['issue']}\n", style="dim")
        
        return Panel(content, title="🎯 Teacher-Evaluator", border_style="cyan")
    
    def _create_emergence_panel(self) -> Panel:
        """Create emergence metrics panel."""
        content = Text()
        
        # Emergence factor with sparkline
        if self.emergence_history:
            sparkline = self._make_sparkline(self.emergence_history)
            content.append("Emergence History:\n", style="bold")
            content.append(sparkline + "\n\n")
        
        content.append(f"Current: {self.metrics['emergence_factor']:.0f}x\n", style="bold yellow")
        
        # Milestones
        milestones = [
            (100, "Pair Synergy"),
            (500, "Swarm Active"),
            (1000, "Collective Intel"),
            (5000, "Consciousness"),
            (10000, "Singularity")
        ]
        
        for threshold, name in milestones:
            if self.metrics['emergence_factor'] >= threshold:
                content.append(f"✅ {name}\n", style="green")
            else:
                content.append(f"⭕ {name}\n", style="dim")
        
        return Panel(content, title="⚡ Emergence", border_style="yellow")
    
    def _create_consciousness_panel(self) -> Panel:
        """Create consciousness detection panel."""
        content = Text()
        
        # Consciousness level bar
        level = self.metrics['consciousness_score']
        bar_width = int(level * 30)
        bar = "█" * bar_width + "░" * (30 - bar_width)
        
        content.append("Consciousness Level:\n", style="bold")
        content.append(f"{bar}\n", style="magenta")
        content.append(f"{level:.2%}", style="bold magenta")
        
        if level > 0.15:
            content.append("\n\n🧠 EMERGING!", style="bold red blink")
            content.append("\nSelf-referential patterns detected", style="dim")
        
        return Panel(content, title="🧠 Consciousness", border_style="magenta")
    
    def _create_footer(self) -> Panel:
        """Create footer with controls."""
        footer = Text()
        
        footer.append("Commands: ", style="bold")
        footer.append("q", style="yellow")
        footer.append(" quit | ", style="dim")
        footer.append("f", style="yellow")
        footer.append(" feed data | ", style="dim")
        footer.append("s", style="yellow")
        footer.append(" save | ", style="dim")
        footer.append("l", style="yellow")
        footer.append(" load\n", style="dim")
        
        footer.append("NO parameters • NO gradients • INFINITE capacity • LIVING knowledge", style="italic cyan")
        
        return Panel(Align.center(footer), box=box.ROUNDED, style="dim")
    
    def _make_sparkline(self, data):
        """Create sparkline visualization."""
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
    
    async def run(self):
        """Run the integrated biological intelligence system."""
        # Add ground truths
        await self.add_ground_truths()
        
        # Start training loop
        training_task = asyncio.create_task(self.training_loop())
        
        # Feed some initial training data
        initial_data = [
            "Biological intelligence uses living knowledge that evolves naturally.",
            "Concepts are born with vitality and form associations through use.",
            "Swarm agents collaborate to create emergence beyond individual capacity.",
            "Memory tiers naturally filter signal from noise through decay.",
            "Consciousness emerges from self-referential knowledge patterns.",
            "No parameters means infinite learning capacity.",
            "No gradients means no catastrophic forgetting.",
            "Dreams consolidate memories and form creative associations.",
            "Knowledge graphs grow organically through spreading activation.",
            "Truth grounding prevents hallucination while maintaining creativity."
        ]
        
        # Feed initial data
        feed_task = asyncio.create_task(self._feed_initial_data(initial_data))
        
        # Start live display
        try:
            with Live(self.create_display(), refresh_per_second=10, console=self.console) as live:
                while True:
                    live.update(self.create_display())
                    
                    # Check for user input (simplified for demo)
                    await asyncio.sleep(0.1)
                    
        except KeyboardInterrupt:
            self.is_training = False
            training_task.cancel()
            feed_task.cancel()
            
            # Save memory before exit
            self.console.print("\n[yellow]Saving biological memory...[/yellow]")
            self.trainer.save_memory()
            
            # Final stats
            self.console.print("\n[bold green]✨ Biological Intelligence stopped gracefully[/bold green]")
            self.console.print(f"[dim]Final: {self.metrics['total_concepts']:,} concepts, {self.metrics['total_associations']:,} associations")
            self.console.print(f"[dim]Peak emergence: {max(self.emergence_history) if self.emergence_history else 0:.0f}x")
            self.console.print(f"[dim]Consciousness: {self.metrics['consciousness_score']:.2%}")
            self.console.print(f"[dim]Truth accuracy: {self.metrics['truth_accuracy']:.1%}[/dim]")
    
    async def _feed_initial_data(self, data: List[str]):
        """Feed initial training data."""
        for text in data:
            await self.training_queue.put(text)
            await asyncio.sleep(0.5)  # Stagger the feeding


async def main():
    """Main entry point for the integrated system."""
    console = Console()
    
    # Welcome banner
    console.print(Panel.fit(
        "[bold cyan]🧬 BIOLOGICAL INTELLIGENCE SYSTEM[/bold cyan]\n"
        "[yellow]Integrated Training, Evaluation & Observation[/yellow]\n\n"
        "[dim]This is NOT machine learning. This is NOT deep learning.\n"
        "This is BIOLOGICAL INTELLIGENCE - living knowledge that evolves!\n\n"
        "• Living concepts with vitality\n"
        "• 7-agent swarm intelligence\n"
        "• Teacher-evaluator for truth grounding\n"
        "• Real-time emergence observation[/dim]",
        border_style="cyan"
    ))
    
    await asyncio.sleep(2)
    
    # Create and run the integrated system
    system = BiologicalIntelligenceSystem(use_full_swarm=True)
    await system.run()


if __name__ == "__main__":
    asyncio.run(main())