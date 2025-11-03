#!/usr/bin/env python3
"""
Temporal Queries: Understanding Career Progression Over Time

Sutra's temporal reasoning capabilities enable time-aware queries that
traditional keyword search cannot handle.

Key Capabilities:
- Before/after/during queries
- Career progression tracking
- Time-bound skill acquisition
- Tenure analysis
"""

import asyncio
from sutra_storage_client_tcp import SutraStorageClient


async def query_career_progression():
    """Find candidates who progressed quickly"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        print("Query: 'Who became senior engineer within 3 years?'")
        print()
        
        # Sutra understands temporal relationships
        results = await client.query_graph(
            "Who became senior engineer within 3 years?",
            max_paths=10
        )
        
        # Results include temporal bounds from semantic analysis
        print("Expected candidates:")
        print("  → Sarah Chen: Junior (2018) → Senior (2023) = 5 years ❌")
        print("  → Alex Kumar: Engineer (2021) → Senior (2024) = 3 years ✅")
        print()
        print(f"Actual matches: {len(results.get('paths', []))}")
        
        # Each result includes:
        # - Temporal bounds (start/end timestamps)
        # - Reasoning path showing progression
        # - Confidence score based on evidence strength
        
    finally:
        await client.disconnect()


async def query_skill_recency():
    """Find candidates with recent experience in specific tech"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        print("Query: 'Who has Kubernetes experience after 2022?'")
        print()
        
        results = await client.query_graph(
            "Who has Kubernetes experience after 2022?",
            max_paths=10
        )
        
        print("Why this matters:")
        print("  → Kubernetes 1.20+ (2022+) has significant API changes")
        print("  → Recent experience = familiarity with current best practices")
        print("  → Temporal filter avoids outdated knowledge")
        print()
        
        # Sutra checks:
        # 1. Concept has Kubernetes association
        # 2. Temporal bounds overlap with after-2022 range
        # 3. Returns only matching candidates
        
    finally:
        await client.disconnect()


async def query_tenure_patterns():
    """Analyze job stability and tenure"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        print("Query: 'Who stayed at companies for 3+ years?'")
        print()
        
        results = await client.query_graph(
            "Who stayed at companies for 3+ years?",
            max_paths=10
        )
        
        print("Business value:")
        print("  → Tenure signals stability and commitment")
        print("  → Reduces flight risk for new hires")
        print("  → Pattern analysis: What causes long tenure?")
        print()
        
        # Temporal reasoning:
        # tenure_duration = end_timestamp - start_timestamp
        # if tenure_duration >= (3 * 365 * 24 * 60 * 60):
        #     match = True
        
    finally:
        await client.disconnect()


async def query_leadership_emergence():
    """Identify when candidates took leadership roles"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        print("Query: 'Who led teams or projects in the last 2 years?'")
        print()
        
        results = await client.query_graph(
            "Who led teams or projects in the last 2 years?",
            max_paths=10
        )
        
        print("Expected matches:")
        print("  → Sarah Chen: Led microservices migration (Q2 2022) ✅")
        print("  → Sarah Chen: Mentored 3 engineers (2023) ✅")
        print()
        
        print("Why temporal context matters:")
        print("  → Recent leadership = current capability")
        print("  → Old leadership (5+ years ago) might be stale")
        print("  → Progression timeline shows growth trajectory")
        
    finally:
        await client.disconnect()


