import { Box, List, ListItem, ListItemButton, Typography, CircularProgress } from '@mui/material'
import { useNavigate, useParams } from 'react-router-dom'
import { useInfiniteQuery } from '@tanstack/react-query'
import { memo, useMemo, useCallback, useEffect, useRef } from 'react'
import { conversationApi } from '../services/api'
import type { Conversation } from '../types/api'
import { ConversationSkeleton } from './LoadingSkeleton'

interface ConversationListProps {
  spaceId?: string
}

const PAGE_SIZE = 50

function ConversationListComponent({ spaceId }: ConversationListProps) {
  const navigate = useNavigate()
  const { conversationId } = useParams()
  const loadMoreRef = useRef<HTMLDivElement>(null)

  // Fetch conversations with infinite loading
  const {
    data,
    isLoading,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['conversations', spaceId],
    queryFn: ({ pageParam = 1 }) =>
      conversationApi.listConversations(pageParam, PAGE_SIZE, spaceId),
    getNextPageParam: (lastPage, pages) => {
      // If the last page has fewer items than PAGE_SIZE, we've reached the end
      if (lastPage.conversations.length < PAGE_SIZE) return undefined
      return pages.length + 1
    },
    initialPageParam: 1,
  })

  // Intersection observer for infinite scroll
  useEffect(() => {
    if (!loadMoreRef.current || !hasNextPage || isFetchingNextPage) return

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          fetchNextPage()
        }
      },
      { threshold: 0.1 }
    )

    observer.observe(loadMoreRef.current)
    return () => observer.disconnect()
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  // Flatten all pages into single conversations array - memoize to avoid recalculation
  const conversations = useMemo(() => {
    if (!data?.pages) return []
    return data.pages.flatMap(page => page.conversations)
  }, [data?.pages])
  
  // Group conversations by date - memoize to avoid recalculation
  const groupByDate = useCallback((conversations: Conversation[]) => {
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
  }, [])

  const truncateText = useCallback((text: string, maxLength: number = 50) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }, [])
  
  // Memoize grouped conversations to avoid recalculation
  const grouped = useMemo(() => {
    if (conversations.length === 0) return {}
    return groupByDate(conversations)
  }, [conversations, groupByDate])

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
  
  if (conversations.length === 0) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary" align="center">
          No conversations yet
        </Typography>
      </Box>
    )
  }

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
      
      {/* Infinite scroll trigger */}
      {hasNextPage && (
        <Box ref={loadMoreRef} sx={{ p: 2, textAlign: 'center' }}>
          {isFetchingNextPage ? (
            <CircularProgress size={24} />
          ) : (
            <Typography variant="caption" color="text.secondary">
              Loading more...
            </Typography>
          )}
        </Box>
      )}
    </Box>
  )
}

// Export memoized version - only re-render if spaceId changes
export default memo(ConversationListComponent, (prevProps, nextProps) => {
  return prevProps.spaceId === nextProps.spaceId
})
