import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid as MuiGrid,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Computer as ComputerIcon,
  Storage as StorageIcon
} from '@mui/icons-material';

interface StorageNode {
  node_id: string;
  status: string;
  pid: number;
  endpoint: string;
}

interface GridAgent {
  agent_id: string;
  hostname: string;
  platform: string;
  status: string;
  max_storage_nodes: number;
  current_storage_nodes: number;
  last_heartbeat: number;
  storage_nodes: StorageNode[];
}

interface GridClusterStatus {
  total_agents: number;
  healthy_agents: number;
  total_storage_nodes: number;
  running_storage_nodes: number;
  status: string;
  timestamp: string;
}

interface SpawnNodeForm {
  agent_id: string;
  port: number;
  storage_path: string;
  memory_limit_mb: number;
}

const Grid: React.FC = () => {
  const [agents, setAgents] = useState<GridAgent[]>([]);
  const [clusterStatus, setClusterStatus] = useState<GridClusterStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [spawnDialogOpen, setSpawnDialogOpen] = useState(false);
  const [spawnForm, setSpawnForm] = useState<SpawnNodeForm>({
    agent_id: '',
    port: 50053,
    storage_path: '/tmp/storage',
    memory_limit_mb: 512
  });

  const fetchGridData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [agentsResponse, statusResponse] = await Promise.all([
        fetch('/api/grid/agents'),
        fetch('/api/grid/status')
      ]);

      if (!agentsResponse.ok || !statusResponse.ok) {
        throw new Error('Failed to fetch Grid data');
      }

      const agentsData = await agentsResponse.json();
      const statusData = await statusResponse.json();

      setAgents(agentsData.agents);
      setClusterStatus(statusData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleSpawnNode = async () => {
    try {
      const response = await fetch('/api/grid/spawn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(spawnForm),
      });

      const result = await response.json();

      if (result.success) {
        setSpawnDialogOpen(false);
        fetchGridData(); // Refresh data
      } else {
        setError(result.error || 'Failed to spawn node');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to spawn node');
    }
  };

  const handleStopNode = async (agentId: string, nodeId: string) => {
    try {
      const response = await fetch('/api/grid/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_id: agentId,
          node_id: nodeId,
        }),
      });

      const result = await response.json();

      if (result.success) {
        fetchGridData(); // Refresh data
      } else {
        setError(result.error || 'Failed to stop node');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop node');
    }
  };

  useEffect(() => {
    fetchGridData();
    const interval = setInterval(fetchGridData, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'running':
        return 'success';
      case 'degraded':
      case 'stopped':
        return 'warning';
      case 'unavailable':
      case 'crashed':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Sutra Grid Management
        </Typography>
        <Box>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchGridData} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<PlayArrowIcon />}
            onClick={() => setSpawnDialogOpen(true)}
          >
            Spawn Node
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Cluster Status Overview */}
      <MuiGrid container spacing={3} sx={{ mb: 4 }}>
        <MuiGrid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <ComputerIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Box>
                  <Typography variant="h6">{clusterStatus?.total_agents || 0}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Total Agents
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </MuiGrid>
        <MuiGrid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <ComputerIcon sx={{ mr: 1, color: 'success.main' }} />
                <Box>
                  <Typography variant="h6">{clusterStatus?.healthy_agents || 0}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Healthy Agents
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </MuiGrid>
        <MuiGrid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <StorageIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Box>
                  <Typography variant="h6">{clusterStatus?.total_storage_nodes || 0}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Storage Nodes
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </MuiGrid>
        <MuiGrid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <StorageIcon sx={{ mr: 1, color: 'success.main' }} />
                <Box>
                  <Typography variant="h6">{clusterStatus?.running_storage_nodes || 0}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    Running Nodes
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </MuiGrid>
      </MuiGrid>

      {/* Agents List */}
      <Typography variant="h5" gutterBottom>
        Grid Agents
      </Typography>

      {agents.length === 0 ? (
        <Card>
          <CardContent>
            <Typography color="textSecondary" align="center">
              No Grid agents found. Start a Grid Agent to begin.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        agents.map((agent) => (
          <Accordion key={agent.agent_id} sx={{ mb: 2 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" alignItems="center" width="100%">
                <ComputerIcon sx={{ mr: 2 }} />
                <Box flexGrow={1}>
                  <Typography variant="h6">{agent.agent_id}</Typography>
                  <Typography variant="body2" color="textSecondary">
                    {agent.hostname} • {agent.platform}
                  </Typography>
                </Box>
                <Chip
                  label={agent.status}
                  color={getStatusColor(agent.status)}
                  size="small"
                  sx={{ mr: 2 }}
                />
                <Typography variant="body2">
                  {agent.current_storage_nodes}/{agent.max_storage_nodes} nodes
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {agent.storage_nodes.length === 0 ? (
                <Typography color="textSecondary">
                  No storage nodes running on this agent.
                </Typography>
              ) : (
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Node ID</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>PID</TableCell>
                        <TableCell>Endpoint</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {agent.storage_nodes.map((node) => (
                        <TableRow key={node.node_id}>
                          <TableCell>{node.node_id}</TableCell>
                          <TableCell>
                            <Chip
                              label={node.status}
                              color={getStatusColor(node.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{node.pid}</TableCell>
                          <TableCell>{node.endpoint}</TableCell>
                          <TableCell>
                            <Button
                              size="small"
                              color="error"
                              startIcon={<StopIcon />}
                              onClick={() => handleStopNode(agent.agent_id, node.node_id)}
                            >
                              Stop
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </AccordionDetails>
          </Accordion>
        ))
      )}

      {/* Spawn Node Dialog */}
      <Dialog open={spawnDialogOpen} onClose={() => setSpawnDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Spawn Storage Node</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Agent ID"
            fullWidth
            value={spawnForm.agent_id}
            onChange={(e) => setSpawnForm({ ...spawnForm, agent_id: e.target.value })}
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Port"
            type="number"
            fullWidth
            value={spawnForm.port}
            onChange={(e) => setSpawnForm({ ...spawnForm, port: parseInt(e.target.value) })}
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Storage Path"
            fullWidth
            value={spawnForm.storage_path}
            onChange={(e) => setSpawnForm({ ...spawnForm, storage_path: e.target.value })}
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Memory Limit (MB)"
            type="number"
            fullWidth
            value={spawnForm.memory_limit_mb}
            onChange={(e) => setSpawnForm({ ...spawnForm, memory_limit_mb: parseInt(e.target.value) })}
            variant="outlined"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSpawnDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSpawnNode} variant="contained">
            Spawn
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Grid;