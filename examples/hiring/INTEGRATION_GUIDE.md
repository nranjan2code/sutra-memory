# Integration Guide: Sutra + Existing Hiring Stack

**Last Updated:** November 3, 2025

---

## Architecture Overview

Sutra does NOT replace your ATS/HRIS. It augments your existing hiring workflow with explainable reasoning.

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXISTING HIRING STACK                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐         ┌──────────────────┐              │
│  │  ATS            │         │  Calendar        │              │
│  │  (Greenhouse,   │         │  (Calendly,      │              │
│  │   Lever, etc.)  │         │   GoodTime)      │              │
│  └────────┬────────┘         └──────────────────┘              │
│           │                                                      │
│           │ Webhook: New Candidate                              │
│           ▼                                                      │
│  ┌─────────────────┐                                            │
│  │ Resume Parser   │                                            │
│  │ (Textkernel,    │                                            │
│  │  Sovren, etc.)  │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│           │ Structured Data (JSON)                              │
│           ▼                                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              INTEGRATION LAYER (Python)                  │   │
│  │  - Transform ATS data → Sutra concepts                   │   │
│  │  - Batch ingest to Sutra Storage                         │   │
│  │  - Query Sutra for candidate matches                     │   │
│  │  - Send recommendations back to ATS                      │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                        │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              SUTRA AI STORAGE                            │   │
│  │  - Learn candidate profiles                              │   │
│  │  - Track hiring outcomes                                 │   │
│  │  - Build organizational knowledge graph                  │   │
│  │  - Provide explainable recommendations                   │   │
│  └──────────────────────┬──────────────────────────────────┘   │
│                         │                                        │
│                         │ Query API                              │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         HIRING DASHBOARD (Custom UI)                     │   │
│  │  - Natural language queries                              │   │
│  │  - Explainable candidate matches                         │   │
│  │  - Temporal/causal analytics                             │   │
│  │  - Compliance audit trails                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### 1. Data Ingestion (ATS → Sutra)

**Trigger:** ATS webhook when candidate applies

**Flow:**
```python
# ATS sends webhook
{
  "event": "candidate.created",
  "candidate_id": "12345",
  "data": { ... }
}

# Your integration service
@app.post("/webhooks/ats/candidate_created")
async def handle_new_candidate(payload: dict):
    # 1. Parse ATS data
    candidate = parse_ats_candidate(payload)
    
    # 2. Extract structured fields
    resume_data = parse_resume(candidate.resume_url)
    
    # 3. Transform to Sutra concepts
    concepts = transform_to_concepts(candidate, resume_data)
    
    # 4. Batch ingest to Sutra
    await sutra_client.batch_learn(concepts)
    
    # 5. Store mapping (ATS ID ↔ Sutra concept IDs)
    await db.save_mapping(candidate.id, concepts)
```

**Data Transformation Example:**
```python
def transform_to_concepts(candidate, resume_data):
    """Convert ATS data to natural language concepts"""
    
    concepts = []
    
    # Identity
    concepts.append(
        f"{candidate.name} is a {resume_data.current_title}"
    )
    
    # Skills with temporal context
    for skill in resume_data.skills:
        if skill.years_experience:
            concepts.append(
                f"{candidate.name} has {skill.years_experience} years "
                f"experience with {skill.name}"
            )
        else:
            concepts.append(
                f"{candidate.name} has experience with {skill.name}"
            )
    
    # Work history (temporal)
    for job in resume_data.work_history:
        concepts.append(
            f"{candidate.name} was {job.title} at {job.company} "
            f"from {job.start_date} to {job.end_date or 'present'}"
        )
        
        # Achievements (events)
        for achievement in job.achievements:
            concepts.append(
                f"{candidate.name} {achievement.description} "
                f"at {job.company}"
            )
    
    # Education
    for edu in resume_data.education:
        concepts.append(
            f"{candidate.name} has {edu.degree} in {edu.field} "
            f"from {edu.institution}, graduated {edu.year}"
        )
    
    return concepts
```

---

### 2. Candidate Matching (Sutra → ATS)

**Trigger:** Recruiter searches for candidates

**Flow:**
```python
@app.get("/api/candidate_search")
async def search_candidates(role_id: str, query: str):
    # 1. Get job requirements
    job = await db.get_job(role_id)
    
    # 2. Query Sutra for matches
    results = await sutra_client.query_graph(
        f"Who should we interview for {job.title}?",
        max_paths=50
    )
    
    # 3. Extract candidate IDs and reasoning
    candidates = []
    for path in results['paths']:
        candidate_id = extract_candidate_id(path)
        reasoning = extract_reasoning_paths(path)
        confidence = path['confidence']
        
        candidates.append({
            'candidate_id': candidate_id,
            'confidence': confidence,
            'reasoning': reasoning,
            'ats_link': f"{ATS_URL}/candidates/{candidate_id}"
        })
    
    # 4. Sort by confidence
    candidates.sort(key=lambda x: x['confidence'], reverse=True)
    
    # 5. Return to dashboard
    return {
        'query': query,
        'job': job,
        'candidates': candidates[:20],  # Top 20
        'timestamp': datetime.utcnow()
    }
```

