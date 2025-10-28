# Getting Started with Sutra UI Framework

**Build your first application with the unified design system**

**Date:** October 28, 2025  
**Time to complete:** 30 minutes

---

## 🎯 What You'll Build

A simple concept browser using the holographic theme:

```
┌─────────────────────────────────────────────┐
│ 🔍 Search concepts...                       │
└─────────────────────────────────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Concept A       │  │ Concept B       │  │ Concept C       │
│ ▓▓▓▓▓▓▓░░ 87%  │  │ ▓▓▓▓░░░░░ 45%  │  │ ▓▓▓▓▓▓▓▓░ 92%  │
│ Description...  │  │ Description...  │  │ Description...  │
│ [Explore]       │  │ [Explore]       │  │ [Explore]       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 📋 Prerequisites

- Node.js 18+ (`node --version`)
- pnpm 8+ (`pnpm --version`)
- Basic React knowledge
- Text editor (VS Code recommended)

---

## 🚀 Step 1: Install Packages

### Create new project

```bash
# Create project directory
mkdir my-sutra-app
cd my-sutra-app

# Initialize project
pnpm init

# Install framework packages
pnpm add @sutra/ui-core @sutra/ui-themes @sutra/ui-components

# Install peer dependencies
pnpm add react react-dom

# Install dev dependencies
pnpm add -D vite @vitejs/plugin-react typescript @types/react @types/react-dom
```

### Project structure

```
my-sutra-app/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
└── src/
    ├── main.tsx
    ├── App.tsx
    └── components/
        └── ConceptBrowser.tsx
```

---

## 📝 Step 2: Configuration Files

### package.json

```json
{
  "name": "my-sutra-app",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "@sutra/ui-core": "^0.1.0",
    "@sutra/ui-themes": "^0.1.0",
    "@sutra/ui-components": "^0.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.2.0",
    "vite": "^4.4.0"
  }
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"]
}
```

### vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
});
```

### index.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>My Sutra App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

---

## 🎨 Step 3: Create Your App

### src/main.tsx

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### src/App.tsx

```typescript
import { ThemeProvider } from '@sutra/ui-core';
import { holographicTheme } from '@sutra/ui-themes';
import ConceptBrowser from './components/ConceptBrowser';

export default function App() {
  return (
    <ThemeProvider theme={holographicTheme}>
      <div style={{
        minHeight: '100vh',
        background: holographicTheme.tokens.color.background,
        padding: '2rem',
      }}>
        <ConceptBrowser />
      </div>
    </ThemeProvider>
  );
}
```

### src/components/ConceptBrowser.tsx

```typescript
import { useState } from 'react';
import { useTheme } from '@sutra/ui-core';
import { 
  Input, 
  Card, 
  Badge, 
  Button, 
  Text,
  Grid 
} from '@sutra/ui-components';

// Sample data
const concepts = [
  { id: 1, name: 'Neural Networks', confidence: 0.87, description: 'Artificial neural networks are computing systems inspired by biological neural networks.' },
  { id: 2, name: 'Machine Learning', confidence: 0.92, description: 'Machine learning is a method of data analysis that automates analytical model building.' },
  { id: 3, name: 'Deep Learning', confidence: 0.76, description: 'Deep learning is part of a broader family of machine learning methods based on artificial neural networks.' },
  { id: 4, name: 'Transformers', confidence: 0.89, description: 'Transformers are a type of neural network architecture that uses self-attention mechanisms.' },
];

export default function ConceptBrowser() {
  const theme = useTheme();
  const [search, setSearch] = useState('');

  const filteredConcepts = concepts.filter(concept =>
    concept.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      {/* Search Bar */}
      <Input
        placeholder="🔍 Search concepts..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ marginBottom: '2rem' }}
      />

      {/* Concept Grid */}
      <Grid columns={{ xs: 1, md: 2, lg: 3 }} gap="lg">
        {filteredConcepts.map(concept => (
          <Card key={concept.id} variant="holographic">
            <Card.Header>
              <Text variant="h6">{concept.name}</Text>
              <Badge 
                value={concept.confidence} 
                label={`${Math.round(concept.confidence * 100)}%`}
              />
            </Card.Header>
            
            <Card.Content>
              <Text variant="body2" color="secondary">
                {concept.description}
              </Text>
            </Card.Content>
            
            <Card.Actions>
              <Button 
                size="sm" 
                variant="ghost"
                onClick={() => alert(`Exploring ${concept.name}`)}
              >
                Explore
              </Button>
            </Card.Actions>
          </Card>
        ))}
      </Grid>

      {/* No Results */}
      {filteredConcepts.length === 0 && (
        <div style={{ 
          textAlign: 'center', 
          padding: '4rem',
          opacity: 0.5 
        }}>
          <Text variant="body1">No concepts found</Text>
        </div>
      )}
    </div>
  );
}
```

---

## ▶️ Step 4: Run Your App

