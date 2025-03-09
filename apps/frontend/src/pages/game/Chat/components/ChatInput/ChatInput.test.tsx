import { describe, test, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@/testUtils';
import ChatInput from './ChatInput';

describe('ChatInput', () => {
  const mockOnSendMessage = vi.fn();

  beforeEach(() => {
    mockOnSendMessage.mockClear();
  });

  test('renders input field and send button', () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={false} />);

    expect(screen.getByPlaceholderText('Type a message...')).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  test('disables input and button when loading', () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={true} />);

    expect(screen.getByPlaceholderText('Type a message...')).toBeDisabled();
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('calls onSendMessage when submitting non-empty message', async () => {
    const { user } = render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={false} />);

    const input = screen.getByPlaceholderText('Type a message...');
    await user.type(input, 'Hello');
    await user.click(screen.getByRole('button'));

    expect(mockOnSendMessage).toHaveBeenCalledWith('Hello');
    expect(input).toHaveValue('');
  });

  test('button is disabled when message is empty', () => {
    render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={false} />);

    expect(screen.getByRole('button')).toBeDisabled();
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  test('handles form submission with enter key', async () => {
    const { user } = render(<ChatInput onSendMessage={mockOnSendMessage} isLoading={false} />);

    const input = screen.getByPlaceholderText('Type a message...');
    await user.type(input, 'Hello{enter}');

    expect(mockOnSendMessage).toHaveBeenCalledWith('Hello');
    expect(input).toHaveValue('');
  });
});
