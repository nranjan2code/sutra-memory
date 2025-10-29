/**
 * Graph3D Component Stories
 * Interactive documentation and showcase for 3D force-directed graph visualization
 */

import type { Meta, StoryObj } from '@storybook/react';
import { Graph3D, type Graph3DNode, type Graph3DEdge } from '../visualization/Graph3D';
import React from 'react';

// Sample data for stories
const smallGraph3DNodes: Graph3DNode[] = [
  { id: 'ai', content: 'Artificial Intelligence', confidence: 0.95, strength: 0.9, edgeCount: 4, accessCount: 25 },
  { id: 'ml', content: 'Machine Learning', confidence: 0.90, strength: 0.85, edgeCount: 3, accessCount: 20 },
  { id: 'dl', content: 'Deep Learning', confidence: 0.85, strength: 0.80, edgeCount: 2, accessCount: 15 },
  { id: 'nlp', content: 'Natural Language Processing', confidence: 0.80, strength: 0.75, edgeCount: 2, accessCount: 12 },
  { id: 'cv', content: 'Computer Vision', confidence: 0.75, strength: 0.70, edgeCount: 2, accessCount: 10 },
];

const smallGraph3DEdges: Graph3DEdge[] = [
  { source: 'ai', target: 'ml', strength: 0.9, type: 'includes' },
  { source: 'ml', target: 'dl', strength: 0.85, type: 'includes' },
  { source: 'ml', target: 'nlp', strength: 0.75, type: 'enables' },
  { source: 'ml', target: 'cv', strength: 0.70, type: 'enables' },
  { source: 'ai', target: 'nlp', strength: 0.60, type: 'related' },
];

const mediumGraph3DNodes: Graph3DNode[] = [
  ...smallGraph3DNodes,
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

const mediumGraph3DEdges: Graph3DEdge[] = [
  ...smallGraph3DEdges,
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

// Generate large graph for performance testing
const generateLargeGraph3D = (nodeCount: number): { nodes: Graph3DNode[]; edges: Graph3DEdge[] } => {
  const nodes: Graph3DNode[] = [];
  const edges: Graph3DEdge[] = [];

  for (let i = 0; i < nodeCount; i++) {
    nodes.push({
      id: `node${i}`,
      content: `Concept ${i}`,
      confidence: 0.5 + Math.random() * 0.5,
      strength: Math.random(),
      edgeCount: Math.floor(Math.random() * 5),
      accessCount: Math.floor(Math.random() * 20),
    });
  }

  // Create random edges
  for (let i = 0; i < nodeCount * 2; i++) {
    const source = nodes[Math.floor(Math.random() * nodes.length)];
    const target = nodes[Math.floor(Math.random() * nodes.length)];
    if (source !== target) {
      edges.push({
        source: source.id,
        target: target.id,
        strength: 0.3 + Math.random() * 0.7,
      });
    }
  }

  return { nodes, edges };
};

const meta: Meta<typeof Graph3D> = {
  title: 'Visualization/Graph3D',
  component: Graph3D,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component: `
# Graph3D

Production-grade 3D force-directed graph visualization using Three.js and WebGL.

## Features
- **3D Force Simulation**: Realistic physics with D3.js forces
- **WebGL Rendering**: Hardware-accelerated graphics for smooth performance
- **Orbital Controls**: Intuitive camera manipulation (rotate, zoom, pan)
- **Raycasting Interactions**: Precise node selection and hover detection
- **Performance Optimized**: LOD, instancing, frustum culling for 100-10,000 nodes
- **Theme Integration**: Adapts materials and lighting to theme
- **VR/AR Ready**: Foundation for WebXR experiences

## Use Cases
- Large knowledge graph exploration (100-10,000 nodes)
- Immersive data visualization
- Complex relationship discovery
- 3D network analysis
- VR/AR knowledge navigation
        `,
      },
    },
  },
  argTypes: {
    nodes: {
      description: '3D graph nodes with position and metadata',
    },
    edges: {
      description: '3D graph edges connecting nodes',
    },
    selectedNodeId: {
      control: 'text',
      description: 'ID of selected node',
    },
    width: {
      control: { type: 'range', min: 400, max: 1920, step: 50 },
      description: 'Container width',
    },
    height: {
      control: { type: 'range', min: 300, max: 1080, step: 50 },
      description: 'Container height',
    },
    enableControls: {
      control: 'boolean',
      description: 'Enable orbital controls',
    },
    autoRotate: {
      control: 'boolean',
      description: 'Auto-rotate camera',
    },
    autoRotateSpeed: {
      control: { type: 'range', min: 0.5, max: 10, step: 0.5 },
      description: 'Auto-rotation speed',
    },
    showLabels: {
      control: 'boolean',
      description: 'Show node labels (impacts performance)',
    },
    minNodeRadius: {
      control: { type: 'range', min: 0.2, max: 2, step: 0.1 },
      description: 'Minimum node size',
    },
    maxNodeRadius: {
      control: { type: 'range', min: 2, max: 10, step: 0.5 },
      description: 'Maximum node size',
    },
    forceStrength: {
      control: { type: 'range', min: 0.5, max: 3, step: 0.1 },
      description: 'Force simulation strength',
    },
    linkDistance: {
      control: { type: 'range', min: 10, max: 100, step: 5 },
      description: 'Target link distance',
    },
    cameraDistance: {
      control: { type: 'range', min: 200, max: 1000, step: 50 },
      description: 'Initial camera distance',
    },
    fov: {
      control: { type: 'range', min: 45, max: 120, step: 5 },
      description: 'Field of view',
    },
    enableFog: {
      control: 'boolean',
      description: 'Enable distance fog',
    },
    useInstancing: {
      control: 'boolean',
      description: 'Use instanced rendering (for large graphs)',
    },
    enableLOD: {
      control: 'boolean',
      description: 'Enable Level of Detail optimization',
    },
    onSelectNode: { action: 'node-selected' },
    onNodeHover: { action: 'node-hovered' },
  },
};

