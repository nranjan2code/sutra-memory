# Security Fix: JWT Secret Leak

## Issue
The repository contains a hardcoded default JWT secret key in `packages/sutra-api/sutra_api/config.py`:
```python
jwt_secret_key: str = "INSECURE_DEFAULT_SECRET_CHANGE_IN_PRODUCTION"
```

This is a security vulnerability if:
1. Production systems are using this default value
2. Any tokens signed with this key are in circulation

## Immediate Actions Required

### 1. Rotate JWT Secret (If Using Default in Production)
If your production system is using the default secret, you MUST rotate it immediately:

```bash
# Generate a new secure secret
NEW_SECRET=$(openssl rand -hex 32)

# Update your production environment
export SUTRA_JWT_SECRET_KEY="$NEW_SECRET"

# Restart services
docker-compose restart sutra-api
```

**Note:** All existing JWT tokens will be invalidated and users will need to re-authenticate.

### 2. Update All Deployment Configurations

#### Docker Compose (.env file)
```bash
# Add to .env file (do NOT commit this file)
SUTRA_JWT_SECRET_KEY=$(openssl rand -hex 32)
```

#### Kubernetes Secret
```bash
# Create Kubernetes secret
kubectl create secret generic sutra-jwt-secret \
  --from-literal=SUTRA_JWT_SECRET_KEY=$(openssl rand -hex 32) \
  --namespace sutra
```

#### Docker Swarm Secret
```bash
# Create Docker secret
openssl rand -hex 32 | docker secret create sutra_jwt_secret -
```

### 3. GitHub Actions Setup
The release workflow needs the secret for building:

```bash
# Add secret to GitHub repository
gh secret set SUTRA_JWT_SECRET_KEY --body "$(openssl rand -hex 32)"
```

Or via GitHub UI:
1. Go to repository Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Name: `SUTRA_JWT_SECRET_KEY`
4. Value: (paste output of `openssl rand -hex 32`)

### 4. Update Deployment Scripts

Add validation to deployment scripts:

```bash
# In sutra-deploy.sh or similar
if [ -z "$SUTRA_JWT_SECRET_KEY" ]; then
    echo "ERROR: SUTRA_JWT_SECRET_KEY not set"
    echo "Generate with: openssl rand -hex 32"
    exit 1
fi
```

### 5. Verify Fix

After applying changes:

```bash
# Test that the API requires JWT secret
docker-compose up sutra-api

# Should see error if JWT_SECRET_KEY not set:
# ValueError: JWT secret key is required. Set SUTRA_JWT_SECRET_KEY environment variable.
```

## Code Changes Applied

1. **Removed hardcoded default** from `config.py`
2. **Made jwt_secret_key Optional** and added validation
3. **Added __post_init__ validation** to fail fast if secret not provided
4. **Updated GitHub Actions** workflow to use repository secret

## Prevention

### Add to .gitignore
Already present, but verify these patterns exist:
```
.env
.env.*
*secret*
```

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check for potential secrets in staged files
if git diff --cached | grep -iE "(jwt_secret|api_key|password|token).*=.*['\"].*['\"]"; then
    echo "ERROR: Potential secret found in staged changes"
    exit 1
fi
```

### GitHub Secret Scanning
Enable GitHub's secret scanning:
1. Repository Settings > Code security and analysis
2. Enable "Secret scanning"
3. Enable "Push protection"

## Verification Checklist

- [ ] Generated new JWT secret with `openssl rand -hex 32`
- [ ] Updated production environment variables
- [ ] Restarted production services
- [ ] Added SUTRA_JWT_SECRET_KEY to GitHub Actions secrets
- [ ] Verified API starts successfully with new secret
- [ ] Tested authentication flow works with new secret
- [ ] Documented secret location in team password manager
- [ ] Removed hardcoded default from codebase
- [ ] All deployment configs reference environment variable

## Contact
If you need assistance with secret rotation or have questions about this security fix, contact your security team.
