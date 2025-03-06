import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiPlus } from 'react-icons/fi';
import { TaskCard } from './TaskCard';
import { TaskForm } from './TaskForm';
import { useTasks } from '@/hooks/useTasks';
import { Task } from '@/types/task';

export const TaskList = () => {
  const { tasks, loading, error, createTask, updateTask, deleteTask } = useTasks();
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  const handleEdit = (task: Task) => {
    setEditingTask(task);
  };

  const handleAddSubmit = (task: Omit<Task, 'id'>) => {
    createTask(task);
    setShowAddForm(false);
  };

  const handleEditSubmit = (task: Task) => {
    updateTask(task.id, task);
    setEditingTask(null);
  };

  const handleToggleComplete = (id: number, completed: boolean) => {
    updateTask(id, { completed });
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-8 flex justify-center">
        {!showAddForm && (
          <motion.button
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={() => setShowAddForm(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors shadow-md"
          >
            <FiPlus size={20} />
            Add Task
          </motion.button>
        )}
      </div>

      <div className="grid gap-6 grid-cols-1">
        <AnimatePresence>
          {showAddForm && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <TaskForm
                onSubmit={handleAddSubmit}
                onCancel={() => setShowAddForm(false)}
              />
            </motion.div>
          )}

          {tasks.map((task) => (
            editingTask?.id === task.id ? (
              <TaskForm
                key={task.id}
                initialData={task}
                onSubmit={handleEditSubmit}
                onCancel={() => setEditingTask(null)}
              />
            ) : (
              <TaskCard
                key={task.id}
                task={task}
                onEdit={handleEdit}
                onDelete={deleteTask}
                onToggleComplete={handleToggleComplete}
              />
            )
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};