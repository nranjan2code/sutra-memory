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
} from '@mui/material'
import {
  Psychology as PsychologyIcon,
  Visibility,
  VisibilityOff,
  Email as EmailIcon,
  Lock as LockIcon,
} from '@mui/icons-material'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../hooks/useToast'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [localError, setLocalError] = useState<string | null>(null)
  const { login, loading, error } = useAuth()
  const toast = useToast()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLocalError(null)

    // Validation
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

          {/* Login Form */}
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              autoComplete="email"
              autoFocus
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
              disabled={loading}
              autoComplete="current-password"
              sx={{ mb: 3 }}
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
                      disabled={loading}
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
              disabled={loading}
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
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Sign In'
              )}
            </Button>
          </form>

          {/* Footer */}
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Don't have an account? Contact your administrator.
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
