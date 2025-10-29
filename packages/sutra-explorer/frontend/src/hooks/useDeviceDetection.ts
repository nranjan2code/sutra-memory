import { useState, useEffect } from 'react';
import type { DeviceType } from '@types/render';

export interface DeviceDetectionResult {
  deviceType: DeviceType;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  is4K: boolean;
  isVRCapable: boolean;
  screenWidth: number;
  screenHeight: number;
  pixelRatio: number;
}

export function useDeviceDetection(): DeviceDetectionResult {
  const [detection, setDetection] = useState<DeviceDetectionResult>(() =>
    detectDevice()
  );

  useEffect(() => {
    const handleResize = () => {
      setDetection(detectDevice());
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('orientationchange', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('orientationchange', handleResize);
    };
  }, []);

  return detection;
}

function detectDevice(): DeviceDetectionResult {
  const screenWidth = window.innerWidth;
  const screenHeight = window.innerHeight;
  const pixelRatio = window.devicePixelRatio || 1;

  // Check for VR capability
  const isVRCapable = 'xr' in navigator && 'isSessionSupported' in navigator.xr!;

  // Determine device type
  let deviceType: DeviceType;
  let isMobile = false;
  let isTablet = false;
  let isDesktop = false;
  let is4K = false;

  // 4K detection (3840x2160 or higher)
  if (screenWidth >= 3840 || screenHeight >= 2160) {
    deviceType = '4k';
    is4K = true;
  }
  // Mobile detection (< 768px)
  else if (screenWidth < 768) {
    deviceType = 'mobile';
    isMobile = true;
  }
  // Tablet detection (768px - 1024px)
  else if (screenWidth < 1024) {
    deviceType = 'tablet';
    isTablet = true;
  }
  // Desktop
  else {
    deviceType = 'desktop';
    isDesktop = true;
  }

  return {
    deviceType,
    isMobile,
    isTablet,
    isDesktop,
    is4K,
    isVRCapable,
    screenWidth,
    screenHeight,
    pixelRatio,
  };
}