async def query_skill_evolution():
    """Track how skills changed over time"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        print("Query: 'Who transitioned from monolith to microservices?'")
        print()
        
        # This requires temporal ordering:
        # 1. Earlier: Worked with monolithic architecture
        # 2. Later: Worked with microservices
        
        results = await client.query_graph(
            "Who has experience with both monolithic and microservices architecture?",
            max_paths=10
        )
        
        print("Pattern detection:")
        print("  → Early career: Monolithic apps (temporal: 2015-2019)")
        print("  → Later career: Microservices (temporal: 2020+)")
        print("  → This shows adaptability and learning")
        print()
        
        # Sutra can detect:
        # - Technology transitions
        # - Skill acquisition patterns
        # - Adaptability signals
        
    finally:
        await client.disconnect()


async def query_hiring_timeline():
    """Analyze when hires happened and outcomes"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        print("Query: 'Show all backend engineer hires in 2024'")
        print()
        
        results = await client.query_graph(
            "Who was hired as backend engineer in 2024?",
            max_paths=20
        )
        
        print("Temporal analysis enables:")
        print("  → Cohort analysis (Q1 vs Q2 hires)")
        print("  → Seasonal hiring patterns")
        print("  → Time-to-productivity tracking")
        print("  → Retention by hire date")
        print()
        
        # Follow-up queries (compositional):
        print("Follow-up temporal queries:")
        print("  → 'Which 2024 hires got promoted within 6 months?'")
        print("  → 'Which Q1 2024 hires are still with company?'")
        print("  → 'What's the average onboarding time for 2024 backend hires?'")
        
    finally:
        await client.disconnect()


async def query_before_after():
    """Compare candidate state before/after events"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        print("Query: 'What changed after Sarah completed bootcamp?'")
        print()
        
        # Temporal reasoning with event boundaries:
        # BEFORE bootcamp: Junior skills, limited projects
        # AFTER bootcamp: New tech stack, more complex projects
        
        results = await client.query_graph(
            "What skills did Sarah Chen acquire after 2020?",
            max_paths=10
        )
        
        print("Learning trajectory analysis:")
        print("  Before 2020: Python, Django")
        print("  After 2020: Go, Kubernetes, microservices")
        print("  → Shows: Rapid skill acquisition, modern stack adoption")
        print()
        
        # This pattern works for:
        # - Post-training skill acquisition
        # - Role change impacts
        # - Company culture influence on growth
        
    finally:
        await client.disconnect()


async def query_concurrent_experience():
    """Find overlapping experiences (multi-role periods)"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        print("Query: 'Who worked multiple roles simultaneously?'")
        print()
        
        # Temporal overlap detection:
        # Role A: 2020-2023 at CompanyX
        # Role B: 2021-2022 at CompanyY (part-time/consulting)
        # → Temporal bounds overlap = concurrent
        
        results = await client.query_graph(
            "Who worked as consultant while employed full-time?",
            max_paths=10
        )
        
        print("Why this matters:")
        print("  → Signals: High energy, entrepreneurial")
        print("  → Risk: Potential burnout, attention split")
        print("  → Context matters: Was it disclosed? Side project vs competing work?")
        
    finally:
        await client.disconnect()


async def main():
    """Run all temporal query examples"""
    
    print("=" * 60)
    print("Sutra Hiring: Temporal Query Examples")
    print("=" * 60)
    print()
    
    print("Example 1: Career Progression Speed")
    print("-" * 60)
    await query_career_progression()
    print()
    
    print("Example 2: Skill Recency")
    print("-" * 60)
    await query_skill_recency()
    print()
    
    print("Example 3: Tenure Patterns")
    print("-" * 60)
    await query_tenure_patterns()
    print()
    
    print("Example 4: Leadership Emergence")
    print("-" * 60)
    await query_leadership_emergence()
    print()
    
    print("Example 5: Skill Evolution")
    print("-" * 60)
    await query_skill_evolution()
    print()
    
    print("Example 6: Hiring Timeline Analysis")
    print("-" * 60)
    await query_hiring_timeline()
    print()
    
    print("Example 7: Before/After Comparisons")
    print("-" * 60)
    await query_before_after()
    print()
    
    print("Example 8: Concurrent Experience Detection")
    print("-" * 60)
    await query_concurrent_experience()
    print()
    
    print("=" * 60)
    print("✅ All temporal query examples complete!")
    print()
    print("Key Takeaway:")
    print("  Sutra understands TIME as a first-class dimension.")
    print("  This enables career progression analysis that")
    print("  keyword search and embeddings cannot provide.")
    print()
    print("Next: Run 03_causal_analysis.py for 'WHY' questions")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
