/**
 * GraphForce2D - Force-directed graph visualization component
 * 
 * Production-grade D3.js-based force-directed graph for visualizing knowledge graphs.
 * Supports interactive exploration with zoom, pan, drag, and selection.
 * 
 * Features:
 * - Force-directed layout with D3.js simulation
 * - Zoom and pan interactions
 * - Node dragging with fixed positioning
 * - Edge strength visualization
 * - Confidence-based node sizing
 * - Theme-aware styling
 * - Accessible keyboard navigation
 * 
 * Use cases:
 * - Desktop knowledge graph exploration (≥ 768px width)
 * - Medium to large graphs (20-1000 nodes)
 * - Interactive concept discovery
 * - Relationship visualization
 * 
 * @package @sutra/ui-framework
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { useTheme } from '../../core';
import './GraphForce2D.css';

// ============================================================================
// Types
// ============================================================================

export interface GraphNode {
  id: string;
  content: string;
  confidence: number;
  strength?: number;
  edgeCount?: number;
  accessCount?: number;
  metadata?: Record<string, any>;
  // D3 simulation properties (will be added by simulation)
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
  strength: number;
  type?: string;
  metadata?: Record<string, any>;
}

export interface GraphForce2DProps {
  /** Array of graph nodes */
  nodes: GraphNode[];
  /** Array of graph edges */
  edges: GraphEdge[];
  /** Currently selected node ID */
  selectedNodeId?: string | null;
  /** Container width in pixels */
  width: number;
  /** Container height in pixels */
  height: number;
  /** Callback when node is selected */
  onSelectNode?: (node: GraphNode) => void;
  /** Callback when node is hovered */
  onNodeHover?: (node: GraphNode | null) => void;
  /** Enable zoom and pan (default: true) */
  enableZoom?: boolean;
  /** Enable node dragging (default: true) */
  enableDrag?: boolean;
  /** Show edge labels (default: false) */
  showEdgeLabels?: boolean;
  /** Show node labels (default: true) */
  showNodeLabels?: boolean;
  /** Minimum node radius (default: 4) */
  minNodeRadius?: number;
  /** Maximum node radius (default: 20) */
  maxNodeRadius?: number;
  /** Force strength multiplier (default: 1) */
  forceStrength?: number;
  /** Link distance (default: 50) */
  linkDistance?: number;
  /** Charge force strength (default: -300) */
  chargeStrength?: number;
  /** Collision radius multiplier (default: 1.5) */
  collisionMultiplier?: number;
  /** Empty state message */
  emptyMessage?: string;
  /** CSS class name */
  className?: string;
}

interface SimulationNode extends d3.SimulationNodeDatum {
  id: string;
  content: string;
  confidence: number;
  strength?: number;
  edgeCount?: number;
  accessCount?: number;
  metadata?: Record<string, any>;
}

interface SimulationLink extends d3.SimulationLinkDatum<SimulationNode> {
  source: SimulationNode | string;
  target: SimulationNode | string;
  strength: number;
  type?: string;
  metadata?: Record<string, any>;
}

// ============================================================================
// Component
// ============================================================================

