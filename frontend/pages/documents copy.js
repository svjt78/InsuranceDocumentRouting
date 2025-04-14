import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function Documents() {
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/documents')
      .then(res => res.json())
      .then(data => setDocuments(data));
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Documents</h1>
      {documents.length === 0 ? (
        <p>No documents found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {documents.map(doc => (
            <Link key={doc.id} href={`/document/${doc.id}`}>
              <a>
                <div className="border p-4 rounded shadow hover:shadow-lg">
                  <h2 className="text-xl font-semibold">{doc.filename}</h2>
                  <p className="mt-2">Status: {doc.status}</p>
                  <p className="mt-2">Department: {doc.department || 'N/A'}</p>
                </div>
              </a>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
