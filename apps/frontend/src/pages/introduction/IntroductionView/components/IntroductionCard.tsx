import { Box, Card, Stack, Typography } from '@mui/material';

interface IntroductionCardProps {
  title?: string;
  description?: string | string[];
  imageSrc?: string;
  imageAlt?: string;
  slideAnimation: any;
}

const IntroductionCard = ({
  title,
  description,
  imageSrc,
  imageAlt,
  slideAnimation,
}: IntroductionCardProps) => (
  <Card sx={{ p: { xs: 2, md: 4 }, maxWidth: '800px', width: '100%', ...slideAnimation }}>
    <Stack spacing={3}>
      {title && (
        <Typography
          variant="h5"
          component="h2"
          sx={{
            fontWeight: 600,
            borderBottom: '1px solid',
            borderColor: 'divider',
            pb: 1,
          }}
        >
          {title}
        </Typography>
      )}

      {imageSrc && (
        <Box
          component="img"
          src={imageSrc}
          alt={imageAlt || title}
          sx={{
            maxHeight: '300px',
            borderRadius: 1,
            objectFit: 'contain',
          }}
        />
      )}

      <Box sx={{ mt: 1 }}>
        {Array.isArray(description) ? (
          <Stack spacing={2}>
            {description.map((text, index) => (
              <Typography key={index} variant="body1" color="text.secondary">
                {text}
              </Typography>
            ))}
          </Stack>
        ) : (
          <Typography variant="body1" color="text.secondary">
            {description}
          </Typography>
        )}
      </Box>
    </Stack>
  </Card>
);

export default IntroductionCard;
