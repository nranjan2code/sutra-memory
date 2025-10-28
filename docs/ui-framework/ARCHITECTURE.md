# Sutra UI Framework - Technical Architecture

**Deep dive into implementation details**

**Date:** October 28, 2025  
**Status:** Architecture Specification

---

## 🏗️ System Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Applications                                      │
│  sutra-explorer, sutra-control, sutra-client                │
└─────────────────────┬───────────────────────────────────────┘
                      │ imports
┌─────────────────────▼───────────────────────────────────────┐
│  Layer 3: Domain Components                                 │
│  Graph visualization, Chat interface, Dashboard widgets     │
└─────────────────────┬───────────────────────────────────────┘
                      │ imports
┌─────────────────────▼───────────────────────────────────────┐
│  Layer 2: UI Components (@sutra/ui-components)             │
│  Button, Card, Table, Modal, etc.                          │
└─────────────────────┬───────────────────────────────────────┘
                      │ imports
┌─────────────────────▼───────────────────────────────────────┐
│  Layer 1: Core Foundation (@sutra/ui-core)                 │
│  Theme system, hooks, utilities, primitives                 │
└─────────────────────────────────────────────────────────────┘
```

### Package Dependencies

```mermaid
graph TD
    A[Applications] --> B[@sutra/ui-graph]
    A --> C[@sutra/ui-components]
    B --> C
    C --> D[@sutra/ui-core]
    C --> E[@sutra/ui-themes]
    E --> D
    
    style A fill:#6366f1
    style B fill:#06b6d4
    style C fill:#10b981
    style D fill:#f59e0b
    style E fill:#ef4444
```

---

## 📦 Package Specifications

### @sutra/ui-core

**Purpose:** Foundation layer with zero dependencies on styling libraries.

**Size Target:** <15KB gzipped

**Public API:**

```typescript
// Theme system
export { ThemeProvider, useTheme, createTheme } from './theme';
export type { Theme, ThemeConfig, ThemeTokens } from './theme/types';

// Hooks
export { useMediaQuery } from './hooks/useMediaQuery';
export { useBreakpoint } from './hooks/useBreakpoint';
export { useColorScheme } from './hooks/useColorScheme';
export { useReducedMotion } from './hooks/useReducedMotion';
export { useContrastMode } from './hooks/useContrastMode';
export { useFocusVisible } from './hooks/useFocusVisible';
export { useKeyboard } from './hooks/useKeyboard';
export { useGesture } from './hooks/useGesture';

// Utilities
export { cn } from './utils/classnames';
export { tokens } from './utils/tokens';
export { color } from './utils/color';
export { animation } from './utils/animation';
export { accessibility } from './utils/accessibility';

// Types
export type * from './types';
```

**File Structure:**

```
@sutra/ui-core/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts
│   │
│   ├── theme/
│   │   ├── ThemeProvider.tsx        (React context provider)
│   │   ├── useTheme.ts               (Theme consumer hook)
│   │   ├── createTheme.ts            (Theme factory)
│   │   └── types.ts                  (TypeScript definitions)
│   │
│   ├── hooks/
│   │   ├── useMediaQuery.ts          (Responsive queries)
│   │   ├── useBreakpoint.ts          (Current breakpoint)
│   │   ├── useColorScheme.ts         (Dark/light detection)
│   │   ├── useReducedMotion.ts       (a11y: prefers-reduced-motion)
│   │   ├── useContrastMode.ts        (a11y: prefers-contrast)
│   │   ├── useFocusVisible.ts        (a11y: keyboard focus)
│   │   ├── useKeyboard.ts            (Keyboard shortcuts)
│   │   └── useGesture.ts             (Touch/mouse gestures)
│   │
│   ├── utils/
│   │   ├── classnames.ts             (className utilities)
│   │   ├── tokens.ts                 (Token resolution)
│   │   ├── color.ts                  (Color manipulation)
│   │   ├── animation.ts              (Animation helpers)
│   │   └── accessibility.ts          (a11y utilities)
│   │
│   └── types/
│       ├── theme.ts                  (Theme type definitions)
│       ├── component.ts              (Component prop types)
│       └── tokens.ts                 (Token type definitions)
│
└── tests/
    ├── theme.test.ts
    ├── hooks.test.ts
    └── utils.test.ts
