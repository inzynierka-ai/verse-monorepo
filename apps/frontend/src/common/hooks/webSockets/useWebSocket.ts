import { useEffect, useRef, useCallback, useState } from 'react';

interface WebSocketConfig {
  url: string;
  onMessage: (event: MessageEvent) => void;
  onOpen?: () => void;
  onClose?: () => void;
  reconnectAttempts?: number;
  initialDelay?: number;
  maxDelay?: number;
  enabled?: boolean;
  headers?: Record<string, string>;
}

interface WebSocketHookReturn {
  socket: WebSocket | null;
  isConnected: boolean;
  reconnect: () => void;
}

// Keep track of active connections globally to prevent duplicates
const activeConnections = new Map<string, WebSocket>();

export const useWebSocket = ({
  url,
  onMessage,
  onOpen,
  onClose,
  reconnectAttempts = 5,
  initialDelay = 1000,
  maxDelay = 30000,
  enabled = true,
  headers,
}: WebSocketConfig): WebSocketHookReturn => {
  const socket = useRef<WebSocket | null>(null);
  const attempts = useRef(0);
  const [isConnected, setIsConnected] = useState(false);
  const connectTimeoutRef = useRef<number | null>(null);
  const instanceIdRef = useRef<string>(Math.random().toString(36).substring(2, 9));
  
  // Store headers in a ref to prevent unnecessary reconnections
  const headersRef = useRef(headers);
  
  // Update headers ref when headers change
  useEffect(() => {
    headersRef.current = headers;
  }, [headers]);

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

  // Clear any pending connection timeouts
  const clearConnectionTimeout = useCallback(() => {
    if (connectTimeoutRef.current !== null) {
      window.clearTimeout(connectTimeoutRef.current);
      connectTimeoutRef.current = null;
    }
  }, []);

  const connect = useCallback(() => {
    // Don't connect if not enabled or URL is missing
    if (!enabled || !url) {
      if (socket.current) {
        socket.current.close();
        socket.current = null;
        setIsConnected(false);
        activeConnections.delete(`${url}-${instanceIdRef.current}`);
      }
      return;
    }

    // Check if we already have an active connection
    if (socket.current?.readyState === WebSocket.OPEN || 
        socket.current?.readyState === WebSocket.CONNECTING) {
      console.log('WebSocket connection already exists, not creating a new one');
      return;
    }

    // Check if there's already an active connection for this URL globally
    const connectionKey = `${url}-${instanceIdRef.current}`;
    const existingConnection = activeConnections.get(connectionKey);
    
    if (existingConnection && 
        (existingConnection.readyState === WebSocket.OPEN || 
         existingConnection.readyState === WebSocket.CONNECTING)) {
      console.log('Using existing WebSocket connection');
      socket.current = existingConnection;
      
      // If it's already open, trigger the onOpen handler
      if (existingConnection.readyState === WebSocket.OPEN) {
        setIsConnected(true);
        onOpenRef.current?.();
      }
      return;
    }

    console.log(`Creating new WebSocket connection to ${url}`);
    
    // Create a new connection
    const newSocket = new WebSocket(url);
    socket.current = newSocket;
    activeConnections.set(connectionKey, newSocket);

    newSocket.onopen = () => {
      console.log(`WebSocket connected to ${url}`);
      setIsConnected(true);
      attempts.current = 0;
      
      // Send authentication headers if provided
      if (headersRef.current && Object.keys(headersRef.current).length > 0) {
        console.log('Sending authentication message');
        const authMessage = {
          type: 'AUTHENTICATE',
          payload: headersRef.current
        };
        
        if (newSocket.readyState === WebSocket.OPEN) {
          newSocket.send(JSON.stringify(authMessage));
        }
      }
      
      onOpenRef.current?.();
    };

    newSocket.onclose = (event) => {
      console.log(`WebSocket closed: ${event.code} ${event.reason}`);
      setIsConnected(false);
      onCloseRef.current?.();
      
      activeConnections.delete(connectionKey);

      // Only attempt reconnection if this was an abnormal closure 
      // and we haven't exceeded attempts
      if (enabled && 
          attempts.current < reconnectAttempts && 
          event.code !== 1000 && // Normal closure
          event.code !== 1001) { // Going away (page navigation) 
          
        const delay = getBackoffDelay(attempts.current);
        attempts.current++;
        
        console.log(`Attempting reconnect in ${delay}ms (attempt ${attempts.current}/${reconnectAttempts})`);
        
        clearConnectionTimeout();
        connectTimeoutRef.current = window.setTimeout(() => {
          connectTimeoutRef.current = null;
          connect();
        }, delay);
      }
    };

    newSocket.onmessage = (event) => {
      onMessageRef.current(event);
    };

    newSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, [url, enabled, getBackoffDelay, reconnectAttempts, clearConnectionTimeout]);

  const reconnect = useCallback(() => {
    // Only reconnect if we're not already connected/connecting
    if (enabled && 
        (!socket.current || 
         (socket.current.readyState !== WebSocket.OPEN && 
          socket.current.readyState !== WebSocket.CONNECTING))) {
      
      console.log('Manual reconnection triggered');
      
      // Close existing socket if any
      if (socket.current) {
        const oldSocket = socket.current;
        socket.current = null;
        
        try {
          oldSocket.close();
        } catch (e) {
          console.error('Error closing socket during reconnect:', e);
        }
      }
      
      // Reset attempts for manual reconnection
      attempts.current = 0;
      
      // Clear any pending reconnection attempt
      clearConnectionTimeout();
      
      // Trigger connection with small delay to avoid rapid reconnects
      connectTimeoutRef.current = window.setTimeout(() => {
        connectTimeoutRef.current = null;
        connect();
      }, 100);
    } else {
      console.log('Reconnect ignored - already connected or connecting');
    }
  }, [connect, enabled, clearConnectionTimeout]);

  // Effect for initial connection and cleanup
  useEffect(() => {
    if (enabled) {
      connect();
    } else if (socket.current) {
      socket.current.close();
      socket.current = null;
      setIsConnected(false);
      activeConnections.delete(`${url}-${instanceIdRef.current}`);
    }
    
    // Cleanup on unmount or url/enabled change
    return () => {
      clearConnectionTimeout();
      
      if (socket.current) {
        const connectionKey = `${url}-${instanceIdRef.current}`;
        activeConnections.delete(connectionKey);
        
        const oldSocket = socket.current;
        socket.current = null;
        
        try {
          oldSocket.close();
        } catch (e) {
          console.error('Error during socket cleanup:', e);
        }
      }
    };
  }, [url, enabled, connect, clearConnectionTimeout]);

  return {
    socket: socket.current,
    isConnected,
    reconnect,
  };
};