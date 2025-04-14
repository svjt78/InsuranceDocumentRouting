import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import Layout from '../../components/Layout';

export default function DocumentDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [documentData, setDocumentData] = useState(null);
  const [override, setOverride] = useState({
    department: '',
    category: '',
    subcategory: '',
    summary: '',
    action_items: '',
  });

  useEffect(() => {
    if (id) {
      fetch(`http://localhost:8000/document/${id}`)
        .then(res => res.json())
        .then(data => {
          setDocumentData(data);
          setOverride({
            department: data.department || '',
            category: data.category || '',
            subcategory: data.subcategory || '',
            summary: data.summary || '',
            action_items: data.action_items || '',
          });
        });
    }
  }, [id]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setOverride(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetch(`http://localhost:8000/document/${id}/override`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(override),
    })
    .then(res => res.json())
    .then(data => {
      alert("Document override saved!");
      // Optionally refresh document data
    });
  };

  if (!documentData) {
    return (
      <Layout title="Loading...">
        <div className="container mx-auto p-4">
          <p>Loading...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title={`Document ${documentData.id} Details`}>
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Document Details</h1>
        <p><strong>Filename:</strong> {documentData.filename}</p>
        <p><strong>Status:</strong> {documentData.status}</p>
        <p className="mt-4"><strong>Extracted Text:</strong></p>
        <pre className="bg-gray-800 p-2 rounded overflow-auto">{documentData.extracted_text}</pre>
        <hr className="my-4 border-gray-600" />
        <h2 className="text-xl font-bold mb-2">Manual Override</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1">Department</label>
            <select name="department" value={override.department} onChange={handleInputChange} className="w-full p-2 rounded bg-gray-700 text-white">
              <option value="">Select Department</option>
              <option value="Claims">Claims</option>
              <option value="Underwriting">Underwriting</option>
              <option value="Policy Management">Policy Management</option>
            </select>
          </div>
          <div>
            <label className="block mb-1">Category</label>
            <select name="category" value={override.category} onChange={handleInputChange} className="w-full p-2 rounded bg-gray-700 text-white">
              <option value="">Select Category</option>
              <option value="Claim Filing">Claim Filing</option>
              <option value="Renewal">Renewal</option>
              <option value="Policy Application">Policy Application</option>
            </select>
          </div>
          <div>
            <label className="block mb-1">Subcategory</label>
            <select name="subcategory" value={override.subcategory} onChange={handleInputChange} className="w-full p-2 rounded bg-gray-700 text-white">
              <option value="">Select Subcategory</option>
              <option value="New Application">New Application</option>
              <option value="Renewal Notice">Renewal Notice</option>
            </select>
          </div>
          <div>
            <label className="block mb-1">Summary</label>
            <textarea name="summary" value={override.summary} onChange={handleInputChange} className="w-full p-2 rounded bg-gray-700 text-white" rows="4"></textarea>
          </div>
          <div>
            <label className="block mb-1">Action Items</label>
            <textarea name="action_items" value={override.action_items} onChange={handleInputChange} className="w-full p-2 rounded bg-gray-700 text-white" rows="4"></textarea>
          </div>
          <button type="submit" className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">
            Save Override
          </button>
        </form>
      </div>
    </Layout>
  );
}
