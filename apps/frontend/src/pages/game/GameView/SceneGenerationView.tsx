import { useSceneGeneration, SceneGenerationState } from '@/services/api/hooks/useSceneGeneration';
import { Scene } from '@/types/scene.types';
import Button from '@/common/components/Button/Button';
import Card from '@/common/components/Card/Card';
import styles from './SceneGenerationView.module.scss';
import { useEffect } from 'react';

interface SceneGenerationViewProps {
  storyId: string;
  onSceneComplete: (scene: Scene) => void;
  startGeneration: () => void; // Prop to trigger the generation start
}

const SceneGenerationView = ({ storyId, onSceneComplete, startGeneration }: SceneGenerationViewProps) => {
  console.log(storyId);
  const {
    state,
    start,
    reset: resetSceneGeneration,
    isConnected,
  } = useSceneGeneration({
    storyId: storyId,
    onConnectionChange: (connected) => {
      console.log('Scene generation WS connected:', connected);
    },
  });

  // Trigger generation when the component mounts
  useEffect(() => {
    if (isConnected) {
      console.log('Starting scene generation...');
      start();
    }
  }, [isConnected]);

  // Effect to call onSceneComplete when generation finishes
  useEffect(() => {
    if (state.status === 'complete' && state.scene) {
      // Map SceneCompletePayload to Scene type if necessary
      // Assuming state.scene directly matches the Scene type for now
      onSceneComplete(state.scene as Scene);
    }
  }, [state.status, state.scene, onSceneComplete]);

  // --- Loading/Connecting State ---
  if (state.status === 'connecting') {
    return (
      <div className={styles.container}>
        <div className={styles.connectionStatus}>
          <div className={styles.loadingSpinner}></div>
          <p>Connecting to story server...</p>
        </div>
      </div>
    );
  }

  // --- Generating State ---
  if (state.status === 'generating') {
    return (
      <div className={styles.container}>
        <div className={styles.generationHeader}>
          <div className={styles.loadingSpinner}></div>
          <h2>Creating your adventure...</h2>
          {Object.keys(state.actions).length > 0 && (
            <div className={styles.actionsContainer}>
              {Object.entries(state.actions).map(([actionType, actionMessage]) => (
                <p key={actionType} className={styles.actionItem}>
                  {actionMessage}
                </p>
              ))}
            </div>
          )}
        </div>

        <div className={styles.generationProgress}>
          {state.lastLocation && (
            <div className={styles.locationSection}>
              <h3>Location Discovered</h3>
              <Card className={styles.locationCard}>
                {state.lastLocation.imageUrl && (
                  <div className={styles.imageContainer}>
                    <img
                      src={state.lastLocation.imageUrl}
                      alt={state.lastLocation.name}
                      className={styles.locationImage}
                    />
                  </div>
                )}
                <div className={styles.locationInfo}>
                  <h4>{state.lastLocation.name}</h4>
                  <p>{state.lastLocation.description}</p>
                </div>
              </Card>
            </div>
          )}

          {state.lastCharacters.length > 0 && (
            <div className={styles.charactersSection}>
              <h3>Characters Present</h3>
              <div className={styles.charactersGrid}>
                {state.lastCharacters.map((char) => (
                  <Card key={char.uuid} className={styles.characterCard}>
                    {char.imageUrl && (
                      <div className={styles.imageContainer}>
                        <img src={char.imageUrl} alt={char.name} className={styles.characterImage} />
                      </div>
                    )}
                    <div className={styles.characterInfo}>
                      <h4>{char.name}</h4>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // --- Error State ---
  if (state.status === 'error') {
    return (
      <div className={styles.container}>
        <div className={styles.errorSection}>
          <h2>Error generating scene</h2>
          <p>{state.error || 'An unknown error occurred.'}</p>
          <Button onClick={resetSceneGeneration}>Try Again</Button>
        </div>
      </div>
    );
  }

  // --- Idle State (before generation starts or after reset) ---
  if (state.status === 'idle') {
    return (
      <div className={styles.container}>
        <div className={styles.idleState}>
          <p>Preparing scene generation...</p>
        </div>
      </div>
    );
  }

  // Render nothing once complete, as the parent will take over
  return null;
};

export default SceneGenerationView;
