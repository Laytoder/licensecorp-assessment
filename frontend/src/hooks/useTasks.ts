import { useState, useCallback, useEffect, useRef } from 'react';
import { Task, CreateTaskInput, UpdateTaskInput } from '@/types/task';
import { useWebSocket } from './useWebSocket';
import { api } from '@/lib/api';

const WINDOW_SIZE = 60; // Keep 3 pages worth of tasks (assuming 20 tasks per page)
const CLEANUP_THRESHOLD = 80; // Start cleanup when we exceed this number of tasks

export const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const loadedTaskIds = useRef(new Set<number>());

  // Cleanup function to maintain window size
  const cleanupTasks = useCallback((currentTasks: Task[]) => {
    if (currentTasks.length > CLEANUP_THRESHOLD) {
      const tasksToKeep = currentTasks.slice(-WINDOW_SIZE);
      // Update loadedTaskIds to match the kept tasks
      loadedTaskIds.current = new Set(tasksToKeep.map(task => task.id));
      return tasksToKeep;
    }
    return currentTasks;
  }, []);

  // Memoize the WebSocket message handler
  const handleWebSocketMessage = useCallback((message: { event: string; task?: Task; id?: number }) => {
    switch (message.event) {
      case 'created':
        if (currentPage === 1) { // Only add new tasks if we're on the first page
          setTasks(prev => [message.task!, ...cleanupTasks(prev)]);
          loadedTaskIds.current.add(message.task!.id);
        }
        break;
      case 'updated':
        if (loadedTaskIds.current.has(message.task!.id)) {
          setTasks(prev => prev.map(task => 
            task.id === message.task!.id ? message.task! : task
          ));
        }
        break;
      case 'deleted':
        if (loadedTaskIds.current.has(message.id!)) {
          setTasks(prev => prev.filter(task => task.id !== message.id));
          loadedTaskIds.current.delete(message.id!);
        }
        break;
    }
  }, [currentPage, cleanupTasks]);

  // Handle WebSocket updates only for loaded tasks
  const { isConnected } = useWebSocket(handleWebSocketMessage);

  const loadMoreTasks = useCallback(async () => {
    if (loading || !hasMore) return;

    try {
      setLoading(true);
      const newTasks = await api.getTasks(currentPage);
      
      if (newTasks.length === 0) {
        setHasMore(false);
      } else {
        setTasks(prev => {
          const combined = [...prev, ...newTasks];
          // Update loaded task IDs and cleanup if necessary
          newTasks.forEach((task: Task) => loadedTaskIds.current.add(task.id));
          return cleanupTasks(combined);
        });
        setCurrentPage(prev => prev + 1);
      }
      setError(null);
    } catch (err) {
      setError('Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  }, [currentPage, loading, hasMore, cleanupTasks]);

  const createTask = async (input: CreateTaskInput) => {
    try {
      await api.createTask(input);
      setError(null);
    } catch (err) {
      setError('Failed to create task');
    }
  };

  const updateTask = async (id: number, input: UpdateTaskInput) => {
    try {
      await api.updateTask(id, input);
      setError(null);
    } catch (err) {
      setError('Failed to update task');
    }
  };

  const deleteTask = async (id: number) => {
    try {
      await api.deleteTask(id);
      setError(null);
    } catch (err) {
      setError('Failed to delete task');
    }
  };

  // Load initial page only after WebSocket connection is established
  useEffect(() => {
    if (isConnected) {
      loadMoreTasks();
    }
  }, [isConnected, loadMoreTasks]); // Load first page when WebSocket connects

  return {
    tasks,
    loading,
    error,
    hasMore,
    loadMoreTasks,
    createTask,
    updateTask,
    deleteTask,
    isConnected,
  };
}; 