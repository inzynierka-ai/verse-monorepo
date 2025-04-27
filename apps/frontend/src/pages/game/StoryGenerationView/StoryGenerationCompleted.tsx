import { useNavigate } from '@tanstack/react-router';
import styles from './StoryGenerationView.module.scss';
import Button from '@/common/components/Button';
import { StoryCreated } from '@/services/api/hooks';
import { Character } from '@/types/character.types';
import { useCreateStory, createStoryFromGeneration } from '@/services/api/hooks/useCreateStory';
import { useState } from 'react';

interface StoryGenerationCompletedProps {
  story?: StoryCreated;
  character?: Character;
  onReset: () => void;
}

const StoryGenerationCompleted = ({ story, character, onReset }: StoryGenerationCompletedProps) => {
  const navigate = useNavigate();
  const [isCreating, setIsCreating] = useState(false);
  const createStoryMutation = useCreateStory();

  const handleExploreStories = () => {
    navigate({ to: '/stories' });
  };

  const handleBeginAdventure = async () => {
    console.log(story, character);
    if (!story || !character) return;

    try {
      setIsCreating(true);
      const storyData = createStoryFromGeneration(story, character);
      const response = await createStoryMutation.mutateAsync(storyData);

      // Navigate to the play page with the new story ID
      navigate({ to: `/play/${response.id}` });
    } catch (error) {
      console.error('Failed to create story:', error);
      setIsCreating(false);
    }
  };

  return (
    <div className={styles.content}>
      <h1 className={styles.title}>Your Story Awaits</h1>

      {story && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Story</h2>
          <p className={styles.storyDescription}>{story.description}</p>

          {story.rules.length > 0 && (
            <>
              <h3>Story Rules</h3>
              <ul className={styles.storyRules}>
                {story.rules.map((rule, index) => (
                  <li key={index}>{rule}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}

      {character && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>{character.name}</h2>
          <div className={styles.characterInfo}>
            <div className={styles.characterImageContainer}>
              <img src={character.imageUrl} alt={`${character.name}`} className={styles.characterImage} />
            </div>
            <p>{character.description}</p>
            <div>
              <h3>Personality Traits</h3>
              <div>
                {character.personalityTraits.map((trait, index) => (
                  <span key={index} className={styles.trait}>
                    {trait}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <h3>Backstory</h3>
              <p>{character.backstory}</p>
            </div>

            {character.goals.length > 0 && (
              <div>
                <h3>Goals</h3>
                <ul>
                  {character.goals.map((goal, index) => (
                    <li key={index}>{goal}</li>
                  ))}
                </ul>
              </div>
            )}

            {character.relationships.length > 0 && (
              <div>
                <h3>Relationships</h3>
                <ul>
                  {character.relationships.map((rel, index) => (
                    <li key={index}>
                      <strong>{rel.name}</strong> ({rel.type}) - {rel.backstory}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      <div className={styles.buttonContainer}>
        <Button onClick={handleExploreStories}>Explore Stories</Button>
        <Button onClick={handleBeginAdventure}>Begin adventure</Button>
        <Button onClick={onReset} variant="secondary">
          Create Another Story
        </Button>
      </div>
    </div>
  );
};

export default StoryGenerationCompleted; 