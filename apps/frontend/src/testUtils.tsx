import { ReactElement } from 'react';
import { render as rtlRender, RenderOptions, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import userEvent from '@testing-library/user-event';
import { afterEach, vi } from 'vitest';
import '@testing-library/jest-dom';

// Clean up after each test
afterEach(() => {
  vi.clearAllMocks();
});

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient;
}

export function render(
  ui: ReactElement,
  { queryClient = createTestQueryClient(), ...renderOptions }: CustomRenderOptions = {},
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
  }

  return {
    user: userEvent.setup(),
    ...rtlRender(ui, { wrapper: Wrapper, ...renderOptions }),
  };
}

export { screen, userEvent };
