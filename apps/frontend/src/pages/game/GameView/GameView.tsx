import { useState, useEffect } from 'react';
import { Box, Container, Paper, Typography, CircularProgress, Button } from '@mui/material';
import { useCharacter } from '@/services/api/hooks/useCharacter';
import { useLocation } from '@/services/api/hooks/useLocation';
import Chat from '../Chat/Chat';
import { gameRoute } from '@/router';
import { useScene } from '@/services/api/hooks/useScene';
import { useNavigate } from '@tanstack/react-router';

// Simple state management for the game
interface GameState {
  chapterId: string | null;
  sceneId: string | null;
  characterId: string | null;
}

// Type definitions based on API returns
interface Character {
  id: string;
  name: string;
  avatar: string;
  description?: string;
}

interface Location {
  id: string;
  name: string;
  background: string;
  description?: string;
}

interface Scene {
  id: string;
  location_id: string;
  prompt?: string;
}

const GameView = () => {
  const { storyId } = gameRoute.useParams();
  const navigate = useNavigate();
  
  // State to track current game progress
  const [gameState, setGameState] = useState<GameState>({
    chapterId: null,
    sceneId: null,
    characterId: null,
  });
  
  // For demo purposes, we'll use a default scene and character
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // In a real implementation, you would fetch the player's current progress
    // for this story from an API
    const fetchGameState = async () => {
      try {
        // Simulate API call to get current game state
        setTimeout(() => {
          setGameState({
            chapterId: '1', // Default to first chapter
            sceneId: '1',   // Default to first scene
            characterId: '1' // Default character
          });
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Failed to load game state:', error);
        setLoading(false);
      }
    };
    
    fetchGameState();
  }, [storyId]);
  
  const { data: scene, isLoading: isLoadingScene } = useScene(gameState.sceneId || '1');
  const { data: character, isLoading: isLoadingCharacter } = useCharacter(gameState.characterId || '1');
  const { data: location, isLoading: isLoadingLocation } = useLocation(
    scene?.location_id ? String(scene.location_id) : '1'
  );


  if (loading || isLoadingCharacter || isLoadingLocation) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  // Provide default values if data is missing
  const characterData = character as Character || { 
    id: '1', 
    name: 'Unknown Character', 
    avatar: 'https://via.placeholder.com/150' 
  };
  
  const locationData = location as Location || { 
    id: '1', 
    name: 'Unknown Location', 
    background: 'https://via.placeholder.com/1200x800' 
  };

  return (
    <Box
      sx={{
        height: '100vh',
        backgroundImage: `url(${locationData.background})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <Container maxWidth="lg" sx={{ height: '100%', py: 2 }}>
        <Box display="flex" flexDirection="column" height="100%">
          <Box display="flex" justifyContent="space-between" mb={2}>
            <Typography variant="h4">Story: {storyId}</Typography>
          </Box>
          
          <Box display="flex" gap={2} height="100%">
            <Paper elevation={3} sx={{ p: 2, minWidth: 200 }}>
              <Box
                component="img"
                src={characterData.avatar}
                alt={characterData.name}
                sx={{ width: '100%', borderRadius: 1 }}
              />
              <Typography variant="h6" mt={2}>
                {characterData.name}
              </Typography>
              <Typography variant="body2" mt={1}>
                Location: {locationData.name}
              </Typography>
            </Paper>
            <Box flex={1}>
              {gameState.sceneId && (
                <Chat uuid={gameState.sceneId} />
              )}
            </Box>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default GameView;
