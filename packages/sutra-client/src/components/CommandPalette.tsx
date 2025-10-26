/**
 * CommandPalette Component
 * 
 * Modal search interface with Cmd+K shortcut.
 * Provides quick access to conversations, messages, and spaces.
 */

import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuickSearch, SearchResult } from '../hooks/useSearch';
import SearchResults from './SearchResults';
import './CommandPalette.css';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const modalRef = useRef<HTMLDivElement>(null);

  const { query, setQuery, results, isLoading, clear } = useQuickSearch();
  const [selectedIndex, setSelectedIndex] = useState<number>(0);

  // Focus input when opened
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Reset state when closed
  useEffect(() => {
    if (!isOpen) {
      clear();
      setSelectedIndex(0);
    }
  }, [isOpen, clear]);

  // Keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Get all results as flat list
      const allResults = getAllResults();

      switch (e.key) {
        case 'Escape':
          e.preventDefault();
          onClose();
          break;

        case 'ArrowDown':
          e.preventDefault();
          setSelectedIndex((prev) => 
            Math.min(prev + 1, allResults.length - 1)
          );
          break;

        case 'ArrowUp':
          e.preventDefault();
          setSelectedIndex((prev) => Math.max(prev - 1, 0));
          break;

        case 'Enter':
          e.preventDefault();
          if (allResults[selectedIndex]) {
            handleResultSelect(allResults[selectedIndex]);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, results, onClose]);

  // Click outside to close
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (modalRef.current && !modalRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, onClose]);

  // Get all results as flat list for keyboard navigation
  const getAllResults = (): SearchResult[] => {
    if (!results) return [];

    const allResults: SearchResult[] = [];
    
    // Add conversations
    allResults.push(...results.groups.conversations.results);
    
    // Add messages
    allResults.push(...results.groups.messages.results);
    
    // Add spaces
    allResults.push(...results.groups.spaces.results);

    return allResults;
  };

  // Handle result selection
  const handleResultSelect = (result: SearchResult) => {
    // Navigate based on result type
    switch (result.type) {
      case 'conversation':
        navigate(`/conversations/${result.id}`);
        break;
      case 'message':
        // Navigate to conversation containing the message
        navigate(`/conversations/${result.metadata.conversation_id}`);
        break;
      case 'space':
        navigate(`/spaces/${result.id}`);
        break;
    }

    onClose();
  };

  // Don't render if not open
  if (!isOpen) return null;

  return (
    <div className="command-palette-overlay">
      <div className="command-palette-modal" ref={modalRef}>
        {/* Search Input */}
        <div className="command-palette-header">
          <svg
            className="search-icon"
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16zM19 19l-4.35-4.35"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search conversations, messages, spaces..."
            className="command-palette-input"
            autoComplete="off"
            spellCheck={false}
          />

          {isLoading && (
            <div className="loading-spinner">
              <div className="spinner" />
            </div>
          )}

          {query && (
            <button
              className="clear-button"
              onClick={() => setQuery('')}
              aria-label="Clear search"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0zM5.354 4.646a.5.5 0 1 0-.708.708L7.293 8l-2.647 2.646a.5.5 0 0 0 .708.708L8 8.707l2.646 2.647a.5.5 0 0 0 .708-.708L8.707 8l2.647-2.646a.5.5 0 0 0-.708-.708L8 7.293 5.354 4.646z" />
              </svg>
            </button>
          )}
        </div>

        {/* Results */}
        <div className="command-palette-results">
          {!query && (
            <div className="empty-state">
              <p className="empty-state-title">Search Sutra AI</p>
              <p className="empty-state-description">
                Find conversations, messages, and spaces using semantic search.
              </p>
              <div className="keyboard-hints">
                <kbd>↑</kbd> <kbd>↓</kbd> to navigate
                <span className="separator">•</span>
                <kbd>Enter</kbd> to select
                <span className="separator">•</span>
                <kbd>Esc</kbd> to close
              </div>
            </div>
          )}

          {query && !isLoading && results && results.total_count === 0 && (
            <div className="empty-state">
              <p className="empty-state-title">No results found</p>
              <p className="empty-state-description">
                Try a different search term or check your filters.
              </p>
            </div>
          )}

          {results && results.total_count > 0 && (
            <SearchResults
              results={results}
              selectedIndex={selectedIndex}
              onSelect={handleResultSelect}
              onHover={setSelectedIndex}
            />
          )}
        </div>

        {/* Footer */}
        <div className="command-palette-footer">
          <div className="footer-left">
            {results && results.total_count > 0 && (
              <span className="result-count">
                {results.total_count} result{results.total_count !== 1 ? 's' : ''}
              </span>
            )}
          </div>
          <div className="footer-right">
            <span className="hint">
              <kbd>Cmd</kbd>+<kbd>K</kbd> to search
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
