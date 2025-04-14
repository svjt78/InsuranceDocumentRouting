import Head from 'next/head';
import Link from 'next/link';

export default function Layout({ children, title = "Insurance Dashboard" }) {
  return (
    <div className="min-h-screen relative bg-[#0c0d15] text-white">
      <Head>
        <title>{title}</title>
        <meta name="description" content="Insurance Document Management Dashboard" />
      </Head>

      {/* Fixed Sidebar */}
      <aside className="fixed top-0 left-0 bottom-0 w-64 bg-[#051530] p-4">
        <h2 className="text-lg font-bold mb-6">
          <Link href="/">
            <a className="hover:underline">Dashboard</a>
          </Link>
        </h2>
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

      {/* Main content area offset from the sidebar and footer height */}
      <div className="ml-64 pb-16">
        {children}
      </div>

      {/* Fixed Footer */}
      <footer className="fixed bottom-0 left-0 right-0 bg-[#010b1b] p-4 text-center">
        &copy; {new Date().getFullYear()} Insurance App
      </footer>
    </div>
  );
}
