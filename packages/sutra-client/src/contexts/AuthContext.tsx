import { createContext, useState, useContext, useEffect, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../services/api'

interface ApiError {
  response?: {
    data?: {
      detail?: string
    }
  }
}

interface User {
  id: string
  email: string
  role: string
  organization: string
  active: boolean
  created_at: string
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  loading: boolean
  error: string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  
  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('sutra_token')
      if (token) {
        try {
          const userData = await authApi.getCurrentUser()
          setUser(userData)
        } catch (err) {
          console.error('Failed to validate session:', err)
          localStorage.removeItem('sutra_token')
          localStorage.removeItem('sutra_refresh_token')
        }
      }
      setLoading(false)
    }
    
    checkAuth()
  }, [])
  
  const login = async (email: string, password: string) => {
    try {
      setError(null)
      setLoading(true)
      const response = await authApi.login(email, password)
      
      // Store tokens
      localStorage.setItem('sutra_token', response.access_token)
      localStorage.setItem('sutra_refresh_token', response.refresh_token)
      
      // Set user
      setUser(response.user)
      
      // Navigate to home
      navigate('/')
    } catch (err) {
      const apiError = err as ApiError
      const errorMessage = apiError.response?.data?.detail || 'Login failed'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setLoading(false)
    }
  }
  
  const logout = async () => {
    try {
      setLoading(true)
      await authApi.logout()
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear local state regardless of API call success
      localStorage.removeItem('sutra_token')
      localStorage.removeItem('sutra_refresh_token')
      setUser(null)
      setLoading(false)
      navigate('/login')
    }
  }
  
  return (
    <AuthContext.Provider value={{ user, login, logout, loading, error }}>
      {children}
    </AuthContext.Provider>
  )
}

// Hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
