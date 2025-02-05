/**
 * Documentation page component for the Lean Six Sigma RAG Chatbot.
 * 
 * Features:
 * - Document list navigation
 * - Markdown content rendering
 * - Search functionality
 * - Responsive design
 */

import { useState } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemButton,
  TextField,
  Breadcrumbs,
  Link,
  Chip,
  CircularProgress,
  Alert,
  useTheme,
  useMediaQuery,
  Drawer,
  IconButton,
} from '@mui/material';
import {
  Search as SearchIcon,
  Menu as MenuIcon,
  Folder as FolderIcon,
  Description as FileIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { useQuery } from '@tanstack/react-query';
import { listDocuments, getDocumentContent, Document } from '../services/docs';

export default function Documentation() {
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileOpen, setMobileOpen] = useState(false);
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Fetch document list
  const { data: documents, isLoading: isLoadingDocs, error: docsError } = useQuery({
    queryKey: ['documents'],
    queryFn: listDocuments,
  });

  // Fetch selected document content
  const { data: docContent, isLoading: isLoadingContent } = useQuery({
    queryKey: ['document', selectedDoc],
    queryFn: () => getDocumentContent(selectedDoc!),
    enabled: !!selectedDoc,
  });

  // Filter documents based on search query
  const filteredDocs = documents?.filter((doc) => {
    const searchLower = searchQuery.toLowerCase();
    return (
      doc.title.toLowerCase().includes(searchLower) ||
      doc.category.toLowerCase().includes(searchLower) ||
      doc.tags.some((tag) => tag.toLowerCase().includes(searchLower))
    );
  });

  // Group documents by category
  const groupedDocs = filteredDocs?.reduce((acc, doc) => {
    if (!acc[doc.category]) {
      acc[doc.category] = [];
    }
    acc[doc.category].push(doc);
    return acc;
  }, {} as Record<string, Document[]>);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const documentsList = (
    <Box sx={{ width: '100%', maxWidth: 360 }}>
      <Box sx={{ p: 2 }}>
        <TextField
          fullWidth
          placeholder="Search documentation..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />,
          }}
          size="small"
        />
      </Box>
      
      {isLoadingDocs ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : docsError ? (
        <Alert severity="error" sx={{ m: 2 }}>
          Failed to load documentation
        </Alert>
      ) : (
        <List component="nav">
          {groupedDocs && Object.entries(groupedDocs).map(([category, docs]) => (
            <Box key={category}>
              <ListItem>
                <ListItemText
                  primary={category}
                  primaryTypographyProps={{
                    variant: 'subtitle2',
                    color: 'primary',
                    fontWeight: 'bold',
                  }}
                />
              </ListItem>
              {docs.map((doc) => (
                <ListItemButton
                  key={doc.path}
                  selected={selectedDoc === doc.path}
                  onClick={() => {
                    setSelectedDoc(doc.path);
                    if (isMobile) {
                      setMobileOpen(false);
                    }
                  }}
                  sx={{ pl: 4 }}
                >
                  <FileIcon sx={{ mr: 1, fontSize: 20, color: 'action.active' }} />
                  <ListItemText
                    primary={doc.title}
                    secondary={doc.subcategory}
                    primaryTypographyProps={{
                      variant: 'body2',
                    }}
                    secondaryTypographyProps={{
                      variant: 'caption',
                    }}
                  />
                </ListItemButton>
              ))}
            </Box>
          ))}
        </List>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100%' }}>
      {/* Mobile drawer toggle */}
      {isMobile && (
        <IconButton
          color="inherit"
          aria-label="open drawer"
          edge="start"
          onClick={handleDrawerToggle}
          sx={{ position: 'fixed', left: 16, top: 72, zIndex: 1100 }}
        >
          <MenuIcon />
        </IconButton>
      )}

      {/* Sidebar */}
      {isMobile ? (
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            '& .MuiDrawer-paper': {
              width: 320,
              mt: '64px', // Account for AppBar
              height: 'calc(100% - 64px)',
            },
          }}
        >
          {documentsList}
        </Drawer>
      ) : (
        <Box
          component="nav"
          sx={{
            width: 320,
            flexShrink: 0,
            borderRight: 1,
            borderColor: 'divider',
          }}
        >
          {documentsList}
        </Box>
      )}

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - 320px)` },
          ml: { xs: 0, md: '320px' },
        }}
      >
        {selectedDoc && docContent ? (
          <Paper sx={{ p: 4 }}>
            <Typography variant="h4" gutterBottom>
              {docContent.metadata.title}
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Breadcrumbs>
                <Link color="inherit" href="#">
                  {docContent.metadata.category}
                </Link>
                {docContent.metadata.subcategory && (
                  <Link color="inherit" href="#">
                    {docContent.metadata.subcategory}
                  </Link>
                )}
                <Typography color="text.primary">
                  {docContent.metadata.title}
                </Typography>
              </Breadcrumbs>
            </Box>

            {docContent.metadata.tags && (
              <Box sx={{ mb: 3 }}>
                {docContent.metadata.tags.map((tag) => (
                  <Chip
                    key={tag}
                    label={tag}
                    size="small"
                    sx={{ mr: 1, mb: 1 }}
                  />
                ))}
              </Box>
            )}

            <Box sx={{ mt: 4 }}>
              <ReactMarkdown>{docContent.content}</ReactMarkdown>
            </Box>

            <Box sx={{ mt: 4, pt: 2, borderTop: 1, borderColor: 'divider' }}>
              <Typography variant="caption" color="text.secondary">
                Last updated: {docContent.metadata.last_updated}
              </Typography>
            </Box>
          </Paper>
        ) : (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              minHeight: '50vh',
            }}
          >
            {isLoadingContent ? (
              <CircularProgress />
            ) : (
              <>
                <FolderIcon sx={{ fontSize: 64, color: 'action.active', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  Select a document to view its content
                </Typography>
              </>
            )}
          </Box>
        )}
      </Box>
    </Box>
  );
} 