import styles from './StoryGenerationView.module.scss';

interface StoryGenerationLoadingProps {
  message: string;
}

const StoryGenerationLoading = ({ message }: StoryGenerationLoadingProps) => {
  return (
    <div className={styles.content}>
      <div className={styles.loadingContainer}>
        <div className={styles.loadingIndicator} />
        <h2>Generating Your Story</h2>
        <p>{message}</p>
      </div>
    </div>
  );
};

export default StoryGenerationLoading; 