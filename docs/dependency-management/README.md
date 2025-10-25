# Dependency Management Documentation

## Overview

The Sutra Dependency Management System provides comprehensive security scanning, vulnerability tracking, and compliance monitoring for all project dependencies across Python, Rust, and Node.js ecosystems.

## Documentation Index

### Getting Started
- **[Quick Start Guide](./QUICK_START.md)** - Get up and running in 5 minutes
- **[Architecture Overview](./ARCHITECTURE.md)** - System components and data flow
- **[Design Document](./DESIGN.md)** - Design principles and decisions

### User Guides
- **[Control Center Guide](./guides/CONTROL_CENTER.md)** - Using the UI dashboard
- **[CLI Guide](./guides/CLI_USAGE.md)** - Command-line scanning
- **[API Reference](./guides/API_REFERENCE.md)** - REST API documentation

### Configuration
- **[GitHub Actions Setup](./config/GITHUB_ACTIONS.md)** - CI/CD integration
- **[Dependabot Configuration](./config/DEPENDABOT.md)** - Automated updates
- **[Security Policies](./config/SECURITY_POLICIES.md)** - Custom rules

### Operations
- **[Monitoring Guide](./ops/MONITORING.md)** - Metrics and alerts
- **[Incident Response](./ops/INCIDENT_RESPONSE.md)** - Vulnerability handling
- **[Maintenance](./ops/MAINTENANCE.md)** - Regular tasks

### Development
- **[Plugin Development](./dev/PLUGIN_DEVELOPMENT.md)** - Extending scanners
- **[Testing Guide](./dev/TESTING.md)** - Test strategies
- **[Contributing](./dev/CONTRIBUTING.md)** - How to contribute

## Key Features

### 🔍 Vulnerability Scanning
- Multi-language support (Python, Rust, Node.js)
- Real-time detection with severity classification
- CVE tracking and remediation guidance
- Automated PR blocking for critical issues

### 📊 SBOM Generation
- CycloneDX format support
- SPDX format support
- Component inventory tracking
- License compliance reporting

### 🔄 Automated Updates
- Dependabot integration
- Grouped update strategies
- Security update prioritization
- Version pinning policies

### 📈 Health Monitoring
- 0-100 health score system
- Package-level metrics
- Trend analysis
- Historical tracking

### 🎨 Control Center UI
- Real-time dashboard
- Interactive vulnerability explorer
- Filter and search capabilities
- SBOM download

## Quick Reference

### Common Commands

```bash
# Run local scan
./scripts/scan-dependencies.sh

# Check Python vulnerabilities
pip-audit

# Check Rust vulnerabilities
cargo audit

# Check Node.js vulnerabilities
npm audit

# Generate SBOM
curl http://localhost:8000/api/dependencies/sbom > sbom.json
```

### API Endpoints

```
GET  /api/dependencies/scan         - Trigger full scan
GET  /api/dependencies/summary      - Get summary stats
GET  /api/dependencies/sbom         - Generate SBOM
GET  /api/dependencies/vulnerabilities - List vulnerabilities
```

### Environment Variables

```bash
SUTRA_SCAN_TIMEOUT=30           # Scan timeout in seconds
SUTRA_CACHE_TTL=3600           # Cache duration in seconds
SUTRA_MAX_PARALLEL_SCANS=10    # Parallel scan limit
```

## Integration Points

### With Sutra Control Center
- Integrated dashboard at `/dependencies`
- Backend service in `packages/sutra-control/backend/`
- React component in `packages/sutra-control/src/components/`

### With CI/CD
- GitHub Actions workflow in `.github/workflows/`
- Dependabot config in `.github/dependabot.yml`
- Pre-commit hooks available

### With Monitoring
- Prometheus metrics exported
- Health endpoint at `/health`
- Event logging for audit trails

## Security Considerations

### Threat Model
- Supply chain attacks
- Typosquatting
- Dependency confusion
- License violations

### Controls
- Daily vulnerability scanning
- Automated update PRs
- License compliance checking
- SBOM tracking

## Performance

### Scanning Performance
- Parallel package scanning: 10 concurrent
- Average scan time: <30s for full project
- Cache TTL: 1 hour
- Incremental scanning supported

### Storage
- Reports stored as JSON
- 30-day retention policy
- Compression for archives
- ~1MB per full scan report

## Troubleshooting

### Common Issues

**Scanner not found:**
```bash
pip install pip-audit
cargo install cargo-audit
```

**Scan timeout:**
- Increase timeout in environment
- Check network connectivity
- Verify registry access

**No vulnerabilities detected:**
- Ensure tools are updated
- Check if packages are installed
- Verify scan coverage

## Support

- **Documentation:** This directory
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Security:** security@sutra.ai

## License

Dependency Management System is part of Sutra AI and follows the same licensing model:
- Simple Edition: Free (no license required)
- Community Edition: $99/month
- Enterprise Edition: $999/month

---

**Last Updated:** 2025-10-25
**Version:** 1.0.0
**Status:** Production Ready