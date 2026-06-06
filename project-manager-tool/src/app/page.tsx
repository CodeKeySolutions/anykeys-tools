import ProjectList from './components/project/ProjectList';

export default function Home() {
  return (
    <main className="max-w-4xl mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Project Management Tool</h1>
      <ProjectList />
    </main>
  );
}