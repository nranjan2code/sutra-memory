import { useState, useEffect } from 'react'
import { ThemeProvider, CssBaseline } from '@mui/material'
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
import HomePage from './pages/HomePage'
import Login from './pages/Login'
import ChatInterface from './components/ChatInterface'

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
            </AuthProvider>
          </BrowserRouter>
        </ThemeProvider>
        </SnackbarProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
