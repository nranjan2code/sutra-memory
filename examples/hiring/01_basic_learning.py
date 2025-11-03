#!/usr/bin/env python3
"""
Basic Learning: Ingesting Candidate Data into Sutra

This example shows how to feed structured hiring data into Sutra's
unified learning pipeline. All data goes through TCP storage server.

Prerequisites:
- Sutra storage server running (sutra deploy)
- Resume parser output (or manual structured data)
"""

import asyncio
from sutra_storage_client_tcp import SutraStorageClient


async def learn_candidate_profile():
    """Learn a single candidate's complete profile"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        # Candidate: Sarah Chen
        # Source: Resume parser output → structured data
        
        # 1. Basic identity (Entity type)
        concept_id = await client.learn_concept(
            "Sarah Chen is a Senior Backend Engineer"
        )
        print(f"✓ Learned identity: {concept_id}")
        
        # 2. Technical skills (Entity + Definitional types)
        await client.learn_concept(
            "Sarah Chen has 6 years experience with Go programming language"
        )
        await client.learn_concept(
            "Sarah Chen has 4 years experience with Kubernetes"
        )
        await client.learn_concept(
            "Sarah Chen has experience with PostgreSQL, Redis, and Kafka"
        )
        print("✓ Learned technical skills")
        
        # 3. Career timeline (Temporal type)
        await client.learn_concept(
            "Sarah Chen was Junior Developer at StartupX from January 2018 to December 2019"
        )
        await client.learn_concept(
            "Sarah Chen was Backend Engineer at TechCorp from January 2020 to March 2023"
        )
        await client.learn_concept(
            "Sarah Chen is Senior Backend Engineer at BigCo since April 2023"
        )
        print("✓ Learned career progression")
        
        # 4. Achievements (Event type with temporal bounds)
        await client.learn_concept(
            "Sarah Chen led microservices migration project in Q2 2022"
        )
        await client.learn_concept(
            "Sarah Chen reduced API latency by 60% in August 2022"
        )
        await client.learn_concept(
            "Sarah Chen mentored 3 junior engineers in 2023"
        )
        print("✓ Learned achievements")
        
        # 5. Domain expertise (Causal + Definitional)
        await client.learn_concept(
            "Sarah Chen designed distributed payment processing system"
        )
        await client.learn_concept(
            "Sarah Chen has expertise in high-throughput event streaming"
        )
        print("✓ Learned domain expertise")
        
        # 6. Education (Temporal + Entity)
        await client.learn_concept(
            "Sarah Chen has BS in Computer Science from MIT, graduated 2018"
        )
        print("✓ Learned education")
        
        # 7. Preferences/Constraints (Condition type)
        await client.learn_concept(
            "Sarah Chen prefers remote work or hybrid arrangements"
        )
        await client.learn_concept(
            "Sarah Chen requires minimum 180K salary"
        )
        print("✓ Learned preferences")
        
        print("\n✅ Complete candidate profile learned!")
        print(f"   Candidate: Sarah Chen")
        print(f"   Concepts ingested: ~15")
        print(f"   Semantic types: Entity, Temporal, Event, Causal, Condition")
        
    finally:
        await client.disconnect()


async def learn_job_requirements():
    """Learn job posting requirements"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        # Job: Senior Backend Engineer role
        
        # 1. Role definition (Definitional)
        await client.learn_concept(
            "Senior Backend Engineer role requires distributed systems expertise"
        )
        await client.learn_concept(
            "Senior Backend Engineer must have 5+ years backend development experience"
        )
        print("✓ Learned role requirements")
        
        # 2. Technical requirements (Rule + Condition types)
        await client.learn_concept(
            "Senior Backend Engineer must have experience with Go or Rust"
        )
        await client.learn_concept(
            "Senior Backend Engineer should have Kubernetes experience"
        )
        await client.learn_concept(
            "Senior Backend Engineer requires database design expertise"
        )
        print("✓ Learned technical requirements")
        
        # 3. Soft skills (Definitional)
        await client.learn_concept(
            "Senior Backend Engineer should demonstrate leadership and mentoring"
        )
        await client.learn_concept(
            "Senior Backend Engineer must have strong communication skills"
        )
        print("✓ Learned soft skill requirements")
        
        # 4. Compensation (Quantitative)
        await client.learn_concept(
            "Senior Backend Engineer role offers 170K to 220K salary range"
        )
        await client.learn_concept(
            "Senior Backend Engineer role includes equity compensation"
        )
        print("✓ Learned compensation details")
        
        print("\n✅ Job requirements learned!")
        
    finally:
        await client.disconnect()


