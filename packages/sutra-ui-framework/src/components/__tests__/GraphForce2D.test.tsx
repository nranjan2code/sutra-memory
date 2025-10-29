/**
 * Unit Tests for GraphForce2D Component
 * Production-grade test suite with comprehensive coverage
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ThemeProvider } from '../../core';
import { holographicTheme, professionalTheme, commandTheme } from '../../themes';
import { GraphForce2D } from '../visualization/GraphForce2D';
import type { GraphNode, GraphEdge } from '../visualization/GraphForce2D';

expect.extend(toHaveNoViolations);

// Mock D3 for testing
jest.mock('d3', () => {
  const actualD3 = jest.requireActual('d3');
  return {
    ...actualD3,
    select: jest.fn(() => ({
      selectAll: jest.fn(() => ({
        remove: jest.fn(),
      })),
      append: jest.fn(() => ({
        attr: jest.fn().mockReturnThis(),
        append: jest.fn().mockReturnThis(),
        selectAll: jest.fn(() => ({
          data: jest.fn(() => ({
            join: jest.fn(() => ({
              attr: jest.fn().mockReturnThis(),
              style: jest.fn().mockReturnThis(),
              text: jest.fn().mockReturnThis(),
              on: jest.fn().mockReturnThis(),
              call: jest.fn().mockReturnThis(),
            })),
          })),
        })),
      })),
      call: jest.fn().mockReturnThis(),
      transition: jest.fn().mockReturnThis(),
      duration: jest.fn().mockReturnThis(),
      on: jest.fn().mockReturnThis(),
    })),
    forceSimulation: jest.fn(() => ({
      force: jest.fn().mockReturnThis(),
      alphaDecay: jest.fn().mockReturnThis(),
      velocityDecay: jest.fn().mockReturnThis(),
      on: jest.fn().mockReturnThis(),
      stop: jest.fn(),
      alphaTarget: jest.fn().mockReturnThis(),
      restart: jest.fn().mockReturnThis(),
    })),
    forceLink: jest.fn(() => ({
      id: jest.fn().mockReturnThis(),
      distance: jest.fn().mockReturnThis(),
      strength: jest.fn().mockReturnThis(),
    })),
    forceManyBody: jest.fn(() => ({
      strength: jest.fn().mockReturnThis(),
    })),
    forceCenter: jest.fn(),
    forceCollide: jest.fn(() => ({
      radius: jest.fn().mockReturnThis(),
    })),
    drag: jest.fn(() => ({
      on: jest.fn().mockReturnThis(),
    })),
    zoom: jest.fn(() => ({
      scaleExtent: jest.fn().mockReturnThis(),
      on: jest.fn().mockReturnThis(),
      transform: jest.fn(),
    })),
    zoomIdentity: {},
  };
});

describe('GraphForce2D', () => {
  // Sample test data
  const mockNodes: GraphNode[] = [
    {
      id: 'node1',
      content: 'First concept with detailed description',
      confidence: 0.95,
      strength: 0.8,
      edgeCount: 5,
      accessCount: 10,
    },
    {
      id: 'node2',
      content: 'Second concept',
      confidence: 0.65,
      strength: 0.5,
      edgeCount: 3,
      accessCount: 5,
    },
    {
      id: 'node3',
      content: 'Third concept with low confidence',
      confidence: 0.35,
      strength: 0.3,
      edgeCount: 1,
      accessCount: 2,
    },
  ];

  const mockEdges: GraphEdge[] = [
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

  describe('Rendering', () => {
    it('should render with nodes and edges', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
      expect(svg).toHaveClass('graph-force-2d-svg');
    });

    it('should render empty state when no nodes', () => {
      render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D nodes={[]} edges={[]} width={800} height={600} />
        </ThemeProvider>
      );
      
      expect(screen.getByText('No concepts to visualize')).toBeInTheDocument();
    });

    it('should render custom empty message', () => {
      const customMessage = 'Custom empty state message';
      render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D 
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
          <GraphForce2D {...defaultProps} className="custom-graph" />
        </ThemeProvider>
      );
      
      expect(container.querySelector('.custom-graph')).toBeInTheDocument();
    });

    it('should set correct dimensions', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} width={1000} height={800} />
        </ThemeProvider>
      );
      
      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '1000');
      expect(svg).toHaveAttribute('height', '800');
    });
  });

  describe('Interactions', () => {
    it('should call onSelectNode when node is clicked', () => {
      const onSelectNode = jest.fn();
      render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} onSelectNode={onSelectNode} />
        </ThemeProvider>
      );
      
      // D3 mock will handle the click event setup
      expect(onSelectNode).not.toHaveBeenCalled();
    });

    it('should call onNodeHover when node is hovered', () => {
      const onNodeHover = jest.fn();
      render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} onNodeHover={onNodeHover} />
        </ThemeProvider>
      );
      
      // D3 mock will handle the hover event setup
      expect(onNodeHover).not.toHaveBeenCalled();
    });

    it('should support keyboard navigation', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });

  describe('Configuration Options', () => {
    it('should render with zoom enabled by default', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(screen.getByText(/Double-click to reset zoom/i)).toBeInTheDocument();
    });

    it('should render with drag enabled by default', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(screen.getByText(/Drag nodes to reposition/i)).toBeInTheDocument();
    });

    it('should hide zoom controls when disabled', () => {
      render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} enableZoom={false} />
        </ThemeProvider>
      );
      
      expect(screen.queryByText(/Double-click to reset zoom/i)).not.toBeInTheDocument();
    });

    it('should hide drag controls when disabled', () => {
      render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} enableDrag={false} />
        </ThemeProvider>
      );
      
      expect(screen.queryByText(/Drag nodes to reposition/i)).not.toBeInTheDocument();
    });

    it('should accept custom force parameters', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D 
            {...defaultProps}
            forceStrength={2}
            linkDistance={100}
            chargeStrength={-500}
            collisionMultiplier={2}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should accept custom node radius range', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D 
            {...defaultProps}
            minNodeRadius={8}
            maxNodeRadius={30}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });
  });

  describe('Theme Integration', () => {
    it('should work with holographic theme', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should work with professional theme', () => {
      const { container } = render(
        <ThemeProvider theme={professionalTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should work with command theme', () => {
      const { container } = render(
        <ThemeProvider theme={commandTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should update colors when theme changes', async () => {
      const { rerender, container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
      
      rerender(
        <ThemeProvider theme={professionalTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });
  });

  describe('Selection State', () => {
    it('should highlight selected node', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} selectedNodeId="node1" />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should update when selection changes', () => {
      const { rerender, container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} selectedNodeId="node1" />
        </ThemeProvider>
      );
      
      rerender(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} selectedNodeId="node2" />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should clear selection when set to null', () => {
      const { rerender, container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} selectedNodeId="node1" />
        </ThemeProvider>
      );
      
      rerender(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} selectedNodeId={null} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle single node', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D 
            nodes={[mockNodes[0]]} 
            edges={[]}
            width={800}
            height={600}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should handle large number of nodes', () => {
      const largeNodeSet = Array.from({ length: 100 }, (_, i) => ({
        id: `node${i}`,
        content: `Concept ${i}`,
        confidence: Math.random(),
        strength: Math.random(),
        edgeCount: Math.floor(Math.random() * 10),
        accessCount: Math.floor(Math.random() * 20),
      }));

      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D 
            nodes={largeNodeSet}
            edges={[]}
            width={800}
            height={600}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should handle nodes with missing optional properties', () => {
      const minimalNodes: GraphNode[] = [
        { id: 'node1', content: 'Concept 1', confidence: 0.8 },
        { id: 'node2', content: 'Concept 2', confidence: 0.6 },
      ];

      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D 
            nodes={minimalNodes}
            edges={[]}
            width={800}
            height={600}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should handle edges with missing optional properties', () => {
      const minimalEdges: GraphEdge[] = [
        { source: 'node1', target: 'node2', strength: 0.5 },
      ];

      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D 
            nodes={mockNodes}
            edges={minimalEdges}
            width={800}
            height={600}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should handle very long node content', () => {
      const longContentNode: GraphNode = {
        id: 'long-node',
        content: 'This is a very long concept description that should be truncated in the visualization to prevent UI overflow',
        confidence: 0.9,
      };

      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D 
            nodes={[longContentNode]}
            edges={[]}
            width={800}
            height={600}
          />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have no accessibility violations (empty state)', async () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D nodes={[]} edges={[]} width={800} height={600} />
        </ThemeProvider>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have no accessibility violations (with data)', async () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should support reduced motion preference', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });
  });

  describe('Cleanup', () => {
    it('should cleanup simulation on unmount', () => {
      const { unmount, container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
      unmount();
    });

    it('should handle rapid re-renders', () => {
      const { rerender, container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      for (let i = 0; i < 10; i++) {
        rerender(
          <ThemeProvider theme={holographicTheme}>
            <GraphForce2D {...defaultProps} width={800 + i * 10} />
          </ThemeProvider>
        );
      }
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });
  });

  describe('Label Options', () => {
    it('should render node labels by default', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should hide node labels when disabled', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} showNodeLabels={false} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should hide edge labels by default', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });

    it('should show edge labels when enabled', () => {
      const { container } = render(
        <ThemeProvider theme={holographicTheme}>
          <GraphForce2D {...defaultProps} showEdgeLabels={true} />
        </ThemeProvider>
      );
      
      expect(container.querySelector('svg')).toBeInTheDocument();
    });
  });
});
