# Sutra UI Framework - Implementation Roadmap

**Step-by-step guide to building and deploying the unified design system**

**Date:** October 28, 2025  
**Timeline:** 8 weeks  
**First Implementation:** sutra-explorer

---

## 🎯 Overview

### Milestones

```
Week 1-2: Framework Foundation
  ├─ @sutra/ui-core package
  ├─ @sutra/ui-themes (holographic)
  └─ Development tooling

Week 3-4: Sutra Explorer Migration
  ├─ DELETE old sutra-explorer code
  ├─ Build new with framework
  └─ Production deployment

Week 5-6: Control Center Adoption
  ├─ @sutra/ui-themes (command)
  ├─ Migrate sutra-control
  └─ Production deployment

Week 7-8: Client UI Adoption
  ├─ @sutra/ui-themes (professional refined)
  ├─ Migrate sutra-client
  └─ Complete platform unification
```

---

## 📅 Week-by-Week Plan

### Week 1: Core Foundation

**Goal:** Create `@sutra/ui-core` and `@sutra/ui-themes` base packages

#### Day 1-2: Project Setup

```bash
# 1. Create monorepo structure
mkdir -p packages/@sutra/ui-core
mkdir -p packages/@sutra/ui-themes
mkdir -p packages/@sutra/ui-components
mkdir -p packages/@sutra/ui-graph

# 2. Initialize packages
cd packages/@sutra/ui-core
pnpm init
```

**Files to create:**

```
packages/@sutra/ui-core/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts
│   ├── theme/
│   │   ├── ThemeProvider.tsx
│   │   ├── useTheme.ts
│   │   ├── createTheme.ts
│   │   └── types.ts
│   └── utils/
│       ├── classnames.ts
│       └── tokens.ts
└── tests/
    └── theme.test.ts
```

**Package.json:**

```json
{
  "name": "@sutra/ui-core",
  "version": "0.1.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsup src/index.ts --format esm,cjs --dts",
    "dev": "tsup src/index.ts --format esm,cjs --dts --watch",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "tsup": "^7.2.0",
    "typescript": "^5.2.0",
    "vitest": "^0.34.0"
  }
}
```

#### Day 3-4: Theme System Implementation

**Priority files:**

1. `src/theme/types.ts` - TypeScript definitions
2. `src/theme/ThemeProvider.tsx` - React context
3. `src/theme/useTheme.ts` - Theme consumer hook
4. `src/theme/createTheme.ts` - Theme factory

**Key implementation:**

```typescript
// src/theme/types.ts
export interface Theme {
  name: string;
  displayName: string;
  tokens: ThemeTokens;
  components: ComponentTokens;
  accessibility: AccessibilityConfig;
}

export interface ThemeTokens {
  color: ColorTokens;
  typography: TypographyTokens;
  spacing: SpacingTokens;
  shape: ShapeTokens;
  elevation: ElevationTokens;
  animation: AnimationTokens;
}

// ... (see ARCHITECTURE.md for full definitions)
```

#### Day 5: Hooks Implementation

**Create utility hooks:**

- `useMediaQuery` - Responsive breakpoints
- `useBreakpoint` - Current breakpoint
- `useReducedMotion` - Accessibility
- `useFocusVisible` - Keyboard navigation

```typescript
// src/hooks/useMediaQuery.ts
export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia(query).matches;
    }
    return false;
  });

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches);
    
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}
```

---

### Week 2: Themes & Components

**Goal:** Create holographic theme and base components

#### Day 1-2: Holographic Theme

**Create theme package:**

```
packages/@sutra/ui-themes/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts
│   ├── base/
│   │   └── tokens.ts
│   └── holographic/
│       ├── index.ts
│       ├── tokens.ts
│       ├── components.ts
│       └── effects.ts
└── tests/
    └── holographic.test.ts
```

