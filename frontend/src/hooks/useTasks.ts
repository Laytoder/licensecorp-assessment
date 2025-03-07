/* eslint-disable */

import { useState, useCallback, useEffect, useRef } from 'react';
import { Task, CreateTaskInput, UpdateTaskInput } from '@/types/task';
import { useWebSocket } from './useWebSocket';
import { api } from '@/lib/api';

const TASKS_PER_PAGE = 20; // Standard number of tasks per page

export const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const initialLoadDone = useRef(false);

  // Memoize the WebSocket message handler
  const handleWebSocketMessage = useCallback((message: { event: string; task?: Task; id?: number }) => {
    switch (message.event) {
      case 'created':
        // If we're on page 1, add the new task at the top
        if (currentPage === 1) {
          setTasks(prev => [message.task!, ...prev]);
        }
        break;
      case 'updated':
        // Update task if it's on the current page
        setTasks(prev => 
          prev.map(task => task.id === message.task!.id ? message.task! : task)
        );
        break;
      case 'deleted':
        // Remove task if it's on the current page
        setTasks(prev => prev.filter(task => task.id !== message.id));
        break;
    }
  }, [currentPage]);

  // Handle WebSocket updates
  const { isConnected } = useWebSocket(handleWebSocketMessage);

  // Load tasks for a specific page
  const loadPage = useCallback(async (pageNumber: number) => {
    if (loading) return;

    try {
      setLoading(true);
      const response = await api.getTasks(pageNumber);
      
      // Assuming the API returns { tasks: Task[], total_pages: number }
      if (response.tasks) {
        setTasks(response.tasks);
        setTotalPages(response.total_pages || Math.ceil(response.total_count / TASKS_PER_PAGE) || 1);
      } else {
        // Fallback if API doesn't return expected structure
        setTasks(response);
        // Estimate total pages based on whether we got a full page
        if (response.length < TASKS_PER_PAGE && pageNumber === 1) {
          setTotalPages(1);
        } else if (response.length < TASKS_PER_PAGE) {
          setTotalPages(pageNumber);
        } else {
          setTotalPages(Math.max(totalPages, pageNumber + 1));
        }
      }
      
      setCurrentPage(pageNumber);
      setError(null);
    } catch (err) {
      setError('Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  }, [loading, totalPages]);

  // Go to a specific page
  const goToPage = useCallback((pageNumber: number) => {
    // Ensure page number is valid
    const page = Math.max(1, Math.min(pageNumber, totalPages));
    loadPage(page);
  }, [loadPage, totalPages]);

  const createTask = async (input: CreateTaskInput) => {
    try {
      await api.createTask(input);
      // After creating a task, go back to page 1
      goToPage(1);
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
      // Refresh current page after delete
      goToPage(currentPage);
      setError(null);
    } catch (err) {
      setError('Failed to delete task');
    }
  };

  // Load initial page when WebSocket connects and only once
  useEffect(() => {
    if (isConnected && !initialLoadDone.current) {
      initialLoadDone.current = true;
      loadPage(1);
    }
  }, [isConnected]); // Removed loadPage from dependencies to prevent infinite calls

  return {
    tasks,
    loading,
    error,
    currentPage,
    totalPages,
    goToPage,
    createTask,
    updateTask,
    deleteTask,
    isConnected,
  };
}; 