import { useEffect, useRef, useState } from 'react';
import { config } from '@/config/env';
import { Task } from '@/types/task';

interface WebSocketMessage {
  event: 'created' | 'updated' | 'deleted' | 'counter_updated';
  id?: number;
  task?: Task;
  counter?: string;
  value?: number;
  timestamp?: string;
}

export const useWebSocket = (onMessage: (data: WebSocketMessage) => void) => {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    let ws: WebSocket | null = null;

    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        return; // Already connected
      }

      console.log("connecting to socket");
      ws = new WebSocket(config.wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onMessage(data);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        wsRef.current = null;
      };
    };

    connect();

    return () => {
      if (ws) {
        ws.close();
        wsRef.current = null;
        setIsConnected(false);
      }
    };
  }, [onMessage]);

  return { ws: wsRef.current, isConnected };
};