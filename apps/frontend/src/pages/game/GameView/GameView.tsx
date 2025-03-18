import { gameRoute } from '@/router';
import { useNavigate } from '@tanstack/react-router';
import { useLatestScene } from '@/services/api/hooks/useLatestScene';
import { useState } from 'react';
import { Container } from '@/common/components/Container/Container';
import { Card } from '@/common/components/Card/Card';
import Input from '@/common/components/Input/Input';
import Button from '@/common/components/Button/Button';
import { useScene } from '@/common/hooks/useScene';

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
}

const GameView = () => {
  const { storyId } = gameRoute.useParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  
  // Fetch the latest scene for this story
  const { data: scene, isLoading: isLoadingScene, error } = useLatestScene(storyId);
  
  // Select the first character from the scene for now (in a real app, you might let the user choose)
  const selectedCharacter = scene?.characters?.[0];
  
  // Setup scene and messages
  const { sendMessage, isConnected: wsConnected } = useScene({
    sceneId: scene?.id?.toString() || '',
    onConnectionChange: setIsConnected
  });
  
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
      <Container>
        <div className={styles.gameContainer}>
          {/* Location information */}
          <div className={styles.locationInfo}>
            <Card>
              <h2>{scene.location?.name || 'Unknown Location'}</h2>
              <p>{scene.location?.description || 'No description available'}</p>
            </Card>
          </div>
          
          {/* Character information */}
          <div className={styles.characterInfo}>
            <Card>
              {selectedCharacter ? (
                <>
                  <div className={styles.characterHeader}>
                    <img 
                      src={selectedCharacter.avatar} 
                      alt={selectedCharacter.name} 
                      className={styles.avatar}
                    />
                    <h2>{selectedCharacter.name}</h2>
                  </div>
                  <p>{selectedCharacter.description || 'No description available'}</p>
                </>
              ) : (
                <p>No character information available</p>
              )}
            </Card>
          </div>
          
          {/* Message display area */}
          <div className={styles.messagesContainer}>
            {scene.messages && scene.messages.length > 0 ? (
              <div className={styles.messages}>
                {scene.messages.map((msg, index) => (
                  <div 
                    key={index} 
                    className={`${styles.message} ${msg.role === 'user' ? styles.userMessage : styles.assistantMessage}`}
                  >
                    <div className={styles.messageContent}>{msg.content}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className={styles.emptyMessages}>
                <p>Your adventure awaits. Send a message to begin...</p>
              </div>
            )}
          </div>
          
          {/* Message input area */}
          <div className={styles.inputContainer}>
            <div className={styles.connectionStatus}>
              {isConnected ? 
                <span className={styles.connected}>Connected</span> : 
                <span className={styles.disconnected}>Disconnected</span>
              }
            </div>
            <div className={styles.inputWrapper}>
              <Input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your message..."
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
      </Container>
    </div>
  );
};

export default GameView;