export default meta;
type Story = StoryObj<typeof Graph3D>;

// ============================================================================
// Basic Examples
// ============================================================================

export const Default: Story = {
  args: {
    nodes: smallGraph3DNodes,
    edges: smallGraph3DEdges,
    width: 1000,
    height: 700,
  },
};

export const SmallGraph: Story = {
  args: {
    nodes: smallGraph3DNodes,
    edges: smallGraph3DEdges,
    width: 1000,
    height: 700,
  },
  parameters: {
    docs: {
      description: {
        story: 'Small 3D graph with 5 nodes',
      },
    },
  },
};

export const MediumGraph: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1200,
    height: 800,
  },
  parameters: {
    docs: {
      description: {
        story: 'Medium 3D graph with 15 nodes',
      },
    },
  },
};

export const LargeGraph: Story = {
  args: {
    ...generateLargeGraph3D(100),
    width: 1400,
    height: 900,
    useInstancing: true,
    enableLOD: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Large 3D graph with 100 nodes - optimized with instancing and LOD',
      },
    },
  },
};

export const EmptyState: Story = {
  args: {
    nodes: [],
    edges: [],
    width: 1000,
    height: 700,
    emptyMessage: 'No 3D concepts to visualize',
  },
  parameters: {
    docs: {
      description: {
        story: 'Empty state display',
      },
    },
  },
};

// ============================================================================
// Camera & Controls
// ============================================================================

export const AutoRotating: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1000,
    height: 700,
    autoRotate: true,
    autoRotateSpeed: 2.0,
  },
  parameters: {
    docs: {
      description: {
        story: 'Automatically rotating camera for showcase mode',
      },
    },
  },
};

export const FastAutoRotation: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1000,
    height: 700,
    autoRotate: true,
    autoRotateSpeed: 8.0,
  },
  parameters: {
    docs: {
      description: {
        story: 'Fast rotation for dramatic effect',
      },
    },
  },
};

export const ControlsDisabled: Story = {
  args: {
    nodes: smallGraph3DNodes,
    edges: smallGraph3DEdges,
    width: 1000,
    height: 700,
    enableControls: false,
  },
  parameters: {
    docs: {
      description: {
        story: 'Static camera with no user controls',
      },
    },
  },
};

export const CloseCamera: Story = {
  args: {
    nodes: smallGraph3DNodes,
    edges: smallGraph3DEdges,
    width: 1000,
    height: 700,
    cameraDistance: 250,
  },
  parameters: {
    docs: {
      description: {
        story: 'Close-up view with camera closer to graph',
      },
    },
  },
};

export const WideAngle: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1000,
    height: 700,
    fov: 100,
  },
  parameters: {
    docs: {
      description: {
        story: 'Wide field of view for panoramic perspective',
      },
    },
  },
};

// ============================================================================
// Visual Effects
// ============================================================================

export const WithFog: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1000,
    height: 700,
    enableFog: true,
    cameraDistance: 600,
  },
  parameters: {
    docs: {
      description: {
        story: 'Atmospheric fog for depth perception',
      },
    },
  },
};

