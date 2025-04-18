import React from 'react'
import ReactDOM from 'react-dom/client'
import { router, RouterProvider } from './router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

// Import global styles
import '@/common/styles/global.scss';
import Container from './common/components/Container/Container';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1 minute
      refetchOnWindowFocus: false,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <Container>
        <RouterProvider router={router} />
        <ReactQueryDevtools initialIsOpen={false} />
      </Container>
    </QueryClientProvider>
  </React.StrictMode>,
);
