# Dependency Management System Design

## Design Principles

### 1. Zero-Trust Security Model
- **Assume Breach**: Every dependency is a potential vulnerability
- **Defense in Depth**: Multiple layers of scanning and validation
- **Fail Secure**: Block operations when security cannot be verified
- **Continuous Validation**: Regular rescanning of all dependencies

### 2. Developer Experience First
- **Minimal Friction**: Automated scanning without blocking development
- **Clear Actionability**: Specific remediation steps for each issue
- **Progressive Disclosure**: Summary view with drill-down capabilities
- **Context-Aware**: Understand development vs production dependencies

### 3. Multi-Language Parity
- **Consistent Interface**: Same UI/API regardless of language
- **Unified Reporting**: Single dashboard for all ecosystems
- **Cross-Language Insights**: Identify common vulnerabilities
- **Native Tool Integration**: Use best-in-class tools per language

## User Interface Design

### Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Dependency Management                    [Scan] [Download]  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Health   │ │ Total    │ │ Vulns    │ │ Updates  │      │
│  │   85     │ │  347     │ │   3      │ │   24     │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
├─────────────────────────────────────────────────────────────┤
│  [Overview] [Vulnerabilities] [Details]                      │
├─────────────────────────────────────────────────────────────┤
│  Package Overview                                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Package │ Type │ Deps │ Outdated │ Vulns │ Action │    │
│  ├─────────┼──────┼──────┼──────────┼───────┼────────┤    │
│  │ sutra-  │ Py   │  23  │    2     │   0   │   ▼    │    │
│  │ storage │ Rust │  45  │    5     │   1   │   ▼    │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Visual Design System

#### Color Palette
- **Critical**: `#D32F2F` (Red 700)
- **High**: `#F57C00` (Orange 700)
- **Medium**: `#FBC02D` (Yellow 700)
- **Low**: `#388E3C` (Green 700)
- **Info**: `#1976D2` (Blue 700)
- **Success**: `#4CAF50` (Green 500)

#### Typography
- **Headers**: Roboto Medium, 24px
- **Subheaders**: Roboto Regular, 18px
- **Body**: Roboto Regular, 14px
- **Monospace**: Roboto Mono, 13px

#### Icons
- **Vulnerability**: Shield with exclamation
- **Update**: Arrow circle up
- **License**: Document with checkmark
- **SBOM**: Package with list

### Interaction Patterns

#### Progressive Disclosure
1. **Level 1**: Summary cards (4 metrics)
2. **Level 2**: Package list with key metrics
3. **Level 3**: Expanded package with dependencies
4. **Level 4**: Individual dependency details

#### Real-time Updates
- WebSocket connection for scan progress
- Optimistic UI updates for user actions
- Background refresh every 5 minutes
- Visual indicators for stale data (>1 hour)

## API Design

### RESTful Endpoints

```yaml
/api/dependencies:
  /scan:
    GET: Trigger full system scan
    Response: { job_id, status, estimated_time }
  
  /summary:
    GET: Get summary statistics
    Response: { packages, dependencies, vulnerabilities, health_score }
  
  /packages:
    GET: List all packages with health
    Response: [{ name, type, health, metrics }]
  
  /packages/{id}:
    GET: Get package details
    Response: { package, dependencies, vulnerabilities }
  
  /vulnerabilities:
    GET: List all vulnerabilities
    Query: severity, package_type, limit, offset
    Response: { items: [], total, page }
  
  /sbom:
    GET: Generate SBOM
    Query: format (cyclonedx|spdx)
    Response: SBOM document
  
  /licenses:
    GET: Get license report
    Response: { compliant: [], violations: [] }
```

### WebSocket Events

```javascript
// Client → Server
{ type: "SCAN_START", payload: { packages: ["all"] } }
{ type: "SCAN_CANCEL", payload: { job_id: "..." } }

// Server → Client
{ type: "SCAN_PROGRESS", payload: { job_id, percent, current_package } }
{ type: "SCAN_COMPLETE", payload: { job_id, summary } }
{ type: "VULNERABILITY_FOUND", payload: { package, severity, cve } }
{ type: "UPDATE_AVAILABLE", payload: { package, current, latest } }
```

## Data Models

### Core Entities

