'use client';

import { TaskList } from '@/components/TaskList';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Real-Time Task List
        </h1>
        <TaskList />
      </div>
    </div>
  );
} 