import { ReactElement, useEffect } from 'react';
import { useNavigate } from '@tanstack/react-router';
import styles from './StoryGenerationView.module.scss';
import { StoryGenerationRequest } from '@/services/api/hooks';
import StoryGenerationForm from './StoryGenerationForm';
import StoryGenerationLoading from './StoryGenerationLoading';
import StoryGenerationError from './StoryGenerationError';
import StoryGenerationCompleted from './StoryGenerationCompleted';
import { useStoryGeneration } from '@/services/api/hooks/useStoryGeneration';
import { useAuth } from '@/common/hooks/useAuth';

const StoryGenerationView = (): ReactElement => {
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();
  
  // Add debug logging
  useEffect(() => {
    console.log('StoryGenerationView rendered, isLoggedIn:', isLoggedIn);
    console.log('Token in localStorage:', localStorage.getItem('auth-token'));
  }, [isLoggedIn]);
  
  // Delay the redirect slightly to prevent flash redirects
  useEffect(() => {
    if (!isLoggedIn) {
      console.log('Not logged in, redirecting to login page...');
      const timer = setTimeout(() => {
        navigate({ to: '/login' });
      }, 100); // Small delay to prevent flashing
      return () => clearTimeout(timer);
    }
  }, [isLoggedIn, navigate]);
  
  const { state: generationState, generateStory, reset } = useStoryGeneration();
  console.log(generationState);
  const handleGenerateStory = (data: StoryGenerationRequest) => {
    generateStory(data);
  };
  
  const handleReset = () => {
    reset();
  };
  
  // Show loading indicator rather than nothing
  if (!isLoggedIn) {
    return <div className={styles.container}>Checking authentication...</div>;
  }
  
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