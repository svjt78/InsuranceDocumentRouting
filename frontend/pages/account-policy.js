// frontend/pages/account-policy.js

import { useEffect, useState } from 'react';
import AccountPolicyView from '../components/AccountPolicyView';
import Layout from '../components/Layout';

export default function AccountPolicyPage() {
  const [data, setData] = useState([]);

  const fetchData = () =>
    fetch('http://localhost:8000/accounts')
      .then((r) => r.json())
      .then(setData)
      .catch(console.error);

  useEffect(() => {
    // initial load
    fetchData();

    // open WebSocket to receive new‐document notifications
    const ws = new WebSocket('ws://localhost:8000/ws/accounts');
    ws.onmessage = (evt) => {
      const msg = JSON.parse(evt.data);
      if (msg.type === 'new_document') {
        fetchData();
      }
    };
    ws.onerror = console.error;
    return () => {
      ws.close();
    };
  }, []);

  return (
    <Layout title="Account/Policy View">
      {/* Container for header and refresh */}
      <div className="pt-0.5">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Account/Policy View</h1>
          {/* Placeholder for alignment; actual refresh is in child component */}
        </div>
        <AccountPolicyView data={data} onRefresh={fetchData} />
      </div>
    </Layout>
  );
}
