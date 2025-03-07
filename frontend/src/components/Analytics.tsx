import React from 'react';
import { motion } from 'framer-motion';
import { FiPlusCircle, FiEdit, FiTrash2 } from 'react-icons/fi';
import { useAnalytics } from '@/hooks/useAnalytics';

export const Analytics: React.FC = () => {
  const { counters, loading, error } = useAnalytics();
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <h2 className="text-xl font-semibold mb-4 text-gray-800">Real-Time Analytics</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {loading ? (
        <div className="flex justify-center p-4">
          <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <CounterCard 
            title="Tasks Created" 
            count={counters.tasks_created} 
            icon={<FiPlusCircle className="text-green-500" size={24} />} 
          />
          <CounterCard 
            title="Tasks Updated" 
            count={counters.tasks_updated} 
            icon={<FiEdit className="text-blue-500" size={24} />} 
          />
          <CounterCard 
            title="Tasks Deleted" 
            count={counters.tasks_deleted} 
            icon={<FiTrash2 className="text-red-500" size={24} />} 
          />
        </div>
      )}
    </div>
  );
};

interface CounterCardProps {
  title: string;
  count: number;
  icon: React.ReactNode;
}

const CounterCard: React.FC<CounterCardProps> = ({ title, count, icon }) => {
  return (
    <motion.div 
      className="bg-gray-50 rounded-lg p-4 border border-gray-200"
      initial={{ opacity: 0, y: 5 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
    >
      <div className="flex items-center mb-2">
        {icon}
        <h3 className="ml-2 font-medium text-gray-700">{title}</h3>
      </div>
      <div className="mt-2">
        <span className="text-3xl font-bold text-gray-800">
          <AnimatedCounter value={count} />
        </span>
      </div>
    </motion.div>
  );
};

// Animated counter for smooth transitions
interface AnimatedCounterProps {
  value: number;
}

const AnimatedCounter: React.FC<AnimatedCounterProps> = ({ value }) => {
  return (
    <motion.span
      key={value}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
    >
      {value.toLocaleString()}
    </motion.span>
  );
}; 