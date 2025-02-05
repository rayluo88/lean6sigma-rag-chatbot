/**
 * Mobile navigation component.
 * 
 * This component provides:
 * - Mobile-optimized navigation menu
 * - Close handler for the mobile drawer
 * - Same navigation items as desktop but with mobile-friendly layout
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
  IconButton,
} from '@mui/material';
import {
  Home as HomeIcon,
  Chat as ChatIcon,
  Description as DocsIcon,
  AccountCircle as ProfileIcon,
  Login as LoginIcon,
  PersonAdd as RegisterIcon,
  Close as CloseIcon,
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

interface MobileNavigationProps {
  onClose: () => void;
}

export default function MobileNavigation({ onClose }: MobileNavigationProps) {
  const { isAuthenticated } = useAuth();

  return (
    <div>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Typography variant="h6" noWrap component="div">
          Menu
        </Typography>
        <IconButton onClick={onClose}>
          <CloseIcon />
        </IconButton>
      </Toolbar>
      <Divider />
      <List>
        {/* Public Routes */}
        <ListItem button component={RouterLink} to="/" onClick={onClose}>
          <ListItemIcon>
            <HomeIcon />
          </ListItemIcon>
          <ListItemText primary="Home" />
        </ListItem>

        <ListItem button component={RouterLink} to="/documentation" onClick={onClose}>
          <ListItemIcon>
            <DocsIcon />
          </ListItemIcon>
          <ListItemText primary="Documentation" />
        </ListItem>

        {/* Authentication Routes */}
        {!isAuthenticated ? (
          <>
            <ListItem button component={RouterLink} to="/login" onClick={onClose}>
              <ListItemIcon>
                <LoginIcon />
              </ListItemIcon>
              <ListItemText primary="Login" />
            </ListItem>
            <ListItem button component={RouterLink} to="/register" onClick={onClose}>
              <ListItemIcon>
                <RegisterIcon />
              </ListItemIcon>
              <ListItemText primary="Register" />
            </ListItem>
          </>
        ) : (
          <>
            <ListItem button component={RouterLink} to="/chat" onClick={onClose}>
              <ListItemIcon>
                <ChatIcon />
              </ListItemIcon>
              <ListItemText primary="Chat" />
            </ListItem>
            <ListItem button component={RouterLink} to="/profile" onClick={onClose}>
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