---

### 3. Outcome Learning (ATS → Sutra)

**Trigger:** Candidate hired, rejected, or leaves company

**Flow:**
```python
# Webhook: Candidate hired
@app.post("/webhooks/ats/candidate_hired")
async def handle_hire(payload: dict):
    candidate_id = payload['candidate_id']
    job_id = payload['job_id']
    start_date = payload['start_date']
    
    # Learn hiring decision
    await sutra_client.learn_concept(
        f"Candidate {candidate_id} hired for {job_id} on {start_date}"
    )
    
    # Schedule follow-up outcome tracking
    schedule_onboarding_check(candidate_id, start_date + timedelta(days=30))
    schedule_performance_check(candidate_id, start_date + timedelta(days=90))


# Scheduled: Track onboarding outcome
async def check_onboarding_outcome(candidate_id: str):
    # Get from HRIS or survey
    outcome = await hris.get_onboarding_status(candidate_id)
    
    if outcome.status == 'successful':
        await sutra_client.learn_concept(
            f"Candidate {candidate_id} completed onboarding successfully "
            f"within {outcome.duration_days} days"
        )
    else:
        await sutra_client.learn_concept(
            f"Candidate {candidate_id} struggled with {outcome.issue} "
            f"during onboarding"
        )


# Scheduled: Track performance
async def check_performance(candidate_id: str):
    review = await hris.get_performance_review(candidate_id)
    
    await sutra_client.learn_concept(
        f"Candidate {candidate_id} received {review.rating} "
        f"in performance review"
    )
    
    # Learn causal factors if available
    if review.strengths:
        for strength in review.strengths:
            await sutra_client.learn_concept(
                f"Candidate {candidate_id}'s {strength} contributed to success"
            )
```

---

### 4. Analytics Dashboard

**Query Interface:**
```python
@app.get("/api/analytics/query")
async def run_analytics_query(query: str):
    """Natural language analytics queries"""
    
    # Examples:
    # - "What causes successful backend hires?"
    # - "Which interviewers have highest accuracy?"
    # - "Show hiring trends for 2024"
    
    results = await sutra_client.query_graph(query, max_paths=30)
    
    # Extract insights
    insights = extract_insights(results)
    
    return {
        'query': query,
        'insights': insights,
        'reasoning_paths': results['paths'],
        'confidence': results.get('overall_confidence'),
        'timestamp': datetime.utcnow()
    }
```

---

## Sample Integration Code

### Complete Integration Service

