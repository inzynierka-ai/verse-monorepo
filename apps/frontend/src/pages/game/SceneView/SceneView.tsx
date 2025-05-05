import { sceneRoute } from '@/router';
import { useNavigate } from '@tanstack/react-router';
import { useLatestScene } from '@/services/api/hooks/useLatestScene';
import Button from '@/common/components/Button/Button';
import { Character } from '@/types/character.types';
import { useState } from 'react';
import styles from './SceneView.module.scss';

const SceneView = () => {
  const { storyId, sceneId } = sceneRoute.useParams();
  const navigate = useNavigate();
  const [descriptionExpanded, setDescriptionExpanded] = useState(false);

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

  const handleFinishScene = () => {
    // This will be implemented later
    console.log('Finish scene clicked');
  };

  const toggleDescription = () => {
    setDescriptionExpanded(!descriptionExpanded);
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

  const npcCharacters = scene.characters.filter((character) => character.role === 'npc');

  return (
    <div className={styles.sceneView}>
      <div className={styles.sceneHeader}>
        <h1>{scene.location.name}</h1>
        <Button onClick={handleBackToStories} variant="secondary">
          Back to Stories
        </Button>
      </div>

      <div className={styles.sceneContent}>
        {/* Left Column - Scene Context */}
        <div className={styles.sceneContextColumn}>
          <div className={`${styles.sceneDescription} ${!descriptionExpanded ? styles.descriptionCollapsed : ''}`}>
            <p>{scene.description}</p>
            <button className={styles.toggleDescription} onClick={toggleDescription}>
              {descriptionExpanded ? 'Show Less' : 'Read More'}
            </button>
          </div>

          <div className={styles.locationInfo}>
            <div className={styles.locationSectionHeader}>
              <h2>Location</h2>
            </div>
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
        </div>

        {/* Right Column - Characters */}
        <div className={styles.charactersColumn}>
          <div className={styles.charactersSection}>
            <div className={styles.charactersSectionHeader}>
              <div className={styles.charactersTitle}>
                <h2>Characters</h2>
                <span className={styles.characterCount}>{npcCharacters.length}</span>
              </div>
            </div>
            <div className={styles.charactersGrid}>
              {npcCharacters.map((character) => (
                <div
                  key={character.uuid}
                  className={styles.characterCard}
                  onClick={() => handleCharacterClick(character)}
                >
                  <div className={styles.characterPortrait}>
                    <img src={character.image_dir} alt={character.name} />
                  </div>
                  <div className={styles.characterInfo}>
                    <h3>{character.name}</h3>
                  </div>
                </div>
              ))}
            </div>
            <div className={styles.finishSceneContainer}>
              <Button variant="danger" fullWidth onClick={handleFinishScene}>
                Finish Scene
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SceneView;
