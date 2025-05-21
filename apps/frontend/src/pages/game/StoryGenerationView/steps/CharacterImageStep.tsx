import styles from '../StoryGenerationView.module.scss';
import { Character } from '@/types/character.types';
import Button from '@/common/components/Button';

interface CharacterImageStepProps {
  character: Character;
  onNext: () => void;
}

const CharacterImageStep = ({ character, onNext }: CharacterImageStepProps) => {
  return (
    <div className={styles.section}>
      <h2 className={styles.sectionTitle}>Meet You, {character.name}</h2>

      <div className={styles.characterImageContainer}>
        <img src={character.image_dir} alt={`${character.name}`} className={styles.characterImage} />
      </div>

      <div className={styles.buttonContainer}>
        <Button onClick={onNext}>Continue</Button>
      </div>
    </div>
  );
};

export default CharacterImageStep;
