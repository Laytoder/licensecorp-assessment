/* eslint-disable */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiSave, FiX } from 'react-icons/fi';
import { Task } from '@/types/task';

interface TaskFormProps {
  initialData?: Task;
  onSubmit: (task: any) => void;
  onCancel: () => void;
}

export const TaskForm: React.FC<TaskFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    title: initialData?.title || '',
    description: initialData?.description || '',
    completed: initialData?.completed || false,
    expiry_date: initialData?.expiry_date || '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Only include non-empty optional fields
    const submissionData = {
      ...formData,
      description: formData.description.trim() || undefined,
      expiry_date: formData.expiry_date || undefined,
    };
    onSubmit(initialData ? { ...submissionData, id: initialData.id } : submissionData);
  };

  return (
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      onSubmit={handleSubmit}
      className="bg-white rounded-lg shadow-md p-6 relative hover:shadow-lg transition-shadow duration-300"
    >
      <div className="absolute top-4 right-4 flex gap-2">
        <button
          type="submit"
          className="text-gray-600 hover:text-green-600 transition-colors"
          aria-label="Save task"
        >
          <FiSave size={18} />
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="text-gray-600 hover:text-red-600 transition-colors"
          aria-label="Cancel"
        >
          <FiX size={18} />
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            type="text"
            id="title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description (optional)
          </label>
          <textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
          />
        </div>

        <div>
          <label htmlFor="expiry_date" className="block text-sm font-medium text-gray-700 mb-1">
            Due Date (optional)
          </label>
          <input
            type="date"
            id="expiry_date"
            value={formData.expiry_date}
            onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="completed"
            checked={formData.completed}
            onChange={(e) => setFormData({ ...formData, completed: e.target.checked })}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="completed" className="text-sm font-medium text-gray-700">
            Mark as completed
          </label>
        </div>
      </div>
    </motion.form>
  );
}; 