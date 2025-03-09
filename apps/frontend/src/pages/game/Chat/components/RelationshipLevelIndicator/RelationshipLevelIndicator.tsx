import { Box, Typography, LinearProgress } from '@mui/material';
import { useEffect, useState } from 'react';

interface RelationshipLevelIndicatorProps {
  level: number;
}

const RelationshipLevelIndicator = ({ level }: RelationshipLevelIndicatorProps) => {
  const [prevLevel, setPrevLevel] = useState(level);
  const [isAnimating, setIsAnimating] = useState(false);
  const isImproving = level > prevLevel;

  useEffect(() => {
    if (level !== prevLevel) {
      setIsAnimating(true);
      const timer = setTimeout(() => {
        setIsAnimating(false);
        setPrevLevel(level);
      }, 1000);

      return () => clearTimeout(timer);
    }
  }, [level, prevLevel]);

  return (
    <Box
      sx={{
        mb: 2,
        position: 'sticky',
        top: 0,
        zIndex: 1,
        bgcolor: 'grey.100',
        pt: 2,
        pb: 1,
      }}
    >
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="caption" color="text.secondary">
          Relationship Level
        </Typography>
        {isAnimating && (
          <Typography
            variant="caption"
            color={isImproving ? 'success.main' : 'error.main'}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 0.5,
            }}
          >
            {isImproving ? '+' : '-'}
            {Math.abs(level - prevLevel).toFixed(1)}
          </Typography>
        )}
      </Box>
      <LinearProgress
        variant="determinate"
        value={level}
        sx={{
          height: 8,
          borderRadius: 1,
          backgroundColor: 'grey.300',
          '& .MuiLinearProgress-bar': {
            transition: 'transform 0.5s ease-in-out, background-color 0.5s ease-in-out',
            backgroundColor: isAnimating
              ? isImproving
                ? 'success.main'
                : 'error.main'
              : 'primary.main',
          },
        }}
      />
    </Box>
  );
};

export default RelationshipLevelIndicator;
