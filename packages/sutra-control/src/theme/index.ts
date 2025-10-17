import { createTheme, ThemeOptions } from '@mui/material/styles';
import { alpha } from '@mui/material/styles';

// M3 Color Tokens
const primaryPalette = {
  50: '#e8eaf6',
  100: '#c5cae9',
  200: '#9fa8da',
  300: '#7986cb',
  400: '#5c6bc0',
  500: '#3f51b5', // Primary
  600: '#3949ab',
  700: '#303f9f',
  800: '#283593',
  900: '#1a237e',
};

const surfaceVariants = {
  surface: '#0f1629',
  surfaceContainer: '#1a2332',
  surfaceContainerHigh: '#252e3d',
  surfaceContainerHighest: '#303948',
  surfaceBright: '#364048',
  surfaceDim: '#0a0e1a',
  onSurface: '#e3e8ef',
  onSurfaceVariant: '#c3c8d0',
  outline: '#8d9199',
  outlineVariant: '#42474e',
};

const baseThemeOptions: ThemeOptions = {
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1',
      light: '#818cf8',
      dark: '#4f46e5',
      contrastText: '#ffffff',
    },
    secondary: {
      main: '#06b6d4',
      light: '#22d3ee',
      dark: '#0891b2',
      contrastText: '#ffffff',
    },
    success: {
      main: '#10b981',
      light: '#34d399',
      dark: '#059669',
    },
    warning: {
      main: '#f59e0b',
      light: '#fbbf24',
      dark: '#d97706',
    },
    error: {
      main: '#ef4444',
      light: '#f87171',
      dark: '#dc2626',
    },
    background: {
      default: surfaceVariants.surface,
      paper: surfaceVariants.surfaceContainer,
    },
    surface: {
      main: surfaceVariants.surfaceContainer,
      light: surfaceVariants.surfaceContainerHigh,
      dark: surfaceVariants.surfaceDim,
    },
    text: {
      primary: surfaceVariants.onSurface,
      secondary: surfaceVariants.onSurfaceVariant,
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
      '"Apple Color Emoji"',
      '"Segoe UI Emoji"',
      '"Segoe UI Symbol"',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 700,
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
      lineHeight: 1.5,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
    },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.5,
      color: surfaceVariants.onSurfaceVariant,
    },
  },
  shape: {
    borderRadius: 12,
  },
  spacing: 8,
};

export const theme = createTheme({
  ...baseThemeOptions,
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarColor: `${surfaceVariants.outline} ${surfaceVariants.surfaceContainer}`,
          '&::-webkit-scrollbar, & *::-webkit-scrollbar': {
            backgroundColor: 'transparent',
            width: '8px',
            height: '8px',
          },
          '&::-webkit-scrollbar-thumb, & *::-webkit-scrollbar-thumb': {
            borderRadius: '8px',
            backgroundColor: surfaceVariants.outline,
            border: `2px solid ${surfaceVariants.surfaceContainer}`,
          },
          '&::-webkit-scrollbar-thumb:focus, & *::-webkit-scrollbar-thumb:focus': {
            backgroundColor: surfaceVariants.onSurfaceVariant,
          },
          '&::-webkit-scrollbar-thumb:active, & *::-webkit-scrollbar-thumb:active': {
            backgroundColor: surfaceVariants.onSurfaceVariant,
          },
          '&::-webkit-scrollbar-thumb:hover, & *::-webkit-scrollbar-thumb:hover': {
            backgroundColor: surfaceVariants.onSurfaceVariant,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: ({ theme }) => ({
          backgroundImage: 'none',
          backgroundColor: surfaceVariants.surfaceContainer,
          border: `1px solid ${surfaceVariants.outlineVariant}`,
          boxShadow: 'none',
          transition: theme.transitions.create(['transform', 'box-shadow'], {
            duration: theme.transitions.duration.short,
          }),
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: `0 4px 20px ${alpha(theme.palette.primary.main, 0.15)}`,
          },
        }),
      },
    },
    MuiButton: {
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: '24px',
          textTransform: 'none',
          fontWeight: 600,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        }),
        contained: ({ theme }) => ({
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          '&:hover': {
            background: `linear-gradient(135deg, ${theme.palette.primary.light} 0%, ${theme.palette.primary.main} 100%)`,
          },
        }),
        outlined: ({ theme }) => ({
          borderColor: surfaceVariants.outline,
          '&:hover': {
            borderColor: theme.palette.primary.main,
            backgroundColor: alpha(theme.palette.primary.main, 0.08),
          },
        }),
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: '16px',
          fontWeight: 500,
        },
        filled: ({ theme, ownerState }) => {
          const colors = {
            success: theme.palette.success.main,
            error: theme.palette.error.main,
            warning: theme.palette.warning.main,
            info: theme.palette.info.main,
          };
          
          const color = colors[ownerState.color as keyof typeof colors] || theme.palette.primary.main;
          
          return {
            backgroundColor: alpha(color, 0.2),
            color: color,
          };
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: surfaceVariants.surfaceContainer,
          border: `1px solid ${surfaceVariants.outlineVariant}`,
        },
        elevation1: {
          boxShadow: `0 2px 8px ${alpha('#000000', 0.1)}`,
        },
        elevation4: {
          boxShadow: `0 4px 16px ${alpha('#000000', 0.15)}`,
        },
        elevation8: {
          boxShadow: `0 8px 24px ${alpha('#000000', 0.2)}`,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: surfaceVariants.surfaceContainer,
          borderBottom: `1px solid ${surfaceVariants.outlineVariant}`,
          boxShadow: 'none',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: surfaceVariants.surfaceContainer,
          borderRight: `1px solid ${surfaceVariants.outlineVariant}`,
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: ({ theme }) => ({
          borderRadius: '12px',
          margin: '4px 8px',
          '&.Mui-selected': {
            backgroundColor: alpha(theme.palette.primary.main, 0.12),
            '&:hover': {
              backgroundColor: alpha(theme.palette.primary.main, 0.16),
            },
            '& .MuiListItemIcon-root': {
              color: theme.palette.primary.main,
            },
          },
          '&:hover': {
            backgroundColor: alpha(surfaceVariants.onSurface, 0.08),
          },
        }),
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: ({ theme }) => ({
          '& .MuiOutlinedInput-root': {
            borderRadius: '12px',
            backgroundColor: surfaceVariants.surfaceContainerHigh,
            '& fieldset': {
              borderColor: surfaceVariants.outline,
            },
            '&:hover fieldset': {
              borderColor: theme.palette.primary.main,
            },
            '&.Mui-focused fieldset': {
              borderColor: theme.palette.primary.main,
            },
          },
        }),
      },
    },
  },
});

// Extended theme interface for TypeScript
declare module '@mui/material/styles' {
  interface Palette {
    surface: Palette['primary'];
  }

  interface PaletteOptions {
    surface?: PaletteOptions['primary'];
  }
}

export default theme;