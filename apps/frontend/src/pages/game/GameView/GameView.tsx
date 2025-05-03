import { gameRoute } from '@/router';
import { useNavigate } from '@tanstack/react-router';
import { useState, useCallback } from 'react';
import SceneGenerationView from './SceneGenerationView';
import { Scene } from '@/types/scene.types';
import Button from '@/common/components/Button/Button';
import { useLatestScene } from '@/services/api/hooks/useLatestScene';
import { useQueryClient } from '@tanstack/react-query';

import styles from './GameView.module.scss';

const GameView = () => {
  const { storyId } = gameRoute.useParams();
  console.log('storyId', storyId);
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const queryClient = useQueryClient();

  const { data: currentScene, isLoading, error, isError } = useLatestScene(storyId || '');

  // Determine if we need to generate a new scene
  // 404 error means no scene exists yet
  const errorMessage = error instanceof Error ? error.message : '';
  const needsGeneration = isError && errorMessage.includes('404');

  const handleSceneComplete = useCallback(
    (scene: Scene) => {
      console.log('Scene generation complete:', scene);
      // Invalidate the query to fetch the latest scene
      queryClient.invalidateQueries({ queryKey: ['latest-scene', storyId] });
    },
    [queryClient, storyId],
  );

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

  if (isError && !needsGeneration) {
    return (
      <div className={styles.error}>
        <h2>Error loading scene</h2>
        <p>{errorMessage || 'Failed to fetch scene data.'}</p>
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

  navigate({ to: '/play/$storyId/scenes/$sceneId', params: { storyId, sceneId: currentScene.uuid }, replace: true });
  return null;
};

export default GameView;
