import { ReactElement, useState } from 'react';
import { SimpleGameInput } from '@/services/api/hooks/useStoryGeneration';
import formStyles from './SimpleStoryGenerationForm.module.scss';
import viewStyles from './StoryGenerationView.module.scss';
import Button from '@/common/components/Button';

interface SimpleStoryGenerationFormProps {
  onSubmit: (data: SimpleGameInput) => void;
}

const SimpleStoryGenerationForm = ({ onSubmit }: SimpleStoryGenerationFormProps): ReactElement => {
  const [formData, setFormData] = useState<SimpleGameInput>({
    story_description: '',
    character_description: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className={viewStyles.content}>
      <h1 className={viewStyles.title}>Create Your Story</h1>
      <p className={viewStyles.subtitle}>
        Describe your world and character in simple terms. Let AI fill in the details.
      </p>

      <form className={formStyles.form} onSubmit={handleSubmit}>
        <div className={viewStyles.section}>
          <h2 className={viewStyles.sectionTitle}>Story World</h2>
          <div className={formStyles.formGroup}>
            <label htmlFor="story_description" className={formStyles.label}>
              Describe the story world you want to play in
            </label>
            <textarea
              id="story_description"
              name="story_description"
              className={formStyles.textarea}
              value={formData.story_description}
              onChange={handleChange}
              placeholder="Example: A cyberpunk city in 2077 where corporations rule and technology has advanced beyond recognition."
              rows={5}
              required
            />
          </div>
        </div>

        <div className={viewStyles.section}>
          <h2 className={viewStyles.sectionTitle}>Your Character</h2>
          <div className={formStyles.formGroup}>
            <label htmlFor="character_description" className={formStyles.label}>
              Describe your character
            </label>
            <textarea
              id="character_description"
              name="character_description"
              className={formStyles.textarea}
              value={formData.character_description}
              onChange={handleChange}
              placeholder="Example: A former corporate security specialist who went rogue after discovering dark secrets about their employer."
              rows={5}
              required
            />
          </div>
        </div>

        <div className={viewStyles.buttonContainer}>
          <Button type="submit" fullWidth>
            Generate Story
          </Button>
        </div>
      </form>
    </div>
  );
};

export default SimpleStoryGenerationForm;