```typescript
interface Dependency {
  id: string;
  name: string;
  version: string;
  latest_version?: string;
  package_type: 'python' | 'rust' | 'node';
  package_file: string;
  license?: string;
  homepage?: string;
  repository?: string;
  outdated: boolean;
  dev_dependency: boolean;
  vulnerabilities: Vulnerability[];
  metadata: Record<string, any>;
}

interface Vulnerability {
  id: string;
  package: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  cve?: string;
  cwe?: string;
  description: string;
  published_date: Date;
  fixed_version?: string;
  current_version: string;
  references: string[];
  cvss_score?: number;
  exploit_available: boolean;
}

interface PackageHealth {
  package_path: string;
  package_name: string;
  package_type: string;
  total_dependencies: number;
  direct_dependencies: number;
  transitive_dependencies: number;
  outdated_count: number;
  vulnerable_count: number;
  critical_vulns: number;
  high_vulns: number;
  license_issues: number;
  last_scanned: Date;
  scan_duration_ms: number;
  health_score: number;
  dependencies: Dependency[];
}

interface ScanResult {
  id: string;
  timestamp: Date;
  duration_ms: number;
  packages_scanned: number;
  total_dependencies: number;
  vulnerabilities_found: number;
  updates_available: number;
  license_violations: number;
  health_score: number;
  packages: PackageHealth[];
}
```

## Security Design

### Threat Model

#### External Threats
1. **Supply Chain Attacks**: Malicious dependencies
2. **Typosquatting**: Similar package names
3. **Dependency Confusion**: Internal vs external packages
4. **Zero-Day Vulnerabilities**: Unknown vulnerabilities

#### Internal Threats
1. **Outdated Dependencies**: Known vulnerabilities
2. **License Violations**: Legal compliance issues
3. **Transitive Dependencies**: Hidden vulnerabilities
4. **Development Dependencies**: Production leakage

### Security Controls

#### Preventive Controls
- Dependency pinning in production
- Private registry for internal packages
- Automated security scanning in CI/CD
- License approval workflow

#### Detective Controls
- Daily vulnerability scanning
- Real-time dependency monitoring
- SBOM generation and tracking
- Anomaly detection for new dependencies

#### Corrective Controls
- Automated PR creation for updates
- Rollback capabilities
- Patch management process
- Incident response playbooks

## Performance Design

### Scanning Strategy

```python
class ScanStrategy:
    def __init__(self):
        self.max_parallel = 10
        self.timeout_per_package = 30  # seconds
        self.cache_ttl = 3600  # 1 hour
        self.batch_size = 50
    
    async def scan(self, packages):
        # Parallel scanning with rate limiting
        semaphore = asyncio.Semaphore(self.max_parallel)
        
        async def scan_with_limit(package):
            async with semaphore:
                return await self.scan_package(package)
        
        # Batch processing for large sets
        results = []
        for batch in chunks(packages, self.batch_size):
            batch_results = await asyncio.gather(
                *[scan_with_limit(p) for p in batch],
                return_exceptions=True
            )
            results.extend(batch_results)
        
        return results
```

### Caching Strategy

#### Cache Layers
1. **Memory Cache**: 5-minute TTL for hot data
2. **Redis Cache**: 1-hour TTL for scan results
3. **File Cache**: 24-hour TTL for SBOM documents
4. **CDN Cache**: 7-day TTL for static reports

#### Cache Invalidation
- Package update → Invalidate package cache
- New vulnerability → Invalidate all caches
- Manual scan → Force cache refresh
- Time-based → Automatic expiration

### Database Design

```sql
-- Scan results table
CREATE TABLE scan_results (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    duration_ms INTEGER,
    health_score INTEGER,
    summary JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vulnerabilities table
CREATE TABLE vulnerabilities (
    id UUID PRIMARY KEY,
    scan_id UUID REFERENCES scan_results(id),
    package_name TEXT NOT NULL,
    package_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    cve TEXT,
    description TEXT,
    fixed_version TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_vulnerabilities_severity ON vulnerabilities(severity);
CREATE INDEX idx_vulnerabilities_package ON vulnerabilities(package_name);
CREATE INDEX idx_scan_results_timestamp ON scan_results(timestamp DESC);
```

