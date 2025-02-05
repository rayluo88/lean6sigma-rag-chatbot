/**
 * Main App component for the Lean Six Sigma RAG Chatbot frontend.
 * 
 * This component provides:
 * - Root layout structure
 * - Route configuration
 * - Authentication state management
 * - Theme configuration
 */

import { BrowserRouter as Router } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import theme from './theme';
import AppRoutes from './routes';
import Layout from './components/layout/Layout';

// Create a client for React Query
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline /> {/* Reset CSS */}
        <Router>
          <Layout>
            <AppRoutes />
          </Layout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App; 