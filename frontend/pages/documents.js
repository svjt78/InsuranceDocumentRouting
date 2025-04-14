import { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import DocumentCard from '../components/DocumentCard';
import Link from 'next/link';

export default function Documents() {
  const [documents, setDocuments] = useState([]);
  const [selected, setSelected] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/documents')
      .then(res => res.json())
      .then(data => setDocuments(data));
  }, []);

  const toggleSelect = (docId) => {
    if (selected.includes(docId)) {
      setSelected(selected.filter(id => id !== docId));
    } else {
      setSelected([...selected, docId]);
    }
  };

  const handleBulkOverride = () => {
    // Future implementation: open a modal/form to override selected documents.
    console.log("Bulk override for documents:", selected);
    alert("Bulk override functionality is not yet implemented.");
  };

  return (
    <Layout title="Documents">
      <div className="container mx-auto p-4">
        <h1 className="text-2xl font-bold mb-4">Documents</h1>
        {documents.length === 0 ? (
          <p>No documents found.</p>
        ) : (
          <>
            <div className="mb-4">
              <button 
                onClick={handleBulkOverride}
                className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
              >
                Apply Bulk Override
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {documents.map(doc => (
                <div key={doc.id} className="relative">
                  <input 
                    type="checkbox"
                    className="absolute top-2 left-2 z-10"
                    checked={selected.includes(doc.id)}
                    onChange={() => toggleSelect(doc.id)}
                  />
                  <Link href={`/document/${doc.id}`}>
                    <a>
                      <DocumentCard document={doc} />
                    </a>
                  </Link>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}
