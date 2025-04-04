import { ReactElement, useState, useEffect } from 'react';
import styles from './StoryGenerationView.module.scss';
import { StoryGenerationRequest, StoryGenerationState } from '@/services/api/hooks';
import StoryGenerationForm from './StoryGenerationForm';
import StoryGenerationLoading from './StoryGenerationLoading';
import StoryGenerationError from './StoryGenerationError';
import StoryGenerationCompleted from './StoryGenerationCompleted';
import { useStoryGeneration } from '@/services/api/hooks/useStoryGeneration';

const StoryGenerationView = (): ReactElement => {
  const [isEnabled, setIsEnabled] = useState(false);
  const [generationState, setGenerationState] = useState<StoryGenerationState>({
    status: 'idle',
    statusMessage: 'Ready to generate story',
  });
    console.log(generationState)
  // Initialize the hook with state change callback
  const { generateStory, reset } = useStoryGeneration({
    onStateChange: (newState) => setGenerationState(newState),
    enabled: isEnabled
  });
  
  const handleGenerateStory = (data: StoryGenerationRequest) => {
    setIsEnabled(true);
    generateStory(data);
  };
  
  const handleReset = () => {
    reset();
  };
  
  return (
    <div className={styles.container}>
      {generationState.status === 'idle' && (
        <StoryGenerationForm onSubmit={handleGenerateStory} />
      )}
      
      {(generationState.status === 'connecting' || generationState.status === 'generating') && (
        <StoryGenerationLoading message={generationState.statusMessage} />
      )}
      
      {generationState.status === 'error' && (
        <StoryGenerationError 
          errorMessage={generationState.errorMessage || 'Unknown error'} 
          onReset={handleReset}
        />
      )}
      
      {generationState.status === 'complete' && (
        <StoryGenerationCompleted
          world={generationState.world}
          character={generationState.character}
          onReset={handleReset}
        />
      )}
    </div>
  );
};

export default StoryGenerationView; 