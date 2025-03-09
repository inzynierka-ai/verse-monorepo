import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';
import GameView from './pages/game/GameView/GameView';
import IntroductionView from './pages/introduction/IntroductionView/IntroductionView';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => {
  const [showIntroduction, setShowIntroduction] = useState(true);

  return (
    <QueryClientProvider client={queryClient}>
      {showIntroduction ? (
        <IntroductionView
          onComplete={() => setShowIntroduction(false)}
          locationId="0"
          characterId="0"
        />
      ) : (
        <GameView />
      )}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};

export default App;
