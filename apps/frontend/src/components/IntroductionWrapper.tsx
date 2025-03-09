import React from 'react';
import IntroductionView from '../pages/introduction/IntroductionView/IntroductionView';
import { router } from '../router';

export function IntroductionWrapper() {
  const navigate = router.navigate;

  return (
    <IntroductionView onComplete={() => navigate({ to: '/game' })} locationId="1" characterId="1" />
  );
}
