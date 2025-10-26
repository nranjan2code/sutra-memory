import { useState, useRef, useEffect, KeyboardEvent } from 'react'
import { Box, TextField, IconButton, CircularProgress, Typography } from '@mui/material'
import { Send } from '@mui/icons-material'

interface MessageInputProps {
  onSend: (message: string) => void
  isLoading?: boolean
  placeholder?: string
  disabled?: boolean
}

export default function MessageInput({
  onSend,
  isLoading = false,
  placeholder = 'Type a message...',
  disabled = false,
}: MessageInputProps) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea as content grows
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`
    }
  }, [message])

  const handleSend = () => {
    const trimmedMessage = message.trim()
    if (trimmedMessage && !isLoading && !disabled) {
      onSend(trimmedMessage)
      setMessage('')
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    // Send on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Box
      sx={{
        p: 2,
        borderTop: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
      component="form"
      onSubmit={(e) => {
        e.preventDefault()
        handleSend()
      }}
      aria-label="Message input form"
    >
      <Box
        sx={{
          display: 'flex',
          gap: 1,
          alignItems: 'flex-end',
        }}
      >
        <TextField
          inputRef={textareaRef}
          fullWidth
          multiline
          maxRows={8}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          variant="outlined"
          inputProps={{
            'aria-label': 'Message input',
            'aria-describedby': 'message-input-hint',
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              bgcolor: 'background.default',
              '& textarea': {
                resize: 'none',
                overflowY: 'auto',
                maxHeight: 200,
              },
            },
          }}
        />
        
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={!message.trim() || isLoading || disabled}
          aria-label="Send message"
          type="submit"
          sx={{
            bgcolor: 'primary.main',
            color: 'primary.contrastText',
            '&:hover': {
              bgcolor: 'primary.dark',
            },
            '&.Mui-disabled': {
              bgcolor: 'action.disabledBackground',
              color: 'action.disabled',
            },
            width: 48,
            height: 48,
            flexShrink: 0,
          }}
        >
          {isLoading ? (
            <CircularProgress size={24} sx={{ color: 'inherit' }} />
          ) : (
            <Send />
          )}
        </IconButton>
      </Box>

      {/* Accessibility hint */}
      <Typography
        id="message-input-hint"
        variant="caption"
        sx={{
          display: 'block',
          mt: 0.5,
          color: 'text.secondary',
          fontSize: '0.7rem',
        }}
      >
        Press Enter to send, Shift+Enter for new line
      </Typography>
    </Box>
  )
}
