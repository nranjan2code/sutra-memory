/**
 * Sidebar Component
 * Left navigation panel with search and node list
 */

import { Card, Text, Badge } from '@sutra/ui-framework';
import type { Node } from '@types/graph';
import './Sidebar.css';

interface SidebarProps {
  nodes: Node[];
  onSelectNode: (node: Node) => void;
}

export default function Sidebar({ nodes, onSelectNode }: SidebarProps) {
  // Show top 50 nodes by confidence
  const topNodes = [...nodes]
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 50);

  return (
    <aside className="sidebar holo-glass holo-scanlines">
      <div className="sidebar-header">
        <Text variant="h6" color="primary">
          TOP CONCEPTS
        </Text>
        <Badge colorScheme="info" size="sm">
          {topNodes.length}/{nodes.length}
        </Badge>
      </div>

      <div className="sidebar-content">
        {topNodes.map((node) => (
          <Card
            key={node.id}
            variant="default"
            padding="sm"
            interactive
            onClick={() => onSelectNode(node)}
            className="sidebar-node-card"
          >
            <div className="sidebar-node-header">
              <Text variant="body2" weight="medium" className="sidebar-node-title">
                {node.content.substring(0, 40)}
                {node.content.length > 40 ? '...' : ''}
              </Text>
              <Badge
                colorScheme={node.confidence > 0.8 ? 'success' : 'warning'}
                size="sm"
              >
                {Math.round(node.confidence * 100)}%
              </Badge>
            </div>
            <div className="sidebar-node-meta">
              <Text variant="caption" color="secondary">
                {node.edgeCount} connections
              </Text>
            </div>
          </Card>
        ))}
      </div>
    </aside>
  );
}
