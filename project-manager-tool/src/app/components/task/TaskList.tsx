'use client';

import { useEffect, useState } from 'react';
import { Project, Task, TaskStatus } from '../../types';
import { loadProjectById, loadProjects, saveProjects } from '../../lib/storage';


export default function TaskList({ projectId }: { projectId: string }) {
  const [tasks, setTasks] = useState<Task[]>([]);

  useEffect(() => {
    refreshTasks();
  }, []);

  const refreshTasks = () => {
    const project = loadProjectById(projectId);
    setTasks(project?.tasks || []);
  };
  const updateTask = (updatedTask: Task) => {
  
    const project = loadProjectById(projectId);
    if (!project) return;

    project.tasks = project.tasks.map((task) =>
      task.id === updatedTask.id ? updatedTask : task
    );
    setTasks(project.tasks);
    saveProjects([...loadProjects().filter((p) => p.id !== project.id), project]);
  };


  return (
    <div className="mt-4">
      <h3 className="text-lg font-semibold">Tasks</h3>
      {tasks.length === 0 ? (
        <p>No tasks yet.</p>
      ) : (
        <ul className="space-y-2">
          {tasks.map((task) => (
              <li className="border p-2 rounded">
                <span>{task.title}</span> - <span>{task.status}</span>
                <select onChange={(e) => updateTask({ ...task, status: e.target.value as TaskStatus })}>
                  <option value={TaskStatus.TODO}>{TaskStatus.TODO}</option>
                  <option value={TaskStatus.IN_PROGRESS}>{TaskStatus.IN_PROGRESS}</option>
                  <option value={TaskStatus.DONE}>{TaskStatus.DONE}</option>
                </select>
                <button
                  onClick={() => {
                    const project = loadProjectById(projectId);
                    if (!project) return;

                    const updatedTasks = tasks.filter((t) => t.id !== task.id);
                    updateTask(task);
                    setTasks(updatedTasks);
                    refreshTasks();
                  }}
                  className="ml-2 bg-red-500 text-white p-1 rounded"
                >
                  Delete
                </button>
              </li>
          ))}
        </ul>
      )}
      <button
        onClick={() => setTasks([])}
        className="bg-red-500 text-white p-2 rounded"
      >
        Clear Tasks
      </button>
    </div>
  );
}