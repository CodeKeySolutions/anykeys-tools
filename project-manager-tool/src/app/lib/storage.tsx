import { Project } from "../types";

const storageKey = "projects";

export function saveProjects(projects: Project[]) {
    localStorage.setItem(storageKey, JSON.stringify(projects));
}

export function loadProjects(): Project[] {
    const projects = localStorage.getItem(storageKey);
    return projects ? JSON.parse(projects) : [];
}

export function loadProjectById(projectId: string): Project | undefined {
    const projects = loadProjects();
    return projects.find((p) => p.id === projectId);
}

export function clearProjects(projectId?: string) {
    const projects = loadProjects();
    if (!projectId)  return;

    const updatedProjects = projects.filter((p) => p.id !== projectId);
    saveProjects(updatedProjects);    
}
