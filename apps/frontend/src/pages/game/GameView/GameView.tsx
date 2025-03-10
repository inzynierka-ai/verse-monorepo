import { Box, Container, Paper, Typography, CircularProgress } from '@mui/material';
import { useCharacter } from '@/services/api/hooks/useCharacter';
import { useLocation } from '@/services/api/hooks/useLocation';
import Chat from '../Chat/Chat';
import { gameRoute } from '@/router';
import { useScene } from '@/services/api/hooks/useScene';

const GameView = () => {
  const { storyId, chapterId, sceneId } = gameRoute.useParams();
  
  const { data: scene, isLoading: isLoadingScene } = useScene(sceneId);
  const { data: character, isLoading: isLoadingCharacter } = useCharacter('1');
  const { data: location, isLoading: isLoadingLocation } = useLocation(scene?.location_id);

  if (isLoadingCharacter || isLoadingLocation) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!character || !location) return null;

  return (
    <Box
      sx={{
        height: '100vh',
        backgroundImage: `url(${location.background})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <Container maxWidth="lg" sx={{ height: '100%', py: 2 }}>
        <Box display="flex" gap={2} height="100%">
          <Paper elevation={3} sx={{ p: 2, minWidth: 200 }}>
            <Box
              component="img"
              src={character.avatar}
              alt={character.name}
              sx={{ width: '100%', borderRadius: 1 }}
            />
            <Typography variant="h6" mt={2}>
              {character.name}
            </Typography>
          </Paper>
          <Box flex={1}>
            <Chat uuid={sceneId} />
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

export default GameView;
