import { Task } from '@/types/task';
import { useEffect, useRef } from 'react';

interface WebSocketMessage {
  event: 'created' | 'updated' | 'deleted';
  id?: number;
  task?: Task
}

export const useWebSocket = (onMessage: (data: WebSocketMessage) => void) => {
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8001/ws/');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return () => {
      ws.close();
    };
  }, [onMessage]);

  return wsRef.current;
}; 