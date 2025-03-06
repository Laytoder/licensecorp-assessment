import { useEffect } from 'react';
import { useTasks } from '@/hooks/useTasks';
import { TaskItem } from './TaskItem';
import { TaskForm } from './TaskForm';

export const TaskList = () => {
  const { tasks, loading, error, createTask, updateTask, deleteTask } = useTasks();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-8">Task List</h1>
      <TaskForm onSubmit={(title, description) => createTask({ title, description })} />
      <div className="space-y-4 mt-8">
        {tasks.map((task) => (
          <TaskItem 
            key={task.id} 
            task={task}
            onUpdate={(id, completed) => updateTask(id, { completed })}
            onDelete={deleteTask}
          />
        ))}
      </div>
    </div>
  );
}; 