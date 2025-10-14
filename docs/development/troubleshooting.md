# Troubleshooting

Common issues and resolutions when working with Sutra Models.

## Environment

### Virtualenv Not Activated
Symptoms:
- `ModuleNotFoundError`
- Wrong Python interpreter

Fix:
```bash
source venv/bin/activate
which python
```

### PYTHONPATH Missing
Symptoms:
- Imports fail for local packages during tests

Fix:
```bash
export PYTHONPATH=packages/sutra-core:packages/sutra-hybrid
```

## Hybrid (TF-IDF) Persistence

### NotFittedError on Reload
Symptoms:
- `sklearn.exceptions.NotFittedError: The TF-IDF vectorizer is not fitted`

Causes:
- Loading legacy data without vectorizer state

Fixes:
1. Remove legacy knowledge directory and re-run demo:
   ```bash
   rm -rf ./demo_knowledge
   python packages/sutra-hybrid/examples/hybrid_demo.py
   ```
2. Ensure the new pickle state file exists after save:
   - `tfidf_vectorizer.pkl` alongside `embeddings.json`

## Linting and Formatting

### Line Length (E501)
Symptoms:
- `E501 line too long`

Fix:
- Break long strings across lines
- Use Black with line-length 79 or refactor long f-strings

### Import Order
Symptoms:
- isort changes after commit

Fix:
```bash
isort packages/
```

## Testing

### Flaky Tests
Symptoms:
- Tests fail inconsistently

Fix:
```bash
rm -rf .pytest_cache packages/*/.pytest_cache
pytest -vv
```

### Slow Tests
Tips:
- Limit to specific tests while iterating
- Use `-k` to filter by test name

## Reasoning Behavior

### No Results from Semantic Search
Possible causes and actions:
- Threshold too high → lower `threshold`
- Small vocabulary (TF-IDF) → add more training data
- Using TF-IDF instead of semantic embeddings → install `sentence-transformers`

### Concept Strength Not Increasing
Cause:
- `concept.access()` not called in your traversal code

Action:
- Ensure access is called during reasoning/traversal

## Storage

### Data Not Saving
Check:
- Permissions on storage directory
- Exceptions in logs

Manual save:
```bash
python -m sutra_api.main  # starts server
curl -X POST http://localhost:8000/save
```

### Corrupted JSON
Symptoms:
- JSON decode errors on load

Fix:
- Validate JSON with a linter
- Restore from backup or rebuild knowledge base

## API Server

### Port Already in Use
Fix:
```bash
lsof -i :8000
kill -9 <PID>
```

### CORS Errors in Browser
Fix:
- Adjust allowed origins via env:
  ```bash
  export SUTRA_ALLOW_ORIGINS='["http://localhost:3000"]'
  ```

## Performance

### High Memory Usage
Actions:
- Limit the number of learned concepts
- Use TF-IDF embeddings instead of semantic embeddings
- Periodically persist and restart

### Slow Queries
Actions:
- Reduce `max_steps` and `num_paths`
- Optimize association patterns
- Profile hotspots with `cProfile` or similar tools
