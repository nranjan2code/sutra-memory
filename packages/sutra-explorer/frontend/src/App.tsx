import { useState, useEffect } from 'react';
import { Text } from '@sutra/ui-framework';
import Header from '@components/layout/Header';
import Sidebar from '@components/layout/Sidebar';
import Inspector from '@components/layout/Inspector';
import GraphCanvas from '@components/graph/GraphCanvas';
import BottomSheet from '@components/layout/BottomSheet';
import { useDeviceDetection } from '@hooks/useDeviceDetection';
import { useGraphData } from '@hooks/useGraphData';
import type { Node as GraphNode } from '@types/graph';
import './App.css';

function App() {
  const { deviceType, isMobile } = useDeviceDetection();
  const { nodes, edges, loading, error } = useGraphData();
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);

  useEffect(() => {
    // Update sidebar visibility based on device type
    setSidebarOpen(!isMobile);
  }, [isMobile]);

  if (error) {
    return (
      <div className="error-container">
        <Text variant="h4" color="primary">
          Error Loading Graph
        </Text>
        <Text variant="body1" color="secondary">
          {error}
        </Text>
      </div>
    );
  }

  return (
    <div className="app-container">
      <Header
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        nodeCount={nodes.length}
        edgeCount={edges.length}
      />

      <div className="app-layout">
        {sidebarOpen && !isMobile && (
          <Sidebar nodes={nodes} onSelectNode={setSelectedNode} />
        )}

        <main className="app-main">
          <GraphCanvas
            nodes={nodes}
            edges={edges}
            selectedNode={selectedNode}
            onSelectNode={setSelectedNode}
            deviceType={deviceType}
            loading={loading}
          />
        </main>

        {selectedNode && !isMobile && (
          <Inspector node={selectedNode} onClose={() => setSelectedNode(null)} />
        )}
      </div>

      {isMobile && (
        <BottomSheet
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
          isOpen={selectedNode !== null}
        />
      )}
    </div>
  );
}

export default App;
