/**
 * GraphListView - Virtualized list visualization for knowledge graphs
 * 
 * Production-grade component for displaying graph nodes in a scrollable list.
 * Uses react-window for virtualization to handle large datasets efficiently.
 * 
 * Use cases:
 * - Mobile devices (< 768px width)
 * - Small graphs (< 20 nodes)
 * - Search results
 * - Concept browsing
 * 
 * @package @sutra/ui-framework
 */

import React from 'react';
import { FixedSizeList as List } from 'react-window';
import { Card } from '../primitives/Card';
import { Text } from '../primitives/Text';
import { Badge } from '../primitives/Badge';
import './GraphListView.css';

export interface GraphNode {
  id: string;
  content: string;
  confidence: number;
  strength?: number;
  edgeCount?: number;
  accessCount?: number;
  metadata?: Record<string, any>;
}

export interface GraphListViewProps {
  nodes: GraphNode[];
  selectedNodeId?: string | null;
  onSelectNode?: (node: GraphNode) => void;
  onNodeHover?: (node: GraphNode | null) => void;
  containerWidth: number;
  containerHeight: number;
  rowHeight?: number;
  emptyMessage?: string;
  emptyDescription?: string;
  showConfidence?: boolean;
  showEdgeCount?: boolean;
  showStrength?: boolean;
  showAccessCount?: boolean;
  maxContentLength?: number;
}

export const GraphListView: React.FC<GraphListViewProps> = ({
  nodes,
  selectedNodeId,
  onSelectNode,
  onNodeHover,
  containerWidth,
  containerHeight,
  rowHeight = 80,
  emptyMessage = 'No concepts to display',
  emptyDescription = 'The knowledge graph is empty or still loading.',
  showConfidence = true,
  showEdgeCount = true,
  showStrength = true,
  showAccessCount = true,
  maxContentLength = 100,
}) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const node = nodes[index];
    const isSelected = selectedNodeId === node.id;

    const confidenceColorScheme = 
      node.confidence > 0.8 ? 'success' : 
      node.confidence > 0.5 ? 'warning' : 
      'error';

    const truncatedContent = 
      node.content.length > maxContentLength
        ? `${node.content.substring(0, maxContentLength)}...`
        : node.content;

    return (
      <div style={style} className="graph-list-view-row">
        <Card
          variant={isSelected ? 'elevated' : 'default'}
          padding="md"
          interactive
          onClick={() => onSelectNode?.(node)}
          onMouseEnter={() => onNodeHover?.(node)}
          onMouseLeave={() => onNodeHover?.(null)}
          className={`graph-list-view-card ${isSelected ? 'selected' : ''}`}
        >
          <div className="graph-list-view-card-header">
            <Text variant="caption" className="graph-node-id">
              {node.id.substring(0, 8)}
            </Text>
            <div className="graph-badges">
              {showConfidence && (
                <Badge colorScheme={confidenceColorScheme} size="sm">
                  {Math.round(node.confidence * 100)}%
                </Badge>
              )}
              {showEdgeCount && node.edgeCount !== undefined && node.edgeCount > 0 && (
                <Badge colorScheme="info" size="sm">
                  {node.edgeCount} edges
                </Badge>
              )}
            </div>
          </div>

          <div className="graph-list-view-card-content">
            <Text variant="body2" className="graph-node-content">
              {truncatedContent}
            </Text>
          </div>

          <div className="graph-list-view-card-footer">
            {showStrength && node.strength !== undefined && (
              <Text variant="caption" className="graph-metadata">
                Strength: {Math.round(node.strength * 100)}%
              </Text>
            )}
            {showAccessCount && node.accessCount !== undefined && node.accessCount > 0 && (
              <Text variant="caption" className="graph-metadata">
                Accessed: {node.accessCount}x
              </Text>
            )}
          </div>
        </Card>
      </div>
    );
  };

  if (nodes.length === 0) {
    return (
      <div className="graph-list-view-empty">
        <Text variant="h6" color="secondary">
          {emptyMessage}
        </Text>
        <Text variant="body2" color="secondary">
          {emptyDescription}
        </Text>
      </div>
    );
  }

  return (
    <div className="graph-list-view-container">
      <List
        height={containerHeight}
        itemCount={nodes.length}
        itemSize={rowHeight}
        width={containerWidth}
        className="graph-list-view-list"
        overscanCount={3}
      >
        {Row}
      </List>
    </div>
  );
};

GraphListView.displayName = 'GraphListView';
