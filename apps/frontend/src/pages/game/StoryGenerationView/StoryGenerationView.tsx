import { ReactElement, useEffect, useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import styles from './StoryGenerationView.module.scss';
import { AdvancedStoryGenerationRequest, SimpleGameInput } from '@/services/api/hooks/useStoryGeneration';
import StoryGenerationForm from './StoryGenerationForm';
import SimpleStoryGenerationForm from './SimpleStoryGenerationForm';
import StoryGenerationLoading from './StoryGenerationLoading';
import StoryGenerationError from './StoryGenerationError';
import StoryGenerationCompleted from './StoryGenerationCompleted';
import { useStoryGeneration } from '@/services/api/hooks/useStoryGeneration';
import { useAuth } from '@/common/hooks/useAuth';
import { Container } from '@/common/components';

const StoryGenerationView = (): ReactElement => {
  const { isLoggedIn } = useAuth();
  const navigate = useNavigate();
  const [isSimpleMode, setIsSimpleMode] = useState(true);

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
      }, 1000); // Small delay to prevent flashing
      return () => clearTimeout(timer);
    }
  }, [isLoggedIn, navigate]);

  const { state: generationState, generateSimpleStory, generateAdvancedStory, reset } = useStoryGeneration();
  console.log(generationState);

  const handleAdvancedSubmit = (data: AdvancedStoryGenerationRequest) => {
    generateAdvancedStory(data);
  };

  const handleSimpleSubmit = (data: SimpleGameInput) => {
    generateSimpleStory(data.story_description, data.character_description);
  };

  const handleReset = () => {
    reset();
  };

  const toggleMode = () => {
    setIsSimpleMode(!isSimpleMode);
  };

  // Show loading indicator rather than nothing
  if (!isLoggedIn) {
    return <div className={styles.container}>Checking authentication...</div>;
  }

  return (
    <Container>
      {generationState.status === 'idle' && (
        <>
          <div className={styles.modeToggle}>
            <label className={styles.switch}>
              <input type="checkbox" checked={isSimpleMode} onChange={toggleMode} />
              <span className={styles.slider}></span>
            </label>
            <span>{isSimpleMode ? 'Simple Mode' : 'Advanced Mode'}</span>
          </div>

          {isSimpleMode ? (
            <SimpleStoryGenerationForm onSubmit={handleSimpleSubmit} />
          ) : (
            <StoryGenerationForm onSubmit={handleAdvancedSubmit} />
          )}
        </>
      )}

      {(generationState.status === 'connecting' || generationState.status === 'generating') && (
        <StoryGenerationLoading message={generationState.statusMessage} />
      )}

      {generationState.status === 'error' && (
        <StoryGenerationError errorMessage={generationState.errorMessage || 'Unknown error'} onReset={handleReset} />
      )}

      {generationState.status === 'complete' && (
        <StoryGenerationCompleted
          story={generationState.story}
          character={generationState.character}
          onReset={handleReset}
        />
      )}
    </Container>
  );
};

export default StoryGenerationView;
