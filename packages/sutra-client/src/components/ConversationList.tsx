import { Box, List, ListItem, ListItemButton, Typography } from '@mui/material'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { conversationApi } from '../services/api'
import type { Conversation } from '../types/api'
import { ConversationSkeleton } from './LoadingSkeleton'

interface ConversationListProps {
  spaceId?: string
}

export default function ConversationList({ spaceId }: ConversationListProps) {
  const navigate = useNavigate()
  const { conversationId } = useParams()

  // Fetch conversations
  const { data, isLoading, error } = useQuery({
    queryKey: ['conversations', spaceId],
    queryFn: () => conversationApi.listConversations(1, 50, spaceId),
  })

  // Group conversations by date
  const groupByDate = (conversations: Conversation[]) => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    const lastWeek = new Date(today)
    lastWeek.setDate(lastWeek.getDate() - 7)

    const groups: Record<string, Conversation[]> = {
      Today: [],
      Yesterday: [],
      'Last 7 Days': [],
      Older: [],
    }

    conversations.forEach((conv) => {
      const convDate = new Date(conv.created_at)
      const convDay = new Date(convDate.getFullYear(), convDate.getMonth(), convDate.getDate())

      if (convDay.getTime() === today.getTime()) {
        groups.Today.push(conv)
      } else if (convDay.getTime() === yesterday.getTime()) {
        groups.Yesterday.push(conv)
      } else if (convDate >= lastWeek) {
        groups['Last 7 Days'].push(conv)
      } else {
        groups.Older.push(conv)
      }
    })

    return groups
  }

  const truncateText = (text: string, maxLength: number = 50) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  if (isLoading) {
    return (
      <Box sx={{ p: 1 }}>
        <ConversationSkeleton count={5} />
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="error">
          Failed to load conversations
        </Typography>
      </Box>
    )
  }

  const conversations = data?.conversations || []
  if (conversations.length === 0) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary" align="center">
          No conversations yet
        </Typography>
      </Box>
    )
  }

  const grouped = groupByDate(conversations)

  return (
    <Box sx={{ overflow: 'auto', height: '100%' }}>
      {Object.entries(grouped).map(([label, convs]) => {
        if (convs.length === 0) return null

        return (
          <Box key={label} sx={{ mb: 2 }}>
            {/* Group Label */}
            <Typography
              variant="caption"
              sx={{
                px: 2,
                py: 1,
                display: 'block',
                color: 'text.secondary',
                fontWeight: 600,
                textTransform: 'uppercase',
                fontSize: '0.75rem',
              }}
            >
              {label}
            </Typography>

            {/* Conversations */}
            <List disablePadding>
              {convs.map((conv) => {
                const isActive = conv.id === conversationId

                return (
                  <ListItem key={conv.id} disablePadding>
                    <ListItemButton
                      selected={isActive}
                      onClick={() => navigate(`/chat/${conv.id}`)}
                      sx={{
                        px: 2,
                        py: 1.5,
                        borderRadius: 1,
                        mx: 1,
                        mb: 0.5,
                        '&.Mui-selected': {
                          bgcolor: 'primary.main',
                          color: 'primary.contrastText',
                          '&:hover': {
                            bgcolor: 'primary.dark',
                          },
                        },
                      }}
                    >
                      <Box sx={{ overflow: 'hidden', width: '100%' }}>
                        <Typography
                          variant="body2"
                          sx={{
                            fontWeight: isActive ? 600 : 400,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {conv.title || 'New Conversation'}
                        </Typography>
                        {conv.metadata?.last_message && (
                          <Typography
                            variant="caption"
                            sx={{
                              display: 'block',
                              color: isActive ? 'inherit' : 'text.secondary',
                              opacity: isActive ? 0.9 : 1,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              mt: 0.25,
                            }}
                          >
                            {truncateText(conv.metadata.last_message, 40)}
                          </Typography>
                        )}
                      </Box>
                    </ListItemButton>
                  </ListItem>
                )
              })}
            </List>
          </Box>
        )
      })}
    </Box>
  )
}
