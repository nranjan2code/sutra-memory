import { useState, FormEvent } from 'react'
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  InputAdornment,
  IconButton,
  Link,
} from '@mui/material'
import {
  Psychology as PsychologyIcon,
  Visibility,
  VisibilityOff,
  Email as EmailIcon,
  Lock as LockIcon,
  Person as PersonIcon,
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../hooks/useToast'
import { authApi } from '../services/api'

export default function Login() {
  const [isRegistering, setIsRegistering] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [organization, setOrganization] = useState('')
  const [fullName, setFullName] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)
  const [registerLoading, setRegisterLoading] = useState(false)
  const { login, loading, error } = useAuth()
  const toast = useToast()

  const handleRegister = async () => {
    setLocalError(null)
    setRegisterLoading(true)

    // Validation
    if (!email) {
      setLocalError('Email is required')
      setRegisterLoading(false)
      return
    }
    if (!password) {
      setLocalError('Password is required')
      setRegisterLoading(false)
      return
    }
    if (!organization) {
      setLocalError('Organization is required')
      setRegisterLoading(false)
      return
    }
    if (!email.includes('@')) {
      setLocalError('Please enter a valid email')
      setRegisterLoading(false)
      return
    }
    if (password.length < 8) {
      setLocalError('Password must be at least 8 characters')
      setRegisterLoading(false)
      return
    }

    try {
      const response = await authApi.register(email, password, organization, fullName)
      console.log('Registration successful:', response)
      toast.success('Account created successfully! Please log in.')
      
      // Switch to login mode and clear registration fields
      setIsRegistering(false)
      setOrganization('')
      setFullName('')
      setPassword('')
      // Keep email for convenience
    } catch (err) {
      console.error('Registration failed:', err)
      const errorMessage = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Registration failed. Please try again.'
      setLocalError(errorMessage)
      toast.error(errorMessage)
    } finally {
      setRegisterLoading(false)
    }
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    
    if (isRegistering) {
      await handleRegister()
      return
    }

    setLocalError(null)

    // Validation for login
    if (!email) {
      setLocalError('Email is required')
      return
    }
    if (!password) {
      setLocalError('Password is required')
      return
    }
    if (!email.includes('@')) {
      setLocalError('Please enter a valid email')
      return
    }

    try {
      await login(email, password)
      toast.success('Welcome back!')
    } catch (err) {
      // Error is already set in auth context
      console.error('Login failed:', err)
      toast.error('Login failed. Please check your credentials.')
    }
  }

  const displayError = localError || error

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #6750A4 0%, #4F378B 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={3}
          sx={{
            p: 4,
            borderRadius: 4,
            background: '#FFFFFF',
          }}
        >
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <PsychologyIcon
              sx={{
                fontSize: 48,
                color: 'primary.main',
                mb: 2,
              }}
            />
            <Typography
              variant="h4"
              component="h1"
              sx={{ fontWeight: 600, color: 'primary.main', mb: 1 }}
            >
              Sutra AI
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Domain-Specific Explainable AI
            </Typography>
          </Box>

          {/* Error Alert */}
          {displayError && (
            <Alert severity="error" sx={{ mb: 3, borderRadius: 2 }}>
              {displayError}
            </Alert>
          )}

          {/* Login/Register Form */}
          <form onSubmit={handleSubmit}>
            {isRegistering && (
              <TextField
                fullWidth
                label="Organization"
                value={organization}
                onChange={(e) => setOrganization(e.target.value)}
                disabled={loading || registerLoading}
                autoComplete="organization"
                autoFocus={isRegistering}
                sx={{ mb: 2 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PersonIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            )}

            {isRegistering && (
              <TextField
                fullWidth
                label="Full Name (optional)"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                disabled={loading || registerLoading}
                autoComplete="name"
                sx={{ mb: 2 }}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <PersonIcon color="action" />
                    </InputAdornment>
                  ),
                }}
              />
            )}

            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading || registerLoading}
              autoComplete="email"
              autoFocus={!isRegistering}
              sx={{ mb: 2 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <EmailIcon color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="Password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading || registerLoading}
              autoComplete={isRegistering ? "new-password" : "current-password"}
              sx={{ mb: 3 }}
              helperText={isRegistering ? "Minimum 8 characters" : ""}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      disabled={loading || registerLoading}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={loading || registerLoading}
              sx={{
                py: 1.5,
                fontSize: '1rem',
                fontWeight: 600,
                textTransform: 'none',
                boxShadow: 2,
                '&:hover': {
                  boxShadow: 4,
                },
              }}
            >
              {(loading || registerLoading) ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                isRegistering ? 'Create Account' : 'Sign In'
              )}
            </Button>
          </form>

          {/* Footer */}
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              {isRegistering ? 'Already have an account? ' : "Don't have an account? "}
              <Link
                component="button"
                variant="body2"
                onClick={() => {
                  setIsRegistering(!isRegistering)
                  setLocalError(null)
                  setOrganization('')
                  setFullName('')
                  setPassword('')
                }}
                sx={{
                  textDecoration: 'underline',
                  cursor: 'pointer',
                  border: 'none',
                  background: 'none',
                  color: 'primary.main',
                  '&:hover': {
                    color: 'primary.dark',
                  },
                }}
              >
                {isRegistering ? 'Sign in here' : 'Create an account'}
              </Link>
            </Typography>
          </Box>
        </Paper>

        {/* Version Info */}
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
            Sutra AI - Conversation-First Interface
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}
