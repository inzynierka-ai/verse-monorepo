import { useSceneGeneration, SceneGenerationState } from '@/services/api/hooks/useSceneGeneration';
import { Scene } from '@/types/scene.types';
import Button from '@/common/components/Button/Button';
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

  // --- Loading/Generating States ---
  if (state.status === 'connecting' || state.status === 'generating') {
    return (
      <div className={styles.loading}>
        <div className={styles.loadingSpinner}></div>
        <p>Generating scene...</p>
        {state.lastLocation && <p>Found Location: {state.lastLocation.name}</p>}
        {state.lastCharacters.length > 0 && (
          <div>
            <p>Added Characters:</p>
            <ul>
              {state.lastCharacters.map((char) => (
                <li key={char.uuid}>{char.name}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  // --- Error State ---
  if (state.status === 'error') {
    return (
      <div className={styles.error}>
        <h2>Error generating scene</h2>
        <p>{state.error || 'An unknown error occurred.'}</p>
        {/* Resetting will likely re-trigger the startGeneration effect if parent logic allows */}
        <Button onClick={resetSceneGeneration}>Try Again</Button>
      </div>
    );
  }

  // --- Idle State (before generation starts or after reset) ---
  if (state.status === 'idle') {
    return (
      <div className={styles.loading}>
        <p>Preparing scene generation...</p>
      </div>
    );
  }

  // Render nothing once complete, as the parent will take over
  return null;
};

export default SceneGenerationView;
