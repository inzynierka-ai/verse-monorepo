import { useNavigate } from '@tanstack/react-router';
import styles from './StoryGenerationView.module.scss';
import Button from '@/common/components/Button';
import { WorldCreated, Character } from '@/services/api/hooks';

interface StoryGenerationCompletedProps {
  world?: WorldCreated;
  character?: Character;
  onReset: () => void;
}

const StoryGenerationCompleted = ({ world, character, onReset }: StoryGenerationCompletedProps) => {
  const navigate = useNavigate();
  
  const handleExploreStories = () => {
    navigate({ to: '/stories' });
  };
  
  return (
    <div className={styles.content}>
      <h1 className={styles.title}>Your Story Awaits</h1>
      
      {world && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>World</h2>
          <p className={styles.worldDescription}>{world.description}</p>
          
          {world.rules.length > 0 && (
            <>
              <h3>World Rules</h3>
              <ul className={styles.worldRules}>
                {world.rules.map((rule, index) => (
                  <li key={index}>{rule}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
      
      {character && (
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Character: {character.name}</h2>
          <div className={styles.characterInfo}>
            <p>{character.description}</p>
            
            <div>
              <h3>Personality Traits</h3>
              <div>
                {character.personalityTraits.map((trait, index) => (
                  <span key={index} className={styles.trait}>{trait}</span>
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
        <Button onClick={handleExploreStories}>
          Explore Stories
        </Button>
        <Button onClick={onReset} variant="secondary">
          Create Another Story
        </Button>
      </div>
    </div>
  );
};

export default StoryGenerationCompleted; 