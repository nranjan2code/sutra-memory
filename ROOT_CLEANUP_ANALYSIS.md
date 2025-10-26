# Root Directory Cleanup Analysis & Plan

## 🔍 Current State Analysis

### Files to Clean Up

#### Docker Compose Files (Root)
- `docker-compose-grid.yml` - **USED by sutra-deploy.sh** ⚠️
- `docker-compose-secure.yml` - Security variant
- `docker-compose.dev.yml` - Development variant

#### Scripts Directory
- `scripts/generate-secrets.sh` - **USED by sutra-deploy.sh** ⚠️
- `scripts/detect-changes.sh` - Development utility
- `scripts/diagnose-docker-pipeline.sh` - Debugging
- `scripts/smoke-test-embeddings.sh` - Production validation
- `scripts/test-embedding-ha.sh` - HA testing
- Other utility scripts...

#### Other Files
- `selective-update-commands.sh` - Legacy build script
- `docker/haproxy*.cfg` - HAProxy configs

## 📋 Cleanup Strategy

### Phase 1: Safe Consolidation (Immediate)
1. **Move essential scripts** to `sutrabuild/scripts/`
2. **Create compatibility shims** for `sutra-deploy.sh`
3. **Consolidate compose files** into unified system
4. **Remove redundant files**

### Phase 2: Update sutra-deploy.sh (Next)
1. **Update references** to use consolidated locations
2. **Test compatibility** with existing workflows
3. **Update documentation** references

### Phase 3: Complete Cleanup (Future)
1. **Remove deprecated files** in v3.0.0
2. **Update all references** in documentation
3. **Final validation**

## 🎯 Action Plan

### Immediate Actions
- [x] Analyze current dependencies
- [ ] Move scripts to sutrabuild/
- [ ] Create consolidated compose
- [ ] Update sutra-deploy.sh references
- [ ] Test compatibility

### Files to Move/Consolidate
- `scripts/generate-secrets.sh` → `sutrabuild/scripts/`
- `scripts/smoke-test-embeddings.sh` → `sutrabuild/scripts/`
- `docker/haproxy*.cfg` → `sutrabuild/docker/configs/`
- `docker-compose-*.yml` → `sutrabuild/compose/`

### Files to Remove
- `selective-update-commands.sh` (deprecated)
- Unused development scripts
- Redundant compose variants