async def learn_hiring_outcome():
    """Learn from a past hiring decision (training data)"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        # Previous hire: Alex Kumar (successful)
        
        # 1. Hiring decision (Event + Temporal)
        await client.learn_concept(
            "Alex Kumar hired as Backend Engineer on March 15 2024"
        )
        
        # 2. Onboarding outcome (Temporal + Causal)
        await client.learn_concept(
            "Alex Kumar completed onboarding successfully within 2 weeks"
        )
        await client.learn_concept(
            "Alex Kumar shipped first major feature in 30 days"
        )
        
        # 3. Performance (Event + Quantitative)
        await client.learn_concept(
            "Alex Kumar received Exceeds Expectations in Q2 2024 review"
        )
        await client.learn_concept(
            "Alex Kumar promoted to Senior Backend Engineer in September 2024"
        )
        
        # 4. Key success factors (Causal - this is critical!)
        await client.learn_concept(
            "Alex Kumar's Kubernetes experience enabled fast onboarding"
        )
        await client.learn_concept(
            "Alex Kumar's microservices background led to successful migration project"
        )
        
        print("✅ Successful hire outcome learned!")
        print("   This becomes training data for future candidate matching")
        
    finally:
        await client.disconnect()


async def learn_hiring_failure():
    """Learn from a hiring mistake (equally valuable)"""
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        # Previous hire: Bob Smith (unsuccessful)
        
        # 1. Hiring decision
        await client.learn_concept(
            "Bob Smith hired as Backend Engineer on January 10 2024"
        )
        
        # 2. Warning signs (Temporal + Event)
        await client.learn_concept(
            "Bob Smith struggled with distributed systems during onboarding"
        )
        await client.learn_concept(
            "Bob Smith required additional support for microservices concepts"
        )
        
        # 3. Outcome (Event + Temporal)
        await client.learn_concept(
            "Bob Smith left company in May 2024 after 4 months"
        )
        
        # 4. Root cause (Causal - learn from mistakes!)
        await client.learn_concept(
            "Bob Smith's lack of distributed systems experience caused onboarding difficulties"
        )
        await client.learn_concept(
            "Mismatch between Bob Smith's skills and role requirements led to departure"
        )
        
        print("✅ Hiring failure learned!")
        print("   System now knows what to avoid in future hires")
        
    finally:
        await client.disconnect()


async def bulk_learning_from_ats():
    """
    Realistic integration: Parse ATS export and bulk ingest
    
    Typical flow:
    1. Export candidates from ATS (CSV/JSON)
    2. Parse structured fields
    3. Batch learn to Sutra
    """
    
    client = SutraStorageClient()
    await client.connect()
    
    try:
        # Simulated ATS export data
        candidates = [
            {
                "name": "Maria Garcia",
                "title": "Frontend Engineer",
                "years_experience": 4,
                "skills": ["React", "TypeScript", "Next.js"],
                "previous_company": "StartupY",
                "tenure": "2020-2024"
            },
            {
                "name": "David Lee",
                "title": "DevOps Engineer",
                "years_experience": 7,
                "skills": ["Kubernetes", "Terraform", "AWS"],
                "previous_company": "CloudCo",
                "tenure": "2017-2024"
            }
        ]
        
        for candidate in candidates:
            # Convert structured data to natural language for Sutra
            # (Sutra's semantic analyzer extracts structure)
            
            await client.learn_concept(
                f"{candidate['name']} is a {candidate['title']} with "
                f"{candidate['years_experience']} years experience"
            )
            
            skills_str = ", ".join(candidate['skills'])
            await client.learn_concept(
                f"{candidate['name']} has skills in {skills_str}"
            )
            
            await client.learn_concept(
                f"{candidate['name']} worked at {candidate['previous_company']} "
                f"from {candidate['tenure']}"
            )
            
            print(f"✓ Learned {candidate['name']}")
        
        print("\n✅ Bulk learning complete!")
        print(f"   Candidates processed: {len(candidates)}")
        
    finally:
        await client.disconnect()


async def main():
    """Run all learning examples"""
    
    print("=" * 60)
    print("Sutra Hiring: Basic Learning Examples")
    print("=" * 60)
    print()
    
    print("Example 1: Learn Complete Candidate Profile")
    print("-" * 60)
    await learn_candidate_profile()
    print()
    
    print("Example 2: Learn Job Requirements")
    print("-" * 60)
    await learn_job_requirements()
    print()
    
    print("Example 3: Learn Successful Hire (Training Data)")
    print("-" * 60)
    await learn_hiring_outcome()
    print()
    
    print("Example 4: Learn Hiring Failure (Also Training Data!)")
    print("-" * 60)
    await learn_hiring_failure()
    print()
    
    print("Example 5: Bulk Learning from ATS Export")
    print("-" * 60)
    await bulk_learning_from_ats()
    print()
    
    print("=" * 60)
    print("✅ All examples complete!")
    print()
    print("Next steps:")
    print("  → Run 02_temporal_queries.py to query career timelines")
    print("  → Run 03_causal_analysis.py to analyze hiring patterns")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