```

**Key Implementation: Theme Provider**

```typescript
// src/theme/ThemeProvider.tsx

import React, { createContext, useContext, useMemo } from 'react';
import { Theme, ThemeConfig } from './types';
import { createTheme } from './createTheme';

const ThemeContext = createContext<Theme | undefined>(undefined);

interface ThemeProviderProps {
  theme: Theme | ThemeConfig;
  children: React.ReactNode;
}

export function ThemeProvider({ theme, children }: ThemeProviderProps) {
  const resolvedTheme = useMemo(() => {
    return 'name' in theme ? theme : createTheme(theme);
  }, [theme]);

  // Inject CSS variables
  React.useEffect(() => {
    const root = document.documentElement;
    
    // Semantic tokens
    Object.entries(resolvedTheme.tokens.color).forEach(([key, value]) => {
      root.style.setProperty(`--color-${key}`, value);
    });
    
    // Component tokens
    Object.entries(resolvedTheme.tokens.spacing).forEach(([key, value]) => {
      root.style.setProperty(`--spacing-${key}`, value);
    });
    
    // Animation tokens
    Object.entries(resolvedTheme.tokens.animation.duration).forEach(([key, value]) => {
      root.style.setProperty(`--duration-${key}`, value);
    });
  }, [resolvedTheme]);

  return (
    <ThemeContext.Provider value={resolvedTheme}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): Theme {
  const theme = useContext(ThemeContext);
  if (!theme) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return theme;
}
```

---

### @sutra/ui-themes

**Purpose:** Pre-built theme definitions.

**Size Target:** <8KB per theme (gzipped)

**Public API:**

```typescript
// Themes
export { holographicTheme } from './holographic';
export { professionalTheme } from './professional';
export { commandTheme } from './command';

// Base tokens (shared)
export { baseTokens } from './base';
export { createCustomTheme } from './custom';

// Types
export type { HolographicConfig, ProfessionalConfig, CommandConfig } from './types';
```

**File Structure:**

```
@sutra/ui-themes/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts
│   │
│   ├── base/
│   │   ├── tokens.ts                 (Shared semantic tokens)
│   │   ├── breakpoints.ts            (Responsive breakpoints)
│   │   └── accessibility.ts          (a11y defaults)
│   │
│   ├── holographic/
│   │   ├── index.ts                  (Holographic theme)
│   │   ├── tokens.ts                 (Color, effects tokens)
│   │   ├── components.ts             (Component overrides)
│   │   └── effects.ts                (Glow, scanlines, blur)
│   │
│   ├── professional/
│   │   ├── index.ts                  (Professional theme)
│   │   ├── tokens.ts                 (Material Design 3 tokens)
│   │   └── components.ts             (Component overrides)
│   │
│   ├── command/
│   │   ├── index.ts                  (Command theme)
│   │   ├── tokens.ts                 (Dark command center tokens)
│   │   ├── components.ts             (Component overrides)
│   │   └── effects.ts                (Subtle glow effects)
│   │
│   └── custom/
│       └── createCustomTheme.ts      (Theme factory)
│
└── tests/
    ├── holographic.test.ts
    ├── professional.test.ts
    └── command.test.ts
```

**Key Implementation: Holographic Theme**

```typescript
// src/holographic/index.ts

import { Theme } from '@sutra/ui-core';
import { baseTokens } from '../base/tokens';
import { holographicEffects } from './effects';

export const holographicTheme: Theme = {
  name: 'holographic',
  displayName: 'Holographic HUD',
  
  tokens: {
    ...baseTokens,
    
    // Color overrides
    color: {
      primary: '#00ffff',           // Cyan
      primaryHover: '#00e6e6',
      primaryActive: '#00cccc',
      
      secondary: '#00d4d4',         // Mid cyan
      
      success: '#00ffaa',           // Green-cyan
      warning: '#ffff00',           // Yellow
      error: '#ff0066',             // Pink-red
      info: '#00aaff',              // Blue-cyan
      
      surface: '#0a0e1a',           // Near black
      surfaceHover: '#12182c',
      surfaceActive: '#1a2440',
      
      background: '#000000',        // Pure black
      
      text: {
        primary: '#e0e6ed',         // Bright white
        secondary: '#8892a0',       // Mid gray
        tertiary: '#6b7280',        // Dark gray
        disabled: '#4a5568',        // Very dark gray
      },
      
      border: {
        default: '#2d3748',
        hover: '#00ffff',           // Cyan on hover
        focus: '#00ffff',           // Cyan on focus
      },
    },
    
    // Typography overrides
    typography: {
      ...baseTokens.typography,
      fontFamily: {
        base: '"Roboto Mono", "Courier New", monospace',
        heading: '"Roboto Mono", "Courier New", monospace',
        code: '"Roboto Mono", "Courier New", monospace',
      },
    },
    
    // Effect tokens (unique to holographic)
    effects: holographicEffects,
  },
  
  // Component-specific overrides
  components: {
    button: {
      primary: {
        background: 'transparent',
        border: '1px solid var(--color-primary)',
        color: 'var(--color-primary)',
        boxShadow: '0 0 10px rgba(0, 255, 255, 0.3), 0 0 20px rgba(0, 255, 255, 0.2)',
        
        hover: {
          background: 'rgba(0, 255, 255, 0.1)',
          boxShadow: '0 0 15px rgba(0, 255, 255, 0.5), 0 0 30px rgba(0, 255, 255, 0.3)',
        },
      },
    },
    
    card: {
      background: 'rgba(10, 14, 26, 0.8)',
      backdropFilter: 'blur(20px)',
      border: '1px solid rgba(0, 255, 255, 0.2)',
      boxShadow: '0 0 20px rgba(0, 255, 255, 0.1)',
      
      // Scanline effect
      backgroundImage: `
        repeating-linear-gradient(
          0deg,
          rgba(0, 255, 255, 0.05) 0px,
          transparent 1px,
          transparent 2px
        )
      `,
    },
  },
  
  // Accessibility settings
  accessibility: {
    contrastRatio: 14.6,           // WCAG AAA
    colorblindSafe: true,          // Single-hue system
    reducedMotion: true,           // Respects user preference
    focusVisible: true,            // Always show focus
    screenReaderOptimized: true,
  },
};
```

**Key Implementation: Effect System**

```typescript
// src/holographic/effects.ts

export const holographicEffects = {
  glow: {
    enabled: true,
    levels: {
      low: {
        blur: [8],
        opacity: [0.2],
        spread: 2,
      },
      medium: {
        blur: [10, 20],
        opacity: [0.3, 0.2],
        spread: 4,
      },
      high: {
        blur: [10, 20, 40],
        opacity: [0.3, 0.2, 0.1],
        spread: 8,
      },
    },
    
    // CSS generator
    toCss(level: 'low' | 'medium' | 'high', color: string) {
      const config = this.levels[level];
      return config.blur.map((blur, i) => 
        `0 0 ${blur}px rgba(${color}, ${config.opacity[i]})`
      ).join(', ');
    },
  },
  
  scanlines: {
    enabled: true,
    height: 2,
    opacity: 0.05,
    color: '#00ffff',
    
    // CSS generator
    toCss() {
      return `
        repeating-linear-gradient(
          0deg,
          rgba(${this.color}, ${this.opacity}) 0px,
          transparent 1px,
          transparent ${this.height}px
        )
      `;
    },
  },
  
  frostedGlass: {
    enabled: true,
    blur: 20,
    opacity: 0.1,
    brightness: 1.2,
    
    // CSS generator
    toCss() {
      return `
        backdrop-filter: blur(${this.blur}px) brightness(${this.brightness});
        background: rgba(255, 255, 255, ${this.opacity});
      `;
    },
  },
  
  edgeHighlight: {
    enabled: true,
    width: 1,
    opacity: 0.3,
    color: '#00ffff',
    
    // CSS generator
    toCss(side: 'top' | 'right' | 'bottom' | 'left' | 'all' = 'all') {
      const border = `${this.width}px solid rgba(${this.color}, ${this.opacity})`;
      
      if (side === 'all') {
        return `border: ${border};`;
      }
      
      return `border-${side}: ${border};`;
    },
  },
};
```

---

### @sutra/ui-components

**Purpose:** Reusable UI components.

**Size Target:** <50KB gzipped (all components, tree-shakeable)

**Public API:**

```typescript
// Layout
export { Container, Grid, Stack, Spacer } from './layout';
export { Sidebar, Header, Footer } from './layout';

// Primitives
export { Button } from './primitives/Button';
export { Input } from './primitives/Input';
export { Card } from './primitives/Card';
export { Badge } from './primitives/Badge';
export { Avatar } from './primitives/Avatar';

// Data Display
export { Table } from './data-display/Table';
export { List } from './data-display/List';
export { Chart } from './data-display/Chart';
export { CodeBlock } from './data-display/CodeBlock';

// Feedback
export { Alert } from './feedback/Alert';
export { Toast } from './feedback/Toast';
export { Skeleton } from './feedback/Skeleton';
export { Progress } from './feedback/Progress';
export { Spinner } from './feedback/Spinner';

// Navigation
export { Tabs } from './navigation/Tabs';
export { Breadcrumbs } from './navigation/Breadcrumbs';
export { Menu } from './navigation/Menu';
export { Pagination } from './navigation/Pagination';

// Overlays
export { Modal } from './overlays/Modal';
export { Drawer } from './overlays/Drawer';
export { Popover } from './overlays/Popover';
export { Tooltip } from './overlays/Tooltip';

// Forms
export { Form } from './forms/Form';
export { Select } from './forms/Select';
export { Checkbox } from './forms/Checkbox';
export { Radio } from './forms/Radio';
export { Switch } from './forms/Switch';
```

**File Structure:**

```
@sutra/ui-components/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts
│   │
│   ├── primitives/
│   │   ├── Button/
│   │   │   ├── Button.tsx
│   │   │   ├── Button.styles.ts
│   │   │   ├── Button.test.tsx
│   │   │   └── index.ts
│   │   ├── Input/
│   │   ├── Card/
│   │   └── ...
│   │
│   ├── layout/
│   │   ├── Container/
│   │   ├── Grid/
│   │   ├── Sidebar/
│   │   └── ...
│   │
│   ├── data-display/
│   ├── feedback/
│   ├── navigation/
│   ├── overlays/
│   └── forms/
│
└── tests/
    └── components/
```

**Key Implementation: Theme-Aware Button**

```typescript
// src/primitives/Button/Button.tsx

import React from 'react';
import { useTheme } from '@sutra/ui-core';
import { getButtonStyles } from './Button.styles';

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  icon,
  iconPosition = 'left',
  fullWidth = false,
  children,
  onClick,
  type = 'button',
}: ButtonProps) {
  const theme = useTheme();
  const styles = getButtonStyles(theme, { variant, size, loading, disabled, fullWidth });

  return (
    <button
      type={type}
      className={styles.root}
      disabled={disabled || loading}
      onClick={onClick}
      aria-busy={loading}
      aria-disabled={disabled || loading}
    >
      {loading && <span className={styles.spinner} />}
      {!loading && icon && iconPosition === 'left' && (
        <span className={styles.iconLeft}>{icon}</span>
      )}
      <span className={styles.label}>{children}</span>
      {!loading && icon && iconPosition === 'right' && (
        <span className={styles.iconRight}>{icon}</span>
      )}
    </button>
  );
}
```

```typescript
// src/primitives/Button/Button.styles.ts

