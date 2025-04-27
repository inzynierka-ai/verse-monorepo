import { gameRoute } from '@/router';
import { useNavigate } from '@tanstack/react-router';
import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/services/api/client';
import SceneGenerationView from './SceneGenerationView';
import { Scene } from '@/types/scene.types';
import { Container } from '@/common/components/Container/Container';
import { Card } from '@/common/components/Card/Card';
import Input from '@/common/components/Input/Input';
import Button from '@/common/components/Button/Button';

import styles from './GameView.module.scss';

const GameView = () => {
  const { storyId } = gameRoute.useParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [currentScene, setCurrentScene] = useState<Scene | null>(null);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [needsGeneration, setNeedsGeneration] = useState(false);

  const handleSceneComplete = useCallback((scene: Scene) => {
    console.log('Scene generation complete:', scene);
    setCurrentScene(scene);
    setNeedsGeneration(false);
  }, []);

  useEffect(() => {
    const fetchLatestScene = async () => {
      if (!storyId) return;
      setIsLoading(true);
      setFetchError(null);
      setNeedsGeneration(false);
      setCurrentScene(null);

      try {
        const latestScene = await apiClient.get<Scene>(`/game/stories/${storyId}/scene/latest`);
        setCurrentScene(latestScene);
        setNeedsGeneration(false);
      } catch (error: any) {
        if (error.message?.includes('404')) {
          console.log('No existing scene found, need to generate.');
          setNeedsGeneration(true);
        } else {
          console.error('Error fetching latest scene:', error);
          setFetchError(error.message || 'Failed to fetch scene data.');
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchLatestScene();
  }, [storyId]);

  const handleSendMessage = () => {
    if (message.trim() && storyId && currentScene) {
      console.log('Sending message:', message);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <div className={styles.loadingSpinner}></div>
        <p>Loading your adventure...</p>
      </div>
    );
  }

  if (fetchError && !needsGeneration) {
    return (
      <div className={styles.error}>
        <h2>Error loading scene</h2>
        <p>{fetchError}</p>
        <Button onClick={() => navigate({ to: '/' })}>Return to Home</Button>
      </div>
    );
  }

  if (needsGeneration) {
    return (
      <SceneGenerationView
        storyId={storyId}
        onSceneComplete={handleSceneComplete}
        startGeneration={() => {
          console.log('GameView instructing SceneGenerationView to start generation.');
        }}
      />
    );
  }

  if (!currentScene) {
    return (
      <div className={styles.error}>
        <h2>Error</h2>
        <p>Scene data is missing.</p>
        <Button onClick={() => navigate({ to: '/' })}>Return to Home</Button>
      </div>
    );
  }

  const selectedCharacter = currentScene.characters?.[0];

  return (
    <div
      className={styles.gameView}
      style={
        currentScene.location?.imageUrl ? { backgroundImage: `url(${currentScene.location.imageUrl})` } : undefined
      }
    >
      <div className={styles.gameContainer}>
        <div className={styles.locationInfo}>
          <Card>
            <h2>{currentScene.location?.name || 'Unknown Location'}</h2>
            <p>{currentScene.description || 'No description available.'}</p>
          </Card>
        </div>

        <div className={styles.characterInfo}>
          <Card>
            {selectedCharacter ? (
              <>
                <div className={styles.characterHeader}>
                  <img src={selectedCharacter.imageUrl} alt={selectedCharacter.name} className={styles.avatar} />
                  <h2>{selectedCharacter.name}</h2>
                </div>
                <p>{selectedCharacter.description || 'No description available'}</p>
              </>
            ) : (
              <p>No character information available</p>
            )}
            {currentScene.characters && currentScene.characters.length > 1 && (
              <div>
                <h3>Other Characters:</h3>
                <ul>
                  {currentScene.characters.slice(1).map((char) => (
                    <li key={char.uuid}>{char.name}</li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        </div>

        <div className={styles.messagesContainer}>
          <div className={styles.emptyMessages}>
            <p>Chat functionality needs to be implemented separately.</p>
          </div>
        </div>

        <div className={styles.inputContainer}>
          <div className={styles.connectionStatus}>
            <span className={styles.disconnected}>Chat Disconnected</span>
          </div>
          <div className={styles.inputWrapper}>
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={'Type your message...'}
              fullWidth
              disabled={false}
            />
            <Button onClick={handleSendMessage} disabled={!message.trim()}>
              Send
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameView;
