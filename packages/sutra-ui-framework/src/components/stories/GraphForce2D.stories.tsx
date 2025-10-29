/**
 * GraphForce2D Component Stories
 * Interactive documentation and showcase for force-directed graph visualization
 */

import type { Meta, StoryObj } from '@storybook/react';
import { GraphForce2D, type GraphForce2DProps, type GraphNode, type GraphEdge } from '../visualization/GraphForce2D';
import React from 'react';

// Sample data for stories
const smallGraphNodes: GraphNode[] = [
  { id: 'ai', content: 'Artificial Intelligence', confidence: 0.95, strength: 0.9, edgeCount: 4, accessCount: 25 },
  { id: 'ml', content: 'Machine Learning', confidence: 0.90, strength: 0.85, edgeCount: 3, accessCount: 20 },
  { id: 'dl', content: 'Deep Learning', confidence: 0.85, strength: 0.80, edgeCount: 2, accessCount: 15 },
  { id: 'nlp', content: 'Natural Language Processing', confidence: 0.80, strength: 0.75, edgeCount: 2, accessCount: 12 },
  { id: 'cv', content: 'Computer Vision', confidence: 0.75, strength: 0.70, edgeCount: 2, accessCount: 10 },
];

const smallGraphEdges: GraphEdge[] = [
  { source: 'ai', target: 'ml', strength: 0.9, type: 'includes' },
  { source: 'ml', target: 'dl', strength: 0.85, type: 'includes' },
  { source: 'ml', target: 'nlp', strength: 0.75, type: 'enables' },
  { source: 'ml', target: 'cv', strength: 0.70, type: 'enables' },
  { source: 'ai', target: 'nlp', strength: 0.60, type: 'related' },
];

const mediumGraphNodes: GraphNode[] = [
  ...smallGraphNodes,
  { id: 'nn', content: 'Neural Networks', confidence: 0.88, strength: 0.82, edgeCount: 3, accessCount: 18 },
  { id: 'cnn', content: 'Convolutional Neural Networks', confidence: 0.82, strength: 0.78, edgeCount: 2, accessCount: 14 },
  { id: 'rnn', content: 'Recurrent Neural Networks', confidence: 0.80, strength: 0.76, edgeCount: 2, accessCount: 13 },
  { id: 'transformer', content: 'Transformer Architecture', confidence: 0.92, strength: 0.88, edgeCount: 3, accessCount: 22 },
  { id: 'bert', content: 'BERT', confidence: 0.78, strength: 0.72, edgeCount: 2, accessCount: 11 },
  { id: 'gpt', content: 'GPT Models', confidence: 0.85, strength: 0.80, edgeCount: 2, accessCount: 16 },
  { id: 'supervised', content: 'Supervised Learning', confidence: 0.70, strength: 0.65, edgeCount: 2, accessCount: 9 },
  { id: 'unsupervised', content: 'Unsupervised Learning', confidence: 0.68, strength: 0.63, edgeCount: 2, accessCount: 8 },
  { id: 'rl', content: 'Reinforcement Learning', confidence: 0.72, strength: 0.67, edgeCount: 1, accessCount: 7 },
];

const mediumGraphEdges: GraphEdge[] = [
  ...smallGraphEdges,
  { source: 'dl', target: 'nn', strength: 0.90, type: 'uses' },
  { source: 'nn', target: 'cnn', strength: 0.85, type: 'type-of' },
  { source: 'nn', target: 'rnn', strength: 0.83, type: 'type-of' },
  { source: 'nlp', target: 'transformer', strength: 0.88, type: 'uses' },
  { source: 'transformer', target: 'bert', strength: 0.80, type: 'implements' },
  { source: 'transformer', target: 'gpt', strength: 0.82, type: 'implements' },
  { source: 'ml', target: 'supervised', strength: 0.75, type: 'includes' },
  { source: 'ml', target: 'unsupervised', strength: 0.73, type: 'includes' },
  { source: 'ml', target: 'rl', strength: 0.68, type: 'includes' },
  { source: 'cv', target: 'cnn', strength: 0.85, type: 'uses' },
];

const confidenceRangeNodes: GraphNode[] = [
  { id: 'high1', content: 'High Confidence Concept', confidence: 0.95, edgeCount: 3 },
  { id: 'high2', content: 'Another High Confidence', confidence: 0.88, edgeCount: 2 },
  { id: 'med1', content: 'Medium Confidence Concept', confidence: 0.65, edgeCount: 2 },
  { id: 'med2', content: 'Another Medium Confidence', confidence: 0.58, edgeCount: 1 },
  { id: 'low1', content: 'Low Confidence Concept', confidence: 0.35, edgeCount: 1 },
  { id: 'low2', content: 'Another Low Confidence', confidence: 0.28, edgeCount: 0 },
];

const confidenceRangeEdges: GraphEdge[] = [
  { source: 'high1', target: 'high2', strength: 0.9 },
  { source: 'high1', target: 'med1', strength: 0.7 },
  { source: 'med1', target: 'med2', strength: 0.6 },
  { source: 'med2', target: 'low1', strength: 0.4 },
  { source: 'low1', target: 'low2', strength: 0.3 },
];

