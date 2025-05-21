import { ReactElement, useState, useEffect } from 'react';
import styles from './CharactersCarousel.module.scss';

interface CharactersCarouselProps {
  totalCharacters?: number;
  autoRotateInterval?: number;
  className?: string;
}

const CharactersCarousel = ({
  totalCharacters = 13,
  autoRotateInterval = 3000,
  className,
}: CharactersCarouselProps): ReactElement => {
  const [activeCharIndex, setActiveCharIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveCharIndex((prevIndex) => (prevIndex + 1) % totalCharacters);
    }, autoRotateInterval);

    return () => clearInterval(interval);
  }, [totalCharacters, autoRotateInterval]);

  const getPositionClass = (index: number) => {
    // Calculate relative position to active character
    const diff = (index - activeCharIndex + totalCharacters) % totalCharacters;

    if (diff === 0) return styles.active; // Current character
    if (diff === 1) return styles.next; // Next character (right)
    if (diff === 2) return styles.nextAfter; // Character after next (far right)
    if (diff === totalCharacters - 1) return styles.previous; // Previous character (left)
    if (diff === totalCharacters - 2) return styles.previousBefore; // Character before previous (far left)

    return styles.hidden; // Hide other characters
  };

  return (
    <div className={`${styles.characterShowcase} ${className || ''}`}>
      <div className={styles.characterCarousel}>
        {Array.from({ length: totalCharacters }).map((_, index) => (
          <div key={index} className={`${styles.characterCard} ${getPositionClass(index)}`}>
            <img
              src={`/characters/character-${index + 1}.png`}
              alt={`AI Generated Character ${index + 1}`}
              className={styles.characterImage}
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default CharactersCarousel;
