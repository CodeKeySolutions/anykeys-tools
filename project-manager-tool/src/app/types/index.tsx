export interface Task {
  id: string;
  title: string;
  status: TaskStatus;
  projectId: string;
}
export enum TaskStatus {
  TODO = 'To-Do',
  IN_PROGRESS = 'In Progress',
  DONE = 'Done',
}

export interface Project {
  id: string;
  name: string;
  description: string;
  tasks: Task[];
}