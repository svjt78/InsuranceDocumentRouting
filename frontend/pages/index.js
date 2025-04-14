import Layout from '../components/Layout';
import Link from 'next/link';

export default function Home() {
  return (
    <Layout title="Home">
      <div className="flex flex-col items-center justify-center h-full">
        <h1 className="mt-1 text-4xl font-bold mb-4">Insurance Document Dashboard</h1>
        <p className="text-lg mb-8">Manage your insurance documents effectively.</p>
        <Link href="/documents">
          <a className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors">
            View Documents
          </a>
        </Link>
      </div>
    </Layout>
  );
}
