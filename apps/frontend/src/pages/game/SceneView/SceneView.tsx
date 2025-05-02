import { sceneRoute } from '@/router';
import { useNavigate } from '@tanstack/react-router';
import { useLatestScene } from '@/services/api/hooks/useLatestScene';
import Button from '@/common/components/Button/Button';
import { Character } from '@/types/character.types';
import styles from './SceneView.module.scss';

const SceneView = () => {
  const { storyId, sceneId } = sceneRoute.useParams();
  const navigate = useNavigate();

  const { data: scene, isLoading, error } = useLatestScene(storyId);

  const handleCharacterClick = (character: Character) => {
    navigate({
      to: '/play/$storyId/scenes/$sceneId/characters/$characterId',
      params: { storyId, sceneId, characterId: character.uuid },
    });
  };

  const handleBackToStories = () => {
    navigate({ to: '/stories' });
  };

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <div className={styles.loadingSpinner}></div>
        <p>Loading scene...</p>
      </div>
    );
  }

  if (error || !scene) {
    return (
      <div className={styles.error}>
        <h2>Error loading scene</h2>
        <p>{error instanceof Error ? error.message : 'Failed to fetch scene data.'}</p>
        <Button onClick={handleBackToStories}>Return to Stories</Button>
      </div>
    );
  }

  return (
    <div className={styles.sceneView}>
      <div className={styles.sceneHeader}>
        <h1>{scene.location.name}</h1>
        <Button onClick={handleBackToStories} variant="secondary">
          Back to Stories
        </Button>
      </div>

      <div className={styles.sceneDescription}>
        <p>{scene.description}</p>
      </div>

      <div className={styles.locationInfo}>
        <h2>Location</h2>
        <div className={styles.locationCard}>
          <div className={styles.locationImage}>
            <img src={scene.location.image_dir} alt={scene.location.name} />
          </div>

          <div className={styles.locationDetails}>
            <h3>{scene.location.name}</h3>
            <p>{scene.location.description}</p>
          </div>
        </div>
      </div>

      <div className={styles.charactersSection}>
        <h2>Characters</h2>
        <div className={styles.charactersGrid}>
          {scene.characters
            .filter((character) => character.role === 'npc')
            .map((character) => (
              <div
                key={character.uuid}
                className={styles.characterCard}
                onClick={() => handleCharacterClick(character)}
              >
                <div className={styles.characterPortrait}>
                  <img src={character.image_dir} alt={character.name} />
                </div>
                <h3>{character.name}</h3>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
};

export default SceneView;
