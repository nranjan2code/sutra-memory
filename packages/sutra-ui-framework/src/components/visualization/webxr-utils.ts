/**
 * WebXR Utilities for VR/AR Support
 * 
 * Foundation utilities for WebXR integration in Graph3D component.
 * Provides hooks and helpers for VR/AR experiences.
 * 
 * @package @sutra/ui-framework
 */

import { useEffect, useState, useCallback } from 'react';
import * as THREE from 'three';

// ============================================================================
// Types
// ============================================================================

export interface WebXRSessionConfig {
  mode: 'immersive-vr' | 'immersive-ar' | 'inline';
  requiredFeatures?: string[];
  optionalFeatures?: string[];
}

export interface WebXRController {
  grip: THREE.Group | null;
  pointer: THREE.Group | null;
  connected: boolean;
}

export interface WebXRState {
  isSupported: boolean;
  isSessionActive: boolean;
  mode: 'immersive-vr' | 'immersive-ar' | 'inline' | null;
  controllers: WebXRController[];
}

// ============================================================================
// Hooks
// ============================================================================

/**
 * Hook to check WebXR support
 */
export const useWebXRSupport = (): { vrSupported: boolean; arSupported: boolean } => {
  const [vrSupported, setVrSupported] = useState(false);
  const [arSupported, setArSupported] = useState(false);

  useEffect(() => {
    if (!navigator.xr) {
      return;
    }

    navigator.xr.isSessionSupported('immersive-vr').then(setVrSupported).catch(() => setVrSupported(false));
    navigator.xr.isSessionSupported('immersive-ar').then(setArSupported).catch(() => setArSupported(false));
  }, []);

  return { vrSupported, arSupported };
};

/**
 * Hook to manage WebXR session
 */
export const useWebXRSession = (
  renderer: THREE.WebGLRenderer | null,
  config: WebXRSessionConfig
): {
  startSession: () => Promise<void>;
  endSession: () => Promise<void>;
  isActive: boolean;
} => {
  const [isActive, setIsActive] = useState(false);

  const startSession = useCallback(async () => {
    if (!renderer || !navigator.xr) {
      throw new Error('WebXR not supported');
    }

    try {
      const session = await navigator.xr.requestSession(config.mode, {
        requiredFeatures: config.requiredFeatures,
        optionalFeatures: config.optionalFeatures,
      });

      await renderer.xr.setSession(session);
      setIsActive(true);

      session.addEventListener('end', () => {
        setIsActive(false);
      });
    } catch (error) {
      console.error('Failed to start WebXR session:', error);
      throw error;
    }
  }, [renderer, config]);

  const endSession = useCallback(async () => {
    if (!renderer || !renderer.xr.getSession()) {
      return;
    }

    const session = renderer.xr.getSession();
    if (session) {
      await session.end();
    }
    setIsActive(false);
  }, [renderer]);

  return { startSession, endSession, isActive };
};

// ============================================================================
// Utilities
// ============================================================================

/**
 * Initialize WebXR for a Three.js renderer
 */
export const initializeWebXR = (renderer: THREE.WebGLRenderer): void => {
  renderer.xr.enabled = true;
};

/**
 * Create VR controller helpers
 */
export const createVRControllers = (renderer: THREE.WebGLRenderer): WebXRController[] => {
  const controllers: WebXRController[] = [];

  for (let i = 0; i < 2; i++) {
    const controller = {
      grip: renderer.xr.getControllerGrip(i),
      pointer: renderer.xr.getController(i),
      connected: false,
    };

    // Add event listeners for connection
    controller.pointer.addEventListener('connected', () => {
      controller.connected = true;
    });

    controller.pointer.addEventListener('disconnected', () => {
      controller.connected = false;
    });

    controllers.push(controller);
  }

  return controllers;
};

/**
 * Setup teleportation for VR
 */
