import { render, screen } from '@/testUtils';
import IntroductionView from './IntroductionView';
import { useCharacter } from '@/hooks/useCharacter';
import { useLocation } from '@/hooks/useLocation';
import { vi, type Mock } from 'vitest';
import { waitFor } from '@testing-library/react';

vi.mock('@/hooks/useCharacter');
vi.mock('@/hooks/useLocation');

describe('IntroductionView', () => {
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
    description: 'test-description',
    name: 'test-name',
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

  test('renders story introduction initially', () => {
    render(<IntroductionView onComplete={vi.fn()} locationId="0" characterId="0" />);

    expect(screen.getByText(/In a world where AI and humans coexist/)).toBeInTheDocument();
    expect(screen.getByText('Next')).toBeInTheDocument();
  });

  test('shows character information after click', async () => {
    const { user } = render(
      <IntroductionView onComplete={vi.fn()} locationId="0" characterId="0" />,
    );

    await user.click(screen.getByText('Next'));

    expect(await screen.findByText(`Location: ${mockLocation.name}`)).toBeInTheDocument();
  });

  test('shows character information after click', async () => {
    const { user } = render(
      <IntroductionView onComplete={vi.fn()} locationId="0" characterId="0" />,
    );

    await user.click(screen.getByText('Next'));
    await user.click(screen.getByText('Next'));

    expect(await screen.findByText(`Character: ${mockCharacter.name}`)).toBeInTheDocument();
  });

  test('calls onComplete after final step', async () => {
    const onComplete = vi.fn();
    const { user } = render(
      <IntroductionView onComplete={onComplete} locationId="0" characterId="0" />,
    );

    // Navigate through all steps
    await user.click(screen.getByText('Next'));
    await user.click(screen.getByText('Next'));
    await user.click(screen.getByText('Next'));
    await user.click(screen.getByText('Start Game'));

    await waitFor(() => {
      expect(onComplete).toHaveBeenCalled();
    });
  });
});
