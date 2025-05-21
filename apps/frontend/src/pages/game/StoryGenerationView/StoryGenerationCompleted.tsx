import { useNavigate } from '@tanstack/react-router';
import { useState, useEffect } from 'react';
import styles from './StoryGenerationView.module.scss';
import Button from '@/common/components/Button';

import { Character } from '@/types/character.types';
import { Story } from '@/types/story.types';

import { StoryDescriptionStep, CharacterImageStep, CharacterDetailsStep, CharacterGoalsStep } from './steps';

interface StoryGenerationCompletedProps {
  story?: Story;
  character?: Character;
  onReset: () => void;
}

const StoryGenerationCompleted = ({ story, character, onReset }: StoryGenerationCompletedProps) => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [animating, setAnimating] = useState(false);

  const handleBeginAdventure = async () => {
    if (!story) return;
    navigate({ to: `/play/${story.uuid}`, replace: true });
  };

  const nextStep = () => {
    if (animating) return;

    setAnimating(true);
    setTimeout(() => {
      setCurrentStep((prevStep) => prevStep + 1);
      setAnimating(false);
    }, 300);
  };

  // If story or character is missing, show an error message
  if (!story || !character) {
    return (
      <div className={styles.content}>
        <h1 className={styles.title}>Something went wrong</h1>
        <p>We couldn't load your story or character information.</p>
        <div className={styles.buttonContainer}>
          <Button onClick={onReset} variant="secondary">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // Render the appropriate step based on currentStep
  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return <StoryDescriptionStep story={story} onNext={nextStep} />;
      case 1:
        return <CharacterImageStep character={character} onNext={nextStep} />;
      case 2:
        return <CharacterDetailsStep character={character} onNext={nextStep} />;
      case 3:
        return <CharacterGoalsStep character={character} onNext={handleBeginAdventure} />;
      default:
        return null;
    }
  };

  return (
    <div className={styles.content}>
      <div className={styles.stepContainer}>
        <div className={`${styles.step} ${animating ? styles.stepExit : styles.stepEnter}`}>{renderStep()}</div>
      </div>

      {/* Always show this button at the bottom */}
      {currentStep === 3 && (
        <div className={styles.buttonContainer}>
          <Button onClick={onReset} variant="secondary">
            Create Another Story
          </Button>
        </div>
      )}
    </div>
  );
};

export default StoryGenerationCompleted;