```python
# integration_service.py

from fastapi import FastAPI, BackgroundTasks
from sutra_storage_client_tcp import SutraStorageClient
import httpx
from typing import List, Dict

app = FastAPI()

# Sutra client (connection pool)
sutra_client = SutraStorageClient()

# ATS configuration
ATS_BASE_URL = os.getenv("ATS_BASE_URL")
ATS_API_KEY = os.getenv("ATS_API_KEY")


@app.on_event("startup")
async def startup():
    await sutra_client.connect()


@app.on_event("shutdown")
async def shutdown():
    await sutra_client.disconnect()


# === ATS Webhooks ===

@app.post("/webhooks/greenhouse/candidate_created")
async def greenhouse_candidate_created(payload: dict, bg: BackgroundTasks):
    """Greenhouse webhook: New candidate applied"""
    
    # Process in background to return quickly
    bg.add_task(ingest_candidate, payload)
    return {"status": "accepted"}


async def ingest_candidate(payload: dict):
    """Background task: Parse and learn candidate"""
    
    candidate_id = payload['candidate']['id']
    
    # 1. Fetch full candidate data from Greenhouse API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ATS_BASE_URL}/candidates/{candidate_id}",
            headers={"Authorization": f"Bearer {ATS_API_KEY}"}
        )
        candidate = response.json()
    
    # 2. Parse resume (if available)
    resume_data = None
    if candidate.get('resume_url'):
        resume_data = await parse_resume(candidate['resume_url'])
    
    # 3. Transform to concepts
    concepts = transform_candidate_to_concepts(candidate, resume_data)
    
    # 4. Batch learn to Sutra
    for concept in concepts:
        await sutra_client.learn_concept(concept)
    
    print(f"✅ Learned candidate {candidate_id}: {len(concepts)} concepts")


@app.post("/webhooks/greenhouse/candidate_hired")
async def greenhouse_candidate_hired(payload: dict, bg: BackgroundTasks):
    """Greenhouse webhook: Candidate hired"""
    
    candidate_id = payload['candidate']['id']
    job_id = payload['job']['id']
    
    # Learn hiring decision
    await sutra_client.learn_concept(
        f"Candidate {candidate_id} hired for job {job_id} "
        f"on {payload['hired_at']}"
    )
    
    # Schedule outcome tracking
    bg.add_task(schedule_outcome_tracking, candidate_id)
    
    return {"status": "accepted"}


# === Candidate Search API ===

@app.get("/api/search/candidates")
async def search_candidates(job_id: str, limit: int = 20):
    """Find candidates matching job requirements"""
    
    # 1. Get job requirements
    job = await fetch_job_from_ats(job_id)
    
    # 2. Construct Sutra query
    query = f"Who should we interview for {job['title']}?"
    
    # 3. Query Sutra
    results = await sutra_client.query_graph(query, max_paths=50)
    
    # 4. Rank and format
    candidates = rank_candidates(results, limit)
    
    return {
        'job': job,
        'candidates': candidates,
        'query': query
    }


# === Analytics API ===

@app.get("/api/analytics")
async def run_analytics(query: str):
    """Natural language analytics queries"""
    
    results = await sutra_client.query_graph(query, max_paths=30)
    
    return {
        'query': query,
        'results': results,
        'timestamp': datetime.utcnow()
    }


# === Helper Functions ===

def transform_candidate_to_concepts(candidate: dict, resume_data: dict) -> List[str]:
    """Convert ATS candidate data to Sutra concepts"""
    
    concepts = []
    
    name = candidate.get('name', f"Candidate {candidate['id']}")
    
    # Basic info
    if candidate.get('current_title'):
        concepts.append(f"{name} is a {candidate['current_title']}")
    
    # Skills from resume
    if resume_data and resume_data.get('skills'):
        for skill in resume_data['skills']:
            concepts.append(f"{name} has experience with {skill}")
    
    # Work history
    if resume_data and resume_data.get('work_history'):
        for job in resume_data['work_history']:
            concepts.append(
                f"{name} was {job['title']} at {job['company']} "
                f"from {job['start_date']} to {job.get('end_date', 'present')}"
            )
    
    return concepts


async def fetch_job_from_ats(job_id: str) -> dict:
    """Fetch job details from ATS"""
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{ATS_BASE_URL}/jobs/{job_id}",
            headers={"Authorization": f"Bearer {ATS_API_KEY}"}
        )
        return response.json()


def rank_candidates(results: dict, limit: int) -> List[dict]:
    """Extract and rank candidates from Sutra results"""
    
    candidates = []
    
    for path in results.get('paths', []):
        # Extract candidate info from reasoning path
        # (Implementation depends on your data structure)
        candidates.append({
            'confidence': path.get('confidence'),
            'reasoning': path.get('description'),
            # ... other fields
        })
    
    # Sort by confidence
    candidates.sort(key=lambda x: x['confidence'], reverse=True)
    
    return candidates[:limit]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

---

## Deployment

### Docker Compose Setup

```yaml
version: '3.8'

services:
  # Sutra services (from main deployment)
  sutra-storage:
    image: sutra-storage:latest
    ports:
      - "7000:7000"
    environment:
      - SUTRA_EDITION=simple
  
  sutra-api:
    image: sutra-api:latest
    ports:
      - "8000:8000"
    depends_on:
      - sutra-storage
  
  # Integration service
  hiring-integration:
    build: ./integration
    ports:
      - "8080:8080"
    environment:
      - SUTRA_STORAGE_URL=tcp://sutra-storage:7000
      - ATS_BASE_URL=https://harvest.greenhouse.io/v1
      - ATS_API_KEY=${GREENHOUSE_API_KEY}
    depends_on:
      - sutra-storage
```

---

## Testing Integration

```bash
# 1. Start Sutra
SUTRA_EDITION=simple sutra deploy

# 2. Start integration service
docker-compose up hiring-integration

# 3. Test candidate ingestion
curl -X POST http://localhost:8080/webhooks/greenhouse/candidate_created \
  -H "Content-Type: application/json" \
  -d @test_candidate.json

# 4. Test candidate search
curl "http://localhost:8080/api/search/candidates?job_id=12345"

# 5. Test analytics
curl "http://localhost:8080/api/analytics?query=What+causes+successful+hires"
```

---

## Next Steps

1. **Review** `01_basic_learning.py` to understand data ingestion
2. **Customize** transformation logic for your ATS data schema
3. **Deploy** integration service alongside Sutra
4. **Configure** ATS webhooks to point to your integration service
5. **Monitor** ingestion and query performance
6. **Iterate** based on hiring manager feedback

---

## Support

- **Documentation:** `/docs/README.md`
- **Examples:** `/samples/hiring/*.py`
- **Issues:** GitHub Issues
