/**
 * BottomSheet Component
 * Mobile drawer for node details
 */

import { Card, Text, Badge, Button } from '@sutra/ui-framework';
import type { Node } from '@types/graph';
import './BottomSheet.css';

interface BottomSheetProps {
  node: Node | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function BottomSheet({ node, isOpen, onClose }: BottomSheetProps) {
  if (!node || !isOpen) return null;

  return (
    <>
      <div className="bottom-sheet-backdrop" onClick={onClose} />
      <div className="bottom-sheet holo-glass">
        <div className="bottom-sheet-handle" />
        
        <div className="bottom-sheet-content">
          <Card variant="default" padding="md">
            <div className="bottom-sheet-header">
              <Text variant="h6" weight="bold">
                {node.content.substring(0, 60)}
                {node.content.length > 60 ? '...' : ''}
              </Text>
              <Button variant="ghost" icon="✕" onClick={onClose} aria-label="Close" />
            </div>

            <div className="bottom-sheet-metrics">
              <div className="metric">
                <Text variant="caption" color="secondary">
                  Confidence
                </Text>
                <Badge
                  colorScheme={node.confidence > 0.8 ? 'success' : 'warning'}
                  size="sm"
                >
                  {Math.round(node.confidence * 100)}%
                </Badge>
              </div>
              <div className="metric">
                <Text variant="caption" color="secondary">
                  Edges
                </Text>
                <Badge colorScheme="info" size="sm">
                  {node.edgeCount}
                </Badge>
              </div>
            </div>

            <div className="bottom-sheet-actions">
              <Button variant="primary" size="sm" fullWidth>
                Expand
              </Button>
              <Button variant="secondary" size="sm" fullWidth>
                Path
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </>
  );
}
