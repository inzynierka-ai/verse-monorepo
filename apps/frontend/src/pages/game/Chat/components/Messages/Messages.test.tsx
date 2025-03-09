import { render, screen } from '@/testUtils';
import Messages from './Messages';
import { Message } from '@/types/chat';

describe('Messages', () => {
  const mockMessages: Message[] = [
    { role: 'user', content: 'Hello', threadId: 'test-thread-id' },
    { role: 'assistant', content: 'Hi there!', threadId: 'test-thread-id' },
  ];

  test('renders messages correctly', () => {
    render(<Messages messages={mockMessages} />);

    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });

  test('renders relationship level when provided', () => {
    render(<Messages messages={mockMessages} relationshipLevel={75} />);

    expect(screen.getByText('Relationship Level')).toBeInTheDocument();
    expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '75');
  });

  test('does not render relationship level when not provided', () => {
    render(<Messages messages={mockMessages} />);

    expect(screen.queryByText('Relationship Level')).not.toBeInTheDocument();
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  });
});
