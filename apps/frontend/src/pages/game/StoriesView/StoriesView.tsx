import { useState, useEffect } from 'react';
import { Box, Container, Paper, Typography, CircularProgress, List, ListItem, ListItemButton, ListItemText } from '@mui/material';
import { useNavigate } from '@tanstack/react-router';
import { apiClient } from '@/services/api/client';

// Define Story interface
interface Story {
  id: string;
  title: string;
  description: string;
}

const StoriesView = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStories = async () => {
      try {
        setIsLoading(true);
        const response = await apiClient.get<Story[]>('/api/stories/');
        setStories(response);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch stories:', err);
        setError('Failed to load stories. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchStories();
  }, []);

  const handleStoryClick = (storyId: string) => {
    navigate({ to: `/play/${storyId}` });
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Available Stories
      </Typography>
      
      <Paper elevation={3} sx={{ p: 2 }}>
        {stories.length === 0 ? (
          <Typography>No stories available.</Typography>
        ) : (
          <List>
            {stories.map((story) => (
              <ListItem key={story.id} disablePadding>
                <ListItemButton onClick={() => handleStoryClick(story.id)}>
                  <ListItemText 
                    primary={story.title}
                    secondary={story.description}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
    </Container>
  );
};

export default StoriesView;