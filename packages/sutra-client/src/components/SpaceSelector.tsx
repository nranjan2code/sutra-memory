import { useState } from 'react'
import {
  Box,
  Select,
  MenuItem,
  FormControl,
  CircularProgress,
  IconButton,
  Tooltip,
  SelectChangeEvent,
} from '@mui/material'
import { Add, Settings, Folder } from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import { spaceApi } from '../services/api'
import type { Space } from '../types/api'

interface SpaceSelectorProps {
  selectedSpaceId: string | null
  onSpaceChange: (spaceId: string) => void
  onManageSpaces: () => void
  onCreateSpace: () => void
}

export default function SpaceSelector({
  selectedSpaceId,
  onSpaceChange,
  onManageSpaces,
  onCreateSpace,
}: SpaceSelectorProps) {
  // Fetch spaces
  const { data: spacesData, isLoading } = useQuery({
    queryKey: ['spaces'],
    queryFn: () => spaceApi.listSpaces(),
  })

  const spaces = spacesData?.spaces || []
  const currentSpace = spaces.find((s) => s.space_id === selectedSpaceId)

  const handleChange = (event: SelectChangeEvent<string>) => {
    onSpaceChange(event.target.value)
  }

  if (isLoading) {
    return (
      <Box
        sx={{
          p: 2,
          display: 'flex',
          justifyContent: 'center',
          borderBottom: '1px solid',
          borderColor: 'divider',
        }}
      >
        <CircularProgress size={24} />
      </Box>
    )
  }

  return (
    <Box
      sx={{
        p: 2,
        borderBottom: '1px solid',
        borderColor: 'divider',
        display: 'flex',
        alignItems: 'center',
        gap: 1,
      }}
    >
      <FormControl fullWidth size="small">
        <Select
          value={selectedSpaceId || ''}
          onChange={handleChange}
          displayEmpty
          renderValue={(value) => {
            if (!value) {
              return (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary' }}>
                  <Folder fontSize="small" />
                  <span>Select a space</span>
                </Box>
              )
            }
            const space = spaces.find((s) => s.space_id === value)
            if (!space) return 'Unknown Space'
            
            return (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box
                  sx={{
                    width: 20,
                    height: 20,
                    borderRadius: '4px',
                    bgcolor: space.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '12px',
                  }}
                >
                  {space.icon === 'folder' ? '📁' : space.icon}
                </Box>
                <span>{space.name}</span>
              </Box>
            )
          }}
          sx={{
            '& .MuiSelect-select': {
              display: 'flex',
              alignItems: 'center',
            },
          }}
        >
          {spaces.length === 0 ? (
            <MenuItem disabled>
              <em>No spaces available</em>
            </MenuItem>
          ) : (
            spaces.map((space) => (
              <MenuItem key={space.space_id} value={space.space_id}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                  <Box
                    sx={{
                      width: 20,
                      height: 20,
                      borderRadius: '4px',
                      bgcolor: space.color,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '12px',
                      flexShrink: 0,
                    }}
                  >
                    {space.icon === 'folder' ? '📁' : space.icon}
                  </Box>
                  <Box sx={{ flex: 1, minWidth: 0 }}>
                    <Box sx={{ fontWeight: 500 }}>{space.name}</Box>
                    <Box
                      sx={{
                        fontSize: '0.75rem',
                        color: 'text.secondary',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {space.conversation_count} conversation{space.conversation_count !== 1 ? 's' : ''} · {space.role}
                    </Box>
                  </Box>
                </Box>
              </MenuItem>
            ))
          )}
        </Select>
      </FormControl>

      <Tooltip title="Create space">
        <IconButton size="small" onClick={onCreateSpace}>
          <Add fontSize="small" />
        </IconButton>
      </Tooltip>

      {currentSpace && currentSpace.role === 'admin' && (
        <Tooltip title="Manage space">
          <IconButton size="small" onClick={onManageSpaces}>
            <Settings fontSize="small" />
          </IconButton>
        </Tooltip>
      )}
    </Box>
  )
}
