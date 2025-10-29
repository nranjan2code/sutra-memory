/**
 * Header Component
 * Top navigation bar with holographic HUD styling
 */

import { Button, Text, Badge } from '@sutra/ui-framework';
import './Header.css';

interface HeaderProps {
  onToggleSidebar: () => void;
  nodeCount: number;
  edgeCount: number;
}

export default function Header({ onToggleSidebar, nodeCount, edgeCount }: HeaderProps) {
  return (
    <header className="header holo-glass">
      <div className="header-left">
        <Button variant="ghost" onClick={onToggleSidebar} icon="☰" aria-label="Toggle sidebar">
          
        </Button>
        <Text variant="h6" weight="bold" className="header-title">
          SUTRA.EXPLORER
        </Text>
      </div>

      <div className="header-center">
        <Badge colorScheme="info" size="sm">
          {nodeCount} nodes
        </Badge>
        <Badge colorScheme="info" size="sm">
          {edgeCount} edges
        </Badge>
      </div>

      <div className="header-right">
        <Button variant="ghost" icon="?" aria-label="Help">
          
        </Button>
        <Button variant="ghost" icon="⚙" aria-label="Settings">
          
        </Button>
      </div>
    </header>
  );
}
