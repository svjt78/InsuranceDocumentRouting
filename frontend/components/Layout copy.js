import Head from 'next/head';
import Link from 'next/link';

export default function Layout({ children, title = "Insurance Dashboard" }) {
  return (
    <div className="min-h-screen bg-[#0c0d15] text-white">
      <Head>
        <title>{title}</title>
        <meta name="description" content="Insurance Document Management Dashboard" />
      </Head>
      <div className="flex">
        <aside className="w-64 bg-[#051530] p-4">
          <h2 className="text-lg font-bold mb-6">Dashboard</h2>
          <nav>
            <ul>
              <li className="mb-4">
                <Link href="/documents">
                  <a className="hover:underline">Documents</a>
                </Link>
              </li>
              <li className="mb-4">
                <Link href="/metrics">
                  <a className="hover:underline">Metrics</a>
                </Link>
              </li>
              <li className="mb-4">
                <Link href="/configuration">
                  <a className="hover:underline">Configuration</a>
                </Link>
              </li>
            </ul>
          </nav>
        </aside>
        <main className="flex-grow p-4">
          {children}
        </main>
      </div>
      <footer className="bg-[#051530] p-4 text-center">
        &copy; {new Date().getFullYear()} Insurance App
      </footer>
    </div>
  );
}
