import { ReactElement } from 'react';
import styles from './ModeToggle.module.scss';

interface ModeToggleProps {
  isSimpleMode: boolean;
  onToggle: () => void;
}

const ModeToggle = ({ isSimpleMode, onToggle }: ModeToggleProps): ReactElement => {
  return (
    <div className={styles.modeToggleContainer}>
      <div className={styles.buttonGroup}>
        <button
          className={`${styles.toggleButton} ${isSimpleMode ? styles.active : ''}`}
          onClick={isSimpleMode ? undefined : onToggle}
        >
          Simple
        </button>
        <button
          className={`${styles.toggleButton} ${!isSimpleMode ? styles.active : ''}`}
          onClick={!isSimpleMode ? undefined : onToggle}
        >
          Advanced
        </button>
      </div>
    </div>
  );
};

export default ModeToggle;
