import React from 'react';
import { FiEdit2, FiTrash2, FiCheck, FiX } from 'react-icons/fi';
import { motion } from 'framer-motion';
import { format } from 'date-fns';
import { Task } from '@/types/task';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (id: number) => void;
  onToggleComplete: (id: number, completed: boolean) => void;
}

export const TaskCard: React.FC<TaskCardProps> = ({
  task,
  onEdit,
  onDelete,
  onToggleComplete,
}) => {
  const isExpired = task.expiry_date ? new Date(task.expiry_date) < new Date() : false;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-white rounded-lg shadow-md p-6 relative hover:shadow-lg transition-shadow duration-300"
    >
      <div className="absolute top-4 right-4 flex gap-2">
        <button
          onClick={() => onEdit(task)}
          className="text-gray-600 hover:text-blue-600 transition-colors"
          aria-label="Edit task"
        >
          <FiEdit2 size={18} />
        </button>
        <button
          onClick={() => onDelete(task.id)}
          className="text-gray-600 hover:text-red-600 transition-colors"
          aria-label="Delete task"
        >
          <FiTrash2 size={18} />
        </button>
      </div>

      <div className="mb-4 flex items-center gap-3">
        <button
          onClick={() => onToggleComplete(task.id, !task.completed)}
          className={`rounded-full p-1 transition-colors ${
            task.completed ? 'bg-green-500 text-white' : 'bg-gray-200'
          }`}
        >
          {task.completed ? <FiCheck size={16} /> : <FiX size={16} />}
        </button>
        <h3 className={`text-xl font-semibold ${task.completed ? 'line-through text-gray-500' : ''}`}>
          {task.title}
        </h3>
      </div>

      {task.description && (
        <p className="text-gray-600 mb-4">{task.description}</p>
      )}

      {task.expiry_date && (
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Due date:</span>
            <span className="text-sm font-medium">
              {format(new Date(task.expiry_date), 'MMM dd, yyyy')}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Status:</span>
            <span
              className={`text-sm font-medium px-2 py-1 rounded-full ${
                isExpired
                  ? 'bg-red-100 text-red-700'
                  : 'bg-green-100 text-green-700'
              }`}
            >
              {isExpired ? 'Expired' : 'Active'}
            </span>
          </div>
        </div>
      )}
    </motion.div>
  );
}; 