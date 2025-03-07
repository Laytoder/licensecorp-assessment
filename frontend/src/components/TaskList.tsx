import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiPlus } from 'react-icons/fi';
import { TaskCard } from './TaskCard';
import { TaskForm } from './TaskForm';
import { useTasks } from '@/hooks/useTasks';
import { useInfiniteScroll } from '@/hooks/useInfiniteScroll';
import { Task } from '@/types/task';

export const TaskList: React.FC = () => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  
  const {
    tasks,
    loading,
    error,
    hasMore,
    loadMoreTasks,
    createTask,
    updateTask,
    deleteTask,
  } = useTasks();

  const { setTarget } = useInfiniteScroll({
    onIntersect: loadMoreTasks,
    enabled: hasMore && !loading,
  });

  const handleAddSubmit = async (taskData: Omit<Task, 'id'>) => {
    try {
      await createTask(taskData);
      setShowAddForm(false);
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const handleEditSubmit = async (task: Task) => {
    try {
      await updateTask(task.id, task);
      setEditingTask(null);
    } catch (error) {
      console.error('Failed to update task:', error);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Error message */}
      {error && (
        <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Add Task Button */}
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

      {/* Task List */}
      <div className="space-y-6">
        <AnimatePresence mode="popLayout">
          {/* Add Form */}
          {showAddForm && (
            <motion.div
              key="add-form"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              layout
            >
              <TaskForm
                onSubmit={handleAddSubmit}
                onCancel={() => setShowAddForm(false)}
              />
            </motion.div>
          )}

          {/* Tasks */}
          {tasks.map((task) => (
            <motion.div
              key={`task-${task.id}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              layout
            >
              {editingTask?.id === task.id ? (
                <TaskForm
                  key={`edit-form-${task.id}`}
                  initialData={task}
                  onSubmit={handleEditSubmit}
                  onCancel={() => setEditingTask(null)}
                />
              ) : (
                <TaskCard
                  key={`task-card-${task.id}`}
                  task={task}
                  onEdit={setEditingTask}
                  onDelete={deleteTask}
                  onToggleComplete={(id, completed) => updateTask(id, { completed })}
                />
              )}
            </motion.div>
          ))}

          {/* Loading indicator and intersection observer target */}
          <motion.div
            key="loading-indicator"
            ref={setTarget}
            className="h-20 flex items-center justify-center"
          >
            {loading && (
              <motion.div
                key="spinner"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"
              />
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};