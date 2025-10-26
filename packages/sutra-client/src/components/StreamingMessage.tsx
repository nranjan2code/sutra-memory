/**
 * StreamingMessage Component
 * 
 * Displays a message that's being streamed with progressive refinement.
 * Shows streaming indicator, partial content, and real-time confidence updates.
 */

import { Avatar, Box, Typography, LinearProgress, Chip } from '@mui/material';
import { SmartToy, Psychology, Insights } from '@mui/icons-material';

interface ProgressState {
  stage: string;
  message: string;
  confidence?: number;
}

interface StreamingMessageProps {
  partialContent: string;
  confidence: number;
  progress: ProgressState | null;
  isStreaming: boolean;
}

export default function StreamingMessage({
  partialContent,
  confidence,
  progress,
  isStreaming,
}: StreamingMessageProps) {
  return (
    <Box
      sx={{
        display: 'flex',
        gap: 2,
        mb: 2,
        alignItems: 'flex-start',
      }}
    >
      {/* Avatar */}
      <Avatar
        sx={{
          bgcolor: 'primary.main',
          width: 32,
          height: 32,
        }}
      >
        <SmartToy sx={{ fontSize: 20 }} />
      </Avatar>

      {/* Message Content */}
      <Box sx={{ flex: 1 }}>
        {/* Progress Indicator */}
        {progress && (
          <Box sx={{ mb: 1.5 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                mb: 0.5,
              }}
            >
              {progress.stage === 'loading_context' && (
                <Psychology sx={{ fontSize: 16, color: 'primary.main' }} />
              )}
              {progress.stage === 'querying_knowledge' && (
                <Insights sx={{ fontSize: 16, color: 'secondary.main' }} />
              )}
              {progress.stage === 'reasoning' && (
                <SmartToy sx={{ fontSize: 16, color: 'success.main' }} />
              )}
              
              <Typography
                variant="caption"
                sx={{
                  color: 'text.secondary',
                  fontStyle: 'italic',
                }}
              >
                {progress.message}
              </Typography>
            </Box>

            {/* Progress bar */}
            {isStreaming && (
              <LinearProgress
                sx={{
                  height: 2,
                  borderRadius: 1,
                  bgcolor: 'action.hover',
                }}
              />
            )}
          </Box>
        )}

        {/* Partial Content */}
        {partialContent && (
          <Box>
            <Typography
              variant="body1"
              sx={{
                color: 'text.primary',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                opacity: isStreaming ? 0.85 : 1,
                transition: 'opacity 0.3s ease',
              }}
            >
              {partialContent}
              {isStreaming && (
                <Box
                  component="span"
                  sx={{
                    display: 'inline-block',
                    width: 8,
                    height: 16,
                    bgcolor: 'primary.main',
                    ml: 0.5,
                    animation: 'blink 1s infinite',
                    '@keyframes blink': {
                      '0%, 49%': { opacity: 1 },
                      '50%, 100%': { opacity: 0 },
                    },
                  }}
                />
              )}
            </Typography>

            {/* Confidence Indicator */}
            {confidence > 0 && (
              <Box sx={{ mt: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={`Confidence: ${Math.round(confidence * 100)}%`}
                  size="small"
                  color={
                    confidence >= 0.8
                      ? 'success'
                      : confidence >= 0.5
                      ? 'warning'
                      : 'error'
                  }
                  variant={isStreaming ? 'outlined' : 'filled'}
                  sx={{
                    fontSize: '0.7rem',
                    height: 20,
                    transition: 'all 0.3s ease',
                  }}
                />
                
                {isStreaming && (
                  <Typography
                    variant="caption"
                    sx={{
                      color: 'text.secondary',
                      fontStyle: 'italic',
                    }}
                  >
                    Refining...
                  </Typography>
                )}
              </Box>
            )}
          </Box>
        )}

        {/* Empty state (initial) */}
        {!partialContent && !progress && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <LinearProgress
              sx={{
                flex: 1,
                height: 2,
                borderRadius: 1,
                bgcolor: 'action.hover',
              }}
            />
            <Typography
              variant="caption"
              sx={{
                color: 'text.secondary',
                fontStyle: 'italic',
              }}
            >
              Thinking...
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}