export const setupVRTeleportation = (
  controller: THREE.Group,
  camera: THREE.Camera,
  onTeleport?: (position: THREE.Vector3) => void
): void => {
  const raycaster = new THREE.Raycaster();
  const tempMatrix = new THREE.Matrix4();

  controller.addEventListener('selectstart', () => {
    // Get controller direction
    tempMatrix.identity().extractRotation(controller.matrixWorld);
    raycaster.ray.origin.setFromMatrixPosition(controller.matrixWorld);
    raycaster.ray.direction.set(0, 0, -1).applyMatrix4(tempMatrix);

    // Calculate teleport position (implement ground plane intersection)
    const teleportPosition = new THREE.Vector3();
    // ... raycasting logic ...

    if (onTeleport) {
      onTeleport(teleportPosition);
    }
  });
};

/**
 * Create AR hit test source
 */
export const createARHitTestSource = async (
  session: XRSession
): Promise<XRHitTestSource | null> => {
  if (!session.requestHitTestSource) {
    return null;
  }

  try {
    const referenceSpace = await session.requestReferenceSpace('viewer');
    const hitTestSource = await session.requestHitTestSource({ space: referenceSpace });
    return hitTestSource;
  } catch (error) {
    console.error('Failed to create AR hit test source:', error);
    return null;
  }
};

/**
 * Handle AR placement
 */
export const handleARPlacement = (
  frame: XRFrame,
  hitTestSource: XRHitTestSource | null,
  referenceSpace: XRReferenceSpace,
  onPlacement: (matrix: THREE.Matrix4) => void
): void => {
  if (!hitTestSource) return;

  const hitTestResults = frame.getHitTestResults(hitTestSource);
  
  if (hitTestResults.length > 0) {
    const hit = hitTestResults[0];
    const pose = hit.getPose(referenceSpace);
    
    if (pose) {
      const matrix = new THREE.Matrix4().fromArray(pose.transform.matrix);
      onPlacement(matrix);
    }
  }
};

/**
 * Setup stereoscopic rendering
 */
export const setupStereoscopicRendering = (
  renderer: THREE.WebGLRenderer,
  camera: THREE.PerspectiveCamera
): void => {
  // WebXR automatically handles stereoscopic rendering
  // This is a placeholder for custom stereo configurations
  renderer.xr.enabled = true;
  
  // Set recommended XR settings
  renderer.xr.setFramebufferScaleFactor(1.0);
};

/**
 * Calculate interpupillary distance for VR
 */
export const calculateIPD = (session: XRSession | null): number => {
  if (!session) return 0.064; // Default IPD in meters
  
  const views = session.renderState.baseLayer?.getViewport;
  if (!views) return 0.064;
  
  // Calculate from view matrices if available
  return 0.064; // Placeholder
};

/**
 * Create XR-compatible scene lighting
 */
export const createXRLighting = (scene: THREE.Scene): void => {
  // Ambient light for general illumination
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
  scene.add(ambientLight);

  // Hemisphere light for outdoor AR
  const hemisphereLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6);
  hemisphereLight.position.set(0, 200, 0);
  scene.add(hemisphereLight);

  // Directional light for shadows
  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(100, 200, 100);
  directionalLight.castShadow = true;
  directionalLight.shadow.camera.top = 100;
  directionalLight.shadow.camera.bottom = -100;
  directionalLight.shadow.camera.left = -100;
  directionalLight.shadow.camera.right = 100;
  scene.add(directionalLight);
};

/**
 * Optimize scene for XR performance
 */
export const optimizeSceneForXR = (scene: THREE.Scene): void => {
  scene.traverse((object) => {
    if (object instanceof THREE.Mesh) {
      // Enable frustum culling
      object.frustumCulled = true;

      // Optimize materials
      if (object.material instanceof THREE.Material) {
        object.material.precision = 'mediump';
        object.material.needsUpdate = true;
      }

      // Enable shadows only for important objects
      object.castShadow = false;
      object.receiveShadow = false;
    }
  });
};

// ============================================================================
// Constants
// ============================================================================

export const XR_FEATURES = {
  REQUIRED: ['local'],
  OPTIONAL: [
    'bounded-floor',
    'hand-tracking',
    'layers',
    'hit-test',
    'anchors',
    'depth-sensing',
  ],
} as const;

export const XR_REFERENCE_SPACES = {
  VIEWER: 'viewer',
  LOCAL: 'local',
  LOCAL_FLOOR: 'local-floor',
  BOUNDED_FLOOR: 'bounded-floor',
  UNBOUNDED: 'unbounded',
} as const;