export const NoFog: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1000,
    height: 700,
    enableFog: false,
  },
  parameters: {
    docs: {
      description: {
        story: 'Clear visibility without fog effect',
      },
    },
  },
};

export const LargeNodes: Story = {
  args: {
    nodes: smallGraph3DNodes,
    edges: smallGraph3DEdges,
    width: 1000,
    height: 700,
    minNodeRadius: 1.5,
    maxNodeRadius: 6,
  },
  parameters: {
    docs: {
      description: {
        story: 'Larger nodes for better visibility',
      },
    },
  },
};

export const SmallNodes: Story = {
  args: {
    nodes: smallGraph3DNodes,
    edges: smallGraph3DEdges,
    width: 1000,
    height: 700,
    minNodeRadius: 0.3,
    maxNodeRadius: 1.5,
  },
  parameters: {
    docs: {
      description: {
        story: 'Smaller nodes for minimalist look',
      },
    },
  },
};

// ============================================================================
// Force Configuration
// ============================================================================

export const TightLayout: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1000,
    height: 700,
    linkDistance: 20,
    forceStrength: 1.5,
  },
  parameters: {
    docs: {
      description: {
        story: 'Compact layout with tight clustering',
      },
    },
  },
};

export const SpacedLayout: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1200,
    height: 800,
    linkDistance: 60,
    forceStrength: 0.7,
  },
  parameters: {
    docs: {
      description: {
        story: 'Spacious layout with spread-out nodes',
      },
    },
  },
};

export const StrongForces: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1000,
    height: 700,
    forceStrength: 2.5,
  },
  parameters: {
    docs: {
      description: {
        story: 'Strong forces for dynamic movement',
      },
    },
  },
};

// ============================================================================
// Performance Modes
// ============================================================================

export const HighPerformance: Story = {
  args: {
    ...generateLargeGraph3D(200),
    width: 1400,
    height: 900,
    useInstancing: true,
    enableLOD: true,
    showLabels: false,
  },
  parameters: {
    docs: {
      description: {
        story: 'Optimized for 200+ nodes with all performance features enabled',
      },
    },
  },
};

export const QualityMode: Story = {
  args: {
    nodes: smallGraph3DNodes,
    edges: smallGraph3DEdges,
    width: 1000,
    height: 700,
    useInstancing: false,
    enableLOD: false,
    showLabels: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Maximum quality for small graphs (no optimizations)',
      },
    },
  },
};

// ============================================================================
// Interaction Scenarios
// ============================================================================

export const WithSelection: Story = {
  args: {
    nodes: smallGraph3DNodes,
    edges: smallGraph3DEdges,
    width: 1000,
    height: 700,
    selectedNodeId: 'ml',
  },
  parameters: {
    docs: {
      description: {
        story: 'Graph with pre-selected node highlighted',
      },
    },
  },
};

export const InteractiveExploration: Story = {
  render: (args) => {
    const [selectedId, setSelectedId] = React.useState<string | null>(null);
    const [hoveredNode, setHoveredNode] = React.useState<Graph3DNode | null>(null);

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
          <div>Confidence: {hoveredNode ? `${(hoveredNode.confidence * 100).toFixed(0)}%` : 'N/A'}</div>
        </div>
        <Graph3D
          {...args}
          selectedNodeId={selectedId}
          onSelectNode={(node) => setSelectedId(node.id)}
          onNodeHover={(node) => setHoveredNode(node)}
        />
      </div>
    );
  },
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1000,
    height: 700,
  },
  parameters: {
    docs: {
      description: {
        story: 'Full interactive example with selection and hover tracking',
      },
    },
  },
};

// ============================================================================
// Responsive Layouts
// ============================================================================

export const FullScreen: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 1920,
    height: 1080,
    autoRotate: true,
    autoRotateSpeed: 1.5,
  },
  parameters: {
    docs: {
      description: {
        story: 'Full screen 3D visualization (1920x1080)',
      },
    },
  },
};

export const SquareViewport: Story = {
  args: {
    nodes: smallGraph3DNodes,
    edges: smallGraph3DEdges,
    width: 800,
    height: 800,
  },
  parameters: {
    docs: {
      description: {
        story: 'Square viewport for balanced composition',
      },
    },
  },
};

export const UltraWide: Story = {
  args: {
    nodes: mediumGraph3DNodes,
    edges: mediumGraph3DEdges,
    width: 2560,
    height: 1080,
    fov: 90,
  },
  parameters: {
    docs: {
      description: {
        story: 'Ultra-wide display (21:9 aspect ratio)',
      },
    },
  },
};