import { Theme, cn } from '@sutra/ui-core';
import { css } from '@emotion/react';

export function getButtonStyles(
  theme: Theme,
  props: { variant: string; size: string; loading: boolean; disabled: boolean; fullWidth: boolean }
) {
  const base = css`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: ${theme.tokens.spacing.sm};
    font-family: ${theme.tokens.typography.fontFamily.base};
    font-weight: ${theme.tokens.typography.fontWeight.medium};
    border-radius: ${theme.tokens.shape.borderRadius.md};
    transition: all ${theme.tokens.animation.duration.fast} ${theme.tokens.animation.easing.easeInOut};
    cursor: pointer;
    user-select: none;
    
    &:focus-visible {
      outline: 2px solid ${theme.tokens.color.primary};
      outline-offset: 2px;
    }
    
    &:disabled {
      cursor: not-allowed;
      opacity: 0.5;
    }
    
    ${props.fullWidth && `width: 100%;`}
  `;

  const variantStyles = theme.components.button[props.variant];
  const sizeStyles = getSizeStyles(theme, props.size);

  return {
    root: cn(base, variantStyles, sizeStyles),
    spinner: css`
      width: 1em;
      height: 1em;
      border: 2px solid currentColor;
      border-top-color: transparent;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
      
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `,
    iconLeft: css`
      display: flex;
      align-items: center;
    `,
    iconRight: css`
      display: flex;
      align-items: center;
    `,
    label: css`
      display: flex;
      align-items: center;
    `,
  };
}

