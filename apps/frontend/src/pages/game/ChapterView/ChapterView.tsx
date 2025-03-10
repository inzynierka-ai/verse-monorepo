import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { useScenes, Scene } from '@/services/api/hooks/useScenes';
import Button from '@/common/components/Button';
import styles from './ChapterView.module.scss';
import { chapterDetailRoute } from '@/router';

const ChapterView = () => {
  const { storyId, chapterId } = chapterDetailRoute.useParams();
  const navigate = useNavigate();
  const [selectedScene, setSelectedScene] = useState<number | null>(null);

  const { data: scenes, isLoading, error } = useScenes(chapterId);

  const handleSceneClick = (scene: Scene) => {
    setSelectedScene(scene.id);
    // Navigate to the scene (implementation will depend on your routing structure)
    navigate({ to: `/stories/${storyId}/chapter/${chapterId}/scene/${scene.id}` });
  };

  const handleBack = () => {
    navigate({ to: `/stories/${storyId}/chapters` });
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div>Loading scenes...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <div>Error loading scenes: {(error as Error).message}</div>
        <Button onClick={handleBack}>Back to Chapters</Button>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Chapter Scenes</h1>
        <Button onClick={handleBack}>Back to Chapters</Button>
      </div>
      
      <div className={styles.scenesList}>
        {scenes && scenes.length > 0 ? (
          scenes.map((scene) => (
            <div
              key={scene.id}
              className={`${styles.sceneItem} ${selectedScene === scene.id ? styles.selected : ''}`}
              onClick={() => handleSceneClick(scene)}
            >
              <div className={styles.sceneTitle}>
                Scene {scene.id}
              </div>
              <div className={styles.scenePrompt}>
                {scene.prompt}
              </div>
              <div className={styles.sceneDetails}>
                Location ID: {scene.location_id}
              </div>
            </div>
          ))
        ) : (
          <div className={styles.emptyState}>No scenes found for this chapter.</div>
        )}
      </div>
    </div>
  );
};

export default ChapterView; 