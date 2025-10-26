import { useState, useEffect, lazy, Suspense } from 'react'
import { ThemeProvider, CssBaseline, Box, CircularProgress } from '@mui/material'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SnackbarProvider } from 'notistack'
import { theme } from './theme'
import { AuthProvider } from './contexts/AuthContext'
import Layout from './components/Layout'
import ChatLayout from './layouts/ChatLayout'
import ProtectedRoute from './components/ProtectedRoute'
import ErrorBoundary from './components/ErrorBoundary'
import KeyboardShortcutsDialog from './components/KeyboardShortcutsDialog'
import { initPerformanceMonitoring } from './utils/performance'

// Lazy load pages for better initial bundle size
const HomePage = lazy(() => import('./pages/HomePage'))
const Login = lazy(() => import('./pages/Login'))
const ChatInterface = lazy(() => import('./components/ChatInterface'))

// Loading fallback component
const LoadingFallback = () => (
  <Box
    display="flex"
    alignItems="center"
    justifyContent="center"
    minHeight="100vh"
    sx={{ backgroundColor: 'background.default' }}
  >
    <CircularProgress />
  </Box>
)

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds
    },
  },
})

function App() {
  const [shortcutsOpen, setShortcutsOpen] = useState(false)

  // Initialize performance monitoring
  useEffect(() => {
    initPerformanceMonitoring()
  }, [])

  // Global keyboard shortcut listener
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // ? key to open shortcuts
      if (e.key === '?' && !e.metaKey && !e.ctrlKey) {
        // Don't trigger if user is typing in input
        const target = e.target as HTMLElement
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') {
          return
        }
        e.preventDefault()
        setShortcutsOpen(true)
      }
      
      // Cmd+/ or Ctrl+/ also opens shortcuts
      if (e.key === '/' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setShortcutsOpen(true)
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [])

  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <SnackbarProvider maxSnack={3}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <KeyboardShortcutsDialog 
              open={shortcutsOpen} 
              onClose={() => setShortcutsOpen(false)} 
            />
            <BrowserRouter>
              <AuthProvider>
                <Suspense fallback={<LoadingFallback />}>
                  <Routes>
                    {/* Public route */}
                    <Route path="/login" element={<Login />} />
                
                {/* Chat routes (conversation-first UI) */}
                <Route
                  path="/chat"
                  element={
                    <ProtectedRoute>
                      <ErrorBoundary>
                        <ChatLayout>
                          <ChatInterface />
                        </ChatLayout>
                      </ErrorBoundary>
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/chat/:conversationId"
                  element={
                    <ProtectedRoute>
                      <ErrorBoundary>
                        <ChatLayout>
                          <ChatInterface />
                        </ChatLayout>
                      </ErrorBoundary>
                    </ProtectedRoute>
                  }
                />
                
                {/* Legacy home route (for backward compatibility) */}
                <Route
                  path="/"
                  element={
                    <ProtectedRoute>
                      <ErrorBoundary>
                        <Layout>
                          <HomePage />
                        </Layout>
                      </ErrorBoundary>
                    </ProtectedRoute>
                  }
                />
                
                {/* Redirect all other routes to chat */}
                <Route path="*" element={<Navigate to="/chat" replace />} />
              </Routes>
                </Suspense>
            </AuthProvider>
          </BrowserRouter>
        </ThemeProvider>
        </SnackbarProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
