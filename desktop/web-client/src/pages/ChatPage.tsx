import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Send, Loader2, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { sutraAPI } from '../api/client';
import { useChatStore } from '../store';

export function ChatPage() {
  const [input, setInput] = useState('');
  const messages = useChatStore((state) => state.messages);
  const addMessage = useChatStore((state) => state.addMessage);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const queryMutation = useMutation({
    mutationFn: async (query: string) => {
      addMessage('user', query);
      return sutraAPI.query(query);
    },
    onSuccess: (data) => {
      addMessage('assistant', data.answer);
    },
    onError: (error: any) => {
      addMessage('assistant', `Error: ${error.message || 'Failed to process query'}`);
    },
  });

  const learnMutation = useMutation({
    mutationFn: async (content: string) => {
      addMessage('user', `/learn ${content}`);
      return sutraAPI.learn(content);
    },
    onSuccess: (data) => {
      addMessage('assistant', `✓ Learned: ${data.message}`);
    },
    onError: (error: any) => {
      addMessage('assistant', `Error: ${error.message || 'Failed to learn'}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || queryMutation.isPending || learnMutation.isPending) return;

    const trimmed = input.trim();
    
    // Check for /learn command
    if (trimmed.startsWith('/learn ')) {
      const content = trimmed.substring(7).trim();
      if (content) {
        learnMutation.mutate(content);
      }
    } else {
      queryMutation.mutate(trimmed);
    }
    
    setInput('');
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const isLoading = queryMutation.isPending || learnMutation.isPending;

  return (
    <div className="h-full flex flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center space-y-4 max-w-md">
              <div className="w-16 h-16 mx-auto rounded-full bg-primary-600/20 flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-primary-500" />
              </div>
              <h2 className="text-2xl font-bold text-white">Start a conversation</h2>
              <p className="text-dark-400">
                Ask questions or teach me something new with <code className="px-2 py-1 bg-dark-800 rounded">/learn</code>
              </p>
              <div className="flex flex-wrap gap-2 justify-center pt-4">
                <button
                  onClick={() => setInput('What can you do?')}
                  className="px-4 py-2 text-sm bg-dark-800 hover:bg-dark-700 rounded-lg transition-colors"
                >
                  What can you do?
                </button>
                <button
                  onClick={() => setInput('/learn The Earth orbits the Sun')}
                  className="px-4 py-2 text-sm bg-dark-800 hover:bg-dark-700 rounded-lg transition-colors"
                >
                  Example: Teach a fact
                </button>
              </div>
            </div>
          </div>
        )}

        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-2xl px-4 py-3 rounded-2xl ${
                  message.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-800 text-dark-100'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <span className="text-xs opacity-50 mt-1 block">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="max-w-2xl px-4 py-3 rounded-2xl bg-dark-800 text-dark-100">
              <Loader2 className="w-5 h-5 animate-spin" />
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-dark-700 p-4">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question or /learn something..."
              disabled={isLoading}
              className="flex-1 px-4 py-3 bg-dark-800 border border-dark-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="px-6 py-3 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-medium transition-colors flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
          <p className="text-xs text-dark-500 mt-2">
            Tip: Use <code className="px-1 py-0.5 bg-dark-800 rounded">/learn [content]</code> to teach new knowledge
          </p>
        </form>
      </div>
    </div>
  );
}
