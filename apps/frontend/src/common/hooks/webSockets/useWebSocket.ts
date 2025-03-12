import { useEffect, useRef, useCallback, useState } from 'react';

interface WebSocketConfig {
  url: string;
  onMessage: (event: MessageEvent) => void;
  onOpen?: () => void;
  onClose?: () => void;
  reconnectAttempts?: number;
  initialDelay?: number;
  maxDelay?: number;
}

interface WebSocketHookReturn {
  socket: WebSocket | null;
  isConnected: boolean;
  reconnect: () => void;
}

export const useWebSocket = ({
  url,
  onMessage,
  onOpen,
  onClose,
  reconnectAttempts = 5,
  initialDelay = 1000,
  maxDelay = 30000,
}: WebSocketConfig): WebSocketHookReturn => {
  const socket = useRef<WebSocket | null>(null);
  const attempts = useRef(0);
  const [isConnected, setIsConnected] = useState(false);

  // Add refs for callbacks
  const onMessageRef = useRef(onMessage);
  const onOpenRef = useRef(onOpen);
  const onCloseRef = useRef(onClose);

  // Update refs when callbacks change
  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    onOpenRef.current = onOpen;
  }, [onOpen]);

  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  const getBackoffDelay = useCallback(
    (attempt: number) => {
      const delay = initialDelay * Math.pow(2, attempt);
      return Math.min(delay, maxDelay);
    },
    [initialDelay, maxDelay],
  );

  const connect = useCallback(() => {
    // if (socket.current) {
    //   socket.current.close();
    // }

    socket.current = new WebSocket(url);

    socket.current.onopen = () => {
      setIsConnected(true);
      attempts.current = 0;
      onOpenRef.current?.();
    };

    socket.current.onclose = () => {
      setIsConnected(false);
      onCloseRef.current?.();

      if (attempts.current < reconnectAttempts) {
        const delay = getBackoffDelay(attempts.current);

        attempts.current++;
        setTimeout(() => connect(), delay);
      }
    };

    socket.current.onmessage = (event) => {
      onMessageRef.current(event);
    };

    socket.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, [url, reconnectAttempts, getBackoffDelay]);

  const reconnect = useCallback(() => {
    attempts.current = 0;
    connect();
  }, [connect]);

  useEffect(() => {
    connect();
    return () => {
      if (socket.current) {
        socket.current.close();
      }
    };
  }, [connect]);

  return {
    socket: socket.current,
    isConnected,
    reconnect,
  };
};
