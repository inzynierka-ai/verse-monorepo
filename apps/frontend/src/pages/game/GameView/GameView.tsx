import { gameRoute } from '@/router';
import { useNavigate } from '@tanstack/react-router';
import { useState, useCallback, useEffect } from 'react';
import SceneGenerationView from './SceneGenerationView';
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

  const handleSceneComplete = useCallback(() => {
    // Invalidate the query to fetch the latest scene
    queryClient.invalidateQueries({ queryKey: ['latest-scene', storyId] });
    setGenerationStarted(false);
  }, [queryClient, storyId]);

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

  useEffect(() => {
    // Navigate when a scene is loaded and conditions are appropriate
    if (currentScene) {
      if (storyId && currentScene.uuid) {
        navigate({
          to: '/play/$storyId/scenes/$sceneId',
          params: { storyId, sceneId: currentScene.uuid },
          replace: true,
        });
      } else {
        console.error('Missing storyId or scene UUID for navigation', { storyId, sceneUuid: currentScene?.uuid });
      }
    }
  }, [currentScene, storyId, navigate]);

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
    return <SceneGenerationView storyId={storyId} onSceneComplete={handleSceneComplete} />;
  }

  if (currentScene) {
    return (
      <div className={styles.loading}>
        <div className={styles.loadingSpinner}></div>
        <p>Redirecting to scene...</p>
      </div>
    );
  }

  return (
    <div className={styles.error}>
      <h2>No Scene Available</h2>
      <p>Could not find an active scene for your adventure. Please try returning home.</p>
      <Button onClick={() => navigate({ to: '/' })}>Return to Home</Button>
    </div>
  );
};

export default GameView;