function getSizeStyles(theme: Theme, size: string) {
  const sizes = {
    sm: css`
      height: 32px;
      padding: 0 ${theme.tokens.spacing.md};
      font-size: ${theme.tokens.typography.fontSize.sm};
    `,
    md: css`
      height: 40px;
      padding: 0 ${theme.tokens.spacing.lg};
      font-size: ${theme.tokens.typography.fontSize.base};
    `,
    lg: css`
      height: 48px;
      padding: 0 ${theme.tokens.spacing.xl};
      font-size: ${theme.tokens.typography.fontSize.lg};
    `,
  };
  
  return sizes[size as keyof typeof sizes];
}
```

---

### @sutra/ui-graph

**Purpose:** Graph visualization with adaptive rendering.

**Size Target:** <120KB gzipped

**Public API:**

```typescript
// Main exports
export { GraphView } from './GraphView';
export { AdaptiveRenderer } from './AdaptiveRenderer';

// Renderers
export { SVGRenderer } from './renderers/SVG';
export { CanvasRenderer } from './renderers/Canvas';
export { WebGLRenderer } from './renderers/WebGL';
export { WebGPURenderer } from './renderers/WebGPU';

// Layouts
export { ForceDirectedLayout } from './layouts/ForceDirected';
export { HierarchicalLayout } from './layouts/Hierarchical';
export { CircularLayout } from './layouts/Circular';

