import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiPlus, FiChevronLeft, FiChevronRight } from 'react-icons/fi';
import { TaskCard } from './TaskCard';
import { TaskForm } from './TaskForm';
import { useTasks } from '@/hooks/useTasks';
import { Task } from '@/types/task';

export const TaskList: React.FC = () => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  
  const {
    tasks,
    loading,
    error,
    currentPage,
    totalPages,
    goToPage,
    createTask,
    updateTask,
    deleteTask,
  } = useTasks();

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

  // Generate pagination buttons
  const renderPaginationButtons = () => {
    const buttons = [];
    const maxVisibleButtons = 7; // Maximum number of page buttons to show (increased from 5)
    
    // For small numbers of pages, just show all buttons
    if (totalPages <= maxVisibleButtons) {
      // Show all pages directly without ellipsis
      for (let i = 1; i <= totalPages; i++) {
        buttons.push(
          <button
            key={`page-${i}`}
            onClick={() => goToPage(i)}
            className={`px-3 py-1 rounded-md ${currentPage === i 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-200 hover:bg-gray-300'}`}
          >
            {i}
          </button>
        );
      }
      return buttons;
    }
    
    // For larger numbers of pages, we need to show a subset with ellipsis
    
    // Always show first page
    buttons.push(
      <button
        key="first-page"
        onClick={() => goToPage(1)}
        className={`px-3 py-1 rounded-md ${currentPage === 1 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-200 hover:bg-gray-300'}`}
      >
        1
      </button>
    );
    
    // Calculate the range of page numbers to display
    let startPage, endPage;
    
    if (currentPage <= 4) {
      // Near the beginning: show first 5 pages then ellipsis then last page
      startPage = 2;
      endPage = 5;
      
      // Add pages 2-5
      for (let i = startPage; i <= endPage; i++) {
        if (i <= totalPages - 1) {
          buttons.push(
            <button
              key={`middle-page-${i}`}
              onClick={() => goToPage(i)}
              className={`px-3 py-1 rounded-md ${currentPage === i 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 hover:bg-gray-300'}`}
            >
              {i}
            </button>
          );
        }
      }
      
      // Add ellipsis if needed
      if (totalPages > 6) {
        buttons.push(<span key="end-ellipsis" className="px-2">...</span>);
      }
      
    } else if (currentPage >= totalPages - 3) {
      // Near the end: show first page then ellipsis then last 5 pages
      startPage = totalPages - 4;
      endPage = totalPages - 1;
      
      // Add ellipsis if needed
      if (startPage > 2) {
        buttons.push(<span key="start-ellipsis" className="px-2">...</span>);
      }
      
      // Add pages totalPages-4 to totalPages-1
      for (let i = startPage; i <= endPage; i++) {
        if (i >= 2) {
          buttons.push(
            <button
              key={`middle-page-${i}`}
              onClick={() => goToPage(i)}
              className={`px-3 py-1 rounded-md ${currentPage === i 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 hover:bg-gray-300'}`}
            >
              {i}
            </button>
          );
        }
      }
      
    } else {
      // In the middle: show first page, ellipsis, current-1 to current+1, ellipsis, last page
      startPage = currentPage - 1;
      endPage = currentPage + 1;
      
      // Add first ellipsis
      buttons.push(<span key="start-ellipsis" className="px-2">...</span>);
      
      // Add the current page and its neighbors
      for (let i = startPage; i <= endPage; i++) {
        buttons.push(
          <button
            key={`middle-page-${i}`}
            onClick={() => goToPage(i)}
            className={`px-3 py-1 rounded-md ${currentPage === i 
              ? 'bg-blue-600 text-white' 
              : 'bg-gray-200 hover:bg-gray-300'}`}
          >
            {i}
          </button>
        );
      }
      
      // Add last ellipsis
      buttons.push(<span key="end-ellipsis" className="px-2">...</span>);
    }
    
    // Always show last page
    buttons.push(
      <button
        key="last-page"
        onClick={() => goToPage(totalPages)}
        className={`px-3 py-1 rounded-md ${currentPage === totalPages 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-200 hover:bg-gray-300'}`}
      >
        {totalPages}
      </button>
    );
    
    return buttons;
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

      {/* Page information */}
      <div className="mb-4 text-center text-sm text-gray-500">
        Page {currentPage} of {totalPages} ({tasks.length} tasks)
      </div>

      {/* Tasks */}
      <div className="space-y-6 mb-8">
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

          {/* Loading indicator */}
          {loading && (
            <motion.div
              key="loading-indicator"
              className="h-20 flex items-center justify-center"
            >
              <motion.div
                key="spinner"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Pagination */}
      <div className="flex justify-center items-center gap-2 mt-6">
        <button
          onClick={() => goToPage(currentPage - 1)}
          disabled={currentPage === 1}
          className={`p-2 rounded-md ${currentPage === 1 
            ? 'text-gray-400 cursor-not-allowed' 
            : 'bg-gray-200 hover:bg-gray-300'}`}
        >
          <FiChevronLeft />
        </button>
        
        {renderPaginationButtons()}
        
        <button
          onClick={() => goToPage(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={`p-2 rounded-md ${currentPage === totalPages 
            ? 'text-gray-400 cursor-not-allowed' 
            : 'bg-gray-200 hover:bg-gray-300'}`}
        >
          <FiChevronRight />
        </button>
      </div>
    </div>
  );
};