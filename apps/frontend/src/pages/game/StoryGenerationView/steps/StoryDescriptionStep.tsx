import styles from '../StoryGenerationView.module.scss';
import { Story } from '@/types/story.types';
import Button from '@/common/components/Button';

interface StoryDescriptionStepProps {
  story: Story;
  onNext: () => void;
}

const StoryDescriptionStep = ({ story, onNext }: StoryDescriptionStepProps) => {
  return (
    <>
      <h1 className={styles.title}>{story.title}</h1>
      <p className={styles.storyBriefDescription}>{story.brief_description}</p>

      <div className={styles.buttonContainer}>
        <Button onClick={onNext}>Continue</Button>
      </div>
    </>
  );
};

export default StoryDescriptionStep;