```bash
# Start development server
pnpm dev

# Open browser
open http://localhost:3000
```

You should see:
- ✅ Black background (holographic theme)
- ✅ Cyan accents with glow effects
- ✅ Search bar at the top
- ✅ Grid of concept cards
- ✅ Confidence badges with visual encoding

---

## 🎨 Step 5: Try Different Themes

### Switch to Professional Theme

```typescript
// src/App.tsx
import { professionalTheme } from '@sutra/ui-themes';

<ThemeProvider theme={professionalTheme}>
  {/* Same components, different look! */}
</ThemeProvider>
```

### Switch to Command Theme

```typescript
// src/App.tsx
import { commandTheme } from '@sutra/ui-themes';

<ThemeProvider theme={commandTheme}>
  {/* Dark command center aesthetic */}
</ThemeProvider>
```

### Runtime Theme Switching

```typescript
import { useState } from 'react';
import { ThemeProvider } from '@sutra/ui-core';
import { holographicTheme, professionalTheme, commandTheme } from '@sutra/ui-themes';

const themes = {
  holographic: holographicTheme,
  professional: professionalTheme,
  command: commandTheme,
};

export default function App() {
  const [themeName, setThemeName] = useState<keyof typeof themes>('holographic');

  return (
    <ThemeProvider theme={themes[themeName]}>
      {/* Theme selector */}
      <select 
        value={themeName} 
        onChange={(e) => setThemeName(e.target.value as keyof typeof themes)}
      >
        <option value="holographic">Holographic</option>
        <option value="professional">Professional</option>
        <option value="command">Command</option>
      </select>

      <ConceptBrowser />
    </ThemeProvider>
  );
}
```

---

## 🧩 Step 6: Explore Components

### Available Components

```typescript
// Layout
import { Container, Grid, Stack, Spacer } from '@sutra/ui-components';

// Primitives
import { Button, Input, Card, Badge, Avatar, Text } from '@sutra/ui-components';

// Data Display
import { Table, List, Chart, CodeBlock } from '@sutra/ui-components';

// Feedback
import { Alert, Toast, Skeleton, Progress, Spinner } from '@sutra/ui-components';

// Navigation
import { Tabs, Breadcrumbs, Menu, Pagination } from '@sutra/ui-components';

// Overlays
import { Modal, Drawer, Popover, Tooltip } from '@sutra/ui-components';
```

### Example: Add a Modal

```typescript
import { useState } from 'react';
import { Button, Modal, Text } from '@sutra/ui-components';

function ConceptDetails({ concept }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setOpen(true)}>
        View Details
      </Button>

      <Modal open={open} onClose={() => setOpen(false)}>
        <Modal.Header>
          <Text variant="h5">{concept.name}</Text>
        </Modal.Header>
        
        <Modal.Content>
          <Text>{concept.description}</Text>
          <Text variant="caption" color="secondary">
            Confidence: {Math.round(concept.confidence * 100)}%
          </Text>
        </Modal.Content>
        
        <Modal.Actions>
          <Button variant="ghost" onClick={() => setOpen(false)}>
            Close
          </Button>
          <Button variant="primary">
            Learn More
          </Button>
        </Modal.Actions>
      </Modal>
    </>
  );
}
```

---

## 🎯 Step 7: Customize Your Theme

### Create a Custom Theme

```typescript
// src/theme/custom.ts
import { createTheme } from '@sutra/ui-core';
import { baseTokens } from '@sutra/ui-themes';

export const myCustomTheme = createTheme({
  name: 'custom',
  displayName: 'My Custom Theme',
  
  tokens: {
    ...baseTokens,
    color: {
      primary: '#ff6b6b',        // Your brand color
      secondary: '#4ecdc4',
      background: '#1a1a2e',
      surface: '#16213e',
      text: {
        primary: '#ffffff',
        secondary: '#b8c5d6',
      },
    },
  },
  
  components: {
    button: {
      primary: {
        background: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%)',
        border: 'none',
        boxShadow: '0 4px 12px rgba(255, 107, 107, 0.3)',
      },
    },
  },
});
```

### Use Your Custom Theme

```typescript
// src/App.tsx
import { myCustomTheme } from './theme/custom';

<ThemeProvider theme={myCustomTheme}>
  <ConceptBrowser />
</ThemeProvider>
```

---

## 📱 Step 8: Make It Responsive

### Add Mobile Support

```typescript
import { useBreakpoint } from '@sutra/ui-core';

export default function ConceptBrowser() {
  const breakpoint = useBreakpoint();
  const isMobile = breakpoint === 'xs' || breakpoint === 'sm';

  return (
    <Grid 
      columns={{ 
        xs: 1,      // 1 column on mobile
        md: 2,      // 2 columns on tablet
        lg: 3,      // 3 columns on desktop
        xl: 4       // 4 columns on large desktop
      }} 
      gap={isMobile ? 'md' : 'lg'}
    >
      {/* Cards */}
    </Grid>
  );
}
```

