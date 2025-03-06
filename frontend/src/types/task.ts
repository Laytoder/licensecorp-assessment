export interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  expiry_date?: string;
  created_at: string;
}

export interface CreateTaskInput {
  title: string;
  description?: string;
  completed?: boolean;
  expiry_date?: string;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string;
  completed?: boolean;
  expiry_date?: string;
} 