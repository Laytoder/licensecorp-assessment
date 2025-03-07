/* eslint-disable */

import { useState, useCallback, useEffect } from 'react';
import { useWebSocket } from './useWebSocket';
import { api } from '@/lib/api';

interface Counters {
  tasks_created: number;
  tasks_updated: number;
  tasks_deleted: number;
}

export const useAnalytics = () => {
  const [counters, setCounters] = useState<Counters>({
    tasks_created: 0,
    tasks_updated: 0,
    tasks_deleted: 0
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load initial analytics data
  const loadAnalytics = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getAnalytics();
      setCounters(data);
      setError(null);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error('Analytics error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Handle WebSocket messages for counter updates
  const handleWebSocketMessage = useCallback((message: any) => {
    if (message.event === 'counter_updated' && message.counter && message.value !== undefined) {
      setCounters(prev => ({
        ...prev,
        [message.counter]: message.value
      }));
    }
  }, []);

  // Connect to WebSocket
  const { isConnected } = useWebSocket(handleWebSocketMessage);

  // Load initial data when WebSocket connects
  useEffect(() => {
    if (isConnected) {
      loadAnalytics();
    }
  }, [isConnected, loadAnalytics]);

  return {
    counters,
    loading,
    error,
    isConnected
  };
}; 