export const GraphForce2D: React.FC<GraphForce2DProps> = ({
  nodes,
  edges,
  selectedNodeId,
  width,
  height,
  onSelectNode,
  onNodeHover,
  enableZoom = true,
  enableDrag = true,
  showEdgeLabels = false,
  showNodeLabels = true,
  minNodeRadius = 4,
  maxNodeRadius = 20,
  forceStrength = 1,
  linkDistance = 50,
  chargeStrength = -300,
  collisionMultiplier = 1.5,
  emptyMessage = 'No concepts to visualize',
  className = '',
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const simulationRef = useRef<d3.Simulation<SimulationNode, SimulationLink> | null>(null);
  const { theme } = useTheme();
  
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Calculate node radius based on confidence and edge count
  const getNodeRadius = useCallback((node: GraphNode): number => {
    const baseRadius = minNodeRadius + (node.confidence * (maxNodeRadius - minNodeRadius));
    const edgeBonus = node.edgeCount ? Math.min(node.edgeCount * 0.5, 5) : 0;
    return Math.min(baseRadius + edgeBonus, maxNodeRadius);
  }, [minNodeRadius, maxNodeRadius]);

  // Get node color based on confidence
  const getNodeColor = useCallback((node: GraphNode): string => {
    if (selectedNodeId === node.id) {
      return theme.tokens.color.primary;
    }
    if (hoveredNodeId === node.id) {
      return theme.tokens.color.secondary;
    }
    
    // Color scale based on confidence
    if (node.confidence > 0.8) {
      return theme.tokens.color.success;
    } else if (node.confidence > 0.5) {
      return theme.tokens.color.warning;
    } else {
      return theme.tokens.color.error;
    }
  }, [selectedNodeId, hoveredNodeId, theme]);

  // Get edge color based on strength
  const getEdgeColor = useCallback((edge: GraphEdge): string => {
    const opacity = 0.2 + (edge.strength * 0.5);
    return theme.tokens.color.text.secondary + Math.round(opacity * 255).toString(16).padStart(2, '0');
  }, [theme]);

  // Initialize D3 force simulation
  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove(); // Clear previous render

    // Create container groups
    const g = svg.append('g').attr('class', 'graph-container');
    const linkGroup = g.append('g').attr('class', 'links');
    const nodeGroup = g.append('g').attr('class', 'nodes');
    const labelGroup = g.append('g').attr('class', 'labels');

    // Prepare data for D3
    const simulationNodes: SimulationNode[] = nodes.map(node => ({ ...node }));
    const simulationLinks: SimulationLink[] = edges.map(edge => ({ ...edge }));

    // Create force simulation
    const simulation = d3.forceSimulation<SimulationNode, SimulationLink>(simulationNodes)
      .force('link', d3.forceLink<SimulationNode, SimulationLink>(simulationLinks)
        .id(d => d.id)
        .distance(linkDistance)
        .strength(d => d.strength * forceStrength))
      .force('charge', d3.forceManyBody<SimulationNode>()
        .strength(chargeStrength * forceStrength))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide<SimulationNode>()
        .radius(d => getNodeRadius(d as GraphNode) * collisionMultiplier))
      .alphaDecay(0.02)
      .velocityDecay(0.4);

    simulationRef.current = simulation;

    // Draw edges
    const link = linkGroup
      .selectAll<SVGLineElement, SimulationLink>('line')
      .data(simulationLinks)
      .join('line')
      .attr('class', 'graph-edge')
      .attr('stroke', d => getEdgeColor(d as GraphEdge))
      .attr('stroke-width', d => 1 + d.strength * 2)
      .attr('stroke-opacity', d => 0.3 + d.strength * 0.4);

    // Draw edge labels (if enabled)
    let edgeLabels: d3.Selection<SVGTextElement, SimulationLink, SVGGElement, unknown> | null = null;
    if (showEdgeLabels) {
      edgeLabels = labelGroup
        .selectAll<SVGTextElement, SimulationLink>('text.edge-label')
        .data(simulationLinks)
        .join('text')
        .attr('class', 'graph-edge-label')
        .attr('text-anchor', 'middle')
        .attr('font-size', '10px')
        .attr('fill', theme.tokens.color.text.secondary)
        .text(d => d.type || `${Math.round(d.strength * 100)}%`);
    }

    // Draw nodes
    const node = nodeGroup
      .selectAll<SVGCircleElement, SimulationNode>('circle')
      .data(simulationNodes)
      .join('circle')
      .attr('class', 'graph-node')
      .attr('r', d => getNodeRadius(d as GraphNode))
      .attr('fill', d => getNodeColor(d as GraphNode))
      .attr('stroke', theme.tokens.color.background)
      .attr('stroke-width', 2)
      .attr('cursor', 'pointer')
      .style('transition', 'fill 0.2s ease, r 0.2s ease');

    // Draw node labels (if enabled)
    let nodeLabels: d3.Selection<SVGTextElement, SimulationNode, SVGGElement, unknown> | null = null;
    if (showNodeLabels) {
      nodeLabels = labelGroup
        .selectAll<SVGTextElement, SimulationNode>('text.node-label')
        .data(simulationNodes)
        .join('text')
        .attr('class', 'graph-node-label')
        .attr('text-anchor', 'middle')
        .attr('dy', d => getNodeRadius(d as GraphNode) + 12)
        .attr('font-size', '11px')
        .attr('fill', theme.tokens.color.text.primary)
        .attr('pointer-events', 'none')
        .text(d => {
          const maxLength = 20;
          return d.content.length > maxLength 
            ? d.content.substring(0, maxLength) + '...' 
            : d.content;
        });
    }

    // Node interactions
    node
      .on('click', (event, d) => {
        event.stopPropagation();
        onSelectNode?.(d as GraphNode);
      })
      .on('mouseenter', (_event, d) => {
        setHoveredNodeId(d.id);
        onNodeHover?.(d as GraphNode);
      })
      .on('mouseleave', () => {
        setHoveredNodeId(null);
        onNodeHover?.(null);
      });

    // Drag behavior
    if (enableDrag) {
      const drag = d3.drag<SVGCircleElement, SimulationNode>()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x;
          d.fy = d.y;
        })
        .on('drag', (event, d) => {
          d.fx = event.x;
          d.fy = event.y;
        })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          // Keep node fixed after drag
          d.fx = event.x;
          d.fy = event.y;
        });

      node.call(drag);
    }

    // Zoom behavior
    if (enableZoom) {
      const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.1, 10])
        .on('zoom', (event) => {
          g.attr('transform', event.transform);
        });

      svg.call(zoom);
      
      // Reset zoom on double-click
      svg.on('dblclick.zoom', () => {
        svg.transition()
          .duration(750)
          .call(zoom.transform as any, d3.zoomIdentity);
      });
    }

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => (d.source as SimulationNode).x || 0)
        .attr('y1', d => (d.source as SimulationNode).y || 0)
        .attr('x2', d => (d.target as SimulationNode).x || 0)
        .attr('y2', d => (d.target as SimulationNode).y || 0);

      if (edgeLabels) {
        edgeLabels
          .attr('x', d => ((d.source as SimulationNode).x! + (d.target as SimulationNode).x!) / 2)
          .attr('y', d => ((d.source as SimulationNode).y! + (d.target as SimulationNode).y!) / 2);
      }

      node
        .attr('cx', d => d.x || 0)
        .attr('cy', d => d.y || 0);

      if (nodeLabels) {
        nodeLabels
          .attr('x', d => d.x || 0)
          .attr('y', d => d.y || 0);
      }
    });

    // Cleanup
    return () => {
      simulation.stop();
      simulationRef.current = null;
    };
  }, [
    nodes,
    edges,
    width,
    height,
    theme,
    getNodeRadius,
    getNodeColor,
    getEdgeColor,
    linkDistance,
    chargeStrength,
    forceStrength,
    collisionMultiplier,
    enableZoom,
    enableDrag,
    showEdgeLabels,
    showNodeLabels,
    onSelectNode,
    onNodeHover,
  ]);

  // Update node colors when selection/hover changes
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll<SVGCircleElement, SimulationNode>('.graph-node')
      .attr('fill', d => getNodeColor(d as GraphNode));
  }, [selectedNodeId, hoveredNodeId, getNodeColor]);

  // Empty state
  if (nodes.length === 0) {
    return (
      <div 
        ref={containerRef}
        className={`graph-force-2d-empty ${className}`}
        style={{ width, height }}
      >
        <div className="graph-force-2d-empty-content">
          <p className="graph-force-2d-empty-message">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef}
      className={`graph-force-2d-container ${className}`}
      style={{ width, height }}
    >
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="graph-force-2d-svg"
      />
      <div className="graph-force-2d-controls">
        {enableZoom && (
          <div className="graph-force-2d-hint">
            <small>Double-click to reset zoom</small>
          </div>
        )}
        {enableDrag && (
          <div className="graph-force-2d-hint">
            <small>Drag nodes to reposition</small>
          </div>
        )}
      </div>
    </div>
  );
};

GraphForce2D.displayName = 'GraphForce2D';