**Implementation:**

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
    color: {
      primary: '#00ffff',
      background: '#000000',
      surface: '#0a0e1a',
      text: {
        primary: '#e0e6ed',
        secondary: '#8892a0',
      },
      // ... (see ARCHITECTURE.md)
    },
  },
  
  components: {
    button: {
      primary: {
        background: 'transparent',
        border: '1px solid var(--color-primary)',
        boxShadow: '0 0 10px rgba(0, 255, 255, 0.3)',
      },
    },
    // ... (see ARCHITECTURE.md)
  },
  
  accessibility: {
    contrastRatio: 14.6,
    colorblindSafe: true,
  },
};
```

#### Day 3-5: Base Components

**Create component package:**

```
packages/@sutra/ui-components/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts
│   └── primitives/
│       ├── Button/
│       │   ├── Button.tsx
│       │   ├── Button.styles.ts
│       │   └── index.ts
│       ├── Card/
│       ├── Badge/
│       └── Text/
└── tests/
    └── components/
```

**Priority components:**

1. **Button** - Primary interaction
2. **Card** - Content container
3. **Badge** - Status indicator
4. **Text** - Typography
5. **Spinner** - Loading state

**Implementation pattern:**

```typescript
// src/primitives/Button/Button.tsx
import React from 'react';
import { useTheme } from '@sutra/ui-core';
import { getButtonStyles } from './Button.styles';

export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}

export function Button({ 
  variant = 'primary', 
  size = 'md',
  children,
  onClick 
}: ButtonProps) {
  const theme = useTheme();
  const styles = getButtonStyles(theme, { variant, size });

  return (
    <button className={styles.root} onClick={onClick}>
      {children}
    </button>
  );
}
```

---

### Week 3-4: Sutra Explorer Migration

**Goal:** DELETE old code, build new sutra-explorer with framework

#### Day 1: Preparation

**Tasks:**

1. ✅ Backup current sutra-explorer (git tag: `pre-framework-migration`)
2. ✅ Document current features
3. ✅ Create feature parity checklist
4. ✅ Set up new package structure

```bash
# Backup
git tag pre-framework-migration-explorer
git push origin pre-framework-migration-explorer

