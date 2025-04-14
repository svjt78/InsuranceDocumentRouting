import { useState } from 'react';
import Layout from '../components/Layout';

export default function Configuration() {
  const [bucketMappings, setBucketMappings] = useState([
    { id: 1, bucket: 'Policy', department: 'Policy Management' },
    { id: 2, bucket: 'Claims', department: 'Claims' },
    { id: 3, bucket: 'Underwriting', department: 'Underwriting' },
  ]);

  const [newMapping, setNewMapping] = useState({ bucket: '', department: '' });
  const [emailSettings, setEmailSettings] = useState({ department: '', emails: '' });
  const [ingestionMode, setIngestionMode] = useState('Real-Time');

  const handleAddMapping = () => {
    setBucketMappings([...bucketMappings, { id: Date.now(), ...newMapping }]);
    setNewMapping({ bucket: '', department: '' });
  };

  const handleMappingChange = (id, field, value) => {
    setBucketMappings(bucketMappings.map(m => m.id === id ? { ...m, [field]: value } : m));
  };

  const handleDeleteMapping = (id) => {
    setBucketMappings(bucketMappings.filter(m => m.id !== id));
  };

  return (
    <Layout title="Configuration">
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Configuration</h1>
        {/* Bucket Mapping Section */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-2">MinIO Bucket Mapping</h2>
          <table className="min-w-full bg-[#1e1e2f]">
            <thead>
              <tr>
                <th className="py-2 px-4 border-b">Bucket</th>
                <th className="py-2 px-4 border-b">Department</th>
                <th className="py-2 px-4 border-b">Actions</th>
              </tr>
            </thead>
            <tbody>
              {bucketMappings.map(mapping => (
                <tr key={mapping.id}>
                  <td className="py-2 px-4 border-b">
                    <input 
                      type="text" 
                      value={mapping.bucket} 
                      onChange={(e) => handleMappingChange(mapping.id, 'bucket', e.target.value)} 
                      className="bg-transparent border border-gray-600 p-1 rounded text-white"
                    />
                  </td>
                  <td className="py-2 px-4 border-b">
                    <select 
                      value={mapping.department} 
                      onChange={(e) => handleMappingChange(mapping.id, 'department', e.target.value)} 
                      className="bg-transparent border border-gray-600 p-1 rounded text-white"
                    >
                      <option value="">Select</option>
                      <option value="Policy Management">Policy Management</option>
                      <option value="Claims">Claims</option>
                      <option value="Underwriting">Underwriting</option>
                      <option value="Customer Service">Customer Service</option>
                      <option value="Billing & Finance">Billing & Finance</option>
                      <option value="Marketing & Sales">Marketing & Sales</option>
                      <option value="Legal & Compliance">Legal & Compliance</option>
                    </select>
                  </td>
                  <td className="py-2 px-4 border-b">
                    <button 
                      onClick={() => handleDeleteMapping(mapping.id)} 
                      className="text-red-500 hover:underline"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-4 flex space-x-2">
            <input 
              type="text" 
              placeholder="New Bucket" 
              value={newMapping.bucket} 
              onChange={(e) => setNewMapping({ ...newMapping, bucket: e.target.value })} 
              className="p-2 rounded bg-gray-700 text-white"
            />
            <input 
              type="text" 
              placeholder="Department" 
              value={newMapping.department} 
              onChange={(e) => setNewMapping({ ...newMapping, department: e.target.value })} 
              className="p-2 rounded bg-gray-700 text-white"
            />
            <button 
              onClick={handleAddMapping} 
              className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
            >
              Add Mapping
            </button>
          </div>
        </section>
        {/* Email Notification Settings */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-2">Email Notification Settings</h2>
          <div className="space-y-4">
            <input 
              type="text" 
              placeholder="Department" 
              value={emailSettings.department} 
              onChange={(e) => setEmailSettings({ ...emailSettings, department: e.target.value })}
              className="w-full p-2 rounded bg-gray-700 text-white"
            />
            <input 
              type="text" 
              placeholder="Notification Emails (comma separated)" 
              value={emailSettings.emails} 
              onChange={(e) => setEmailSettings({ ...emailSettings, emails: e.target.value })}
              className="w-full p-2 rounded bg-gray-700 text-white"
            />
            <button className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">
              Save Email Settings
            </button>
          </div>
        </section>
        {/* Ingestion Mode */}
        <section>
          <h2 className="text-xl font-semibold mb-2">Ingestion Mode</h2>
          <div className="flex items-center space-x-4">
            <label>
              <input 
                type="radio" 
                name="ingestion" 
                value="Real-Time" 
                checked={ingestionMode === 'Real-Time'} 
                onChange={() => setIngestionMode('Real-Time')} 
                className="mr-2"
              />
              Real-Time
            </label>
            <label>
              <input 
                type="radio" 
                name="ingestion" 
                value="Mini-Batch" 
                checked={ingestionMode === 'Mini-Batch'} 
                onChange={() => setIngestionMode('Mini-Batch')} 
                className="mr-2"
              />
              Mini-Batch
            </label>
          </div>
          <p className="mt-2 text-gray-400">
            Real-Time mode processes documents instantly, while Mini-Batch mode processes documents in batches.
          </p>
        </section>
      </div>
    </Layout>
  );
}
