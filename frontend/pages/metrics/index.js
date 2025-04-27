// frontend/pages/metrics/index.jsx
import React from 'react';
import Layout from '../../components/Layout';
import Dashboard from '../../metrics/Dashboard';

export default function MetricsPage() {
  return (
    <Layout title="Metrics & KPIs">
      <main className="container mx-auto px-4 py-6">
        <header>
          <h1 className="text-3xl font-semibold mb-6">Metrics &amp; KPIs</h1>
        </header>
        <Dashboard />
      </main>
    </Layout>
  );
}
