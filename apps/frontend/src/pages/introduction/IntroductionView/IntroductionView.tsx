import { Box, Button } from '@mui/material';
import { useState } from 'react';
import { useLocation } from '@/hooks/useLocation';
import { useCharacter } from '@/hooks/useCharacter';
import IntroductionCard from './components/IntroductionCard';
import { useWebSocket } from '@/hooks/webSockets/useWebSocket';

interface IntroductionViewProps {
  onComplete: () => void;
  locationId: string;
  characterId: string;
}

const STORY_DESCRIPTION = [
  'In a world where AI and humans coexist, relationships between the two species have become increasingly complex.',
  'You find yourself in a unique position to bridge the gap between artificial and human consciousness.',
  'Every conversation, every choice you make will shape the future of this delicate relationship.',
];

const IntroductionView = ({ onComplete, locationId, characterId }: IntroductionViewProps) => {
  const [step, setStep] = useState(0);
  const [direction, setDirection] = useState('left');
  const [isFadingOut, setIsFadingOut] = useState(false);
  const { data: location } = useLocation(locationId);
  const { data: character } = useCharacter(characterId);

  const slideAnimation = {
    animation: isFadingOut
      ? 'fadeOut 0.5s ease-in-out forwards'
      : `${direction}Slide 0.5s ease-in-out forwards`,
    '@keyframes fadeOut': {
      '0%': { opacity: 1, transform: 'translateY(0)' },
      '100%': { opacity: 0, transform: 'translateY(-20px)' },
    },
    '@keyframes leftSlide': {
      '0%': { transform: 'translateX(100%)', opacity: 0 },
      '100%': { transform: 'translateX(0)', opacity: 1 },
    },
    '@keyframes rightSlide': {
      '0%': { transform: 'translateX(-100%)', opacity: 0 },
      '100%': { transform: 'translateX(0)', opacity: 1 },
    },
  };

  const renderContent = () => {
    const content = {
      0: (
        <IntroductionCard
          key={`${step}-${direction}`}
          description={STORY_DESCRIPTION}
          slideAnimation={slideAnimation}
        />
      ),
      1: (
        <IntroductionCard
          key={`${step}-${direction}`}
          title={`Location: ${location?.name}`}
          description={location?.description}
          imageSrc={location?.background}
          imageAlt={location?.name}
          slideAnimation={slideAnimation}
        />
      ),
      2: (
        <IntroductionCard
          key={`${step}-${direction}`}
          title={`Character: ${character?.name}`}
          description={character?.description}
          imageSrc={character?.avatar}
          imageAlt={character?.name}
          slideAnimation={slideAnimation}
        />
      ),
      3: (
        <IntroductionCard
          key={`${step}-${direction}`}
          title="Ready to Begin?"
          description="Your journey awaits. Make choices wisely as they will shape the future of AI-human relations."
          slideAnimation={slideAnimation}
        />
      ),
    };

    return content[step as keyof typeof content];
  };

  const handleNext = () => {
    if (step < 3) {
      setDirection('left');
      setStep(step + 1);
    } else {
      setIsFadingOut(true);
      setTimeout(() => {
        onComplete();
      }, 500); // Match animation duration
    }
  };

  const handlePrevious = () => {
    if (step > 0) {
      setDirection('right');
      setStep(step - 1);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        width: '100%',
        gap: 4,
        p: { xs: 2, sm: 4 },
        bgcolor: 'background.default',
      }}
    >
      {renderContent()}
      <Box
        sx={{
          display: 'flex',
          gap: 2,
        }}
      >
        {step > 0 && (
          <Button variant="outlined" onClick={handlePrevious} sx={{ minWidth: 100 }}>
            Back
          </Button>
        )}
        <Button variant="contained" onClick={handleNext} sx={{ minWidth: 100 }}>
          {step === 3 ? 'Start Game' : 'Next'}
        </Button>
      </Box>
    </Box>
  );
};

export default IntroductionView;
