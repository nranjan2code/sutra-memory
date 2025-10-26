import { useState } from 'react'
import { Box, Drawer, IconButton, TextField, useMediaQuery, useTheme } from '@mui/material'
import { Menu, Search as SearchIcon } from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import ConversationList from './ConversationList'
import SpaceSelector from './SpaceSelector'
import SpaceManagement from './SpaceManagement'
import { conversationApi } from '../services/api'

interface SidebarProps {
  open: boolean
  onClose: () => void
}

const SIDEBAR_WIDTH = 280

export default function Sidebar({ open, onClose }: SidebarProps) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const [searchQuery, setSearchQuery] = useState('')
  const [currentSpaceId, setCurrentSpaceId] = useState<string | null>(null)
  const [showSpaceManagement, setShowSpaceManagement] = useState(false)
  const [spaceManagementMode, setSpaceManagementMode] = useState<'create' | 'edit'>('create')

  // Create new conversation mutation
  const createConversation = useMutation({
    mutationFn: () => conversationApi.createConversation(currentSpaceId || 'default-space'),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      navigate(`/chat/${data.conversation.id}`)
      if (isMobile) {
        onClose()
      }
    },
  })

  const handleNewChat = () => {
    if (!currentSpaceId) {
      alert('Please select a space first')
      return
    }
    createConversation.mutate()
  }

  const handleSpaceChange = (spaceId: string) => {
    setCurrentSpaceId(spaceId)
    // Reload conversations for new space
    queryClient.invalidateQueries({ queryKey: ['conversations'] })
  }

  const handleCreateSpace = () => {
    setSpaceManagementMode('create')
    setShowSpaceManagement(true)
  }

  const handleManageSpace = () => {
    setSpaceManagementMode('edit')
    setShowSpaceManagement(true)
  }

  const sidebarContent = (
    <Box
      sx={{
        width: SIDEBAR_WIDTH,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
        borderRight: '1px solid',
        borderColor: 'divider',
      }}
      role="navigation"
      aria-label="Conversation sidebar"
    >
      {/* Space Selector */}
      <SpaceSelector
        selectedSpaceId={currentSpaceId}
        onSpaceChange={handleSpaceChange}
        onManageSpaces={handleManageSpace}
        onCreateSpace={handleCreateSpace}
      />

      {/* Search */}
      <Box sx={{ p: 2, pb: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search conversations..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          inputProps={{
            'aria-label': 'Search conversations',
          }}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
          }}
        />
      </Box>

      {/* Conversation List */}
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <ConversationList spaceId={currentSpaceId || undefined} />
      </Box>

      {/* Space Management Dialog */}
      <SpaceManagement
        open={showSpaceManagement}
        onClose={() => setShowSpaceManagement(false)}
        spaceId={currentSpaceId}
        mode={spaceManagementMode}
      />
    </Box>
  )

  // Mobile: use temporary drawer
  if (isMobile) {
    return (
      <Drawer
        anchor="left"
        open={open}
        onClose={onClose}
        ModalProps={{
          keepMounted: true, // Better mobile performance
        }}
      >
        {sidebarContent}
      </Drawer>
    )
  }

  // Desktop: always visible
  return (
    <Box
      sx={{
        width: open ? SIDEBAR_WIDTH : 0,
        flexShrink: 0,
        transition: theme.transitions.create('width', {
          easing: theme.transitions.easing.sharp,
          duration: theme.transitions.duration.enteringScreen,
        }),
        overflow: 'hidden',
      }}
    >
      {sidebarContent}
    </Box>
  )
}

// Mobile menu button (separate component for use in layout)
export function SidebarToggle({ onClick }: { onClick: () => void }) {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))

  if (!isMobile) return null

  return (
    <IconButton
      edge="start"
      color="inherit"
      aria-label="menu"
      onClick={onClick}
      sx={{ mr: 2 }}
    >
      <Menu />
    </IconButton>
  )
}
