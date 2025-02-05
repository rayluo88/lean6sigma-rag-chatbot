/**
 * Home page component for the Lean Six Sigma RAG Chatbot.
 * 
 * Features:
 * - Hero section with value proposition
 * - Key features overview
 * - Call-to-action buttons
 * - Responsive design
 */

import { Box, Button, Container, Grid, Typography, Card, CardContent } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  Speed as SpeedIcon,
  Psychology as PsychologyIcon,
  LibraryBooks as LibraryIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

const features = [
  {
    icon: <PsychologyIcon sx={{ fontSize: 40 }} />,
    title: 'AI-Powered Guidance',
    description: 'Get expert Lean Six Sigma advice using advanced RAG-based AI technology.',
  },
  {
    icon: <LibraryIcon sx={{ fontSize: 40 }} />,
    title: 'Comprehensive Resources',
    description: 'Access a rich knowledge base of LSS methodologies, tools, and best practices.',
  },
  {
    icon: <SpeedIcon sx={{ fontSize: 40 }} />,
    title: 'Instant Answers',
    description: 'Get immediate responses to your Lean Six Sigma questions and challenges.',
  },
  {
    icon: <AnalyticsIcon sx={{ fontSize: 40 }} />,
    title: 'Process Optimization',
    description: 'Learn how to improve efficiency and reduce waste in your operations.',
  },
];

export default function Home() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          bgcolor: 'primary.main',
          color: 'primary.contrastText',
          py: 8,
          mb: 6,
          borderRadius: 2,
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography
                variant="h1"
                sx={{
                  fontSize: { xs: '2.5rem', md: '3.5rem' },
                  fontWeight: 700,
                  mb: 2,
                }}
              >
                Lean Six Sigma Excellence with AI
              </Typography>
              <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
                Get instant, expert guidance for your process improvement journey using our
                AI-powered chatbot.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                {isAuthenticated ? (
                  <Button
                    variant="contained"
                    color="secondary"
                    size="large"
                    onClick={() => navigate('/chat')}
                  >
                    Start Chatting
                  </Button>
                ) : (
                  <>
                    <Button
                      variant="contained"
                      color="secondary"
                      size="large"
                      onClick={() => navigate('/register')}
                    >
                      Get Started Free
                    </Button>
                    <Button
                      variant="outlined"
                      color="inherit"
                      size="large"
                      onClick={() => navigate('/login')}
                    >
                      Login
                    </Button>
                  </>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              {/* Add hero image or illustration here */}
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ mb: 8 }}>
        <Typography
          variant="h2"
          align="center"
          sx={{ mb: 6 }}
        >
          Why Choose Our Platform?
        </Typography>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'center',
                      mb: 2,
                      color: 'primary.main',
                    }}
                  >
                    {feature.icon}
                  </Box>
                  <Typography
                    variant="h5"
                    component="h3"
                    align="center"
                    gutterBottom
                  >
                    {feature.title}
                  </Typography>
                  <Typography
                    variant="body1"
                    align="center"
                    color="text.secondary"
                  >
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Call to Action Section */}
      <Box
        sx={{
          bgcolor: 'secondary.main',
          color: 'secondary.contrastText',
          py: 8,
          borderRadius: 2,
        }}
      >
        <Container maxWidth="lg">
          <Typography
            variant="h3"
            align="center"
            sx={{ mb: 3 }}
          >
            Ready to Transform Your Process?
          </Typography>
          <Typography
            variant="h6"
            align="center"
            sx={{ mb: 4, opacity: 0.9 }}
          >
            Join now and get started with our free tier - no credit card required.
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={() => navigate(isAuthenticated ? '/chat' : '/register')}
            >
              {isAuthenticated ? 'Start Chatting' : 'Get Started Free'}
            </Button>
          </Box>
        </Container>
      </Box>
    </Box>
  );
} 