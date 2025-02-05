/**
 * Navigation component for desktop view.
 * 
 * This component provides:
 * - Main navigation links
 * - Authentication status-based navigation
 * - User profile section
 */

import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Toolbar,
  Typography,
} from '@mui/material';
import {
  Home as HomeIcon,
  Chat as ChatIcon,
  Description as DocsIcon,
  AccountCircle as ProfileIcon,
  Login as LoginIcon,
  PersonAdd as RegisterIcon,
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export default function Navigation() {
  const { isAuthenticated } = useAuth();

  return (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Menu
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {/* Public Routes */}
        <ListItem button component={RouterLink} to="/">
          <ListItemIcon>
            <HomeIcon />
          </ListItemIcon>
          <ListItemText primary="Home" />
        </ListItem>

        <ListItem button component={RouterLink} to="/documentation">
          <ListItemIcon>
            <DocsIcon />
          </ListItemIcon>
          <ListItemText primary="Documentation" />
        </ListItem>

        {/* Authentication Routes */}
        {!isAuthenticated ? (
          <>
            <ListItem button component={RouterLink} to="/login">
              <ListItemIcon>
                <LoginIcon />
              </ListItemIcon>
              <ListItemText primary="Login" />
            </ListItem>
            <ListItem button component={RouterLink} to="/register">
              <ListItemIcon>
                <RegisterIcon />
              </ListItemIcon>
              <ListItemText primary="Register" />
            </ListItem>
          </>
        ) : (
          <>
            <ListItem button component={RouterLink} to="/chat">
              <ListItemIcon>
                <ChatIcon />
              </ListItemIcon>
              <ListItemText primary="Chat" />
            </ListItem>
            <ListItem button component={RouterLink} to="/profile">
              <ListItemIcon>
                <ProfileIcon />
              </ListItemIcon>
              <ListItemText primary="Profile" />
            </ListItem>
          </>
        )}
      </List>
    </div>
  );
} 