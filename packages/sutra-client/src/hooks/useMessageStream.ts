/**
 * useMessageStream Hook
 * 
 * Manages Server-Sent Events (SSE) connection for streaming message responses.
 * Handles progressive message refinement with confidence updates.
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../services/api';

interface UserMessage {
  id: string;
  content: string;
  timestamp: string;
}

interface ProgressEvent {
  stage: string;
  message: string;
  confidence?: number;
}

interface ChunkEvent {
  content: string;
  confidence: number;
}

interface CompleteEvent {
  id: string;
  conversation_id: string;
  role: string;
  content: string;
  timestamp: string;
  metadata: {
    reasoning_depth: string;
    concepts_used: string[];
    confidence: number;
  };
}

interface StreamState {
  isStreaming: boolean;
  userMessage: UserMessage | null;
  progress: ProgressEvent | null;
  partialContent: string;
  confidence: number;
  finalMessage: CompleteEvent | null;
  error: string | null;
}

interface UseMessageStreamReturn {
  state: StreamState;
  sendMessage: (conversationId: string, message: string) => void;
  cancel: () => void;
}

export function useMessageStream(): UseMessageStreamReturn {
  const [state, setState] = useState<StreamState>({
    isStreaming: false,
    userMessage: null,
    progress: null,
    partialContent: '',
    confidence: 0,
    finalMessage: null,
    error: null,
  });

  const eventSourceRef = useRef<EventSource | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const cancel = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setState((prev) => ({
      ...prev,
      isStreaming: false,
    }));
  }, []);

  const sendMessage = useCallback(
    (conversationId: string, message: string) => {
      // Cancel any existing stream
      cancel();

      // Reset state
      setState({
        isStreaming: true,
        userMessage: null,
        progress: null,
        partialContent: '',
        confidence: 0,
        finalMessage: null,
        error: null,
      });

      // Get auth token
      const token = localStorage.getItem('token');
      if (!token) {
        setState((prev) => ({
          ...prev,
          isStreaming: false,
          error: 'Authentication required',
        }));
        return;
      }

      // Create EventSource connection
      // Note: EventSource doesn't support POST or custom headers directly,
      // so we use a workaround with fetch + ReadableStream
      const controller = new AbortController();
      abortControllerRef.current = controller;

      const url = `${API_BASE_URL}/conversations/${conversationId}/message/stream`;

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message,
          reasoning_depth: 'balanced',
        }),
        signal: controller.signal,
      })
        .then(async (response) => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          const reader = response.body?.getReader();
          if (!reader) {
            throw new Error('No response body');
          }

          const decoder = new TextDecoder();
          let buffer = '';

          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              break;
            }

            buffer += decoder.decode(value, { stream: true });

            // Process complete SSE messages
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || ''; // Keep incomplete message in buffer

            for (const line of lines) {
              if (!line.trim()) continue;

              // Parse SSE format
              const eventMatch = line.match(/^event: (.+)$/m);
              const dataMatch = line.match(/^data: (.+)$/m);

              if (eventMatch && dataMatch) {
                const eventType = eventMatch[1];
                const eventData = JSON.parse(dataMatch[1]);

                handleEvent(eventType, eventData);
              } else if (dataMatch) {
                // No explicit event type (default to 'message')
                const eventData = JSON.parse(dataMatch[1]);
                handleEvent('message', eventData);
              }
            }
          }

          // Mark streaming as complete
          setState((prev) => ({
            ...prev,
            isStreaming: false,
          }));
        })
        .catch((error) => {
          if (error.name === 'AbortError') {
            // User cancelled
            return;
          }

          console.error('Streaming error:', error);
          setState((prev) => ({
            ...prev,
            isStreaming: false,
            error: error.message || 'Failed to stream message',
          }));
        });
    },
    [cancel]
  );

  const handleEvent = (eventType: string, data: Record<string, unknown>) => {
    switch (eventType) {
      case 'user_message':
        setState((prev) => ({
          ...prev,
          userMessage: data as UserMessage,
        }));
        break;

      case 'progress':
        setState((prev) => ({
          ...prev,
          progress: data as ProgressEvent,
          confidence: data.confidence || prev.confidence,
        }));
        break;

      case 'chunk':
        setState((prev) => ({
          ...prev,
          partialContent: data.content,
          confidence: data.confidence,
        }));
        break;

      case 'complete':
        setState((prev) => ({
          ...prev,
          finalMessage: data as CompleteEvent,
          partialContent: data.content,
          confidence: data.metadata.confidence,
          isStreaming: false,
        }));
        break;

      case 'error':
        setState((prev) => ({
          ...prev,
          error: data.message || 'An error occurred',
          isStreaming: false,
        }));
        break;

      default:
        console.warn('Unknown event type:', eventType, data);
    }
  };

  return {
    state,
    sendMessage,
    cancel,
  };
}
