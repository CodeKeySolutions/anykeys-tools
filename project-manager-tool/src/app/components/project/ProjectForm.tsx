'use client';

import { useState } from 'react';
import { Project } from '../../types';
import { loadProjects, saveProjects } from '../../lib/storage';
import { v4 as uuidv4 } from 'uuid';

export default function ProjectForm({ onProjectAdded }: { onProjectAdded: () => void }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newProject: Project = {
      id: uuidv4(),
      name,
      description,
      tasks: [],
    };
    const projects = loadProjects();
    saveProjects([...projects, newProject]);
    setName('');
    setDescription('');
    onProjectAdded();
  };

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <div className="mb-4">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Project Name"
          className="w-full p-2 border rounded"
          required
        />
      </div>
      <div className="mb-4">
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Project Description"
          className="w-full p-2 border rounded"
        />
      </div>
      <button type="submit" className="bg-blue-500 text-white p-2 rounded">
        Add Project
      </button>
    </form>
  );
}