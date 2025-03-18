import { render, screen } from '@/testUtils';
import Chat from './Chat';
import { useMessages } from '@/common/hooks/useMessages';
import { useAnalysis } from '@/common/hooks/useAnalysis';
import { useSendMessage } from '@/common/hooks/useSendMessage';
import { vi, type Mock } from 'vitest';

// Mock the hooks
vi.mock('@/hooks/useMessages');
vi.mock('@/hooks/useAnalysis');
vi.mock('@/hooks/useSendMessage');

describe('ChatView', () => {
  const mockMessages = [
    { role: 'user', content: 'Hello' },
    { role: 'assistant', content: 'Hi there!' },
  ];

  const mockAnalysis = {
    relationshipLevel: 75,
    availableActions: [],
  };

  beforeEach(() => {
    (useMessages as Mock).mockReturnValue({
      data: mockMessages,
    });

    (useAnalysis as Mock).mockReturnValue({
      data: mockAnalysis,
    });

    (useSendMessage as Mock).mockReturnValue({
      sendMessage: vi.fn(),
      isLoading: false,
      streamingMessage: null,
    });
  });

  test('renders messages and chat input', () => {
    render(<Chat uuid="test-uuid" />);

    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
  });

  test('displays streaming message when available', () => {
    (useSendMessage as Mock).mockReturnValue({
      sendMessage: vi.fn(),
      isLoading: true,
      streamingMessage: { role: 'assistant', content: 'Typing...' },
    });

    render(<Chat uuid="test-uuid" />);

    expect(screen.getByText('Typing...')).toBeInTheDocument();
  });
});
