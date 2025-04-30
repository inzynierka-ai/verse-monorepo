import { ReactElement } from 'react';
import { Link, useNavigate } from '@tanstack/react-router';
import Container from '@/common/components/Container/Container';
import Button from '@/common/components/Button/Button';
import styles from './StoriesView.module.scss';
import { useStories } from '@/services/api/hooks/useStory';

const StoriesView = (): ReactElement => {
  const { data: stories = [], isLoading, error } = useStories();
  const navigate = useNavigate();

  const handleCreateStory = () => {
    navigate({ to: '/create-story' });
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <p>Loading stories...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <p>Failed to load stories. Please try again later.</p>
      </div>
    );
  }

  return (
    <Container>
      <div className={styles.header}>
        <h1>Available Stories</h1>
        <Button onClick={handleCreateStory} variant="secondary">
          Create New Story
        </Button>
      </div>

      {stories.length === 0 ? (
        <div className={styles.emptyState}>No stories available.</div>
      ) : (
        <div className={styles.storiesList}>
          {stories.map((story) => (
            <Link key={story.uuid} className={styles.storyItem} to="/play/$storyId" params={{ storyId: story.uuid }}>
              <div className={styles.storyTitle}>{story.title}</div>
              <div className={styles.storyDescription}>{story.description}</div>
            </Link>
          ))}
        </div>
      )}
    </Container>
  );
};

export default StoriesView;
