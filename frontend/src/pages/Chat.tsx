/**
 * Chat page component for the Lean Six Sigma RAG Chatbot.
 * 
 * Features:
 * - Message input and history
 * - Query limit tracking
 * - Markdown rendering
 * - Responsive design
 */

import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  CircularProgress,
  Alert,
  LinearProgress,
  Card,
  CardContent,
  useTheme,
  Snackbar,
} from '@mui/material';
import { Send as SendIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { sendMessage, getRemainingQueries, getChatHistory, ChatHistoryItem } from '../services/chat';
import { useAuth } from '../hooks/useAuth';

interface ChatMessageType extends Omit<ChatHistoryItem, 'created_at'> {
  type: 'user' | 'bot';
  timestamp: Date;
}

export default function Chat() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessageType[]>([]);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { token } = useAuth();
  const theme = useTheme();
  const queryClient = useQueryClient();

  // Get remaining queries
  const { data: queryLimit, isError: isQueryLimitError } = useQuery({
    queryKey: ['remainingQueries'],
    queryFn: getRemainingQueries,
    refetchInterval: 60000, // Refresh every minute
  });

  // Get chat history
  const { data: historicalMessages, isLoading: isLoadingHistory } = useQuery({
    queryKey: ['chatHistory'],
    queryFn: getChatHistory,
    onSuccess: (data) => {
      const formattedHistory = data.map((msg) => ({
        id: msg.id,
        type: 'bot' as const,
        query: msg.query,
        response: msg.response,
        timestamp: new Date(msg.created_at),
      }));
      setChatHistory(formattedHistory);
    },
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: sendMessage,
    onSuccess: (data) => {
      // Add bot response to chat history
      const botMessage: ChatMessageType = {
        id: data.history_id,
        type: 'bot',
        query: message,
        response: data.response,
        timestamp: new Date(),
      };
      setChatHistory((prev) => [...prev, botMessage]);
      
      // Update remaining queries
      queryClient.setQueryData(['remainingQueries'], data.remaining_queries);
      
      // Clear any existing error
      setError(null);
    },
    onError: (error: Error) => {
      setError(error.message);
    },
  });

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim()) return;

    // Add user message to chat history
    const userMessage: ChatMessageType = {
      id: Date.now(), // Temporary ID
      type: 'user',
      query: message,
      response: message, // For user messages, response is the same as query
      timestamp: new Date(),
    };
    setChatHistory((prev) => [...prev, userMessage]);
    
    // Clear input
    setMessage('');

    // Send message to API
    sendMessageMutation.mutate({ query: message });
  };

  const handleErrorClose = () => {
    setError(null);
  };

  if (isLoadingHistory) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      {/* Query limit indicator */}
      {queryLimit && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Daily Queries Remaining: {queryLimit.daily_queries_remaining} / {queryLimit.daily_queries_limit}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={(queryLimit.daily_queries_remaining / queryLimit.daily_queries_limit) * 100}
            sx={{ height: 8, borderRadius: 4 }}
          />
        </Paper>
      )}

      {/* Query limit error */}
      {isQueryLimitError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Unable to fetch query limit information
        </Alert>
      )}

      {/* Chat messages */}
      <Paper
        sx={{
          flex: 1,
          mb: 2,
          p: 2,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        {chatHistory.map((msg) => (
          <Card
            key={msg.id}
            sx={{
              alignSelf: msg.type === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
              bgcolor: msg.type === 'user' ? 'primary.main' : 'background.paper',
            }}
          >
            <CardContent>
              <Typography
                variant="body1"
                color={msg.type === 'user' ? 'primary.contrastText' : 'text.primary'}
              >
                {msg.type === 'bot' ? (
                  <ReactMarkdown>{msg.response}</ReactMarkdown>
                ) : (
                  msg.query
                )}
              </Typography>
              <Typography
                variant="caption"
                color={msg.type === 'user' ? 'primary.contrastText' : 'text.secondary'}
                sx={{ opacity: 0.7, mt: 1, display: 'block' }}
              >
                {msg.timestamp.toLocaleTimeString()}
              </Typography>
            </CardContent>
          </Card>
        ))}
        
        {sendMessageMutation.isPending && (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Paper>

      {/* Message input */}
      <Paper
        component="form"
        onSubmit={handleSubmit}
        sx={{
          p: 2,
          display: 'flex',
          gap: 2,
          alignItems: 'center',
        }}
      >
        <TextField
          fullWidth
          placeholder="Ask about Lean Six Sigma..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={sendMessageMutation.isPending}
          multiline
          maxRows={4}
          sx={{ flex: 1 }}
        />
        <IconButton
          type="submit"
          color="primary"
          disabled={!message.trim() || sendMessageMutation.isPending}
        >
          <SendIcon />
        </IconButton>
      </Paper>

      {/* Error snackbar */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={handleErrorClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleErrorClose} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
} 