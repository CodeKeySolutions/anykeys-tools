import React from 'react';
import { Task } from '../../types';

const TaskComponent: React.FC<{ task: Task }> = ({ task }) => {
  return (
    <li className="border p-2 rounded">
      <span>{task.title}</span> - <span>{task.status}</span><button></button>
    </li>
  );
};

export default TaskComponent;
