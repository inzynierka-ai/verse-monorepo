import styles from './StoryGenerationView.module.scss';
import Button from '@/common/components/Button';

interface StoryGenerationErrorProps {
  errorMessage: string;
  onReset: () => void;
}

const StoryGenerationError = ({ errorMessage, onReset }: StoryGenerationErrorProps) => {
  return (
    <div className={styles.content}>
      <h1 className={styles.title}>Error</h1>
      <div className={styles.errorMessage}>
        {errorMessage || 'An unexpected error occurred while generating your story.'}
      </div>
      <div className={styles.buttonContainer}>
        <Button onClick={onReset} variant="secondary">
          Try Again
        </Button>
      </div>
    </div>
  );
};

export default StoryGenerationError; 