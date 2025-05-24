import { Character } from '@/types/character.types';
import Button from '@/common/components/Button/Button';
import styles from './CharacterDetailsModal.module.scss';

interface CharacterDetailsModalProps {
  character: Character;
  isOpen: boolean;
  onClose: () => void;
}

const CharacterDetailsModal = ({ character, isOpen, onClose }: CharacterDetailsModalProps) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className={styles.modalBackdrop} onClick={handleBackdropClick}>
      <div className={styles.modalContent}>
        <div className={styles.modalHeader}>
          <Button onClick={onClose} className={styles.closeButton} variant="secondary" aria-label="Close">
            ×
          </Button>
        </div>

        <div className={styles.characterDetails}>
          <div className={styles.characterAvatar}>
            <img src={character.image_dir} alt={character.name} />
          </div>

          <div className={styles.characterInfo}>
            <h2>{character.name}</h2>
            <p className={styles.description}>{character.description || character.brief_description}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CharacterDetailsModal;
