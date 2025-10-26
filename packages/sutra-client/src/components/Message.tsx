import { Box, Typography, Avatar, Paper } from '@mui/material'
import { Person, SmartToy } from '@mui/icons-material'
import { memo, useMemo } from 'react'
import type { Message as MessageType } from '../types/api'
import ReasoningPathView from './ReasoningPathView'

interface MessageProps {
  message: MessageType
  conversationId?: string
}

// Memoized Message component to prevent unnecessary re-renders
function MessageComponent({ message, conversationId }: MessageProps) {
  const isUser = message.type === 'user'
  
  // Format timestamp - memoize to avoid recalculation
  const formattedTime = useMemo(() => {
    const date = new Date(message.timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    
    return date.toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    })
  }, [message.timestamp])

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        gap: 2,
        mb: 3,
      }}
      role="article"
      aria-label={`${isUser ? 'Your' : 'Assistant'} message`}
    >
      {/* Avatar */}
      <Avatar
        sx={{
          bgcolor: isUser ? 'primary.main' : 'secondary.main',
          width: 36,
          height: 36,
          flexShrink: 0,
        }}
        aria-label={isUser ? 'User avatar' : 'Assistant avatar'}
      >
        {isUser ? <Person fontSize="small" /> : <SmartToy fontSize="small" />}
      </Avatar>

      {/* Message Content */}
      <Box
        sx={{
          maxWidth: '70%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: isUser ? 'flex-end' : 'flex-start',
        }}
      >
        {/* Message Bubble */}
        <Paper
          elevation={1}
          sx={{
            px: 2,
            py: 1.5,
            bgcolor: isUser ? 'primary.main' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary',
            borderRadius: 2,
            borderTopRightRadius: isUser ? 0 : 2,
            borderTopLeftRadius: isUser ? 2 : 0,
          }}
        >
          <Typography
            variant="body1"
            sx={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {message.content}
          </Typography>

          {/* Show confidence for assistant messages */}
          {!isUser && message.metadata?.confidence && (
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                mt: 1,
                opacity: 0.7,
                fontSize: '0.75rem',
              }}
            >
              Confidence: {Math.round(message.metadata.confidence * 100)}%
            </Typography>
          )}
        </Paper>

        {/* Timestamp */}
        <Typography
          variant="caption"
          sx={{
            mt: 0.5,
            color: 'text.secondary',
            fontSize: '0.75rem',
          }}
        >
          {formattedTime}
        </Typography>

        {/* Reasoning Path Visualization for assistant messages */}
        {!isUser && conversationId && message.id && (
          <Box sx={{ width: '100%', mt: 1 }}>
            <ReasoningPathView
              messageId={message.id}
              conversationId={conversationId}
              confidence={message.metadata?.confidence as number | undefined}
            />
          </Box>
        )}
      </Box>
    </Box>
  )
}

// Export memoized version - only re-render if message or conversationId changes
export default memo(MessageComponent, (prevProps, nextProps) => {
  return (
    prevProps.message.id === nextProps.message.id &&
    prevProps.message.content === nextProps.message.content &&
    prevProps.message.timestamp === nextProps.message.timestamp &&
    prevProps.conversationId === nextProps.conversationId
  )
})
