'use client';

import { useState } from 'react';
import { saveProjects, loadProjects, loadProjectById } from '../../lib/storage';
import { v4 as uuidv4 } from 'uuid';
import { Task, TaskStatus } from '@/app/types';

export default function TaskForm({ projectId, onTaskAdded }: { projectId: string; onTaskAdded: () => void }) {
  const [Task, setTask] = useState<Task>({
    id: uuidv4(),
    title: '',
    status: TaskStatus.TODO,
    projectId: projectId,
  });
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const projects = loadProjects();

    const updatedProjects = projects.map((project) =>
      project.id === projectId
        ? {
            ...project,
            tasks: [...project.tasks, { id: Task.id, title: Task.title, status: Task.status, projectId: Task.projectId }],
          }
        : project
    );
  
    saveProjects(updatedProjects);
    onTaskAdded();
  
   
  };


  const handleRemoveTask = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    const projects = loadProjects();
    const updatedProjects = projects.map((project) =>
      project.id === projectId
        ? {
            ...project,
            tasks: project.tasks.filter((task) => task.id !== Task.id),
          }
        : project
    );
    saveProjects(updatedProjects);
    onTaskAdded();
  };

  return (
    <form onSubmit={handleSubmit} className="mt-4">
      <div className="mb-2">
        <input
          type="text"
          value={Task?.title || ''}
          onChange={(e) => setTask({ ...Task, title: e.target.value })}
          placeholder="Task Title"
          className="w-full p-2 border rounded"
          required
        />
      </div>
      <div className="mb-2">
        <select
          value={Task?.status || TaskStatus.TODO}
          onChange={(e) => setTask({ ...Task, status: e.target.value as TaskStatus })}
          className="p-2 border rounded"
        >
          <option value={TaskStatus.TODO}>{TaskStatus.TODO}</option>
          <option value={TaskStatus.IN_PROGRESS}>{TaskStatus.IN_PROGRESS}</option>
          <option value={TaskStatus.DONE}>{TaskStatus.DONE}</option>
        </select>
      </div>
      <button type="submit" name="add-task"className="bg-green-500 text-white p-2 rounded">
        Add Task
      </button>
    </form>
  );
}