// Interactions
export { ZoomController } from './interactions/Zoom';
export { PanController } from './interactions/Pan';
export { SelectController } from './interactions/Select';
export { DragController } from './interactions/Drag';

// Types
export type * from './types';
```

**Key Implementation: Adaptive Renderer**

```typescript
// src/AdaptiveRenderer.tsx

import React, { useEffect, useState } from 'react';
import { useTheme } from '@sutra/ui-core';
import { GraphData, RenderingContext, RendererConfig } from './types';
import { selectOptimalRenderer } from './selection';
import { SVGRenderer, CanvasRenderer, WebGLRenderer, WebGPURenderer } from './renderers';

export interface AdaptiveRendererProps {
  data: GraphData;
  interactions?: Array<'zoom' | 'pan' | 'select' | 'drag'>;
  effects?: Array<'glow' | 'scanlines' | 'frosted-glass'>;
  forceRenderer?: 'svg' | 'canvas' | 'webgl' | 'webgpu';
  onNodeClick?: (nodeId: string) => void;
  onNodeHover?: (nodeId: string | null) => void;
}

export function AdaptiveRenderer({
  data,
  interactions = ['zoom', 'pan', 'select'],
  effects = [],
  forceRenderer,
  onNodeClick,
  onNodeHover,
}: AdaptiveRendererProps) {
  const theme = useTheme();
  const [context, setContext] = useState<RenderingContext | null>(null);
  const [renderer, setRenderer] = useState<RendererConfig | null>(null);

  // Detect rendering context
  useEffect(() => {
    const detectContext = async (): Promise<RenderingContext> => {
      return {
        device: detectDevice(),
        nodeCount: data.nodes.length,
        screenSize: {
          width: window.innerWidth,
          height: window.innerHeight,
        },
        gpuTier: await detectGPUTier(),
        capabilities: {
          webgl: detectWebGL(),
          webgl2: detectWebGL2(),
          webgpu: await detectWebGPU(),
          offscreenCanvas: 'OffscreenCanvas' in window,
        },
      };
    };

    detectContext().then(setContext);
  }, [data.nodes.length]);

  // Select optimal renderer
  useEffect(() => {
    if (!context) return;

    if (forceRenderer) {
      setRenderer({ id: forceRenderer, priority: 100, canHandle: () => true, performance: { fps: 60, memory: 100 } });
    } else {
      const optimal = selectOptimalRenderer(context);
      setRenderer(optimal);
    }
  }, [context, forceRenderer]);

  if (!context || !renderer) {
    return <div>Loading...</div>;
  }

  // Render with selected renderer
  const RendererComponent = getRendererComponent(renderer.id);
  
  return (
    <RendererComponent
      data={data}
      theme={theme}
      interactions={interactions}
      effects={effects}
      onNodeClick={onNodeClick}
      onNodeHover={onNodeHover}
    />
  );
}

