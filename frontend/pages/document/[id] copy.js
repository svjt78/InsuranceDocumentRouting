import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';

export default function DocumentDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [document, setDocument] = useState(null);

  useEffect(() => {
    if (id) {
      fetch(`http://localhost:8000/document/${id}`)
        .then(res => res.json())
        .then(data => setDocument(data));
    }
  }, [id]);

  if (!document) {
    return <p>Loading...</p>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Document Details</h1>
      <p><strong>Filename:</strong> {document.filename}</p>
      <p><strong>Status:</strong> {document.status}</p>
      <p><strong>Department:</strong> {document.department}</p>
      <p><strong>Category:</strong> {document.category}</p>
      <p><strong>Subcategory:</strong> {document.subcategory}</p>
      <p><strong>Summary:</strong> {document.summary}</p>
      <p><strong>Action Items:</strong> {document.action_items}</p>
      {/* Override form and bulk actions can be added here */}
    </div>
  );
}