### Add Touch Gestures

```typescript
import { useGesture } from '@sutra/ui-core';

function SwipeableCard({ concept }) {
  const bind = useGesture({
    onSwipeLeft: () => console.log('Swiped left'),
    onSwipeRight: () => console.log('Swiped right'),
  });

  return (
    <Card {...bind()}>
      {/* Card content */}
    </Card>
  );
}
```

---

## ♿ Step 9: Ensure Accessibility

### Add Keyboard Navigation

```typescript
import { useKeyboard } from '@sutra/ui-core';

export default function ConceptBrowser() {
  const [selectedIndex, setSelectedIndex] = useState(0);

  useKeyboard({
    'ArrowRight': () => setSelectedIndex(i => Math.min(i + 1, concepts.length - 1)),
    'ArrowLeft': () => setSelectedIndex(i => Math.max(i - 1, 0)),
    'Enter': () => alert(`Selected ${concepts[selectedIndex].name}`),
  });

  return (
    <Grid>
      {concepts.map((concept, i) => (
        <Card 
          key={concept.id}
          tabIndex={0}
          aria-selected={i === selectedIndex}
          style={{ 
            outline: i === selectedIndex ? '2px solid cyan' : 'none' 
          }}
        >
          {/* Card content */}
        </Card>
      ))}
    </Grid>
  );
}
```

### Add Screen Reader Support

```typescript
<Card 
  role="article"
  aria-label={`${concept.name} with ${Math.round(concept.confidence * 100)}% confidence`}
>
  <Card.Header>
    <Text variant="h6" id={`concept-${concept.id}-title`}>
      {concept.name}
    </Text>
    <Badge 
      value={concept.confidence}
      aria-label={`Confidence: ${Math.round(concept.confidence * 100)} percent`}
    />
  </Card.Header>
  
  <Card.Content>
    <Text 
      variant="body2"
      aria-describedby={`concept-${concept.id}-title`}
    >
      {concept.description}
    </Text>
  </Card.Content>
</Card>
```

---

## 🚀 Step 10: Build for Production

```bash
# Build optimized bundle
pnpm build

# Check bundle size
ls -lh dist/assets/*.js

# Preview production build
pnpm preview
```

### Expected Bundle Sizes

```
dist/assets/
├── index-abc123.js      (~150KB)  # Your app
├── vendor-def456.js     (~100KB)  # React + framework
└── chunk-ghi789.js      (~50KB)   # Lazy-loaded components

Total: ~300KB (gzipped: ~100KB)
```

---

## 🎉 Next Steps

### Learn More

1. **[Design Principles](./DESIGN_PRINCIPLES.md)** - Understanding the "why"
2. **[Architecture](./ARCHITECTURE.md)** - Deep technical dive
3. **[Component API](./components/)** - Detailed component docs
4. **[Theme Guide](./themes/)** - Creating custom themes

### Examples

- 📊 [Dashboard Example](../examples/dashboard/)
- 🔍 [Search Interface](../examples/search/)
- 💬 [Chat Interface](../examples/chat/)
- 📈 [Graph Visualization](../examples/graph/)

### Join the Community

- 💬 Discord: [sutra-ai.dev/discord](https://sutra-ai.dev/discord)
- 🐛 Issues: [github.com/sutra-ai/ui-framework/issues](https://github.com/sutra-ai/ui-framework/issues)
- 📖 Docs: [docs.sutra-ai.dev](https://docs.sutra-ai.dev)

---

## 🆘 Troubleshooting

### Issue: "Cannot find module '@sutra/ui-core'"

```bash
# Ensure packages are installed
pnpm install

# Check package.json dependencies
cat package.json | grep @sutra
```

### Issue: "Theme not applying"

```typescript
// Ensure ThemeProvider wraps your app
<ThemeProvider theme={holographicTheme}>
  <App />  {/* All components inside provider */}
</ThemeProvider>
```

### Issue: "Components not styled"

```typescript
// Check if you're importing from correct package
import { Button } from '@sutra/ui-components';  // ✅ Correct
import { Button } from '@sutra/ui-core';        // ❌ Wrong (core has no components)
```

### Issue: "Build errors"

```bash
# Clear cache and rebuild
rm -rf node_modules dist
pnpm install
pnpm build
```

---

## 📊 Checklist

**Before moving to production:**

- [ ] All components render correctly
- [ ] Theme switching works
- [ ] Responsive on mobile/tablet/desktop
- [ ] Keyboard navigation works
- [ ] Screen reader tested (NVDA/JAWS/VoiceOver)
- [ ] Color contrast meets WCAG AA
- [ ] Bundle size < 500KB (gzipped < 150KB)
- [ ] Load time < 2s on 3G
- [ ] No console errors/warnings
- [ ] Performance: 60fps on interactions

---

**Congratulations!** 🎉 You've built your first Sutra AI application with the unified framework.

*Zero backward compatibility. Clean slate. Framework-first.*