function getRendererComponent(id: string) {
  switch (id) {
    case 'svg':
      return SVGRenderer;
    case 'canvas':
      return CanvasRenderer;
    case 'webgl':
    case 'webgl2':
      return WebGLRenderer;
    case 'webgpu':
      return WebGPURenderer;
    default:
      return SVGRenderer; // Fallback
  }
}

// Device detection helpers
function detectDevice(): 'mobile' | 'tablet' | 'desktop' | '4k' | 'vr' {
  const width = window.innerWidth;
  
  if (width >= 3840) return '4k';
  if (width >= 1024) return 'desktop';
  if (width >= 768) return 'tablet';
  return 'mobile';
}

async function detectGPUTier(): Promise<0 | 1 | 2 | 3> {
  // Simplified GPU tier detection
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');
  
  if (!gl) return 0;
  
  const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
  if (!debugInfo) return 1;
  
  const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
  
  // High-end GPUs
  if (/RTX 40|RTX 30|RX 7000|RX 6000/i.test(renderer)) return 3;
  // Mid-range GPUs
  if (/RTX 20|GTX 16|RX 5000/i.test(renderer)) return 2;
  // Low-end GPUs
  if (/GTX|RX|Intel/i.test(renderer)) return 1;
  
  return 0;
}

function detectWebGL(): boolean {
  const canvas = document.createElement('canvas');
  return !!canvas.getContext('webgl');
}

function detectWebGL2(): boolean {
  const canvas = document.createElement('canvas');
  return !!canvas.getContext('webgl2');
}

async function detectWebGPU(): Promise<boolean> {
  return 'gpu' in navigator;
}
```

---

## 🎨 CSS-in-JS Strategy

### Why Emotion?

```
✅ Theme-aware: Access theme tokens in styles
✅ Type-safe: Full TypeScript support
✅ Performance: Auto-optimization, critical CSS
✅ SSR-ready: Server-side rendering support
✅ Small: 7KB gzipped
✅ Zero-config: No build step required
```

### Style Patterns

**Pattern 1: Inline Styles (Simple)**

```typescript
import { css } from '@emotion/react';

const buttonStyle = css`
  background: var(--color-primary);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
`;

<button css={buttonStyle}>Click me</button>
```

**Pattern 2: Style Functions (Theme-aware)**

```typescript
import { useTheme } from '@sutra/ui-core';

function MyComponent() {
  const theme = useTheme();
  
  return (
    <div css={{
      background: theme.tokens.color.surface,
      border: `1px solid ${theme.tokens.color.border.default}`,
      borderRadius: theme.tokens.shape.borderRadius.md,
    }}>
      Content
    </div>
  );
}
```

**Pattern 3: Styled Components (Reusable)**

```typescript
import styled from '@emotion/styled';
import { Theme } from '@sutra/ui-core';

