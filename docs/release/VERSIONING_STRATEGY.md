# Versioning Strategy

**Semantic versioning guidelines for Sutra AI releases**

---

## Overview

Sutra AI follows [Semantic Versioning 2.0.0](https://semver.org/) to provide predictable, meaningful version numbers for customers and developers.

---

## Version Number Format

```
MAJOR.MINOR.PATCH

Example: 2.1.3
         │ │ │
         │ │ └─ PATCH: Bug fixes (backward compatible)
         │ └─── MINOR: New features (backward compatible)
         └───── MAJOR: Breaking changes
```

---

## When to Bump Versions

### PATCH Version (2.0.0 → 2.0.1)

**Increment when:**
- ✅ Bug fixes
- ✅ Security patches
- ✅ Documentation updates
- ✅ Internal refactoring (no API changes)
- ✅ Performance improvements (no behavior changes)
- ✅ Dependency updates (patch versions only)

**Examples:**
- Fixed memory leak in storage server
- Patched SQL injection vulnerability
- Corrected typo in API error message
- Optimized database query performance

**Customer Impact:**
- No code changes required
- Safe to deploy immediately
- Recommended for all customers

**Command:**
```bash
./sutra-deploy.sh release patch
```

---

### MINOR Version (2.0.0 → 2.1.0)

**Increment when:**
- ✅ New features added
- ✅ New API endpoints
- ✅ New optional parameters
- ✅ Functionality improvements
- ✅ Deprecated features (still working)
- ✅ New configuration options

**Examples:**
- Added semantic search API endpoint
- New NLG service with streaming support
- Added optional `timeout` parameter to queries
- Introduced bulk ingestion API
- Added support for new embedding models

**Customer Impact:**
- Can use new features
- Existing code continues to work
- No migration required
- Opt-in to new functionality

**Command:**
```bash
./sutra-deploy.sh release minor
```

---

### MAJOR Version (2.0.0 → 3.0.0)

**Increment when:**
- ⚠️ Breaking API changes
- ⚠️ Removed deprecated features
- ⚠️ Changed default behavior
- ⚠️ Renamed/removed endpoints
- ⚠️ Changed data formats
- ⚠️ Incompatible architecture changes

**Examples:**
- Changed API response format from XML to JSON
- Removed deprecated `/v1/query` endpoint
- Changed authentication from API key to OAuth
- Migrated from gRPC to REST API
- Required new database schema

**Customer Impact:**
- **Requires code changes**
- Migration guide needed
- Testing required before upgrade
- Advance notice required (30+ days)
- May need customer support calls

**Command:**
```bash
./sutra-deploy.sh release major
```

**Process:**
1. Announce breaking changes 30+ days in advance
2. Provide detailed migration guide
3. Offer beta testing period
4. Schedule customer support calls
5. Monitor closely after release

---

## Special Versions

### Pre-release Versions

**Format:** `MAJOR.MINOR.PATCH-prerelease`

**Examples:**
- `2.1.0-alpha.1` - Early development, unstable
- `2.1.0-beta.1` - Feature complete, testing
- `2.1.0-rc.1` - Release candidate, final testing

**Use for:**
- Internal testing
- Beta customer programs
- Early access features

**Command:**
```bash
# Manual - not in automated script
echo "2.1.0-beta.1" > VERSION
git tag v2.1.0-beta.1
git push origin v2.1.0-beta.1
```

### Build Metadata

**Format:** `MAJOR.MINOR.PATCH+build`

**Examples:**
- `2.0.1+20251026` - Build date
- `2.0.1+sha.abc1234` - Git commit

**Use for:**
- Tracking specific builds
- Debugging customer issues
- Internal build identification

---

## Decision Tree

```
┌─────────────────────────────────────┐
│  Does it break existing code?      │
└─────────────┬───────────────────────┘
              │
        Yes ──┴── No
         │         │
         ▼         ▼
    ┌────────┐  ┌────────────────────┐
    │ MAJOR  │  │ Does it add a      │
    │ 3.0.0  │  │ new feature?       │
    └────────┘  └─────┬──────────────┘
                      │
                Yes ──┴── No
                 │         │
                 ▼         ▼
            ┌────────┐  ┌────────┐
            │ MINOR  │  │ PATCH  │
            │ 2.1.0  │  │ 2.0.1  │
            └────────┘  └────────┘
```

---

## Breaking Changes Checklist

Before marking something as a breaking change, consider:

### API Changes
- [ ] Removed endpoint or parameter
- [ ] Changed response format
- [ ] Changed required parameters
- [ ] Changed default behavior
- [ ] Changed error codes

### Data Changes
- [ ] Database schema migration required
- [ ] File format changed
- [ ] Configuration format changed
- [ ] Data migration required

### Behavior Changes
- [ ] Changed algorithm output
- [ ] Changed calculation method
- [ ] Changed error handling
- [ ] Changed performance characteristics

**If ANY are checked → MAJOR version bump**

---

## Release Schedule

### Recommended for Small Teams

| Version Type | Frequency | Planning |
|-------------|-----------|----------|
| **Patch** | As needed | 1-2 days |
| **Minor** | 2-4 weeks | 1 week |
| **Major** | 3-6 months | 1-2 months |

### Patch Releases
- **When:** Critical bugs, security issues
- **Process:** Fast track, minimal testing
- **Notification:** Email customers if security-related

### Minor Releases
- **When:** Sprint/iteration complete
- **Process:** Full testing, release notes
- **Notification:** Changelog, optional announcement

### Major Releases
- **When:** Significant milestone reached
- **Process:** Extensive testing, migration guide, customer communication
- **Notification:** 30+ day advance notice, webinar, support calls

---

## Version History Example

### Sutra AI Version History

```
v3.0.0 (Future) - Breaking Changes
├── Changed API from gRPC to REST
├── Removed deprecated endpoints
└── New authentication system

v2.2.0 - Feature Release
├── Added streaming responses
├── New bulk ingestion API
└── Support for custom embeddings

v2.1.1 - Patch Release
├── Fixed memory leak in storage
└── Updated dependencies

v2.1.0 - Feature Release
├── Semantic search API
├── NLG service improvements
└── Grid monitoring dashboard

v2.0.1 - Patch Release
├── Fixed edge case in HNSW search
└── Security patch for embedding service

v2.0.0 - Major Release (Initial Customer Release)
├── Production-ready system
├── Complete API documentation
└── Enterprise edition support
```

---

## Customer Communication Templates

### Patch Release Announcement

```
Subject: Sutra AI v2.0.1 - Bug Fix Release

We've released v2.0.1 with bug fixes and improvements.

What's Fixed:
- Fixed memory leak in storage server
- Corrected error handling in API

Upgrade: Safe to deploy immediately
Compatibility: Fully backward compatible
Action Required: None (optional upgrade)

Details: https://github.com/YOUR_ORG/sutra-models/releases/v2.0.1
```

### Minor Release Announcement

```
Subject: Sutra AI v2.1.0 - New Features Available

We're excited to announce v2.1.0 with new features!

What's New:
- Semantic search API for advanced queries
- Streaming response support
- Bulk ingestion for faster data loading

Upgrade: Recommended within 2 weeks
Compatibility: Fully backward compatible
Action Required: Review new features documentation

Details: https://github.com/YOUR_ORG/sutra-models/releases/v2.1.0
```

### Major Release Announcement (30 Days Before)

```
Subject: [Action Required] Sutra AI v3.0.0 Coming Soon

IMPORTANT: Breaking changes in v3.0.0 releasing in 30 days.

What's Changing:
- API migrating from gRPC to REST
- Authentication system updated
- Deprecated endpoints removed

Action Required:
1. Review migration guide: [link]
2. Schedule upgrade testing
3. Contact support for migration help

Timeline:
- Today: Announcement
- +2 weeks: Beta available
- +4 weeks: Final release

Support: We're here to help! Schedule a call: [link]
```

---

## Version Compatibility Matrix

### Edition Compatibility

| Version | Simple | Community | Enterprise |
|---------|--------|-----------|------------|
| 2.0.x   | ✅     | ✅        | ✅         |
| 2.1.x   | ✅     | ✅        | ✅         |
| 2.2.x   | ✅     | ✅        | ✅         |
| 3.0.x   | ✅*    | ✅        | ✅         |

*Limited features in Simple edition

### Upgrade Paths

```
Current → Target    | Effort | Breaking Changes
--------------------|--------|------------------
2.0.x → 2.0.y      | Low    | None
2.0.x → 2.1.x      | Low    | None
2.0.x → 3.0.x      | High   | Yes - see migration guide
2.1.x → 2.2.x      | Low    | None
2.x.x → 3.0.x      | High   | Yes - see migration guide
```

---

## Best Practices

### DO
✅ Follow semantic versioning strictly
✅ Document ALL changes in CHANGELOG.md
✅ Test thoroughly before major releases
✅ Communicate breaking changes early
✅ Provide migration guides for major versions
✅ Keep backward compatibility for minor/patch
✅ Tag releases in git

### DON'T
❌ Skip version numbers (2.0.0 → 2.2.0)
❌ Reuse version numbers
❌ Make breaking changes in patch/minor releases
❌ Release without testing
❌ Surprise customers with breaking changes
❌ Forget to update CHANGELOG.md

---

## FAQ

**Q: Can I skip from 2.0.0 to 2.2.0?**
A: No, increment sequentially: 2.0.0 → 2.1.0 → 2.2.0

**Q: I made a mistake in a release. What now?**
A: Create a new patch release fixing the issue. Don't delete/reuse versions.

**Q: When should I use pre-release versions?**
A: For beta testing with select customers before official release.

**Q: How long should I support old versions?**
A: Support at least the current major version and previous major version.

**Q: Can I backport fixes to old versions?**
A: Yes, create branch from old tag and release patch (e.g., 2.0.2 after 2.1.0 is out).

---

## Tools & Automation

### Check Version
```bash
./sutra-deploy.sh version
cat VERSION
```

### Validate Version Format
```bash
# Should match: MAJOR.MINOR.PATCH
cat VERSION | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$'
```

### Compare Versions
```bash
# List all tags
git tag -l

# Compare two versions
git diff v2.0.0..v2.1.0
```

---

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Release Process](RELEASE_PROCESS.md)
- [Quick Reference](QUICK_REFERENCE.md)

---

**Last Updated:** October 26, 2025  
**Version:** 1.0
