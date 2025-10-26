import { useEffect, useRef, useCallback } from 'react'
import { Box, Typography } from '@mui/material'
import { useParams } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { conversationApi } from '../services/api'
import Message from './Message'
import MessageInput from './MessageInput'
import StreamingMessage from './StreamingMessage'
import { MessageSkeleton } from './LoadingSkeleton'
import { useMessageStream } from '../hooks/useMessageStream'
import { useToast } from '../hooks/useToast'
import type { Message as MessageType } from '../types/api'

export default function ChatInterface() {
  const { conversationId } = useParams()
  const queryClient = useQueryClient()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { state: streamState, sendMessage: sendStreamMessage } = useMessageStream()
  const toast = useToast()

  // Fetch messages
  const {
    data: messagesData,
    isLoading: messagesLoading,
    error: messagesError,
  } = useQuery({
    queryKey: ['messages', conversationId],
    queryFn: () => conversationApi.loadMessages(conversationId!, 100, 0),
    enabled: !!conversationId,
  })

  // Scroll to bottom when messages change or streaming updates - memoize callback
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])
  
  useEffect(() => {
    scrollToBottom()
  }, [messagesData?.messages, streamState.partialContent, scrollToBottom])

  // Invalidate messages when streaming completes
  useEffect(() => {
    if (streamState.finalMessage) {
      queryClient.invalidateQueries({ queryKey: ['messages', conversationId] })
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      toast.success('Message sent successfully!')
    }
  }, [streamState.finalMessage, conversationId, queryClient, toast])

  // Show error toast when streaming fails
  useEffect(() => {
    if (streamState.error) {
      toast.error(streamState.error)
    }
  }, [streamState.error, toast])

  // Handle send - memoize callback to prevent unnecessary re-renders
  const handleSend = useCallback((message: string) => {
    if (conversationId) {
      sendStreamMessage(conversationId, message)
    }
  }, [conversationId, sendStreamMessage])

  // No conversation selected
  if (!conversationId) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 4,
        }}
      >
        <Box sx={{ textAlign: 'center', maxWidth: 500 }}>
          <Typography variant="h4" gutterBottom color="primary">
            Welcome to Sutra AI
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Start a new conversation or select an existing one from the sidebar.
          </Typography>
        </Box>
      </Box>
    )
  }

  // Loading state
  if (messagesLoading) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box sx={{ flex: 1, overflow: 'auto' }}>
          <MessageSkeleton count={3} />
        </Box>
      </Box>
    )
  }

  // Error state
  if (messagesError) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 4,
        }}
      >
        <Typography variant="body1" color="error">
          Failed to load messages. Please try again.
        </Typography>
      </Box>
    )
  }

  const messages = messagesData?.messages || []

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          p: 3,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {messages.length === 0 ? (
          <Box
            sx={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography variant="body1" color="text.secondary">
              Start the conversation by sending a message below.
            </Typography>
          </Box>
        ) : (
          <>
            {messages.map((message: MessageType) => (
              <Message key={message.id} message={message} conversationId={conversationId} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}

        {/* Streaming message indicator */}
        {streamState.isStreaming && (
          <StreamingMessage
            partialContent={streamState.partialContent}
            confidence={streamState.confidence}
            progress={streamState.progress}
            isStreaming={true}
          />
        )}

        {/* Error indicator */}
        {streamState.error && (
          <Box sx={{ p: 2, bgcolor: 'error.light', borderRadius: 1, mb: 2 }}>
            <Typography variant="body2" color="error.dark">
              {streamState.error}
            </Typography>
          </Box>
        )}
      </Box>

      {/* Message Input Area */}
      <MessageInput
        onSend={handleSend}
        isLoading={streamState.isStreaming}
        disabled={!conversationId || streamState.isStreaming}
        placeholder="Type your message..."
      />
    </Box>
  )
}
