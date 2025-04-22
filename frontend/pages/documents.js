// frontend/pages/documents.js
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "../components/Layout";
import DocumentCard from "../components/DocumentCard";

export default function Documents() {
  const router = useRouter();

  const [documents, setDocuments] = useState([]);
  const [selected, setSelected]     = useState([]);

  /* ---------------------- load list ----------------------- */
  const loadDocuments = async () => {
    const res  = await fetch("http://localhost:8000/documents");
    const data = await res.json();
    setDocuments(data);
    setSelected([]); // clear selection on refresh
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  /* ------------------------- delete ------------------------------- */
  const handleDelete = async (id) => {
    if (!confirm("Delete this document record?")) return;
    await fetch(`http://localhost:8000/document/${id}`, { method: "DELETE" });
    setDocuments(prev => prev.filter(d => d.id !== id));
    setSelected(prev => prev.filter(dId => dId !== id));
  };

  /* ------------------------- bulk delete -------------------------- */
  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${selected.length} selected documents?`)) return;
    await Promise.all(
      selected.map(id => fetch(`http://localhost:8000/document/${id}`, { method: "DELETE" }))
    );
    loadDocuments();
  };

  /* --------------------- selection toggle ------------------------- */
  const toggleSelect = (docId) =>
    setSelected(prev =>
      prev.includes(docId)
        ? prev.filter(id => id !== docId)
        : [...prev, docId]
    );

  /* --------------------------- refresh ---------------------------- */
  const handleRefresh = () => {
    loadDocuments();
  };

  /* --------------------------- render ----------------------------- */
  return (
    <Layout title="Documents">
      <div className="container mx-auto p-4">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Documents</h1>
          <div className="flex space-x-2">
            <button
              onClick={handleBulkDelete}
              disabled={selected.length === 0}
              className={`px-4 py-2 rounded ${
                selected.length === 0
                  ? "bg-gray-500 cursor-not-allowed"
                  : "bg-red-600 hover:bg-red-700"
              }`}
            >
              Bulk Delete
            </button>
            <button
              onClick={handleRefresh}
              className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
            >
              Refresh
            </button>
          </div>
        </div>

        {documents.length === 0 ? (
          <p>No documents found.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documents.map((doc) => (
              <div key={doc.id} className="relative">
                {/* selection checkbox */}
                <input
                  type="checkbox"
                  className="absolute top-2 left-2 z-10"
                  checked={selected.includes(doc.id)}
                  onClick={(e) => e.stopPropagation()}
                  onChange={() => toggleSelect(doc.id)}
                />
                <DocumentCard
                  document={doc}
                  onDelete={handleDelete}
                  onOpen={(id) => router.push(`/document/${id}`)}
                />
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
