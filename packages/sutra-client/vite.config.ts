import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  
  // Development server configuration
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Don't rewrite - keep /api prefix for sutra-api routes
        // rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },

  // Production build optimization
  build: {
    // Target modern browsers for optimal performance
    target: 'es2020',
    
    // Output directory
    outDir: 'dist',
    
    // Generate sourcemaps for debugging (can be disabled for prod)
    sourcemap: true,
    
    // Minification
    minify: 'esbuild',
    
    // Chunk size warnings
    chunkSizeWarningLimit: 1000,
    
    // Code splitting and optimization
    rollupOptions: {
      output: {
        // Manual chunking for better caching
        manualChunks: {
          // React core
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          
          // Material UI
          'vendor-mui': [
            '@mui/material',
            '@mui/icons-material',
            '@emotion/react',
            '@emotion/styled'
          ],
          
          // React Query
          'vendor-query': ['@tanstack/react-query'],
          
          // Graph visualization (heavy dependency)
          'vendor-graph': ['reactflow'],
          
          // Utilities
          'vendor-utils': ['axios', 'zustand', 'notistack', 'web-vitals']
        },
        
        // Asset naming
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.');
          const ext = info?.[info.length - 1];
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext ?? '')) {
            return 'assets/images/[name]-[hash][extname]';
          } else if (/woff2?|ttf|eot/i.test(ext ?? '')) {
            return 'assets/fonts/[name]-[hash][extname]';
          }
          return 'assets/[name]-[hash][extname]';
        },
        
        // Chunk naming
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js'
      }
    },
    
    // Optimize dependencies
    commonjsOptions: {
      include: [/node_modules/]
    }
  },

  // Dependency optimization
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@mui/material',
      '@tanstack/react-query',
      'axios'
    ]
  },

  // Environment variable prefix
  envPrefix: 'VITE_',

  // Preview server (for testing production builds)
  preview: {
    port: 8080,
    host: true
  }
})