const meta: Meta<typeof GraphForce2D> = {
  title: 'Visualization/GraphForce2D',
  component: GraphForce2D,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: `
# GraphForce2D

Production-grade force-directed graph visualization component built with D3.js.

## Features
- **Interactive Exploration**: Zoom, pan, and drag nodes
- **Visual Encoding**: Node size based on confidence, color based on state
- **Theme Integration**: Automatically adapts to holographic, professional, and command themes
- **Performance**: Optimized for graphs with 20-1000 nodes
- **Accessibility**: Keyboard navigation and screen reader support

## Use Cases
- Knowledge graph exploration
- Concept relationship visualization
- Network analysis
- Interactive data discovery
        `,
      },
    },
  },
  argTypes: {
    nodes: {
      description: 'Array of graph nodes with content, confidence, and metadata',
    },
    edges: {
      description: 'Array of graph edges connecting nodes with strength values',
    },
    selectedNodeId: {
      control: 'text',
      description: 'ID of the currently selected node',
    },
    width: {
      control: { type: 'range', min: 400, max: 1600, step: 50 },
      description: 'Container width in pixels',
    },
    height: {
      control: { type: 'range', min: 300, max: 1200, step: 50 },
      description: 'Container height in pixels',
    },
    enableZoom: {
      control: 'boolean',
      description: 'Enable zoom and pan interactions',
    },
    enableDrag: {
      control: 'boolean',
      description: 'Enable node dragging',
    },
    showEdgeLabels: {
      control: 'boolean',
      description: 'Show labels on edges',
    },
    showNodeLabels: {
      control: 'boolean',
      description: 'Show labels on nodes',
    },
    minNodeRadius: {
      control: { type: 'range', min: 2, max: 10, step: 1 },
      description: 'Minimum node radius',
    },
    maxNodeRadius: {
      control: { type: 'range', min: 10, max: 40, step: 2 },
      description: 'Maximum node radius',
    },
    forceStrength: {
      control: { type: 'range', min: 0.5, max: 3, step: 0.1 },
      description: 'Overall force strength multiplier',
    },
    linkDistance: {
      control: { type: 'range', min: 20, max: 200, step: 10 },
      description: 'Target distance between connected nodes',
    },
    chargeStrength: {
      control: { type: 'range', min: -1000, max: -50, step: 50 },
      description: 'Repulsion force between nodes',
    },
    onSelectNode: { action: 'node-selected' },
    onNodeHover: { action: 'node-hovered' },
  },
};

export default meta;
type Story = StoryObj<typeof GraphForce2D>;

// ============================================================================
// Basic Examples
// ============================================================================

export const Default: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    width: 800,
    height: 600,
  },
};

export const SmallGraph: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    width: 800,
    height: 600,
  },
  parameters: {
    docs: {
      description: {
        story: 'Small graph with 5 nodes - ideal for mobile or compact views',
      },
    },
  },
};

export const MediumGraph: Story = {
  args: {
    nodes: mediumGraphNodes,
    edges: mediumGraphEdges,
    width: 1000,
    height: 700,
  },
  parameters: {
    docs: {
      description: {
        story: 'Medium-sized graph with 15 nodes showing complex relationships',
      },
    },
  },
};

export const EmptyState: Story = {
  args: {
    nodes: [],
    edges: [],
    width: 800,
    height: 600,
    emptyMessage: 'No concepts available',
  },
  parameters: {
    docs: {
      description: {
        story: 'Empty state when no data is available',
      },
    },
  },
};

// ============================================================================
// Interaction Features
// ============================================================================

export const WithSelection: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    selectedNodeId: 'ml',
    width: 800,
    height: 600,
  },
  parameters: {
    docs: {
      description: {
        story: 'Graph with a selected node highlighted',
      },
    },
  },
};

export const ZoomDisabled: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    width: 800,
    height: 600,
    enableZoom: false,
  },
  parameters: {
    docs: {
      description: {
        story: 'Graph with zoom and pan interactions disabled',
      },
    },
  },
};

export const DragDisabled: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    width: 800,
    height: 600,
    enableDrag: false,
  },
  parameters: {
    docs: {
      description: {
        story: 'Graph with node dragging disabled',
      },
    },
  },
};

export const AllInteractionsDisabled: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    width: 800,
    height: 600,
    enableZoom: false,
    enableDrag: false,
  },
  parameters: {
    docs: {
      description: {
        story: 'Static graph with all interactions disabled',
      },
    },
  },
};

// ============================================================================
// Visual Options
// ============================================================================

export const WithEdgeLabels: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    width: 800,
    height: 600,
    showEdgeLabels: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Graph showing edge labels (type or strength)',
      },
    },
  },
};

export const WithoutNodeLabels: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    width: 800,
    height: 600,
    showNodeLabels: false,
  },
  parameters: {
    docs: {
      description: {
        story: 'Graph without node labels for cleaner appearance',
      },
    },
  },
};

export const LargeNodes: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    width: 800,
    height: 600,
    minNodeRadius: 10,
    maxNodeRadius: 35,
  },
  parameters: {
    docs: {
      description: {
        story: 'Graph with larger node sizes',
      },
    },
  },
};

