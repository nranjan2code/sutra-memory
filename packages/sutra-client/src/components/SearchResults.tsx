/**
 * SearchResults Component
 * 
 * Displays grouped search results with highlighting and keyboard navigation.
 */

import { memo, useMemo, useCallback } from 'react';
import { GroupedSearchResults, SearchResult } from '../hooks/useSearch';
import './SearchResults.css';

interface SearchResultsProps {
  results: GroupedSearchResults;
  selectedIndex: number;
  onSelect: (result: SearchResult) => void;
  onHover: (index: number) => void;
}

function SearchResultsComponent({
  results,
  selectedIndex,
  onSelect,
  onHover
}: SearchResultsProps) {
  // Flatten results for index tracking - memoize to avoid recalculation
  const allResults = useMemo(() => [
    ...results.groups.conversations.results,
    ...results.groups.messages.results,
    ...results.groups.spaces.results
  ], [results.groups.conversations.results, results.groups.messages.results, results.groups.spaces.results])

  // Get global index for a result - memoize callback
  const getResultIndex = useCallback((result: SearchResult): number => {
    return allResults.findIndex((r) => r.id === result.id);
  }, [allResults])

  // Highlight matches in text - memoize callback
  const highlightText = useCallback((_text: string, _score: number): JSX.Element => {
    // For now, simple bold rendering
    // In production, you'd want to highlight actual query matches
    return <span>{_text}</span>;
  }, [])

  // Format timestamp - memoize callback
  const formatTimestamp = useCallback((timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
  }, [])

  return (
    <div className="search-results">
      {/* Conversations */}
      {results.groups.conversations.count > 0 && (
        <div className="result-group">
          <div className="group-header">
            <span className="group-title">
              <svg className="group-icon" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M2.5 3.5a.5.5 0 0 1 0-1h11a.5.5 0 0 1 0 1h-11zm2-2a.5.5 0 0 1 0-1h7a.5.5 0 0 1 0 1h-7zM0 13a1.5 1.5 0 0 0 1.5 1.5h13A1.5 1.5 0 0 0 16 13V6a1.5 1.5 0 0 0-1.5-1.5h-13A1.5 1.5 0 0 0 0 6v7zm1.5.5A.5.5 0 0 1 1 13V6a.5.5 0 0 1 .5-.5h13a.5.5 0 0 1 .5.5v7a.5.5 0 0 1-.5.5h-13z" />
              </svg>
              Conversations
            </span>
            <span className="group-count">{results.groups.conversations.count}</span>
          </div>
          <div className="group-results">
            {results.groups.conversations.results.map((result) => {
              const index = getResultIndex(result);
              const isSelected = index === selectedIndex;

              return (
                <div
                  key={result.id}
                  className={`result-item ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelect(result)}
                  onMouseEnter={() => onHover(index)}
                >
                  <div className="result-icon">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3 1h10v8H5V6z" />
                    </svg>
                  </div>
                  <div className="result-content">
                    <div className="result-title">
                      {highlightText(result.title, result.score)}
                    </div>
                    <div className="result-meta">
                      <span className="meta-item">
                        {result.metadata.message_count || 0} messages
                      </span>
                      {result.metadata.starred && (
                        <span className="meta-item starred">
                          ⭐ Starred
                        </span>
                      )}
                      <span className="meta-item">
                        {formatTimestamp(result.metadata.updated_at)}
                      </span>
                    </div>
                  </div>
                  <div className="result-score">
                    <span className="score-badge">
                      {Math.round(result.score * 100)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Messages */}
      {results.groups.messages.count > 0 && (
        <div className="result-group">
          <div className="group-header">
            <span className="group-title">
              <svg className="group-icon" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M2.678 11.894a1 1 0 0 1 .287.801 10.97 10.97 0 0 1-.398 2c1.395-.323 2.247-.697 2.634-.893a1 1 0 0 1 .71-.074A8.06 8.06 0 0 0 8 14c3.996 0 7-2.807 7-6 0-3.192-3.004-6-7-6S1 4.808 1 8c0 1.468.617 2.83 1.678 3.894zm-.493 3.905a21.682 21.682 0 0 1-.713.129c-.2.032-.352-.176-.273-.362a9.68 9.68 0 0 0 .244-.637l.003-.01c.248-.72.45-1.548.524-2.319C.743 11.37 0 9.76 0 8c0-3.866 3.582-7 8-7s8 3.134 8 7-3.582 7-8 7a9.06 9.06 0 0 1-2.347-.306c-.52.263-1.639.742-3.468 1.105z" />
              </svg>
              Messages
            </span>
            <span className="group-count">{results.groups.messages.count}</span>
          </div>
          <div className="group-results">
            {results.groups.messages.results.map((result) => {
              const index = getResultIndex(result);
              const isSelected = index === selectedIndex;

              return (
                <div
                  key={result.id}
                  className={`result-item ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelect(result)}
                  onMouseEnter={() => onHover(index)}
                >
                  <div className={`result-icon ${result.metadata.role}`}>
                    {result.metadata.role === 'user' ? (
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M2 5a2 2 0 012-2h12a2 2 0 012 2v10a2 2 0 01-2 2H4a2 2 0 01-2-2V5zm3.293 1.293a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 01-1.414-1.414L7.586 10 5.293 7.707a1 1 0 010-1.414zM11 12a1 1 0 100 2h3a1 1 0 100-2h-3z" />
                      </svg>
                    )}
                  </div>
                  <div className="result-content">
                    <div className="result-snippet">
                      {highlightText(result.content, result.score)}
                    </div>
                    <div className="result-meta">
                      <span className="meta-item">
                        {result.metadata.role === 'user' ? 'You' : 'Sutra AI'}
                      </span>
                      <span className="meta-item">
                        {formatTimestamp(result.metadata.timestamp)}
                      </span>
                    </div>
                  </div>
                  <div className="result-score">
                    <span className="score-badge">
                      {Math.round(result.score * 100)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Spaces */}
      {results.groups.spaces.count > 0 && (
        <div className="result-group">
          <div className="group-header">
            <span className="group-title">
              <svg className="group-icon" width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M9.828 3h3.982a2 2 0 0 1 1.992 2.181l-.637 7A2 2 0 0 1 13.174 14H2.825a2 2 0 0 1-1.991-1.819l-.637-7a1.99 1.99 0 0 1 .342-1.31L.5 3a2 2 0 0 1 2-2h3.672a2 2 0 0 1 1.414.586l.828.828A2 2 0 0 0 9.828 3zm-8.322.12C1.72 3.042 1.95 3 2.19 3h5.396l-.707-.707A1 1 0 0 0 6.172 2H2.5a1 1 0 0 0-1 .981l.006.139z" />
              </svg>
              Spaces
            </span>
            <span className="group-count">{results.groups.spaces.count}</span>
          </div>
          <div className="group-results">
            {results.groups.spaces.results.map((result) => {
              const index = getResultIndex(result);
              const isSelected = index === selectedIndex;

              return (
                <div
                  key={result.id}
                  className={`result-item ${isSelected ? 'selected' : ''}`}
                  onClick={() => onSelect(result)}
                  onMouseEnter={() => onHover(index)}
                >
                  <div className="result-icon space">
                    {result.metadata.icon ? (
                      <span className="space-emoji">{result.metadata.icon}</span>
                    ) : (
                      <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" />
                      </svg>
                    )}
                  </div>
                  <div className="result-content">
                    <div className="result-title">
                      {highlightText(result.title, result.score)}
                    </div>
                    {result.content && (
                      <div className="result-description">
                        {result.content}
                      </div>
                    )}
                    <div className="result-meta">
                      <span className="meta-item">
                        {result.metadata.conversation_count || 0} conversations
                      </span>
                    </div>
                  </div>
                  <div className="result-score">
                    <span className="score-badge">
                      {Math.round(result.score * 100)}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

// Export memoized version - only re-render if results or selectedIndex changes
export default memo(SearchResultsComponent, (prevProps, nextProps) => {
  return (
    prevProps.results === nextProps.results &&
    prevProps.selectedIndex === nextProps.selectedIndex
  )
})
