import styles from '../StoryGenerationView.module.scss';
import { Character } from '@/types/character.types';
import Button from '@/common/components/Button';

interface CharacterGoalsStepProps {
  character: Character;
  onNext: () => void;
}

const CharacterGoalsStep = ({ character, onNext }: CharacterGoalsStepProps) => {
  return (
    <div className={styles.section}>
      <h2 className={styles.sectionTitle}>{character.name}'s Goals</h2>

      {character.goals.length > 0 ? (
        <div>
          <ul>
            {character.goals.map((goal, index) => (
              <li key={index}>{goal}</li>
            ))}
          </ul>
        </div>
      ) : (
        <p>No specific goals defined for this character.</p>
      )}

      <div className={styles.buttonContainer}>
        <Button onClick={onNext}>Begin Adventure</Button>
      </div>
    </div>
  );
};

export default CharacterGoalsStep;
