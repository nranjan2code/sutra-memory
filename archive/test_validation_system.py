"""
Integrated Test: Teacher-Evaluator + Biological Intelligence
=============================================================
Demonstrates how the validation system prevents hallucinations
while allowing creative biological learning
"""

import asyncio
import sys
sys.path.append('.')

from src.biological_trainer import BiologicalTrainer
from src.teacher_evaluator import (
    TeacherEvaluatorSystem,
    KnowledgeType,
    TruthLevel
)


async def test_with_validation():
    """Test biological intelligence with validation to prevent hallucinations"""
    
    print("=" * 80)
    print("BIOLOGICAL INTELLIGENCE WITH TEACHER-EVALUATOR SYSTEM")
    print("Preventing Hallucinations While Allowing Creative Learning")
    print("=" * 80)
    
    # Initialize systems
    trainer = BiologicalTrainer()
    validator = TeacherEvaluatorSystem(biological_trainer=trainer)
    
    # Add ground truths
    print("\n1. ESTABLISHING GROUND TRUTHS...")
    ground_truths = [
        ("water formula", "water is H2O", KnowledgeType.FACTUAL, "chemistry"),
        ("gravity effect", "gravity attracts objects", KnowledgeType.RELATIONAL, "physics"),
        ("machine learning", "machine learning learns from data", KnowledgeType.CONCEPTUAL, "AI"),
        ("neural networks", "neural networks have layers", KnowledgeType.FACTUAL, "AI"),
        ("consciousness", "consciousness is awareness", KnowledgeType.CONCEPTUAL, "philosophy"),
    ]
    
    for pattern, truth, k_type, source in ground_truths:
        validator.add_ground_truth(pattern, truth, k_type, source)
    
    print(f"   Added {len(ground_truths)} ground truths")
    
    # Train with mixed content (some true, some potentially hallucinating)
    print("\n2. TRAINING BIOLOGICAL INTELLIGENCE...")
    training_texts = [
        # True statements
        "Water is H2O, composed of hydrogen and oxygen.",
        "Gravity attracts objects according to their mass.",
        "Machine learning learns from data to make predictions.",
        "Neural networks have layers that process information.",
        
        # Creative but valid
        "Intelligence emerges from complex interactions.",
        "Swarm systems exhibit collective behavior.",
        
        # Potential hallucinations
        "Water is definitely always never wet and dry simultaneously.",
        "Gravity is magical and breaks all laws of physics.",
        "Machine learning absolutely always guarantees perfect results.",
        "Neural networks are supernatural entities.",
    ]
    
    validated_count = 0
    hallucination_count = 0
    
    for text in training_texts:
        # Train the biological system
        await trainer.train_from_stream([text])
        
        # Validate the learned knowledge
        concept_id = f"concept_{len(training_texts)}"
        result = await validator.teach_and_evaluate(
            concept_id, 
            text,
            KnowledgeType.CONCEPTUAL
        )
        
        if result.truth_level == TruthLevel.HALLUCINATION:
            print(f"   ❌ HALLUCINATION DETECTED: '{text[:50]}...'")
            hallucination_count += 1
        elif result.is_valid:
            print(f"   ✅ VALID KNOWLEDGE: '{text[:50]}...' (confidence: {result.confidence:.2f})")
            validated_count += 1
        else:
            print(f"   ⚠️  UNCERTAIN: '{text[:50]}...'")
    
    # Show training results
    print(f"\n   Training Results:")
    print(f"   - Valid knowledge: {validated_count}")
    print(f"   - Hallucinations prevented: {hallucination_count}")
    print(f"   - Total processed: {len(training_texts)}")
    
    # Test dream state validation
    print("\n3. TESTING DREAM STATE VALIDATION...")
    
    # Simulate dream consolidation
    # await trainer.memory_system.dream_consolidation()  # Not implemented yet
    print("   Dream consolidation not yet implemented, skipping...")
    
    # Validate dream concepts
    dream_concepts = []
    for concept_id, concept in list(trainer.memory_system.concepts.items())[:5]:
        if 'dream' in concept.content.lower() or len(concept.associations) > 2:
            dream_concepts.append(concept)
    
    if dream_concepts:
        print(f"   Validating {len(dream_concepts)} dream concepts...")
        for concept in dream_concepts:
            result = await validator.teach_and_evaluate(
                f"dream_{concept.id}",
                concept.content,
                KnowledgeType.EMERGENT
            )
            
            if result.is_valid:
                print(f"   💭 DREAM VALID: '{concept.content[:40]}...'")
            else:
                print(f"   💤 DREAM NEEDS GROUNDING: '{concept.content[:40]}...'")
    
    # Query knowledge with validation
    print("\n4. QUERYING WITH VALIDATION...")
    queries = [
        "water composition",
        "gravity effects",
        "machine learning",
        "consciousness awareness"
    ]
    
    for query in queries:
        results = trainer.query_knowledge(query, max_results=3)
        
        print(f"\n   Query: '{query}'")
        for result in results[:2]:
            # Validate retrieved knowledge
            validation = await validator.teach_and_evaluate(
                result['concept_id'],
                result['content'],
                KnowledgeType.CONCEPTUAL
            )
            
            validity = "✅" if validation.is_valid else "❌"
            print(f"   {validity} {result['content'][:60]}... (rel: {result['relevance']:.2f})")
    
    # Show system metrics
    print("\n5. SYSTEM METRICS:")
    metrics = validator.get_metrics()
    # Get memory stats directly from memory system
    memory_stats = {
        'total_concepts': len(trainer.memory_system.concepts),
        'total_associations': len(trainer.memory_system.associations),
        'memory_distribution': {}
    }
    
    print(f"   Validation Metrics:")
    print(f"   - Hallucination rate: {metrics['hallucination_rate']:.2%}")
    print(f"   - Truth accuracy: {metrics['truth_accuracy']:.2%}")
    print(f"   - Total validations: {metrics['total_validations']}")
    
    print(f"\n   Memory Statistics:")
    print(f"   - Total concepts: {memory_stats['total_concepts']}")
    print(f"   - Total associations: {memory_stats['total_associations']}")
    print(f"   - Memory distribution: {memory_stats['memory_distribution']}")
    
    # Demonstrate correction mechanism
    print("\n6. CORRECTION MECHANISM:")
    
    # Intentionally add hallucination
    hallucination = "The moon is made of green cheese and controls human thoughts magically."
    await trainer.train_from_stream([hallucination])
    
    # Validate and correct
    result = await validator.teach_and_evaluate(
        "hall_test",
        hallucination,
        KnowledgeType.FACTUAL
    )
    
    if result.truth_level == TruthLevel.HALLUCINATION:
        print(f"   ❌ Hallucination detected and marked for decay")
        print(f"   📚 Teaching correct patterns from ground truth...")
        
        # The validator automatically corrects via the trainer
        related = validator.teacher.get_related_truths("moon")
        if related:
            for truth in related:
                print(f"   → Teaching: {truth.expected_output}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("The biological intelligence system can learn creatively")
    print("while staying grounded in reality through validation!")
    print("=" * 80)
    
    return trainer, validator


async def test_swarm_consensus():
    """Test how swarm agents reach consensus on knowledge validation"""
    
    print("\n" + "=" * 80)
    print("SWARM CONSENSUS VALIDATION TEST")
    print("=" * 80)
    
    # Import swarm agents
    from src.swarm_agents import (
        MolecularLearningAgent,
        SemanticLearningAgent,
        ConceptualLearningAgent
    )
    
    # Create mini swarm
    agents = [
        MolecularLearningAgent(),
        SemanticLearningAgent(),
        ConceptualLearningAgent()
    ]
    
    # Give them validation capabilities
    for agent in agents:
        agent.validate_knowledge = lambda content: asyncio.coroutine(
            lambda: "true" in content.lower() or "fact" in content.lower()
        )()
    
    # Create evaluator with swarm
    from src.teacher_evaluator import BiologicalEvaluator
    evaluator = BiologicalEvaluator(swarm_agents=agents)
    
    # Test consensus
    test_statements = [
        ("fact_1", "This is a true fact", True),
        ("false_1", "This is false information", False),
        ("mixed_1", "This contains true and false", True),
    ]
    
    print("\nTesting swarm consensus:")
    for stmt_id, content, expected in test_statements:
        consensus = await evaluator._check_swarm_consensus(content)
        status = "✅" if (consensus > 0.5) == expected else "❌"
        print(f"   {status} '{content[:30]}...' - Consensus: {consensus:.2f}")
    
    print("\nSwarm validation ensures distributed truth verification!")


if __name__ == "__main__":
    print("Starting integrated validation tests...\n")
    
    # Run main test
    asyncio.run(test_with_validation())
    
    # Run swarm consensus test
    # asyncio.run(test_swarm_consensus())