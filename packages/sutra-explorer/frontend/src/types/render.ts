/**
 * Rendering strategy types
 */

export type RenderMode = 'list' | 'cluster' | 'force2d' | 'tree' | '2.5d' | '3d' | 'vr';

export type DeviceType = 'mobile' | 'tablet' | 'desktop' | '4k' | 'vr';

export interface RenderStrategy {
  mode: RenderMode;
  reason: string;
  technology: 'react-window' | 'd3' | 'canvas' | 'three.js' | 'webxr';
  fpsTarget: 60 | 120 | 90;
}

export interface ViewportDimensions {
  width: number;
  height: number;
  pixelRatio: number;
}

export interface RenderConfig {
  enableWebGL: boolean;
  enable3D: boolean;
  enableVR: boolean;
  maxNodes: number;
  nodeDetail: 'minimal' | 'medium' | 'full';
  edgeDetail: 'minimal' | 'medium' | 'full';
}
