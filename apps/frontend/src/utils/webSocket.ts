export const sendWebSocketMessage = (socket: WebSocket | null, data: unknown): boolean => {
  if (!socket || socket.readyState !== WebSocket.OPEN) {
    console.error('WebSocket is not connected');
    return false;
  }

  try {
    const message = typeof data === 'string' ? data : JSON.stringify(data);
    console.log(message);
    socket.send(message);
    return true;
  } catch (error) {
    console.error('Error sending message:', error);
    return false;
  }
};
