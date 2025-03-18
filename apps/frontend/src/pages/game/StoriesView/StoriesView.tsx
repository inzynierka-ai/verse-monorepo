import { useState } from 'react';
import { Box, Container, Paper, Typography, CircularProgress, List, ListItem, ListItemButton, ListItemText } from '@mui/material';
import { useNavigate } from '@tanstack/react-router';
import { useStories } from '@/hooks/useStory';

const StoriesView = () => {
  const { data: stories = [], isLoading, error } = useStories();
  const navigate = useNavigate();

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
        <Typography color="error">Failed to load stories. Please try again later.</Typography>
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