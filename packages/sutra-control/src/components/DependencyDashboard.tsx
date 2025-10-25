/**
 * Dependency Dashboard Component for Sutra Control Center
 * Monitors dependencies, vulnerabilities, and provides SBOM generation
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  AlertTitle,
  Button,
  Chip,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Collapse,
  Tabs,
  Tab,
  TextField,
  MenuItem,
  LinearProgress,
  Tooltip,
  Badge
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  BugReport as BugIcon,
  Update as UpdateIcon,
  Assignment as SbomIcon
} from '@mui/icons-material';

interface Vulnerability {
  severity: string;
  cve: string | null;
  description: string;
  fixed_version: string | null;
}

interface Dependency {
  name: string;
  version: string;
  latest_version: string | null;
  outdated: boolean;
  vulnerabilities: Vulnerability[];
}

interface PackageHealth {
  package_type: string;
  total_dependencies: number;
  outdated_count: number;
  vulnerable_count: number;
  critical_vulns: number;
  high_vulns: number;
  last_scanned: string;
  dependencies: Dependency[];
}

interface DependencySummary {
  total_packages: number;
  total_dependencies: number;
  unique_python: number;
  unique_rust: number;
  unique_node: number;
  outdated_dependencies: number;
  vulnerable_dependencies: number;
  critical_vulnerabilities: number;
  high_vulnerabilities: number;
  health_score: number;
}

const DependencyDashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [packages, setPackages] = useState<Record<string, PackageHealth>>({});
  const [summary, setSummary] = useState<DependencySummary | null>(null);
  const [vulnerabilities, setVulnerabilities] = useState<any[]>([]);
  const [selectedTab, setSelectedTab] = useState(0);
  const [severityFilter, setSeverityFilter] = useState('all');
  const [packageTypeFilter, setPackageTypeFilter] = useState('all');
  const [expandedPackages, setExpandedPackages] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [lastScanTime, setLastScanTime] = useState<Date | null>(null);

  // Load summary on mount
  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/dependencies/summary');
      if (!response.ok) throw new Error('Failed to load summary');
      const data = await response.json();
      setSummary(data.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dependency summary');
    } finally {
      setLoading(false);
    }
  };

  const runScan = async () => {
    setScanning(true);
    setError(null);
    try {
      const response = await fetch('/api/dependencies/scan');
      if (!response.ok) throw new Error('Scan failed');
      const data = await response.json();
      setPackages(data.packages);
      setLastScanTime(new Date());
      
      // Reload summary after scan
      await loadSummary();
      
      // Load vulnerabilities
      await loadVulnerabilities();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Dependency scan failed');
    } finally {
      setScanning(false);
    }
  };

  const loadVulnerabilities = async () => {
    try {
      const params = new URLSearchParams();
      if (severityFilter !== 'all') params.append('severity', severityFilter);
      if (packageTypeFilter !== 'all') params.append('package_type', packageTypeFilter);
      
      const response = await fetch(`/api/dependencies/vulnerabilities?${params}`);
      if (!response.ok) throw new Error('Failed to load vulnerabilities');
      const data = await response.json();
      setVulnerabilities(data.vulnerabilities);
    } catch (err) {
      console.error('Failed to load vulnerabilities:', err);
    }
  };

  const downloadSBOM = async () => {
    try {
      const response = await fetch('/api/dependencies/sbom');
      if (!response.ok) throw new Error('SBOM generation failed');
      const sbom = await response.json();
      
      // Create and download file
      const blob = new Blob([JSON.stringify(sbom, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sutra-sbom-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to generate SBOM');
    }
  };

  const togglePackageExpansion = (packagePath: string) => {
    setExpandedPackages(prev => {
      const newSet = new Set(prev);
      if (newSet.has(packagePath)) {
        newSet.delete(packagePath);
      } else {
        newSet.add(packagePath);
      }
      return newSet;
    });
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'high':
        return <WarningIcon sx={{ color: 'orange' }} />;
      case 'moderate':
        return <WarningIcon color="warning" />;
      default:
        return <SecurityIcon color="info" />;
    }
  };

  const getSeverityColor = (severity: string): "error" | "warning" | "info" | "success" | "default" => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'moderate':
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ff9800';
    if (score >= 40) return '#ff5722';
    return '#f44336';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Dependency Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={scanning ? <CircularProgress size={20} /> : <RefreshIcon />}
            onClick={runScan}
            disabled={scanning}
          >
            {scanning ? 'Scanning...' : 'Run Scan'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<SbomIcon />}
            onClick={downloadSBOM}
          >
            Download SBOM
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          <AlertTitle>Error</AlertTitle>
          {error}
        </Alert>
      )}

      {/* Summary Cards */}
      {summary && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Health Score
                </Typography>
                <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                  <CircularProgress
                    variant="determinate"
                    value={summary.health_score}
                    size={80}
                    thickness={4}
                    sx={{ color: getHealthColor(summary.health_score) }}
                  />
                  <Box
                    sx={{
                      top: 0,
                      left: 0,
                      bottom: 0,
                      right: 0,
                      position: 'absolute',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Typography variant="h5" component="div" color="textSecondary">
                      {summary.health_score}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Dependencies
                </Typography>
                <Typography variant="h3">
                  {summary.total_dependencies}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                  <Chip
                    size="small"
                    label={`Python: ${summary.unique_python}`}
                    color="primary"
                  />
                  <Chip
                    size="small"
                    label={`Rust: ${summary.unique_rust}`}
                    sx={{ backgroundColor: '#CE422B', color: 'white' }}
                  />
                  <Chip
                    size="small"
                    label={`Node: ${summary.unique_node}`}
                    sx={{ backgroundColor: '#68a063', color: 'white' }}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Vulnerabilities
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 2 }}>
                  {summary.critical_vulnerabilities > 0 && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <ErrorIcon color="error" />
                      <Typography variant="h4" color="error">
                        {summary.critical_vulnerabilities}
                      </Typography>
                    </Box>
                  )}
                  {summary.high_vulnerabilities > 0 && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <WarningIcon sx={{ color: 'orange' }} />
                      <Typography variant="h4" sx={{ color: 'orange' }}>
                        {summary.high_vulnerabilities}
                      </Typography>
                    </Box>
                  )}
                  {summary.critical_vulnerabilities === 0 && summary.high_vulnerabilities === 0 && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CheckIcon color="success" />
                      <Typography variant="h5" color="success.main">
                        Secure
                      </Typography>
                    </Box>
                  )}
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  {summary.vulnerable_dependencies} vulnerable packages
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Updates Available
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <UpdateIcon color="info" />
                  <Typography variant="h3">
                    {summary.outdated_dependencies}
                  </Typography>
                </Box>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  packages can be updated
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 2 }}>
        <Tabs value={selectedTab} onChange={(_, v) => setSelectedTab(v)}>
          <Tab label="Package Overview" />
          <Tab 
            label={
              <Badge badgeContent={vulnerabilities.length} color="error">
                Vulnerabilities
              </Badge>
            } 
          />
          <Tab label="Detailed Scan Results" />
        </Tabs>
      </Paper>

      {/* Package Overview Tab */}
      {selectedTab === 0 && Object.keys(packages).length > 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Package</TableCell>
                <TableCell>Type</TableCell>
                <TableCell align="center">Dependencies</TableCell>
                <TableCell align="center">Outdated</TableCell>
                <TableCell align="center">Vulnerabilities</TableCell>
                <TableCell align="center">Critical/High</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(packages).map(([path, health]) => {
                const packageName = path.split('/').pop() || path;
                return (
                  <React.Fragment key={path}>
                    <TableRow>
                      <TableCell>{packageName}</TableCell>
                      <TableCell>
                        <Chip 
                          size="small" 
                          label={health.package_type}
                          color={
                            health.package_type === 'python' ? 'primary' :
                            health.package_type === 'rust' ? 'secondary' : 'default'
                          }
                        />
                      </TableCell>
                      <TableCell align="center">{health.total_dependencies}</TableCell>
                      <TableCell align="center">
                        {health.outdated_count > 0 ? (
                          <Chip size="small" label={health.outdated_count} color="warning" />
                        ) : (
                          <CheckIcon color="success" />
                        )}
                      </TableCell>
                      <TableCell align="center">
                        {health.vulnerable_count > 0 ? (
                          <Chip size="small" label={health.vulnerable_count} color="error" />
                        ) : (
                          <CheckIcon color="success" />
                        )}
                      </TableCell>
                      <TableCell align="center">
                        {health.critical_vulns > 0 && (
                          <Chip size="small" label={`C:${health.critical_vulns}`} color="error" />
                        )}
                        {health.high_vulns > 0 && (
                          <Chip 
                            size="small" 
                            label={`H:${health.high_vulns}`} 
                            sx={{ ml: 0.5, backgroundColor: 'orange', color: 'white' }}
                          />
                        )}
                      </TableCell>
                      <TableCell>
                        <IconButton
                          onClick={() => togglePackageExpansion(path)}
                          size="small"
                        >
                          {expandedPackages.has(path) ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell colSpan={7} sx={{ py: 0 }}>
                        <Collapse in={expandedPackages.has(path)}>
                          <Box sx={{ p: 2 }}>
                            <Typography variant="h6" gutterBottom>
                              Dependencies for {packageName}
                            </Typography>
                            <Table size="small">
                              <TableHead>
                                <TableRow>
                                  <TableCell>Package</TableCell>
                                  <TableCell>Current Version</TableCell>
                                  <TableCell>Latest Version</TableCell>
                                  <TableCell>Vulnerabilities</TableCell>
                                </TableRow>
                              </TableHead>
                              <TableBody>
                                {health.dependencies.map((dep) => (
                                  <TableRow key={dep.name}>
                                    <TableCell>{dep.name}</TableCell>
                                    <TableCell>{dep.version}</TableCell>
                                    <TableCell>
                                      {dep.latest_version && dep.outdated ? (
                                        <Chip 
                                          size="small" 
                                          label={dep.latest_version}
                                          color="warning"
                                        />
                                      ) : (
                                        dep.version
                                      )}
                                    </TableCell>
                                    <TableCell>
                                      {dep.vulnerabilities.map((vuln, idx) => (
                                        <Tooltip 
                                          key={idx} 
                                          title={vuln.description}
                                        >
                                          <Chip
                                            size="small"
                                            label={vuln.cve || vuln.severity}
                                            color={getSeverityColor(vuln.severity)}
                                            sx={{ mr: 0.5, mb: 0.5 }}
                                          />
                                        </Tooltip>
                                      ))}
                                    </TableCell>
                                  </TableRow>
                                ))}
                              </TableBody>
                            </Table>
                          </Box>
                        </Collapse>
                      </TableCell>
                    </TableRow>
                  </React.Fragment>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Vulnerabilities Tab */}
      {selectedTab === 1 && (
        <Box>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              select
              label="Severity"
              value={severityFilter}
              onChange={(e) => {
                setSeverityFilter(e.target.value);
                loadVulnerabilities();
              }}
              size="small"
              sx={{ minWidth: 150 }}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="moderate">Moderate</MenuItem>
              <MenuItem value="low">Low</MenuItem>
            </TextField>
            <TextField
              select
              label="Package Type"
              value={packageTypeFilter}
              onChange={(e) => {
                setPackageTypeFilter(e.target.value);
                loadVulnerabilities();
              }}
              size="small"
              sx={{ minWidth: 150 }}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="python">Python</MenuItem>
              <MenuItem value="rust">Rust</MenuItem>
              <MenuItem value="node">Node.js</MenuItem>
            </TextField>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Severity</TableCell>
                  <TableCell>Package</TableCell>
                  <TableCell>Version</TableCell>
                  <TableCell>CVE</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Fixed Version</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {vulnerabilities.map((vuln, idx) => (
                  <TableRow key={idx}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getSeverityIcon(vuln.severity)}
                        <Chip 
                          size="small" 
                          label={vuln.severity}
                          color={getSeverityColor(vuln.severity)}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>{vuln.package}</TableCell>
                    <TableCell>{vuln.version}</TableCell>
                    <TableCell>{vuln.cve || '-'}</TableCell>
                    <TableCell sx={{ maxWidth: 400 }}>
                      <Typography variant="body2" noWrap>
                        {vuln.description}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {vuln.fixed_version ? (
                        <Chip size="small" label={vuln.fixed_version} color="success" />
                      ) : (
                        '-'
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Last Scan Time */}
      {lastScanTime && (
        <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
          Last scan: {lastScanTime.toLocaleString()}
        </Typography>
      )}
    </Box>
  );
};

export default DependencyDashboard;