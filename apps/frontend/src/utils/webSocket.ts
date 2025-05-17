export const sendWebSocketMessage = (socket: WebSocket | null, data: unknown): boolean => {
  console.log('Sending message:', data, socket);
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.error('WebSocket is not connected');
    return false;
  }

  console.log('WebSocket is connected');

  try {
    const message = typeof data === 'string' ? data : JSON.stringify(data);
    socket.send(message);
    return true;
  } catch (error) {
    console.error('Error sending message:', error);
    return false;
  }
};
