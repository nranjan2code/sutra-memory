# Desktop Edition - Release Checklist

Use this checklist for every release of the Desktop Edition.

## Pre-Release (Development)

### Code Quality
- [ ] Web client builds without errors (`npm run build`)
- [ ] TypeScript type checking passes (`npm run type-check`)
- [ ] No console errors in browser devtools
- [ ] All pages render correctly (Chat, Knowledge, Analytics, Settings)
- [ ] Responsive design works on mobile/tablet/desktop

### Functionality Testing
- [ ] Chat interface works
  - [ ] Can send messages
  - [ ] `/learn` command works
  - [ ] Responses display correctly
  - [ ] Message history persists
- [ ] Knowledge browser works
  - [ ] Concepts display in grid
  - [ ] Search/filter works
  - [ ] Delete concept works
  - [ ] Add concept modal works
- [ ] Analytics dashboard shows correct data
  - [ ] Stats update in real-time
  - [ ] Charts/metrics display
- [ ] Settings page accessible
  - [ ] Clear history works
  - [ ] Version info correct

### API Integration
- [ ] `/health` endpoint responds
- [ ] `/api/v1/learn` endpoint works
- [ ] `/api/v1/reason` endpoint works
- [ ] `/api/v1/concepts` endpoint works
- [ ] `/api/v1/stats` endpoint works
- [ ] Error handling works gracefully

### Docker Build
- [ ] Storage server image builds (`sutra-storage:latest`)
- [ ] API server image builds (`sutra-api:latest`)
- [ ] Web client image builds (`sutra-desktop-web:latest`)
- [ ] All services start successfully
- [ ] Health checks pass for all services
- [ ] Services can communicate with each other

## Build Process

### Automated Build
```bash
# Run the complete build script
./desktop/build-desktop-edition.sh
```

Expected output:
- [ ] All 8 steps complete successfully
- [ ] No errors in build logs
- [ ] All Docker images created
- [ ] All containers running
- [ ] End-to-end validation passes

### Manual Verification
```bash
# Check running containers
docker ps | grep sutra-desktop

# Expected: 4 containers
# - sutra-desktop-web
# - sutra-desktop-api
# - sutra-desktop-storage
# - sutra-desktop-embedding
```

## Testing

### Quick Validation
```bash
./desktop/validate-desktop.sh
```

Expected:
- [ ] All checks pass (✓)
- [ ] Web client responds
- [ ] API endpoints work
- [ ] Stats show correct data

### Manual UI Testing
1. [ ] Open http://localhost:3000
2. [ ] Navigate to all pages (Chat, Knowledge, Analytics, Settings)
3. [ ] Test chat: Ask "What can you do?"
4. [ ] Test learning: `/learn The sky is blue`
5. [ ] Test knowledge: Browse concepts, search, delete
6. [ ] Test analytics: Verify metrics update
7. [ ] Test settings: Clear history

### Performance Testing
- [ ] Initial page load < 2 seconds
- [ ] Query response < 1 second
- [ ] Learning < 2 seconds
- [ ] No memory leaks (check browser devtools)
- [ ] Docker containers stable (no restarts)

### Error Handling
- [ ] Invalid query shows error message
- [ ] Network error handled gracefully
- [ ] Empty states display correctly
- [ ] Loading states show spinners

## Documentation

### User Documentation
- [ ] `desktop/DESKTOP_EDITION.md` up to date
- [ ] Installation instructions clear
- [ ] Usage examples work
- [ ] Troubleshooting section complete
- [ ] Screenshots current (if any)

### Developer Documentation  
- [ ] `desktop/web-client/README.md` accurate
- [ ] API client documented
- [ ] Component structure clear
- [ ] Build process documented
- [ ] Architecture diagrams current

### Release Notes
- [ ] Version number updated
- [ ] Changelog created/updated
- [ ] Breaking changes noted
- [ ] New features listed
- [ ] Bug fixes documented

## Pre-Release Checklist

### Version Management
- [ ] Update version in `desktop/web-client/package.json`
- [ ] Update version in `desktop/DESKTOP_EDITION.md`
- [ ] Tag git commit: `git tag v1.0.0`

### Image Tags
- [ ] Docker images tagged with version number
- [ ] Images pushed to registry (if applicable)
- [ ] `latest` tag updated

### Security
- [ ] No hardcoded secrets in code
- [ ] Environment variables documented
- [ ] CORS configured correctly
- [ ] Ports bound to localhost only

## Release

### Create Release Package
```bash
# Export compose file
cp .sutra/compose/desktop.yml desktop/docker-compose.yml

# Create release archive
tar -czf sutra-desktop-v1.0.0.tar.gz \
    desktop/ \
    .sutra/compose/desktop.yml \
    README.md \
    LICENSE
```

### Distribution
- [ ] Release archive created
- [ ] Upload to GitHub releases
- [ ] Docker images available
- [ ] Installation instructions tested on clean system

### Announcement
- [ ] Update main README.md
- [ ] Blog post/announcement (if applicable)
- [ ] Social media (if applicable)
- [ ] Documentation site updated

## Post-Release

### Monitoring
- [ ] Check for user issues
- [ ] Monitor GitHub issues
- [ ] Watch Docker Hub downloads (if applicable)

### User Feedback
- [ ] Collect feedback
- [ ] Prioritize issues
- [ ] Plan next release

## Rollback Plan

If release has critical issues:

```bash
# Stop current version
./desktop/scripts/docker-start.sh stop

# Revert git tag
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0

# Rebuild previous version
git checkout <previous-tag>
./desktop/build-desktop-edition.sh
```

## Emergency Contacts

- **Build Issues**: Check `desktop/build-desktop-edition.sh` logs
- **Runtime Issues**: Check `docker compose logs`
- **Web Client Issues**: Check browser devtools console
- **API Issues**: Check `docker logs sutra-desktop-api`

## Sign-Off

- [ ] Build lead approval: ________________
- [ ] QA approval: ________________
- [ ] Product approval: ________________
- [ ] Release date: ________________
- [ ] Release tag: ________________

---

**Template Version**: 1.0.0  
**Last Updated**: January 21, 2026
