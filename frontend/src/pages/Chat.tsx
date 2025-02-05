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
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { sendMessage, getRemainingQueries, ChatResponse } from '../services/chat';
import { useAuth } from '../hooks/useAuth';

interface ChatMessageType {
  id: number;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

export default function Chat() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessageType[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { token } = useAuth();
  const theme = useTheme();
  const queryClient = useQueryClient();

  // Get remaining queries
  const { data: queryLimit } = useQuery({
    queryKey: ['remainingQueries'],
    queryFn: getRemainingQueries,
    refetchInterval: 60000, // Refresh every minute
  });

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: sendMessage,
    onSuccess: (data) => {
      // Add bot response to chat history
      const botMessage: ChatMessageType = {
        id: chatHistory.length + 2,
        type: 'bot',
        content: data.response,
        timestamp: new Date(),
      };
      setChatHistory((prev) => [...prev, botMessage]);
      
      // Update remaining queries
      queryClient.setQueryData(['remainingQueries'], data.remaining_queries);
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
      id: chatHistory.length + 1,
      type: 'user',
      content: message,
      timestamp: new Date(),
    };
    setChatHistory((prev) => [...prev, userMessage]);
    
    // Clear input
    setMessage('');

    // Send message to API
    sendMessageMutation.mutate({ query: message });
  };

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
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
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
        
        {sendMessageMutation.isError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {sendMessageMutation.error.message}
          </Alert>
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
    </Box>
  );
} 