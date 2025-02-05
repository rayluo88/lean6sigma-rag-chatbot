/**
 * Custom Material-UI theme configuration for the Lean Six Sigma RAG Chatbot.
 * 
 * This theme includes:
 * - Custom color palette
 * - Typography settings
 * - Component style overrides
 * - Responsive breakpoints
 */

import { createTheme } from '@mui/material/styles';

// Define custom colors
const colors = {
  primary: {
    main: '#2E3B55', // Professional dark blue
    light: '#4A5D80',
    dark: '#1A2233',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#38B2AC', // Teal accent
    light: '#4FD1CB',
    dark: '#2C8A85',
    contrastText: '#FFFFFF',
  },
  success: {
    main: '#48BB78', // Green
    light: '#68D391',
    dark: '#2F855A',
  },
  error: {
    main: '#E53E3E', // Red
    light: '#FC8181',
    dark: '#C53030',
  },
  warning: {
    main: '#ED8936', // Orange
    light: '#F6AD55',
    dark: '#C05621',
  },
  info: {
    main: '#4299E1', // Blue
    light: '#63B3ED',
    dark: '#2B6CB0',
  },
  background: {
    default: '#F7FAFC',
    paper: '#FFFFFF',
  },
};

// Create theme
const theme = createTheme({
  palette: colors,
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Prevent all-caps buttons
          borderRadius: '8px',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: '12px',
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        },
      },
    },
  },
  shape: {
    borderRadius: 8,
  },
});

export default theme; 