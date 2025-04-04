import { ReactElement } from 'react';
import styles from './StoryGenerationView.module.scss';
import { StoryGenerationRequest } from '@/services/api/hooks';
import StoryGenerationForm from './StoryGenerationForm';
import StoryGenerationLoading from './StoryGenerationLoading';
import StoryGenerationError from './StoryGenerationError';
import StoryGenerationCompleted from './StoryGenerationCompleted';
import { useStoryGeneration } from '@/services/api/hooks/useStoryGeneration';

const StoryGenerationView = (): ReactElement => {
  
  // Use the hook's internal state directly
  const { state: generationState, generateStory, reset } = useStoryGeneration();
  
  const handleGenerateStory = (data: StoryGenerationRequest) => {
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