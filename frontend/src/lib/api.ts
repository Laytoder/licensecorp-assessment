import { config } from '@/config/env';
import { CreateTaskInput, UpdateTaskInput } from '@/types/task';

export const api = {
  async getTasks() {
    const response = await fetch(`${config.apiUrl}/tasks`);
    if (!response.ok) throw new Error('Failed to fetch tasks');
    return response.json();
  },

  async createTask(data: CreateTaskInput) {
    const response = await fetch(`${config.apiUrl}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create task');
    return response.json();
  },

  async updateTask(id: number, data: UpdateTaskInput) {
    const response = await fetch(`${config.apiUrl}/tasks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update task');
    return response.json();
  },

  async deleteTask(id: number) {
    const response = await fetch(`${config.apiUrl}/tasks/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete task');
    return response.json();
  },
};  