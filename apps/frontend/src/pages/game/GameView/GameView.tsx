import { gameRoute } from '@/router';
import { useNavigate } from '@tanstack/react-router';
import { useLatestScene } from '@/services/api/hooks/useLatestScene';
import { useState, useEffect } from 'react';
import { Container } from '@/common/components/Container/Container';
import { Card } from '@/common/components/Card/Card';
import Input from '@/common/components/Input/Input';
import Button from '@/common/components/Button/Button';
import { useScene } from '@/common/hooks/useScene';
import { useTheme, extractColorsFromImage } from '@/common/hooks/useTheme';

import styles from './GameView.module.scss';

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
  themeType?: 'library' | 'forest' | 'castle' | 'cave' | 'beach' | 'space';
}

const GameView = () => {
  const { storyId } = gameRoute.useParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const { applyTheme, applyCustomTheme } = useTheme();
  
  // Fetch the latest scene for this story
  const { data: scene, isLoading: isLoadingScene, error } = useLatestScene(storyId);
  
  // Select the first character from the scene for now (in a real app, you might let the user choose)
  const selectedCharacter = scene?.characters?.[0];
  
  // Setup scene and messages
  const { sendMessage, isConnected: wsConnected } = useScene({
    sceneId: scene?.id?.toString() || '',
    onConnectionChange: setIsConnected
  });
  
  useEffect(() => {
    // Apply theme based on location when scene loads
    console.log(scene?.location)
    if (scene?.location) {
      if (scene.location.themeType) {
        console.log(scene.location.themeType)
        // If the location has a predefined theme type, use it
        applyTheme(scene.location.themeType);
      } else if (scene.location.background) {
        // Otherwise extract colors from the background image
        extractColorsFromImage(scene.location.background)
          .then(colors => {
            applyCustomTheme(colors);
          })
          .catch(err => {
            console.error('Error extracting colors:', err);
            // Fallback to library theme
            applyTheme('library');
          });
      } else {
        // Fallback to library theme
        applyTheme('library');
      }
    }
  }, [scene?.location, applyTheme, applyCustomTheme]);
  
  const handleSendMessage = () => {
    if (message.trim() && scene?.id) {
      sendMessage(message);
      setMessage('');
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  if (isLoadingScene) {
    return (
      <Container>
        <div className={styles.loading}>
          <div className={styles.loadingSpinner}></div>
          <p>Loading your adventure...</p>
        </div>
      </Container>
    );
  }
  
  if (error || !scene) {
    return (
      <Container>
        <div className={styles.error}>
          <h2>Error loading scene</h2>
          <p>{error?.message || 'Unknown error'}</p>
          <Button onClick={() => navigate({ to: '/' })}>Return to Home</Button>
        </div>
      </Container>
    );
  }

  return (
    <div 
      className={styles.gameView}
      style={scene.location?.background ? { 
        backgroundImage: `url(${scene.location.background})` 
      } : undefined}
    >
      <div className={styles.gameContainer}>
        {scene.location && (
          <div className={styles.locationName}>
            {scene.location.name}
          </div>
        )}

        <div className={styles.characterSection}>
          {selectedCharacter && (
            <>
              <div className={styles.characterAvatar}>
                <img 
                  src={selectedCharacter.avatar} 
                  alt={selectedCharacter.name}
                />
              </div>
              <div className={styles.characterInfo}>
                <h2>{selectedCharacter.name}</h2>
                <p>{selectedCharacter.description}</p>
              </div>
            </>
          )}
        </div>

        <div className={styles.contentSection}>
          <div className={styles.userAvatar}>
            <img src="/me2.png" alt="You" />
          </div>

          {scene.messages && scene.messages.length > 0 && (
            <div className={styles.messageContainer}>
              {scene.messages.slice(-2).map((message, index) => (
                <div 
                  key={`${message.role}-${index}`}
                  className={`${styles.message} ${
                    message.role === 'user' 
                      ? styles.userMessage 
                      : styles.assistantMessage
                  }`}
                >
                  {message.content}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className={styles.inputContainer}>
          <div className={styles.inputWrapper}>
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="What would you like to say..."
              fullWidth
            />
            <Button 
              onClick={handleSendMessage} 
              disabled={!isConnected || !message.trim()}
            >
              Send
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameView;
