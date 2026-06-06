'use client';

import { useEffect, useState } from 'react';
import { Project } from '../../types';
import { loadProjects } from '../../lib/storage';
import TaskForm from '../task/TaskForm';
import TaskList from '../task/TaskList';
import ProjectForm from './ProjectForm';

export default function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);

  const refreshProjects = () => {
    setProjects(loadProjects());
  };

  useEffect(() => {
    refreshProjects();
  }, []);

  return (
    <div className="space-y-6">
      <ProjectForm onProjectAdded={refreshProjects} />
      {projects.map((project) => (
        <div key={project.id} className="border p-4 rounded">
          <h2 className="text-xl font-bold">{project.name}</h2>
          <p>{project.description}</p>
          <TaskForm projectId={project.id} onTaskAdded={refreshProjects} />
          <TaskList projectId={project.id} />
          <button
            onClick={() => {
              const updatedProjects = projects.filter((p) => p.id !== project.id);
              localStorage.setItem('projects', JSON.stringify(updatedProjects));
              refreshProjects();
            }}
            className="mt-2 bg-red-500 text-white p-2 rounded"
          >
            Delete Project
          </button>
        </div>
        
      ))}
    </div>
  );
}