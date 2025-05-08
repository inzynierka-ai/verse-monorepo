import { gameRoute } from '@/router';
import { useNavigate } from '@tanstack/react-router';
import { useState, useCallback, useEffect } from 'react';
import SceneGenerationView from './SceneGenerationView';
import { Scene } from '@/types/scene.types';
import Button from '@/common/components/Button/Button';
import { useLatestScene } from '@/services/api/hooks/useLatestScene';
import { useQueryClient } from '@tanstack/react-query';

import styles from './GameView.module.scss';

const GameView = () => {
  const { storyId } = gameRoute.useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [generationStarted, setGenerationStarted] = useState(false);

  const { data: currentScene, isLoading, error, isError } = useLatestScene(storyId || '');

  // Determine if we need to generate a new scene
  // 404 error means no active scene exists yet (could be completed or not created yet)
  const errorMessage = error instanceof Error ? error.message : '';
  const needsGeneration = isError && errorMessage.includes('404');

  const handleSceneComplete = useCallback(
    (scene: Scene) => {
      // Invalidate the query to fetch the latest scene
      queryClient.invalidateQueries({ queryKey: ['latest-scene', storyId] });
      setGenerationStarted(false);
    },
    [queryClient, storyId],
  );

  const startGeneration = useCallback(() => {
    setGenerationStarted(true);
    console.log('Starting scene generation for story:', storyId);
  }, [storyId]);

  useEffect(() => {
    // Automatically start generation if needed and not already started
    if (needsGeneration && !generationStarted) {
      startGeneration();
    }
  }, [needsGeneration, generationStarted, startGeneration]);

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

  if (needsGeneration || generationStarted) {
    return (
      <SceneGenerationView storyId={storyId} onSceneComplete={handleSceneComplete} startGeneration={startGeneration} />
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
