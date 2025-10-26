import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Typography,
} from '@mui/material'
import { Delete, Close, PersonAdd } from '@mui/icons-material'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { spaceApi } from '../services/api'

interface SpaceManagementProps {
  open: boolean
  onClose: () => void
  spaceId: string | null
  mode: 'create' | 'edit'
}

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`space-tabpanel-${index}`}
      aria-labelledby={`space-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  )
}

export default function SpaceManagement({
  open,
  onClose,
  spaceId,
  mode,
}: SpaceManagementProps) {
  const queryClient = useQueryClient()
  const [currentTab, setCurrentTab] = useState(0)
  const [error, setError] = useState<string | null>(null)

  // Form state for space details
  const [spaceName, setSpaceName] = useState('')
  const [spaceDescription, setSpaceDescription] = useState('')
  const [domainStorage, setDomainStorage] = useState('default')
  const [spaceIcon, setSpaceIcon] = useState('📁')
  const [spaceColor, setSpaceColor] = useState('#6b7280')

  // Member management state
  const [newMemberEmail, setNewMemberEmail] = useState('')
  const [newMemberRole, setNewMemberRole] = useState<'admin' | 'write' | 'read'>('read')

  // Fetch space details if editing
  const { data: spaceData, isLoading: isLoadingSpace } = useQuery({
    queryKey: ['space', spaceId],
    queryFn: () => spaceApi.getSpace(spaceId!),
    enabled: mode === 'edit' && !!spaceId,
  })

  // Update form state when space data is loaded
  useEffect(() => {
    if (spaceData) {
      setSpaceName(spaceData.name)
      setSpaceDescription(spaceData.description)
      setDomainStorage(spaceData.domain_storage)
      setSpaceIcon(spaceData.icon)
      setSpaceColor(spaceData.color)
    }
  }, [spaceData])

  // Fetch members if editing
  const { data: membersData, isLoading: isLoadingMembers } = useQuery({
    queryKey: ['spaceMembers', spaceId],
    queryFn: () => spaceApi.listMembers(spaceId!),
    enabled: mode === 'edit' && !!spaceId,
  })

  const members = membersData?.members || []

  // Create space mutation
  const createSpace = useMutation({
    mutationFn: () =>
      spaceApi.createSpace(
        spaceName,
        domainStorage,
        spaceDescription,
        spaceIcon,
        spaceColor
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spaces'] })
      handleClose()
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to create space')
    },
  })

  // Update space mutation
  const updateSpace = useMutation({
    mutationFn: () =>
      spaceApi.updateSpace(spaceId!, {
        name: spaceName,
        description: spaceDescription,
        icon: spaceIcon,
        color: spaceColor,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spaces'] })
      queryClient.invalidateQueries({ queryKey: ['space', spaceId] })
      handleClose()
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to update space')
    },
  })

  // Delete space mutation
  const deleteSpace = useMutation({
    mutationFn: () => spaceApi.deleteSpace(spaceId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spaces'] })
      handleClose()
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to delete space')
    },
  })

  // Add member mutation
  const addMember = useMutation({
    mutationFn: (data: { userId: string; role: 'admin' | 'write' | 'read' }) =>
      spaceApi.addMember(spaceId!, data.userId, data.role),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spaceMembers', spaceId] })
      setNewMemberEmail('')
      setNewMemberRole('read')
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to add member')
    },
  })

  // Remove member mutation
  const removeMember = useMutation({
    mutationFn: (userId: string) => spaceApi.removeMember(spaceId!, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spaceMembers', spaceId] })
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to remove member')
    },
  })

  // Update member role mutation
  const updateMemberRole = useMutation({
    mutationFn: (data: { userId: string; newRole: 'admin' | 'write' | 'read' }) =>
      spaceApi.updateMemberRole(spaceId!, data.userId, data.newRole),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['spaceMembers', spaceId] })
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to update member role')
    },
  })

  const handleClose = () => {
    setError(null)
    setCurrentTab(0)
    setSpaceName('')
    setSpaceDescription('')
    setDomainStorage('default')
    setSpaceIcon('📁')
    setSpaceColor('#6b7280')
    onClose()
  }

  const handleSubmit = () => {
    setError(null)
    if (mode === 'create') {
      createSpace.mutate()
    } else {
      updateSpace.mutate()
    }
  }

  const handleAddMember = () => {
    if (!newMemberEmail.trim()) {
      setError('Please enter an email address')
      return
    }
    // In a real app, you'd look up the user ID by email
    // For now, we'll use the email as the user ID placeholder
    addMember.mutate({ userId: newMemberEmail, role: newMemberRole })
  }

  const handleDeleteSpace = () => {
    if (window.confirm('Are you sure you want to delete this space? This action cannot be undone.')) {
      deleteSpace.mutate()
    }
  }

  if (isLoadingSpace && mode === 'edit') {
    return (
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogContent>
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>{mode === 'create' ? 'Create New Space' : 'Manage Space'}</span>
          <IconButton onClick={handleClose} size="small">
            <Close />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {mode === 'edit' && (
          <Tabs value={currentTab} onChange={(_, v) => setCurrentTab(v)} sx={{ mb: 2 }}>
            <Tab label="Details" />
            <Tab label="Members" />
          </Tabs>
        )}

        {/* Details Tab */}
        <TabPanel value={currentTab} index={0}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Space Name"
              value={spaceName}
              onChange={(e) => setSpaceName(e.target.value)}
              required
              fullWidth
              autoFocus
              helperText="A descriptive name for your space (e.g., 'Medical Protocols', 'Legal Research')"
            />

            <TextField
              label="Description"
              value={spaceDescription}
              onChange={(e) => setSpaceDescription(e.target.value)}
              multiline
              rows={3}
              fullWidth
              helperText="Optional description of what this space is for"
            />

            <FormControl fullWidth disabled={mode === 'edit'}>
              <InputLabel>Domain Storage</InputLabel>
              <Select
                value={domainStorage}
                onChange={(e) => setDomainStorage(e.target.value)}
                label="Domain Storage"
              >
                <MenuItem value="default">Default</MenuItem>
                <MenuItem value="domain_medical">Medical Knowledge</MenuItem>
                <MenuItem value="domain_legal">Legal Knowledge</MenuItem>
                <MenuItem value="domain_financial">Financial Knowledge</MenuItem>
              </Select>
              {mode === 'edit' && (
                <Typography variant="caption" sx={{ mt: 1, color: 'text.secondary' }}>
                  Domain storage cannot be changed after creation
                </Typography>
              )}
            </FormControl>

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Icon"
                value={spaceIcon}
                onChange={(e) => setSpaceIcon(e.target.value)}
                sx={{ width: 100 }}
                helperText="Emoji"
              />

              <TextField
                label="Color"
                type="color"
                value={spaceColor}
                onChange={(e) => setSpaceColor(e.target.value)}
                sx={{ width: 120 }}
                helperText="Badge color"
              />

              <Box
                sx={{
                  width: 60,
                  height: 60,
                  borderRadius: '8px',
                  bgcolor: spaceColor,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '24px',
                  border: '1px solid',
                  borderColor: 'divider',
                }}
              >
                {spaceIcon}
              </Box>
            </Box>
          </Box>
        </TabPanel>

        {/* Members Tab */}
        {mode === 'edit' && (
          <TabPanel value={currentTab} index={1}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ mb: 2 }}>
                Add Member
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  label="User Email"
                  value={newMemberEmail}
                  onChange={(e) => setNewMemberEmail(e.target.value)}
                  size="small"
                  sx={{ flex: 1 }}
                />
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>Role</InputLabel>
                  <Select
                    value={newMemberRole}
                    onChange={(e) => setNewMemberRole(e.target.value as any)}
                    label="Role"
                  >
                    <MenuItem value="read">Read</MenuItem>
                    <MenuItem value="write">Write</MenuItem>
                    <MenuItem value="admin">Admin</MenuItem>
                  </Select>
                </FormControl>
                <Button
                  variant="contained"
                  startIcon={<PersonAdd />}
                  onClick={handleAddMember}
                  disabled={addMember.isPending}
                >
                  Add
                </Button>
              </Box>
            </Box>

            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              Current Members ({members.length})
            </Typography>

            {isLoadingMembers ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                <CircularProgress size={24} />
              </Box>
            ) : members.length === 0 ? (
              <Alert severity="info">No members yet</Alert>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Email</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Added</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {members.map((member: any) => (
                      <TableRow key={member.user_id}>
                        <TableCell>{member.email}</TableCell>
                        <TableCell>{member.full_name || '-'}</TableCell>
                        <TableCell>
                          <FormControl size="small" sx={{ minWidth: 100 }}>
                            <Select
                              value={member.role}
                              onChange={(e) =>
                                updateMemberRole.mutate({
                                  userId: member.user_id,
                                  newRole: e.target.value as any,
                                })
                              }
                              disabled={updateMemberRole.isPending}
                            >
                              <MenuItem value="read">Read</MenuItem>
                              <MenuItem value="write">Write</MenuItem>
                              <MenuItem value="admin">Admin</MenuItem>
                            </Select>
                          </FormControl>
                        </TableCell>
                        <TableCell>
                          {new Date(member.added_at).toLocaleDateString()}
                        </TableCell>
                        <TableCell align="right">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => removeMember.mutate(member.user_id)}
                            disabled={removeMember.isPending}
                          >
                            <Delete fontSize="small" />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </TabPanel>
        )}
      </DialogContent>

      <DialogActions>
        {mode === 'edit' && spaceData?.role === 'admin' && (
          <Button
            onClick={handleDeleteSpace}
            color="error"
            disabled={deleteSpace.isPending}
            sx={{ mr: 'auto' }}
          >
            Delete Space
          </Button>
        )}
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={
            !spaceName.trim() ||
            createSpace.isPending ||
            updateSpace.isPending
          }
        >
          {mode === 'create' ? 'Create' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
