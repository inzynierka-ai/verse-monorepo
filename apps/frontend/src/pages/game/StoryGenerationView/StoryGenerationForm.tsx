import { FormEvent, useState } from 'react';
import styles from './StoryGenerationView.module.scss';
import Button from '@/common/components/Button';
import Input from '@/common/components/Input';
import { StoryGenerationRequest } from '@/services/api/hooks';

interface StoryGenerationFormProps {
  onSubmit: (data: StoryGenerationRequest) => void;
}

const StoryGenerationForm = ({ onSubmit }: StoryGenerationFormProps) => {
  const [formData, setFormData] = useState<StoryGenerationRequest>({
    world: {
      theme: 'Love',
      genre: 'Fantasy',
      year: 2023,
      setting: 'Medieval village'
    },
    playerCharacter: {
      name: 'John Doe',
      age: 25,
      appearance: 'A tall, dark-haired man with a kind face',
      background: 'John grew up in a small village where he learned to be a blacksmith. He was a skilled blacksmith and was able to make weapons and armor for the village. He was also a good friend to the villagers and was always willing to help them.'
    }
  });
  
  const [errors, setErrors] = useState<{
    theme?: string;
    genre?: string;
    year?: string;
    setting?: string;
    name?: string;
    age?: string;
    appearance?: string;
    background?: string;
  }>({});
  
  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};
    let isValid = true;
    
    // Validate world settings
    if (!formData.world.theme.trim()) {
      newErrors.theme = 'Theme is required';
      isValid = false;
    }
    
    if (!formData.world.genre.trim()) {
      newErrors.genre = 'Genre is required';
      isValid = false;
    }
    
    if (!formData.world.setting.trim()) {
      newErrors.setting = 'Setting is required';
      isValid = false;
    }
    
    // Validate character
    if (!formData.playerCharacter.name.trim()) {
      newErrors.name = 'Character name is required';
      isValid = false;
    }
    
    if (!formData.playerCharacter.appearance.trim()) {
      newErrors.appearance = 'Character appearance is required';
      isValid = false;
    }
    
    if (!formData.playerCharacter.background.trim()) {
      newErrors.background = 'Character background is required';
      isValid = false;
    }
    
    setErrors(newErrors);
    return isValid;
  };
  
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    // Clear validation error when user types
    if (errors[name as keyof typeof errors]) {
      setErrors({ ...errors, [name]: undefined });
    }
    
    // Handle nested properties for world and playerCharacter
    if (name.includes('.')) {
      const [parent, child] = name.split('.');
      if (parent === 'world') {
        setFormData({
          ...formData,
          world: {
            ...formData.world,
            [child]: child === 'year' ? parseInt(value, 10) || 0 : value
          }
        });
      } else if (parent === 'playerCharacter') {
        setFormData({
          ...formData,
          playerCharacter: {
            ...formData.playerCharacter,
            [child]: child === 'age' ? parseInt(value, 10) || 0 : value
          }
        });
      }
    }
  };
  
  return (
    <div className={styles.content}>
      <h1 className={styles.title}>Create Your Story</h1>
      <p className={styles.subtitle}>
        Define your world and character to begin an AI-generated adventure
      </p>
      
      <form className={styles.form} onSubmit={handleSubmit}>
        {/* World Settings Section */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>World Settings</h2>
          
          <div className={styles.formRow}>
            <Input
              label="Theme"
              name="world.theme"
              placeholder="Love, Betrayal, Redemption, etc."
              value={formData.world.theme}
              onChange={handleChange}
              error={errors.theme}
              fullWidth
            />
          </div>
          
          <div className={styles.formRow}>
            <Input
              label="Genre"
              name="world.genre"
              placeholder="Fantasy, Sci-Fi, Mystery, etc."
              value={formData.world.genre}
              onChange={handleChange}
              error={errors.genre}
              fullWidth
            />
          </div>
          
          <div className={styles.formRow}>
            <Input
              label="Year"
              name="world.year"
              type="number"
              placeholder="Year the story takes place"
              value={formData.world.year}
              onChange={handleChange}
              error={errors.year}
              fullWidth
            />
          </div>
          
          <div className={styles.formRow}>
            <Input
              label="Setting"
              name="world.setting"
              placeholder="Medieval village, Space station, etc."
              value={formData.world.setting}
              onChange={handleChange}
              error={errors.setting}
              fullWidth
            />
          </div>
        </div>
        
        {/* Character Section */}
        <div className={styles.section}>
          <h2 className={styles.sectionTitle}>Your Character</h2>
          
          <div className={styles.formRow}>
            <Input
              label="Name"
              name="playerCharacter.name"
              placeholder="Your character's name"
              value={formData.playerCharacter.name}
              onChange={handleChange}
              error={errors.name}
              fullWidth
            />
          </div>
          
          <div className={styles.formRow}>
            <Input
              label="Age"
              name="playerCharacter.age"
              type="number"
              value={formData.playerCharacter.age}
              onChange={handleChange}
              error={errors.age}
              fullWidth
            />
          </div>
          
          <div className={styles.formRow}>
            <Input
              label="Appearance"
              name="playerCharacter.appearance"
              placeholder="Describe your character's appearance"
              value={formData.playerCharacter.appearance}
              onChange={handleChange}
              error={errors.appearance}
              fullWidth
            />
          </div>
          
          <div className={styles.formRow}>
            <Input
              label="Background"
              name="playerCharacter.background"
              placeholder="Your character's history and backstory"
              value={formData.playerCharacter.background}
              onChange={handleChange}
              error={errors.background}
              fullWidth
            />
          </div>
        </div>
        
        <div className={styles.buttonContainer}>
          <Button type="submit" fullWidth>
            Generate Story
          </Button>
        </div>
      </form>
    </div>
  );
};

export default StoryGenerationForm; 