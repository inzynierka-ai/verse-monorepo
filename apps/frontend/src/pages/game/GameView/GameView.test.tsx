import { render, screen } from '@/testUtils';
import GameView from './GameView';
import { useCharacter } from '@/services/api/hooks/useCharacter';
import { useLocation } from '@/services/api/hooks/useLocation';
import { Mock, vi } from 'vitest';

// Mock the hooks
vi.mock('@/hooks/useCharacter');
vi.mock('@/hooks/useLocation');

describe('GameView', () => {
  const mockCharacter = {
    id: 'test-character-id',
    name: 'Test Character',
    avatar: 'test-avatar.jpg',
    relationshipLevel: 50,
    threadId: 'test-thread-id',
  };

  const mockLocation = {
    id: 'test-location-id',
    background: 'test-background.jpg',
  };

  beforeEach(() => {
    (useCharacter as Mock).mockReturnValue({
      data: mockCharacter,
      isLoading: false,
    });

    (useLocation as Mock).mockReturnValue({
      data: mockLocation,
      isLoading: false,
    });
  });

  test('renders loading state', () => {
    (useCharacter as Mock).mockReturnValue({
      data: null,
      isLoading: true,
    });

    render(<GameView />);

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('renders character and chat view when data is loaded', () => {
    render(<GameView />);

    expect(screen.getByText('Test Character')).toBeInTheDocument();
    expect(screen.getByRole('img')).toHaveAttribute('src', 'test-avatar.jpg');
    expect(screen.getByRole('img')).toHaveAttribute('alt', 'Test Character');
  });

  test('returns null when data is not available', () => {
    (useCharacter as Mock).mockReturnValue({
      data: null,
      isLoading: false,
    });

    const { container } = render(<GameView />);
    expect(container.firstChild).toBeNull();
  });
});
