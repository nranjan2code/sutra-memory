/**
 * Inspector Component
 * Right panel showing detailed node information
 */

import { Card, Text, Badge, Button } from '@sutra/ui-framework';
import type { Node } from '@types/graph';
import './Inspector.css';

interface InspectorProps {
  node: Node;
  onClose: () => void;
}

export default function Inspector({ node, onClose }: InspectorProps) {
  return (
    <aside className="inspector holo-glass holo-scanlines">
      <div className="inspector-header">
        <Text variant="h6" color="primary">
          NODE DETAILS
        </Text>
        <Button variant="ghost" icon="✕" onClick={onClose} aria-label="Close" />
      </div>

      <div className="inspector-content">
        <Card variant="outlined" padding="md" className="inspector-section">
          <Text variant="overline" color="secondary">
            ID
          </Text>
          <Text variant="body2" weight="medium" className="mono-text">
            {node.id.substring(0, 16)}...
          </Text>
        </Card>

        <Card variant="outlined" padding="md" className="inspector-section">
          <Text variant="overline" color="secondary">
            CONTENT
          </Text>
          <Text variant="body1">{node.content}</Text>
        </Card>

        <Card variant="outlined" padding="md" className="inspector-section">
          <Text variant="overline" color="secondary">
            METRICS
          </Text>
          <div className="inspector-metrics">
            <div className="metric-item">
              <Text variant="caption" color="secondary">
                Confidence
              </Text>
              <Badge
                colorScheme={node.confidence > 0.8 ? 'success' : 'warning'}
                size="md"
              >
                {Math.round(node.confidence * 100)}%
              </Badge>
            </div>
            <div className="metric-item">
              <Text variant="caption" color="secondary">
                Strength
              </Text>
              <Text variant="body2">{node.strength.toFixed(2)}</Text>
            </div>
            <div className="metric-item">
              <Text variant="caption" color="secondary">
                Connections
              </Text>
              <Badge colorScheme="info" size="md">
                {node.edgeCount}
              </Badge>
            </div>
            <div className="metric-item">
              <Text variant="caption" color="secondary">
                Access Count
              </Text>
              <Text variant="body2">{node.accessCount}</Text>
            </div>
          </div>
        </Card>

        <Card variant="outlined" padding="md" className="inspector-section">
          <Text variant="overline" color="secondary">
            METADATA
          </Text>
          <Text variant="caption" color="tertiary">
            Created: {new Date(node.createdAt).toLocaleString()}
          </Text>
          {node.metadata && Object.keys(node.metadata).length > 0 && (
            <div className="metadata-list">
              {Object.entries(node.metadata).map(([key, value]) => (
                <div key={key} className="metadata-item">
                  <Text variant="caption" color="secondary">
                    {key}:
                  </Text>
                  <Text variant="caption">{String(value)}</Text>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <div className="inspector-actions">
        <Button variant="primary" fullWidth>
          Expand Neighborhood
        </Button>
        <Button variant="secondary" fullWidth>
          Find Path
        </Button>
        <Button variant="ghost" fullWidth>
          Copy ID
        </Button>
      </div>
    </aside>
  );
}
