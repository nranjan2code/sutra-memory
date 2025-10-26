/**
 * useSearch Hook
 * 
 * Hook for semantic search with debouncing and result grouping.
 * Optimized for command palette (Cmd+K) and search pages.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../api/client';

// Types

export interface SearchResult {
  type: 'conversation' | 'message' | 'space';
  id: string;
  title: string;
  content: string;
  metadata: Record<string, any>;
  score: number;
}

export interface SearchGroup {
  count: number;
  results: SearchResult[];
}

export interface GroupedSearchResults {
  total_count: number;
  groups: {
    conversations: SearchGroup;
    messages: SearchGroup;
    spaces: SearchGroup;
  };
}

export interface SearchFilters {
  space_id?: string;
  starred?: boolean;
  date_range?: {
    start: string;
    end: string;
  };
}

export interface UseSearchOptions {
  debounceMs?: number;
  limit?: number;
  filters?: SearchFilters;
  autoSearch?: boolean; // Auto-search on query change
}

export interface UseSearchReturn {
  query: string;
  setQuery: (query: string) => void;
  results: GroupedSearchResults | null;
  isLoading: boolean;
  error: string | null;
  search: (customQuery?: string) => Promise<void>;
  clear: () => void;
}

/**
 * Hook for semantic search with debouncing
 * 
 * @param options - Search options
 * @returns Search state and actions
 * 
 * @example
 * ```tsx
 * const { query, setQuery, results, isLoading } = useSearch({
 *   debounceMs: 300,
 *   limit: 20,
 *   autoSearch: true
 * });
 * 
 * return (
 *   <input
 *     value={query}
 *     onChange={(e) => setQuery(e.target.value)}
 *     placeholder="Search..."
 *   />
 * );
 * ```
 */
export function useSearch(options: UseSearchOptions = {}): UseSearchReturn {
  const {
    debounceMs = 300,
    limit = 30,
    filters = {},
    autoSearch = true
  } = options;

  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<GroupedSearchResults | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Search function
  const search = useCallback(async (customQuery?: string) => {
    const searchQuery = customQuery ?? query;

    // Don't search empty queries
    if (!searchQuery.trim()) {
      setResults(null);
      setError(null);
      return;
    }

    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post<GroupedSearchResults>(
        '/search/query',
        {
          query: searchQuery,
          filters,
          limit
        },
        {
          signal: abortController.signal
        }
      );

      // Only update if not aborted
      if (!abortController.signal.aborted) {
        setResults(response.data);
      }
    } catch (err: any) {
      // Ignore abort errors
      if (err.name === 'AbortError' || err.name === 'CanceledError') {
        return;
      }

      console.error('Search failed:', err);
      setError(err.response?.data?.detail || 'Search failed');
      setResults(null);
    } finally {
      if (!abortController.signal.aborted) {
        setIsLoading(false);
      }
    }
  }, [query, filters, limit]);

  // Clear search
  const clear = useCallback(() => {
    setQuery('');
    setResults(null);
    setError(null);
    setIsLoading(false);

    // Cancel pending request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Clear debounce timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
  }, []);

  // Auto-search with debouncing
  useEffect(() => {
    if (!autoSearch) return;

    // Clear previous timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Don't search empty queries
    if (!query.trim()) {
      setResults(null);
      return;
    }

    // Set new debounce timer
    debounceTimerRef.current = setTimeout(() => {
      search();
    }, debounceMs);

    // Cleanup
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query, autoSearch, debounceMs, search]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  return {
    query,
    setQuery,
    results,
    isLoading,
    error,
    search,
    clear
  };
}

/**
 * Hook for quick search (command palette)
 * 
 * Optimized for fast results with lower limits and shorter debounce.
 * 
 * @example
 * ```tsx
 * const { query, setQuery, results } = useQuickSearch();
 * ```
 */
export function useQuickSearch(): UseSearchReturn {
  return useSearch({
    debounceMs: 200,  // Faster debounce
    limit: 15,        // Fewer results for speed
    autoSearch: true
  });
}

/**
 * Hook for conversation search only
 * 
 * @param filters - Conversation filters
 */
export function useConversationSearch(filters?: SearchFilters) {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (customQuery?: string) => {
    const searchQuery = customQuery ?? query;

    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post<SearchResult[]>(
        '/search/conversations',
        {
          query: searchQuery,
          filters,
          limit: 20
        }
      );

      setResults(response.data);
    } catch (err: any) {
      console.error('Conversation search failed:', err);
      setError(err.response?.data?.detail || 'Search failed');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, [query, filters]);

  const clear = useCallback(() => {
    setQuery('');
    setResults([]);
    setError(null);
  }, []);

  return {
    query,
    setQuery,
    results,
    isLoading,
    error,
    search,
    clear
  };
}

/**
 * Hook for message search only
 * 
 * @param filters - Message filters
 */
export function useMessageSearch(filters?: SearchFilters) {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(async (customQuery?: string) => {
    const searchQuery = customQuery ?? query;

    if (!searchQuery.trim()) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.post<SearchResult[]>(
        '/search/messages',
        {
          query: searchQuery,
          filters,
          limit: 20
        }
      );

      setResults(response.data);
    } catch (err: any) {
      console.error('Message search failed:', err);
      setError(err.response?.data?.detail || 'Search failed');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, [query, filters]);

  const clear = useCallback(() => {
    setQuery('');
    setResults([]);
    setError(null);
  }, []);

  return {
    query,
    setQuery,
    results,
    isLoading,
    error,
    search,
    clear
  };
}