## Integration Design

### CI/CD Integration

```yaml
# GitHub Actions Integration
- name: Dependency Security Check
  uses: sutra-ai/dependency-check@v1
  with:
    fail-on-severity: critical
    create-issues: true
    update-pr: true
    sbom-format: cyclonedx
```

### IDE Integration

```json
// VS Code Extension Settings
{
  "sutra.dependencies.autoScan": true,
  "sutra.dependencies.scanOnSave": false,
  "sutra.dependencies.showInlineWarnings": true,
  "sutra.dependencies.severityThreshold": "high"
}
```

### Monitoring Integration

```python
# Prometheus Metrics
dependency_scan_duration = Histogram(
    'dependency_scan_duration_seconds',
    'Time spent scanning dependencies',
    ['package_type']
)

vulnerability_count = Gauge(
    'dependency_vulnerabilities_total',
    'Total number of vulnerabilities',
    ['severity', 'package_type']
)

health_score = Gauge(
    'dependency_health_score',
    'Overall dependency health score',
    ['package']
)
```

## Extensibility Design

### Plugin Architecture

```python
class ScannerPlugin(ABC):
    @abstractmethod
    async def scan(self, package_path: Path) -> List[Vulnerability]:
        pass
    
    @abstractmethod
    def supports(self, package_type: str) -> bool:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass

class PluginRegistry:
    def __init__(self):
        self.plugins = {}
    
    def register(self, plugin: ScannerPlugin):
        self.plugins[plugin.name] = plugin
    
    async def scan_with_plugins(self, package):
        results = []
        for plugin in self.plugins.values():
            if plugin.supports(package.type):
                result = await plugin.scan(package.path)
                results.extend(result)
        return results
```

### Custom Rules Engine

```yaml
# Custom security policy
rules:
  - id: no-gpl-licenses
    description: Prohibit GPL licenses
    severity: high
    condition: |
      dependency.license in ['GPL', 'AGPL', 'LGPL']
    
  - id: critical-update-required
    description: Require immediate critical updates
    severity: critical
    condition: |
      vulnerability.severity == 'critical' and
      vulnerability.age_days > 7
  
  - id: max-dependency-age
    description: Flag old dependencies
    severity: medium
    condition: |
      dependency.last_update_days > 365
```

## Error Handling Design

### Error Categories

1. **Transient Errors**: Retry with exponential backoff
2. **Configuration Errors**: Fail fast with clear message
3. **Permission Errors**: Request elevation or skip
4. **Network Errors**: Use cached data if available
5. **Tool Errors**: Fallback to alternative scanner

### Error Recovery

```python
class ErrorRecovery:
    async def with_retry(self, func, max_attempts=3):
        for attempt in range(max_attempts):
            try:
                return await func()
            except TransientError as e:
                if attempt == max_attempts - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
            except ToolNotFoundError:
                return self.use_fallback_scanner()
            except NetworkError:
                return self.use_cached_result()
```

## Testing Strategy

### Test Levels

1. **Unit Tests**: Scanner logic, data models
2. **Integration Tests**: API endpoints, tool integration
3. **E2E Tests**: Full scan workflow, UI interactions
4. **Performance Tests**: Scan speed, concurrent operations
5. **Security Tests**: Vulnerability detection accuracy

### Test Data

```python
# Synthetic vulnerability data for testing
TEST_VULNERABILITIES = [
    {
        "package": "test-package",
        "version": "1.0.0",
        "severity": "critical",
        "cve": "CVE-2024-0001",
        "description": "Test critical vulnerability"
    }
]

# Mock scanner for testing
class MockScanner:
    def __init__(self, vulnerabilities=None):
        self.vulnerabilities = vulnerabilities or []
    
    async def scan(self, package):
        # Simulate scan delay
        await asyncio.sleep(0.1)
        return self.vulnerabilities
```

## Documentation Strategy

### User Documentation
- Quick start guide
- API reference
- Configuration guide
- Troubleshooting guide
- Best practices

### Developer Documentation
- Architecture overview
- Plugin development guide
- API client examples
- Contributing guidelines
- Security policy

### Operational Documentation
- Deployment guide
- Monitoring setup
- Backup procedures
- Incident response
- Maintenance schedule