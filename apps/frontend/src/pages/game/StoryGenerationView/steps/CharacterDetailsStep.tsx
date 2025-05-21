import styles from '../StoryGenerationView.module.scss';
import { Character } from '@/types/character.types';
import Button from '@/common/components/Button';

interface CharacterDetailsStepProps {
  character: Character;
  onNext: () => void;
}

const CharacterDetailsStep = ({ character, onNext }: CharacterDetailsStepProps) => {
  return (
    <div className={styles.section}>
      <h2 className={styles.sectionTitle}>{character.name}'s Background</h2>

      <div>
        <h3>Summary</h3>
        <p className={styles.characterBriefDescription}>{character.brief_description}</p>
      </div>

      <div>
        <h3>Backstory</h3>
        <p>{character.backstory}</p>
      </div>

      <div className={styles.buttonContainer}>
        <Button onClick={onNext}>Continue</Button>
      </div>
    </div>
  );
};

export default CharacterDetailsStep;
