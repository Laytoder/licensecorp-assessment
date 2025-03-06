import { useState, useCallback, useEffect } from 'react';
import { Task, CreateTaskInput, UpdateTaskInput } from '@/types/task';
import { useWebSocket } from './useWebSocket';
import { api } from '@/lib/api';

export const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useWebSocket((message) => {
    switch (message.event) {
      case 'created':
        setTasks(prev => [...prev, message.task!]);
        break;
      case 'updated':
        setTasks(prev => prev.map(task => 
          task.id === message.task!.id ? message.task as Task : task
        ));
        break;
      case 'deleted':
        setTasks(prev => prev.filter(task => task.id !== message.id));
        break;
    }
  });

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getTasks();
      setTasks(data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  const createTask = async (input: CreateTaskInput) => {
    try {
      await api.createTask(input);
      setError(null);
    } catch (err) {
      setError('Failed to create task');
    }
  }

  const updateTask = async (id: number, input: UpdateTaskInput) => {
    try {
      await api.updateTask(id, input);
      setError(null);
    } catch (err) {
      setError('Failed to update task');
    }
  }

  const deleteTask = async (id: number) => {
    try {
      await api.deleteTask(id);
      setError(null);
    } catch (err) {
      setError('Failed to delete task');
    }
  }

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  return {
    tasks,
    loading,
    error,
    createTask,
    updateTask,
    deleteTask,
  };
}; 