import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useChapters, Chapter } from '@/services/api/hooks/useChapters';
import Button from '@/common/components/Button';
import styles from './ChaptersView.module.scss';
import { storyChaptersRoute } from '@/router';

type ChaptersViewProps = {
  storyId: string;
};

const ChaptersView = (props: ChaptersViewProps) => {
  const { storyId } = storyChaptersRoute.useParams();
  const navigate = useNavigate();
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null);

  const { data: chapters, isLoading, error } = useChapters(storyId);

  const handleChapterClick = (chapter: Chapter) => {
    setSelectedChapter(chapter.id);
    navigate({ to: `/stories/${storyId}/chapter/${chapter.id}` });
  };

  const handleBack = () => {
    navigate({ to: '/stories' });
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div>Loading chapters...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorMessage}>
        Error loading chapters. Please try again later.
      </div>
    );
  }

  return (
    <div>
      <div className="container">
        <h1>Story Chapters</h1>
        <Button onClick={handleBack}>Back to Stories</Button>
        
        {chapters && chapters.length > 0 ? (
          <div className={styles.chapterList}>
            {chapters.map((chapter) => (
              <div 
                key={chapter.id} 
                className={styles.chapterItem} 
                onClick={() => handleChapterClick(chapter)}
              >
                <div className={styles.chapterTitle}>{chapter.title}</div>
                <div className={styles.chapterDescription}>{chapter.description}</div>
              </div>
            ))}
          </div>
        ) : (
          <div>No chapters available for this story.</div>
        )}
      </div>
    </div>
  );
};

export default ChaptersView; 