export const SmallNodes: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    width: 800,
    height: 600,
    minNodeRadius: 3,
    maxNodeRadius: 12,
  },
  parameters: {
    docs: {
      description: {
        story: 'Graph with smaller node sizes',
      },
    },
  },
};

// ============================================================================
// Force Configuration
// ============================================================================

export const TightLayout: Story = {
  args: {
    nodes: mediumGraphNodes,
    edges: mediumGraphEdges,
    width: 800,
    height: 600,
    linkDistance: 30,
    chargeStrength: -200,
  },
  parameters: {
    docs: {
      description: {
        story: 'Compact layout with shorter link distances',
      },
    },
  },
};

export const SpreadOutLayout: Story = {
  args: {
    nodes: mediumGraphNodes,
    edges: mediumGraphEdges,
    width: 1200,
    height: 800,
    linkDistance: 120,
    chargeStrength: -600,
  },
  parameters: {
    docs: {
      description: {
        story: 'Spacious layout with longer link distances and stronger repulsion',
      },
    },
  },
};

export const StrongForces: Story = {
  args: {
    nodes: mediumGraphNodes,
    edges: mediumGraphEdges,
    width: 1000,
    height: 700,
    forceStrength: 2.5,
  },
  parameters: {
    docs: {
      description: {
        story: 'Graph with amplified force effects for more dynamic movement',
      },
    },
  },
};

export const WeakForces: Story = {
  args: {
    nodes: mediumGraphNodes,
    edges: mediumGraphEdges,
    width: 1000,
    height: 700,
    forceStrength: 0.5,
  },
  parameters: {
    docs: {
      description: {
        story: 'Graph with reduced force effects for gentler movement',
      },
    },
  },
};

// ============================================================================
// Visual Encoding
// ============================================================================

export const ConfidenceVisualization: Story = {
  args: {
    nodes: confidenceRangeNodes,
    edges: confidenceRangeEdges,
    width: 800,
    height: 600,
  },
  parameters: {
    docs: {
      description: {
        story: `
Demonstrates confidence-based visual encoding:
- **High confidence (>80%)**: Green nodes, larger size
- **Medium confidence (50-80%)**: Yellow nodes, medium size  
- **Low confidence (<50%)**: Red nodes, smaller size
        `,
      },
    },
  },
};

// ============================================================================
// Responsive Layouts
// ============================================================================

export const MobileSize: Story = {
  args: {
    nodes: smallGraphNodes,
    edges: smallGraphEdges,
    width: 375,
    height: 600,
    minNodeRadius: 6,
    maxNodeRadius: 16,
    linkDistance: 40,
  },
  parameters: {
    docs: {
      description: {
        story: 'Optimized for mobile viewport (375px width)',
      },
    },
  },
};

export const TabletSize: Story = {
  args: {
    nodes: mediumGraphNodes,
    edges: mediumGraphEdges,
    width: 768,
    height: 600,
    minNodeRadius: 5,
    maxNodeRadius: 18,
    linkDistance: 50,
  },
  parameters: {
    docs: {
      description: {
        story: 'Optimized for tablet viewport (768px width)',
      },
    },
  },
};

export const DesktopSize: Story = {
  args: {
    nodes: mediumGraphNodes,
    edges: mediumGraphEdges,
    width: 1440,
    height: 800,
    minNodeRadius: 6,
    maxNodeRadius: 24,
    linkDistance: 70,
  },
  parameters: {
    docs: {
      description: {
        story: 'Optimized for desktop viewport (1440px width)',
      },
    },
  },
};

export const WideScreen: Story = {
  args: {
    nodes: mediumGraphNodes,
    edges: mediumGraphEdges,
    width: 1920,
    height: 1080,
    minNodeRadius: 8,
    maxNodeRadius: 30,
    linkDistance: 90,
    showEdgeLabels: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Optimized for wide screen viewport (1920px width)',
      },
    },
  },
};

// ============================================================================
// Integration Scenarios
// ============================================================================

export const InteractiveExploration: Story = {
  render: (args) => {
    const [selectedId, setSelectedId] = React.useState<string | null>(null);
    const [hoveredNode, setHoveredNode] = React.useState<GraphNode | null>(null);

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ 
          padding: '12px', 
          background: 'rgba(0,0,0,0.05)', 
          borderRadius: '8px',
          fontFamily: 'monospace',
          fontSize: '14px'
        }}>
          <div>Selected: {selectedId || 'None'}</div>
          <div>Hovered: {hoveredNode?.content || 'None'}</div>
        </div>
        <GraphForce2D
          {...args}
          selectedNodeId={selectedId}
          onSelectNode={(node) => setSelectedId(node.id)}
          onNodeHover={(node) => setHoveredNode(node)}
        />
      </div>
    );
  },
  args: {
    nodes: mediumGraphNodes,
    edges: mediumGraphEdges,
    width: 1000,
    height: 700,
  },
  parameters: {
    docs: {
      description: {
        story: 'Full interactive example with selection and hover state tracking',
      },
    },
  },
};