const StyledCard = styled.div<{ theme: Theme }>`
  background: ${props => props.theme.tokens.color.surface};
  border: 1px solid ${props => props.theme.tokens.color.border.default};
  border-radius: ${props => props.theme.tokens.shape.borderRadius.md};
  padding: ${props => props.theme.tokens.spacing.lg};
  
  ${props => props.theme.name === 'holographic' && `
    backdrop-filter: blur(20px);
    box-shadow: ${props.theme.tokens.effects.glow.toCss('medium', props.theme.tokens.color.primary)};
  `}
`;
```

---

## 🔌 Integration Examples

### Example 1: Migrating Sutra Explorer

**Before (old code):**

```typescript
// packages/sutra-explorer/frontend/src/App.tsx

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#6366f1' },
    // ... hardcoded theme
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Dashboard />
    </ThemeProvider>
  );
}
```

**After (unified framework):**

```typescript
// packages/sutra-explorer/src/App.tsx

import { ThemeProvider } from '@sutra/ui-core';
import { holographicTheme } from '@sutra/ui-themes';
import { GraphView } from '@sutra/ui-graph';

function App() {
  return (
    <ThemeProvider theme={holographicTheme}>
      <GraphView data={graphData} />
    </ThemeProvider>
  );
}
```

---

## 📊 Performance Optimization

### Bundle Size Strategy

```typescript
// Tree-shaking optimization
// Import only what you need

// ❌ Bad: Imports everything
import * as Components from '@sutra/ui-components';

// ✅ Good: Tree-shakeable
import { Button, Card } from '@sutra/ui-components';

// ✅ Better: Direct imports
import { Button } from '@sutra/ui-components/Button';
import { Card } from '@sutra/ui-components/Card';
```

### Code Splitting

```typescript
// Lazy load heavy components
const GraphView = lazy(() => import('@sutra/ui-graph'));
const DataTable = lazy(() => import('@sutra/ui-components/DataTable'));

function App() {
  return (
    <Suspense fallback={<Skeleton />}>
      <GraphView />
    </Suspense>
  );
}
```

### Runtime Performance

```typescript
// Memoization patterns
import { memo, useMemo } from 'react';

export const ExpensiveComponent = memo(({ data }) => {
  const processedData = useMemo(() => {
    return heavyComputation(data);
  }, [data]);
  
  return <div>{processedData}</div>;
});
```

---

## 🧪 Testing Strategy

### Unit Tests (Components)

```typescript
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '@sutra/ui-core';
import { holographicTheme } from '@sutra/ui-themes';
import { Button } from '@sutra/ui-components';

test('Button renders with holographic theme', () => {
  render(
    <ThemeProvider theme={holographicTheme}>
      <Button>Click me</Button>
    </ThemeProvider>
  );
  
  const button = screen.getByRole('button');
  expect(button).toHaveTextContent('Click me');
  expect(button).toHaveStyle({ color: holographicTheme.tokens.color.primary });
});
```

### Visual Regression Tests

```typescript
import { test, expect } from '@playwright/test';

test('Button matches holographic theme snapshot', async ({ page }) => {
  await page.goto('/storybook/?path=/story/button--holographic');
  
  const button = page.locator('button');
  await expect(button).toHaveScreenshot('button-holographic.png');
});
```

### Accessibility Tests

```typescript
import { axe } from 'jest-axe';

test('Button has no accessibility violations', async () => {
  const { container } = render(
    <ThemeProvider theme={holographicTheme}>
      <Button>Click me</Button>
    </ThemeProvider>
  );
  
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

## 📖 Next Steps

1. Review this architecture with team
2. Prototype `@sutra/ui-core` package (Week 1)
3. Build holographic theme (Week 1-2)
4. Migrate sutra-explorer (Week 2-3)
5. Document learnings and iterate

---

**Building a design system that scales.** 🎨

*Zero backward compatibility. Clean slate. Framework-first.*
