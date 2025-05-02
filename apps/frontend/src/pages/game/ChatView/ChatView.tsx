import { useNavigate, useParams } from '@tanstack/react-router';
import { useLatestScene } from '@/services/api/hooks/useLatestScene';
import { useState } from 'react';

import Input from '@/common/components/Input/Input';
import Button from '@/common/components/Button/Button';
import { useScene } from '@/common/hooks/useScene';
import { useMessages } from '@/common/hooks/useMessages';

import styles from './ChatView.module.scss';

const Chat = () => {
  const { storyId, sceneId, characterId } = useParams({
    from: '/play/$storyId/scenes/$sceneId/characters/$characterId',
  });

  const navigate = useNavigate();
  const { data: scene, isLoading: isLoadingScene, error } = useLatestScene(storyId);
  const [message, setMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);

  // Setup scene and real-time messaging with WebSocket
  const { sendMessage, isConnected: wsConnected } = useScene({
    sceneId,
    characterId,
    onConnectionChange: setIsConnected,
  });

  const playerCharacter = scene?.characters.find((c) => c.role === 'player');
  const selectedCharacter = scene?.characters.find((c) => c.uuid === characterId);

  // Get messages that are updated in real-time by the WebSocket handler in useScene
  const { data: messages = [] } = useMessages(sceneId);

  const handleSendMessage = () => {
    if (message.trim()) {
      sendMessage(message);
      setMessage('');
    }
  };

  const handleBackToScene = () => {
    navigate({
      to: '/play/$storyId/scenes/$sceneId',
      params: { storyId, sceneId },
    });
  };

  if (isLoadingScene) {
    return (
      <div className={styles.loading}>
        <div className={styles.loadingSpinner}></div>
        <p>Loading your adventure...</p>
      </div>
    );
  }

  if (error || !scene) {
    return (
      <div className={styles.error}>
        <h2>Error loading scene</h2>
        <p>{error?.message || 'Unknown error'}</p>
        <Button onClick={() => navigate({ to: '/' })}>Return to Home</Button>
      </div>
    );
  }

  return (
    <div
      className={styles.gameView}
      style={
        scene.location?.image_dir
          ? {
              backgroundImage: `url(${scene.location.image_dir})`,
            }
          : undefined
      }
    >
      <div className={styles.gameContainer}>
        <div className={styles.topBar}>
          <Button onClick={handleBackToScene} className={styles.backButton} variant="secondary">
            ← Back to Scene
          </Button>
          {scene.location && <div className={styles.locationName}>{scene.location.name}</div>}
        </div>

        <div className={styles.characterSection}>
          {selectedCharacter && (
            <>
              <div className={styles.characterAvatar}>
                <img src={selectedCharacter.image_dir} alt={selectedCharacter.name} />
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
            <img src={playerCharacter?.image_dir} alt="You" />
          </div>

          {messages && messages.length > 0 && (
            <div className={styles.messageContainer}>
              {messages.slice(-2).map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={`${styles.message} ${
                    message.role === 'user' ? styles.userMessage : styles.assistantMessage
                  }`}
                >
                  {message.content}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className={styles.inputContainer}>
          <form onSubmit={handleSendMessage} className={styles.inputWrapper}>
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="What would you like to say..."
              fullWidth
            />
            <Button type="submit" disabled={!isConnected || !message.trim()}>
              Send
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Chat;
