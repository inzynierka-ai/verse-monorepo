import { sceneRoute } from '@/router';
import { useNavigate } from '@tanstack/react-router';
import { useLatestScene } from '@/services/api/hooks/useLatestScene';
import { useCompleteScene } from '@/services/api/hooks/useCompleteScene';
import Button from '@/common/components/Button/Button';
import Card from '@/common/components/Card/Card';
import { Character } from '@/types/character.types';
import { useEffect, useState } from 'react';
import styles from './SceneView.module.scss';
import { useQueryClient } from '@tanstack/react-query';

const VIEWED_SCENES_KEY = 'verse_viewed_scenes';

const SceneView = () => {
  const { storyId, sceneId } = sceneRoute.useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [showIntroduction, setShowIntroduction] = useState(true);
  const [descriptionExpanded, setDescriptionExpanded] = useState(false);

  const { data: scene, isLoading, error } = useLatestScene(storyId);
  const { mutate: completeScene, isPending: isCompleting } = useCompleteScene();

  // Check if scene has been viewed before
  useEffect(() => {
    if (scene) {
      const viewedScenes = JSON.parse(localStorage.getItem(VIEWED_SCENES_KEY) || '[]');
      const hasBeenViewed = viewedScenes.includes(scene.uuid);
      setShowIntroduction(!hasBeenViewed);
    }
  }, [scene]);

  const handleCharacterClick = (character: Character) => {
    navigate({
      to: '/play/$storyId/scenes/$sceneId/characters/$characterId',
      params: { storyId, sceneId, characterId: character.uuid },
    });
  };

  const handleContinueFromIntro = () => {
    if (scene) {
      // Save this scene as viewed in localStorage
      const viewedScenes = JSON.parse(localStorage.getItem(VIEWED_SCENES_KEY) || '[]');
      if (!viewedScenes.includes(scene.uuid)) {
        viewedScenes.push(scene.uuid);
        localStorage.setItem(VIEWED_SCENES_KEY, JSON.stringify(viewedScenes));
      }
      setShowIntroduction(false);
    }
  };

  const handleShowIntroduction = () => {
    setShowIntroduction(true);
  };

  const handleBackToStories = () => {
    navigate({ to: '/stories' });
  };

  const handleFinishScene = () => {
    completeScene(
      { storyId, sceneId },
      {
        onSuccess: () => {
          navigate({ to: '/play/$storyId', params: { storyId }, replace: true });
          queryClient.invalidateQueries({ queryKey: ['latest-scene', storyId] });
        },
        onError: (error) => {
          console.error('Failed to complete scene:', error);
        },
      },
    );
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
    navigate({ to: '/play/$storyId', params: { storyId }, replace: true });
    return null;
  }

  const npcCharacters = scene.characters.filter((character) => character.role === 'npc');

  // Introduction Overlay
  if (showIntroduction) {
    return (
      <div className={styles.introductionOverlay}>
        <Card className={styles.introductionContent}>
          <h1>Welcome to {scene.location.name}</h1>

          <div className={styles.introductionDescription}>
            <p>{scene.description}</p>
          </div>

          <Button onClick={handleContinueFromIntro} fullWidth>
            Continue to Scene
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className={styles.sceneView}>
      {/* Location Banner */}
      <div className={styles.locationBanner}>
        <img src={scene.location.image_dir} alt={scene.location.name} />
        <div className={styles.locationBannerOverlay}>
          <h1>{scene.location.name}</h1>
          <div className={styles.bannerActions}>
            <Button onClick={handleBackToStories} variant="text" className={styles.iconButton}>
              ←
            </Button>
            <Button onClick={handleShowIntroduction} variant="text" className={styles.iconButton}>
              i
            </Button>
          </div>
        </div>
      </div>

      <div className={styles.sceneContent}>
        {/* Left Column - Location Info */}
        <div className={styles.locationSidebar}>
          <div className={styles.locationInfo}>
            <div className={styles.locationSectionHeader}>
              <h2>Location</h2>
            </div>
            <Card className={styles.locationCard}>
              <div className={styles.locationDetails}>
                <p>{scene.location.brief_description}</p>
              </div>
            </Card>
          </div>
        </div>

        {/* Main Content - Characters */}
        <div className={styles.mainContent}>
          <div className={styles.charactersSection}>
            <div className={styles.charactersSectionHeader}>
              <div className={styles.charactersTitle}>
                <h2>Characters</h2>
                <span className={styles.characterCount}>{npcCharacters.length}</span>
              </div>
              <p className={styles.charactersInstructions}>
                Click on a character to start a conversation and progress through the scene
              </p>
            </div>
            <div className={styles.charactersGrid}>
              {npcCharacters.map((character) => (
                <Card
                  key={character.uuid}
                  className={styles.characterCard}
                  onClick={() => handleCharacterClick(character)}
                >
                  <div className={styles.characterPortrait}>
                    <img src={character.image_dir} alt={character.name} />
                  </div>
                  <div className={styles.characterInfo}>
                    <h3>{character.name}</h3>
                    <Button className={styles.talkButton}>Talk to Character</Button>
                  </div>
                </Card>
              ))}
            </div>
            {scene.messages.length > 0 && (
              <div className={styles.finishSceneContainer}>
                <Button variant="danger" fullWidth onClick={handleFinishScene} disabled={isCompleting}>
                  {isCompleting ? 'Completing Scene...' : 'Finish Scene'}
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SceneView;
