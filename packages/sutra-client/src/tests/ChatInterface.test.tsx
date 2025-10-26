/**
 * Test suite for ChatInterface component
 * 
 * Tests message display, sending, loading states,
 * and integration with streaming.
 * 
 * NOTE: Currently disabled - ChatInterface component needs prop refactoring
 * to support conversationId prop for proper testing.
 */

/*
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import ChatInterface from '../components/ChatInterface';
import * as api from '../services/api';

// Mock API module
vi.mock('../services/api');

// Test wrapper with providers
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  
  return ({ children }: { children: React.ReactNode }) => (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </BrowserRouter>
  );
};

describe('ChatInterface', () => {
  const mockConversationId = 'conv_123';
  
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Message Display', () => {
    it('renders messages from API', async () => {
      const mockMessages = [
        {
          id: 'msg_1',
          role: 'user',
          content: 'Hello',
          timestamp: '2024-10-26T10:00:00Z',
        },
        {
          id: 'msg_2',
          role: 'assistant',
          content: 'Hi there!',
          confidence: 0.95,
          timestamp: '2024-10-26T10:00:01Z',
        },
      ];
      
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({
        messages: mockMessages,
        total: 2,
      });
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      await waitFor(() => {
        expect(screen.getByText('Hello')).toBeInTheDocument();
        expect(screen.getByText('Hi there!')).toBeInTheDocument();
      });
    });
    
    it('distinguishes user and assistant messages visually', async () => {
      const mockMessages = [
        { id: 'msg_1', role: 'user', content: 'User message', timestamp: '2024-10-26T10:00:00Z' },
        { id: 'msg_2', role: 'assistant', content: 'Assistant message', confidence: 0.9, timestamp: '2024-10-26T10:00:01Z' },
      ];
      
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({ messages: mockMessages, total: 2 });
      
      const { container } = render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      await waitFor(() => {
        const userMessage = container.querySelector('.user-message');
        const assistantMessage = container.querySelector('.assistant-message');
        
        expect(userMessage).toBeInTheDocument();
        expect(assistantMessage).toBeInTheDocument();
      });
    });
    
    it('displays confidence scores for assistant messages', async () => {
      const mockMessages = [
        {
          id: 'msg_1',
          role: 'assistant',
          content: 'High confidence answer',
          confidence: 0.95,
          timestamp: '2024-10-26T10:00:00Z',
        },
      ];
      
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({ messages: mockMessages, total: 1 });
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      await waitFor(() => {
        expect(screen.getByText(/95%/i)).toBeInTheDocument();
      });
    });
  });

  describe('Message Sending', () => {
    it('sends message when Enter is pressed', async () => {
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({ messages: [], total: 0 });
      vi.mocked(api.conversationApi.sendMessage).mockResolvedValue({
        user_message: {
          id: 'msg_3',
          role: 'user',
          content: 'Test message',
          timestamp: '2024-10-26T10:00:00Z',
        },
        assistant_message: {
          id: 'msg_4',
          role: 'assistant',
          content: 'Test response',
          confidence: 0.9,
          timestamp: '2024-10-26T10:00:01Z',
        },
      });
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      const input = screen.getByPlaceholderText(/type a message/i);
      
      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
      
      await waitFor(() => {
        expect(api.conversationApi.sendMessage).toHaveBeenCalledWith(
          mockConversationId,
          'Test message'
        );
      });
    });
    
    it('does not send empty messages', async () => {
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({ messages: [], total: 0 });
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      const input = screen.getByPlaceholderText(/type a message/i);
      
      fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
      
      await waitFor(() => {
        expect(api.conversationApi.sendMessage).not.toHaveBeenCalled();
      });
    });
    
    it('disables input while sending', async () => {
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({ messages: [], total: 0 });
      vi.mocked(api.conversationApi.sendMessage).mockImplementation(
        () => new Promise(resolve => setTimeout(resolve, 100))
      );
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      const input = screen.getByPlaceholderText(/type a message/i);
      
      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
      
      await waitFor(() => {
        expect(input).toBeDisabled();
      });
    });
  });

  describe('Loading States', () => {
    it('shows loading skeleton while fetching messages', () => {
      vi.mocked(api.conversationApi.loadMessages).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      expect(screen.getByTestId('message-skeleton')).toBeInTheDocument();
    });
    
    it('hides loading skeleton after messages load', async () => {
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({ messages: [], total: 0 });
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      await waitFor(() => {
        expect(screen.queryByTestId('message-skeleton')).not.toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error message when loading messages fails', async () => {
      vi.mocked(api.conversationApi.loadMessages).mockRejectedValue(
        new Error('Failed to load messages')
      );
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      await waitFor(() => {
        expect(screen.getByText(/failed to load messages/i)).toBeInTheDocument();
      });
    });
    
    it('displays error message when sending message fails', async () => {
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({ messages: [], total: 0 });
      vi.mocked(api.conversationApi.sendMessage).mockRejectedValue(
        new Error('Failed to send message')
      );
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      const input = screen.getByPlaceholderText(/type a message/i);
      
      fireEvent.change(input, { target: { value: 'Test message' } });
      fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' });
      
      await waitFor(() => {
        expect(screen.getByText(/failed to send message/i)).toBeInTheDocument();
      });
    });
  });

  describe('Empty States', () => {
    it('shows empty state when no messages', async () => {
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({ messages: [], total: 0 });
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      await waitFor(() => {
        expect(screen.getByText(/no messages yet/i)).toBeInTheDocument();
      });
    });
    
    it('shows prompt to start conversation', async () => {
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({ messages: [], total: 0 });
      
      render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      await waitFor(() => {
        expect(screen.getByText(/start a conversation/i)).toBeInTheDocument();
      });
    });
  });

  describe('Auto-Scroll', () => {
    it('scrolls to bottom when new message arrives', async () => {
      const mockMessages = [
        { id: 'msg_1', role: 'user', content: 'Message 1', timestamp: '2024-10-26T10:00:00Z' },
      ];
      
      vi.mocked(api.conversationApi.loadMessages).mockResolvedValue({
        messages: mockMessages,
        total: 1,
      });
      
      const { container } = render(<ChatInterface conversationId={mockConversationId} />, {
        wrapper: createWrapper(),
      });
      
      const scrollToSpy = vi.fn();
      const messagesContainer = container.querySelector('.messages-container');
      if (messagesContainer) {
        messagesContainer.scrollTo = scrollToSpy;
      }
      
      await waitFor(() => {
        expect(screen.getByText('Message 1')).toBeInTheDocument();
      });
      
      // Verify scrollTo was called (scroll to bottom)
      expect(scrollToSpy).toHaveBeenCalled();
    });
  });
});


// Example: Hook testing (useMessageStream)
describe('useMessageStream', () => {
  it('receives streaming events in order', async () => {
    // This would test the custom hook
    // See: https://react-hooks-testing-library.com/
  });
  
  it('handles connection errors gracefully', async () => {
    // Test error handling
  });
  
  it('cancels stream on unmount', async () => {
    // Test cleanup
  });
});
*/