# Delete old code
rm -rf packages/sutra-explorer/frontend/src/*
rm -rf packages/sutra-explorer/backend/*

# New structure
mkdir -p packages/sutra-explorer/src/{components,pages,lib}
```

#### Day 2-3: Core UI Implementation

**New file structure:**

```
packages/sutra-explorer/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── components/
│   │   ├── GraphCanvas.tsx
│   │   ├── NodeInspector.tsx
│   │   ├── SearchBar.tsx
│   │   └── MiniMap.tsx
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   └── GraphExplorer.tsx
│   └── lib/
│       ├── api.ts
│       └── graph-data.ts
└── index.html
```

**Main App:**

```typescript
// src/App.tsx
import { ThemeProvider } from '@sutra/ui-core';
import { holographicTheme } from '@sutra/ui-themes';
import { GraphView } from './components/GraphCanvas';

export function App() {
  return (
    <ThemeProvider theme={holographicTheme}>
      <div className="app">
        <GraphView />
      </div>
    </ThemeProvider>
  );
}
```

#### Day 4: Graph Visualization

**Create adaptive graph renderer:**

```typescript
// src/components/GraphCanvas.tsx
import { useState, useEffect } from 'react';
import { useTheme } from '@sutra/ui-core';
import { Card, Badge, Text } from '@sutra/ui-components';

export function GraphView() {
  const theme = useTheme();
  const [graphData, setGraphData] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  return (
    <div className="graph-container">
      <canvas ref={canvasRef} className="graph-canvas" />
      
      {selectedNode && (
        <Card variant="floating" className="node-inspector">
          <Card.Header>
            <Text variant="h6">{selectedNode.name}</Text>
            <Badge value={selectedNode.confidence} />
          </Card.Header>
          <Card.Content>
            <Text variant="body2">{selectedNode.content}</Text>
          </Card.Content>
        </Card>
      )}
    </div>
  );
}
```

#### Day 5: Testing & Refinement

**Tasks:**

1. ✅ Test all interactions (zoom, pan, select)
2. ✅ Test on mobile devices
3. ✅ Accessibility audit
4. ✅ Performance profiling
5. ✅ Fix any issues

**Checklist:**

```
□ 60fps on desktop (1000 nodes)
□ 60fps on mobile (500 nodes)
□ WCAG AAA contrast ratios
□ Keyboard navigation works
□ Touch gestures work
□ Loading states present
□ Error states handled
```

---

### Week 4: Production Deployment

**Goal:** Deploy new sutra-explorer to production

#### Day 1-2: Final Polish

**Tasks:**

1. ✅ Code review
2. ✅ Documentation updates
3. ✅ Build optimization
4. ✅ Bundle size check

```bash
# Build production bundle
pnpm build

# Check bundle size
ls -lh dist/assets/*.js

# Target: <150KB for main bundle
```

#### Day 3: Deployment

**Steps:**

```bash
# 1. Build Docker image
cd packages/sutra-explorer
docker build -t sutra-explorer:latest .

# 2. Update compose file
# .sutra/compose/production.yml
services:
  sutra-explorer:
    image: sutra-explorer:latest
    ports:
      - "3001:80"

# 3. Deploy
SUTRA_EDITION=simple ./sutra deploy

# 4. Smoke test
curl http://localhost:3001
```

#### Day 4-5: Monitoring & Iteration

**Monitor:**

1. ✅ Page load times
2. ✅ Error rates
3. ✅ User feedback
4. ✅ Performance metrics

**Collect metrics:**

```bash
# Lighthouse audit
lighthouse http://localhost:3001 --output json

# Web Vitals
# - FCP: <1.8s (target)
# - LCP: <2.5s (target)
# - TTI: <3.8s (target)
# - FID: <100ms (target)
# - CLS: <0.1 (target)
```

---

### Week 5-6: Control Center Migration

**Goal:** Migrate sutra-control to command theme

#### Day 1-2: Command Theme

**Create command theme:**

```typescript
// packages/@sutra/ui-themes/src/command/index.ts
export const commandTheme: Theme = {
  name: 'command',
  displayName: 'Command Center',
  
  tokens: {
    color: {
      primary: '#6366f1',
      secondary: '#06b6d4',
      surface: '#1a2332',
      background: '#0f1629',
      // ...
    },
  },
  
  effects: {
    glow: {
      enabled: true,
      blur: [8, 16],
      opacity: [0.15, 0.1],
    },
  },
};
```

#### Day 3-5: Migration

**Steps:**

1. ✅ Delete old theme definition
2. ✅ Replace ThemeProvider
3. ✅ Update components to use framework
4. ✅ Test dashboard views
5. ✅ Deploy

```typescript
// Before
import { createTheme } from '@mui/material';

// After
import { ThemeProvider } from '@sutra/ui-core';
import { commandTheme } from '@sutra/ui-themes';
```

---

### Week 7-8: Client UI Migration

**Goal:** Complete platform unification

#### Day 1-2: Professional Theme Refinement

**Enhance existing theme:**

```typescript
// packages/@sutra/ui-themes/src/professional/index.ts
export const professionalTheme: Theme = {
  name: 'professional',
  displayName: 'Professional',
  
  tokens: {
    color: {
      primary: '#6750A4',
      secondary: '#625B71',
      surface: '#FFFFFF',
      background: '#FEF7FF',
      // ... (Material Design 3)
    },
  },
};
```

#### Day 3-5: Migration & Testing

**Full platform test:**

1. ✅ All three apps use unified framework
2. ✅ Theme switching works
3. ✅ Components render correctly in all themes
4. ✅ Performance targets met
5. ✅ Accessibility compliance

---

## 🎯 Success Criteria

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Bundle size (framework) | <200KB | gzip -c dist/*.js \| wc -c |
| Bundle size (per app) | <500KB | Same |
| Load time (mobile) | <2s | Lighthouse |
| Load time (desktop) | <500ms | Lighthouse |
| FPS (mobile) | 60fps | Chrome DevTools |
| FPS (desktop) | 120fps | Chrome DevTools |
| WCAG compliance | AA minimum | axe-core |
| Test coverage | >80% | vitest --coverage |

### Feature Parity

| Feature | Sutra Explorer | Sutra Control | Sutra Client |
|---------|----------------|---------------|--------------|
| Graph visualization | ✅ | N/A | ❌ |
| Dashboard | ✅ | ✅ | ❌ |
| Chat interface | ❌ | ❌ | ✅ |
| Search | ✅ | ✅ | ✅ |
| Dark theme | ✅ | ✅ | ❌ |
| Light theme | ❌ | ❌ | ✅ |
| Mobile responsive | ✅ | ✅ | ✅ |
| Keyboard shortcuts | ✅ | ✅ | ✅ |

### Developer Experience

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to add new UI | <1 week | Track implementation time |
| Component reuse rate | >70% | Count shared components |
| Theme consistency | 100% | Automated checks |
| TypeScript coverage | 100% | tsc --noEmit |
| Lint errors | 0 | eslint |

---

## 🚨 Risk Mitigation

### Risk 1: Performance Regression

**Mitigation:**

- Automated performance tests in CI/CD
- Bundle size limits enforced
- Performance budgets set
- Regular profiling

```yaml
# .github/workflows/performance.yml
- name: Bundle size check
  run: |
    size=$(gzip -c dist/*.js | wc -c)
    if [ $size -gt 204800 ]; then
      echo "Bundle too large: $size bytes"
      exit 1
    fi
```

### Risk 2: Accessibility Issues

**Mitigation:**

- Automated a11y tests (axe-core)
- Manual testing with screen readers
- WCAG checklist per component
- Color contrast validation

```bash
# Run accessibility audit
pnpm test:a11y

# Manual test with NVDA/JAWS/VoiceOver
```

### Risk 3: Breaking Changes

**Mitigation:**

- Git tags before each migration
- Feature flags for gradual rollout
- Monitoring dashboards
- Quick rollback plan

```bash
# Tag before migration
git tag pre-migration-control-v1
git push origin --tags

# Quick rollback if needed
git revert HEAD
```

---

## 📚 Documentation Plan

### Week 1-2: Framework Docs

- [x] README.md (overview)
- [x] ARCHITECTURE.md (technical deep dive)
- [x] IMPLEMENTATION_ROADMAP.md (this file)
- [ ] DESIGN_PRINCIPLES.md
- [ ] GETTING_STARTED.md

### Week 3-4: Component Docs

- [ ] Component API reference
- [ ] Storybook setup
- [ ] Usage examples
- [ ] Migration guides

### Week 5-8: Theme Docs

- [ ] Theme creation guide
- [ ] Customization guide
- [ ] Best practices
- [ ] Troubleshooting

---

## 🎉 Completion Checklist

### Framework (Week 1-2)

- [ ] `@sutra/ui-core` package published
- [ ] `@sutra/ui-themes` package published
- [ ] `@sutra/ui-components` package published
- [ ] Documentation complete
- [ ] Tests passing (>80% coverage)

### Sutra Explorer (Week 3-4)

- [ ] Old code deleted
- [ ] New code implemented
- [ ] All features working
- [ ] Performance targets met
- [ ] Deployed to production

### Sutra Control (Week 5-6)

- [ ] Migrated to framework
- [ ] Command theme implemented
- [ ] Dashboard working
- [ ] Deployed to production

### Sutra Client (Week 7-8)

- [ ] Migrated to framework
- [ ] Professional theme refined
- [ ] Chat interface working
- [ ] Deployed to production

### Platform (Week 8)

- [ ] All apps using unified framework
- [ ] Theme switching works
- [ ] Documentation complete
- [ ] Team trained
- [ ] Success metrics met

---

## 📞 Support

### During Implementation

**Questions?** Contact:
- Technical lead: [Your name]
- Design review: [Designer name]
- Accessibility: [A11y expert]

### After Deployment

**Issues?** Check:
1. Documentation: `docs/ui-framework/`
2. Examples: `packages/sutra-explorer/`
3. Tests: `packages/@sutra/*/tests/`

---

**Let's build the future of Sutra AI UI.** 🚀

*Zero backward compatibility. Clean slate. Framework-first.*
