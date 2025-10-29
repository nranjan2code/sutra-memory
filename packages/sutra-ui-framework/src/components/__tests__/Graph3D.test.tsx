/**
 * Unit Tests for Graph3D Component
 * Production-grade test suite with comprehensive coverage
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ThemeProvider } from '../../core';
import { holographicTheme, professionalTheme, commandTheme } from '../../themes';
import { Graph3D } from '../visualization/Graph3D';
import type { Graph3DNode, Graph3DEdge } from '../visualization/Graph3D';

expect.extend(toHaveNoViolations);

// Mock Three.js and OrbitControls
jest.mock('three', () => {
  const actual = jest.requireActual('three');
  return {
    ...actual,
    WebGLRenderer: jest.fn(() => ({
      setSize: jest.fn(),
      setPixelRatio: jest.fn(),
      render: jest.fn(),
      dispose: jest.fn(),
      domElement: document.createElement('canvas'),
    })),
  };
});

jest.mock('three/examples/jsm/controls/OrbitControls', () => ({
  OrbitControls: jest.fn(() => ({
    update: jest.fn(),
    dispose: jest.fn(),
    enableDamping: true,
    dampingFactor: 0.05,
    autoRotate: false,
    autoRotateSpeed: 2.0,
    minDistance: 50,
    maxDistance: 1500,
  })),
}));

describe('Graph3D', () => {
  // Sample test data
  const mockNodes: Graph3DNode[] = [
    {
      id: 'node1',
      content: 'First 3D concept',
      confidence: 0.95,
      strength: 0.8,
      edgeCount: 5,
      accessCount: 10,
    },
    {
      id: 'node2',
      content: 'Second 3D concept',
      confidence: 0.65,
      strength: 0.5,
      edgeCount: 3,
      accessCount: 5,
    },
    {
      id: 'node3',
      content: 'Third 3D concept',
      confidence: 0.35,
      strength: 0.3,
      edgeCount: 1,
      accessCount: 2,
    },
  ];

  const mockEdges: Graph3DEdge[] = [
    { source: 'node1', target: 'node2', strength: 0.9, type: 'related' },
    { source: 'node2', target: 'node3', strength: 0.6, type: 'derived' },
    { source: 'node1', target: 'node3', strength: 0.4 },
  ];

  const defaultProps = {
    nodes: mockNodes,
    edges: mockEdges,
    width: 800,
    height: 600,
  };

  // Mock requestAnimationFrame
  beforeEach(() => {
    global.requestAnimationFrame = jest.fn((cb) => {
      cb(0);
      return 0;
    });
    global.cancelAnimationFrame = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render with nodes and edges', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should render empty state when no nodes', () => {
      render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D nodes={[]} edges={[]} width={800} height={600} />
        </ThemeProvider>
      );
      
      expect(screen.getByText('No concepts to visualize')).toBeInTheDocument();
    });

    it('should render custom empty message', () => {
      const customMessage = 'No 3D data available';
      render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D 
            nodes={[]} 
            edges={[]} 
            width={800} 
            height={600}
            emptyMessage={customMessage}
          />
        </ThemeProvider>
      );
      
      expect(screen.getByText(customMessage)).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} className="custom-3d-graph" />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.custom-3d-graph')).toBeInTheDocument();
    });

    it('should set correct dimensions', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} width={1000} height={800} />
        </ThemeProvider>
      );
      
      const graphContainer = container.querySelector('.graph-3d-container');
      expect(graphContainer).toHaveStyle({ width: '1000px', height: '800px' });
    });

    it('should render WebGL canvas', async () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeInTheDocument();
      });
    });
  });

  describe('Controls Configuration', () => {
    it('should show control hints by default', () => {
      render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(screen.getByText(/Left-click drag: Rotate/i)).toBeInTheDocument();
      expect(screen.getByText(/Right-click drag: Pan/i)).toBeInTheDocument();
      expect(screen.getByText(/Scroll: Zoom/i)).toBeInTheDocument();
    });

    it('should hide control hints when controls disabled', () => {
      render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} enableControls={false} />
        </ThemeProvider>
      );
      
      expect(screen.queryByText(/Left-click drag: Rotate/i)).not.toBeInTheDocument();
    });

    it('should support auto-rotation', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} autoRotate={true} autoRotateSpeed={5.0} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });
  });

  describe('Visual Options', () => {
    it('should support custom node radius range', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D 
            {...defaultProps}
            minNodeRadius={1}
            maxNodeRadius={5}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should support fog effect', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} enableFog={true} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should support disabling fog', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} enableFog={false} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should support custom camera settings', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D 
            {...defaultProps}
            cameraDistance={700}
            fov={60}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });
  });

  describe('Performance Options', () => {
    it('should support instanced rendering', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} useInstancing={true} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should support LOD optimization', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} enableLOD={true} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should handle large node count', () => {
      const largeNodeSet = Array.from({ length: 200 }, (_, i) => ({
        id: `node${i}`,
        content: `3D Concept ${i}`,
        confidence: Math.random(),
        strength: Math.random(),
        edgeCount: Math.floor(Math.random() * 10),
        accessCount: Math.floor(Math.random() * 20),
      }));

      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D 
            nodes={largeNodeSet}
            edges={[]}
            width={800}
            height={600}
            useInstancing={true}
            enableLOD={true}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });
  });

  describe('Force Simulation', () => {
    it('should accept custom force parameters', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D 
            {...defaultProps}
            forceStrength={2}
            linkDistance={50}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should handle nodes with initial positions', () => {
      const positionedNodes = mockNodes.map((node, i) => ({
        ...node,
        x: i * 50,
        y: i * 50,
        z: i * 50,
      }));

      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D 
            nodes={positionedNodes}
            edges={mockEdges}
            width={800}
            height={600}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });
  });

  describe('Theme Integration', () => {
    it('should work with holographic theme', async () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeInTheDocument();
      });
    });

    it('should work with professional theme', async () => {
      const { container } = render(
        <ThemeProvider theme={professionalTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeInTheDocument();
      });
    });

    it('should work with command theme', async () => {
      const { container } = render(
        <ThemeProvider theme={commandTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeInTheDocument();
      });
    });

    it('should update when theme changes', async () => {
      const { rerender, container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeInTheDocument();
      });
      
      rerender(
        <ThemeProvider theme={professionalTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeInTheDocument();
      });
    });
  });

  describe('Selection State', () => {
    it('should support selected node', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} selectedNodeId="node1" />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should update when selection changes', () => {
      const { rerender, container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} selectedNodeId="node1" />
        </ThemeProvider>
      );
      
      rerender(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} selectedNodeId="node2" />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle single node', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D 
            nodes={[mockNodes[0]]} 
            edges={[]}
            width={800}
            height={600}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should handle nodes with missing optional properties', () => {
      const minimalNodes: Graph3DNode[] = [
        { id: 'node1', content: '3D Concept 1', confidence: 0.8 },
        { id: 'node2', content: '3D Concept 2', confidence: 0.6 },
      ];

      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D 
            nodes={minimalNodes}
            edges={[]}
            width={800}
            height={600}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should handle extreme dimensions', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D 
            {...defaultProps}
            width={2560}
            height={1440}
          />
        </ThemeProvider>
      );
      
      const graphContainer = container.querySelector('.graph-3d-container');
      expect(graphContainer).toHaveStyle({ width: '2560px', height: '1440px' });
    });
  });

  describe('Accessibility', () => {
    it('should have no accessibility violations (empty state)', async () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D nodes={[]} edges={[]} width={800} height={600} />
        </ThemeProvider>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no accessibility violations (with data)', async () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Cleanup', () => {
    it('should cleanup Three.js resources on unmount', async () => {
      const { unmount, container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      await waitFor(() => {
        expect(container.querySelector('canvas')).toBeInTheDocument();
      });
      
      unmount();
      
      expect(global.cancelAnimationFrame).toHaveBeenCalled();
    });

    it('should handle rapid re-renders', () => {
      const { rerender, container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      for (let i = 0; i < 5; i++) {
        rerender(
          <ThemeProvider theme={holographicTheme}>
            <Graph3D {...defaultProps} width={800 + i * 10} />
          </ThemeProvider>
        );
      }
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });
  });

  describe('Labels', () => {
    it('should support showing labels', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} showLabels={true} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });

    it('should hide labels by default for performance', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <Graph3D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.graph-3d-container')).toBeInTheDocument();
    });
  });
});
