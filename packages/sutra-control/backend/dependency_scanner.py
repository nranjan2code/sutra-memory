"""
Dependency Scanner Service for Sutra Control Center
Monitors all package dependencies across Python, Rust, and Node.js
"""

import json
import subprocess
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import toml
import re
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

class PackageType(Enum):
    PYTHON = "python"
    RUST = "rust"
    NODE = "node"

class VulnerabilitySeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    INFO = "info"

@dataclass
class Vulnerability:
    package: str
    severity: VulnerabilitySeverity
    cve: Optional[str]
    description: str
    fixed_version: Optional[str]
    current_version: str

@dataclass
class Dependency:
    name: str
    version: str
    latest_version: Optional[str]
    package_type: PackageType
    package_file: str
    license: Optional[str]
    outdated: bool = False
    vulnerabilities: List[Vulnerability] = None

    def __post_init__(self):
        if self.vulnerabilities is None:
            self.vulnerabilities = []

@dataclass
class PackageHealth:
    package_path: str
    package_type: PackageType
    total_dependencies: int
    outdated_count: int
    vulnerable_count: int
    critical_vulns: int
    high_vulns: int
    last_scanned: datetime
    dependencies: List[Dependency]

class DependencyScanner:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.cache = {}
        self.last_scan = None
        
    async def scan_all_packages(self) -> Dict[str, PackageHealth]:
        """Scan all packages in the project for dependencies and vulnerabilities"""
        results = {}
        
        # Find all package locations
        packages = await self._discover_packages()
        
        # Scan each package in parallel
        tasks = []
        for pkg_path, pkg_type in packages:
            tasks.append(self._scan_package(pkg_path, pkg_type))
        
        health_reports = await asyncio.gather(*tasks, return_exceptions=True)
        
        for report in health_reports:
            if isinstance(report, PackageHealth):
                results[report.package_path] = report
            else:
                logger.error(f"Error scanning package: {report}")
        
        self.last_scan = datetime.now()
        return results
    
    async def _discover_packages(self) -> List[tuple]:
        """Discover all packages in the project"""
        packages = []
        
        # Root level packages
        if (self.project_root / "package.json").exists():
            packages.append((str(self.project_root), PackageType.NODE))
        if (self.project_root / "requirements-dev.txt").exists():
            packages.append((str(self.project_root), PackageType.PYTHON))
        if (self.project_root / "Cargo.toml").exists():
            packages.append((str(self.project_root), PackageType.RUST))
        
        # Package subdirectories
        packages_dir = self.project_root / "packages"
        if packages_dir.exists():
            for pkg_dir in packages_dir.iterdir():
                if pkg_dir.is_dir():
                    if (pkg_dir / "package.json").exists():
                        packages.append((str(pkg_dir), PackageType.NODE))
                    if (pkg_dir / "requirements.txt").exists():
                        packages.append((str(pkg_dir), PackageType.PYTHON))
                    if (pkg_dir / "pyproject.toml").exists():
                        packages.append((str(pkg_dir), PackageType.PYTHON))
                    if (pkg_dir / "Cargo.toml").exists():
                        packages.append((str(pkg_dir), PackageType.RUST))
        
        return packages
    
    async def _scan_package(self, pkg_path: str, pkg_type: PackageType) -> PackageHealth:
        """Scan a single package for dependencies and vulnerabilities"""
        dependencies = []
        
        if pkg_type == PackageType.PYTHON:
            dependencies = await self._scan_python_package(pkg_path)
        elif pkg_type == PackageType.RUST:
            dependencies = await self._scan_rust_package(pkg_path)
        elif pkg_type == PackageType.NODE:
            dependencies = await self._scan_node_package(pkg_path)
        
        # Calculate health metrics
        outdated_count = sum(1 for d in dependencies if d.outdated)
        vulnerable_count = sum(1 for d in dependencies if d.vulnerabilities)
        critical_vulns = sum(
            1 for d in dependencies 
            for v in d.vulnerabilities 
            if v.severity == VulnerabilitySeverity.CRITICAL
        )
        high_vulns = sum(
            1 for d in dependencies 
            for v in d.vulnerabilities 
            if v.severity == VulnerabilitySeverity.HIGH
        )
        
        return PackageHealth(
            package_path=pkg_path,
            package_type=pkg_type,
            total_dependencies=len(dependencies),
            outdated_count=outdated_count,
            vulnerable_count=vulnerable_count,
            critical_vulns=critical_vulns,
            high_vulns=high_vulns,
            last_scanned=datetime.now(),
            dependencies=dependencies
        )
    
    async def _scan_python_package(self, pkg_path: str) -> List[Dependency]:
        """Scan Python package dependencies"""
        dependencies = []
        pkg_path = Path(pkg_path)
        
        # Check for different dependency files
        if (pkg_path / "requirements.txt").exists():
            deps = await self._parse_requirements(pkg_path / "requirements.txt")
            dependencies.extend(deps)
        
        if (pkg_path / "pyproject.toml").exists():
            deps = await self._parse_pyproject(pkg_path / "pyproject.toml")
            dependencies.extend(deps)
        
        # Run pip-audit for vulnerability scanning
        vulnerabilities = await self._run_pip_audit(pkg_path)
        
        # Map vulnerabilities to dependencies
        for dep in dependencies:
            dep.vulnerabilities = vulnerabilities.get(dep.name, [])
        
        # Check for outdated packages
        outdated = await self._check_pip_outdated(pkg_path)
        for dep in dependencies:
            if dep.name in outdated:
                dep.outdated = True
                dep.latest_version = outdated[dep.name]
        
        return dependencies
    
    async def _scan_rust_package(self, pkg_path: str) -> List[Dependency]:
        """Scan Rust package dependencies"""
        dependencies = []
        pkg_path = Path(pkg_path)
        
        if not (pkg_path / "Cargo.toml").exists():
            return dependencies
        
        # Parse Cargo.toml
        with open(pkg_path / "Cargo.toml") as f:
            cargo_data = toml.load(f)
        
        # Extract dependencies
        for dep_name, dep_spec in cargo_data.get("dependencies", {}).items():
            version = dep_spec if isinstance(dep_spec, str) else dep_spec.get("version", "unknown")
            dependencies.append(Dependency(
                name=dep_name,
                version=version,
                latest_version=None,
                package_type=PackageType.RUST,
                package_file=str(pkg_path / "Cargo.toml"),
                license=None
            ))
        
        # Run cargo-audit for vulnerability scanning
        vulnerabilities = await self._run_cargo_audit(pkg_path)
        for dep in dependencies:
            dep.vulnerabilities = vulnerabilities.get(dep.name, [])
        
        # Check for outdated packages
        outdated = await self._check_cargo_outdated(pkg_path)
        for dep in dependencies:
            if dep.name in outdated:
                dep.outdated = True
                dep.latest_version = outdated[dep.name]
        
        return dependencies
    
    async def _scan_node_package(self, pkg_path: str) -> List[Dependency]:
        """Scan Node.js package dependencies"""
        dependencies = []
        pkg_path = Path(pkg_path)
        
        if not (pkg_path / "package.json").exists():
            return dependencies
        
        # Parse package.json
        with open(pkg_path / "package.json") as f:
            pkg_data = json.load(f)
        
        # Extract dependencies
        all_deps = {}
        all_deps.update(pkg_data.get("dependencies", {}))
        all_deps.update(pkg_data.get("devDependencies", {}))
        
        for dep_name, dep_version in all_deps.items():
            dependencies.append(Dependency(
                name=dep_name,
                version=dep_version,
                latest_version=None,
                package_type=PackageType.NODE,
                package_file=str(pkg_path / "package.json"),
                license=None
            ))
        
        # Run npm audit for vulnerability scanning
        vulnerabilities = await self._run_npm_audit(pkg_path)
        for dep in dependencies:
            dep.vulnerabilities = vulnerabilities.get(dep.name, [])
        
        # Check for outdated packages
        outdated = await self._check_npm_outdated(pkg_path)
        for dep in dependencies:
            if dep.name in outdated:
                dep.outdated = True
                dep.latest_version = outdated[dep.name]
        
        return dependencies
    
    async def _parse_requirements(self, req_file: Path) -> List[Dependency]:
        """Parse requirements.txt file"""
        dependencies = []
        with open(req_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Parse package name and version
                    match = re.match(r"([a-zA-Z0-9\-_]+)([><=~!]+)?(.*)?", line)
                    if match:
                        name = match.group(1)
                        version = match.group(3) if match.group(3) else "unknown"
                        dependencies.append(Dependency(
                            name=name,
                            version=version.strip(),
                            latest_version=None,
                            package_type=PackageType.PYTHON,
                            package_file=str(req_file),
                            license=None
                        ))
        return dependencies
    
    async def _parse_pyproject(self, pyproject_file: Path) -> List[Dependency]:
        """Parse pyproject.toml file"""
        dependencies = []
        with open(pyproject_file) as f:
            data = toml.load(f)
        
        # Extract dependencies from various sections
        dep_sections = [
            ["project", "dependencies"],
            ["project", "optional-dependencies"],
            ["tool", "poetry", "dependencies"],
            ["tool", "poetry", "dev-dependencies"]
        ]
        
        for section_path in dep_sections:
            section = data
            for key in section_path:
                section = section.get(key, {})
                if not section:
                    break
            
            if isinstance(section, dict):
                for dep_name, dep_spec in section.items():
                    if dep_name == "python":
                        continue
                    version = dep_spec if isinstance(dep_spec, str) else "unknown"
                    dependencies.append(Dependency(
                        name=dep_name,
                        version=version,
                        latest_version=None,
                        package_type=PackageType.PYTHON,
                        package_file=str(pyproject_file),
                        license=None
                    ))
        
        return dependencies
    
    async def _run_pip_audit(self, pkg_path: Path) -> Dict[str, List[Vulnerability]]:
        """Run pip-audit to check for vulnerabilities"""
        vulnerabilities = {}
        try:
            # Run pip-audit
            result = subprocess.run(
                ["pip-audit", "--format", "json", "--desc"],
                capture_output=True,
                text=True,
                cwd=pkg_path
            )
            
            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                for vuln in audit_data.get("vulnerabilities", []):
                    pkg_name = vuln.get("name")
                    if pkg_name not in vulnerabilities:
                        vulnerabilities[pkg_name] = []
                    
                    vulnerabilities[pkg_name].append(Vulnerability(
                        package=pkg_name,
                        severity=self._map_severity(vuln.get("severity", "unknown")),
                        cve=vuln.get("id"),
                        description=vuln.get("description", ""),
                        fixed_version=vuln.get("fix_versions", [None])[0],
                        current_version=vuln.get("version", "unknown")
                    ))
        except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
            # pip-audit not installed or error running
            pass
        
        return vulnerabilities
    
    async def _run_cargo_audit(self, pkg_path: Path) -> Dict[str, List[Vulnerability]]:
        """Run cargo-audit to check for vulnerabilities"""
        vulnerabilities = {}
        try:
            result = subprocess.run(
                ["cargo", "audit", "--json"],
                capture_output=True,
                text=True,
                cwd=pkg_path
            )
            
            # Parse JSON output line by line
            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        data = json.loads(line)
                        if data.get("type") == "vulnerability":
                            vuln_data = data.get("vulnerability", {})
                            pkg_name = vuln_data.get("package", {}).get("name")
                            if pkg_name:
                                if pkg_name not in vulnerabilities:
                                    vulnerabilities[pkg_name] = []
                                
                                vulnerabilities[pkg_name].append(Vulnerability(
                                    package=pkg_name,
                                    severity=self._map_severity(vuln_data.get("severity", "unknown")),
                                    cve=vuln_data.get("id"),
                                    description=vuln_data.get("title", ""),
                                    fixed_version=None,
                                    current_version=vuln_data.get("package", {}).get("version", "unknown")
                                ))
                    except json.JSONDecodeError:
                        pass
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return vulnerabilities
    
    async def _run_npm_audit(self, pkg_path: Path) -> Dict[str, List[Vulnerability]]:
        """Run npm audit to check for vulnerabilities"""
        vulnerabilities = {}
        try:
            result = subprocess.run(
                ["npm", "audit", "--json"],
                capture_output=True,
                text=True,
                cwd=pkg_path
            )
            
            audit_data = json.loads(result.stdout)
            for advisory_id, advisory in audit_data.get("advisories", {}).items():
                pkg_name = advisory.get("module_name")
                if pkg_name not in vulnerabilities:
                    vulnerabilities[pkg_name] = []
                
                vulnerabilities[pkg_name].append(Vulnerability(
                    package=pkg_name,
                    severity=self._map_severity(advisory.get("severity", "unknown")),
                    cve=advisory.get("cves", [None])[0] if advisory.get("cves") else None,
                    description=advisory.get("title", ""),
                    fixed_version=advisory.get("patched_versions"),
                    current_version=advisory.get("vulnerable_versions", "unknown")
                ))
        except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
            pass
        
        return vulnerabilities
    
    async def _check_pip_outdated(self, pkg_path: Path) -> Dict[str, str]:
        """Check for outdated Python packages"""
        outdated = {}
        try:
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=pkg_path
            )
            
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                for pkg in packages:
                    outdated[pkg["name"]] = pkg["latest_version"]
        except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
            pass
        
        return outdated
    
    async def _check_cargo_outdated(self, pkg_path: Path) -> Dict[str, str]:
        """Check for outdated Rust packages"""
        outdated = {}
        try:
            result = subprocess.run(
                ["cargo", "outdated", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=pkg_path
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for dep in data.get("dependencies", []):
                    if dep.get("outdated"):
                        outdated[dep["name"]] = dep["latest"]
        except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
            pass
        
        return outdated
    
    async def _check_npm_outdated(self, pkg_path: Path) -> Dict[str, str]:
        """Check for outdated Node packages"""
        outdated = {}
        try:
            result = subprocess.run(
                ["npm", "outdated", "--json"],
                capture_output=True,
                text=True,
                cwd=pkg_path
            )
            
            # npm outdated returns non-zero if there are outdated packages
            if result.stdout:
                packages = json.loads(result.stdout)
                for pkg_name, pkg_info in packages.items():
                    outdated[pkg_name] = pkg_info.get("latest", pkg_info.get("wanted"))
        except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
            pass
        
        return outdated
    
    def _map_severity(self, severity: str) -> VulnerabilitySeverity:
        """Map severity string to enum"""
        severity_lower = severity.lower()
        if "critical" in severity_lower:
            return VulnerabilitySeverity.CRITICAL
        elif "high" in severity_lower:
            return VulnerabilitySeverity.HIGH
        elif "moderate" in severity_lower or "medium" in severity_lower:
            return VulnerabilitySeverity.MODERATE
        elif "low" in severity_lower:
            return VulnerabilitySeverity.LOW
        else:
            return VulnerabilitySeverity.INFO
    
    async def generate_sbom(self) -> Dict[str, Any]:
        """Generate Software Bill of Materials (SBOM)"""
        packages = await self.scan_all_packages()
        
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "serialNumber": f"urn:uuid:{datetime.now().isoformat()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "tools": [
                    {"vendor": "Sutra AI", "name": "Dependency Scanner", "version": "1.0.0"}
                ],
                "component": {
                    "type": "application",
                    "bom-ref": "sutra-models",
                    "name": "Sutra Models",
                    "version": "1.0.0"
                }
            },
            "components": []
        }
        
        # Add all dependencies as components
        for pkg_health in packages.values():
            for dep in pkg_health.dependencies:
                component = {
                    "type": "library",
                    "bom-ref": f"{dep.package_type.value}:{dep.name}",
                    "name": dep.name,
                    "version": dep.version,
                    "licenses": [{"license": {"name": dep.license}}] if dep.license else []
                }
                
                # Add vulnerability information
                if dep.vulnerabilities:
                    component["vulnerabilities"] = [
                        {
                            "id": vuln.cve or f"vuln-{dep.name}",
                            "source": {"name": "NVD"},
                            "ratings": [{"severity": vuln.severity.value}],
                            "description": vuln.description
                        }
                        for vuln in dep.vulnerabilities
                    ]
                
                sbom["components"].append(component)
        
        return sbom