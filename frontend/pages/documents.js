// frontend/pages/documents.js
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "../components/Layout";
import DocumentCard from "../components/DocumentCard";

export default function Documents() {
  const router = useRouter();

  const [documents, setDocuments] = useState([]);
  const [selected,   setSelected]   = useState([]);

  /* ---------------------- load list on mount ----------------------- */
  useEffect(() => { loadDocuments(); }, []);

  const loadDocuments = async () => {
    const res  = await fetch("http://localhost:8000/documents");
    const data = await res.json();
    setDocuments(data);
  };

  /* ------------------------- delete ------------------------------- */
  const handleDelete = async (id) => {
    if (!confirm("Delete this document record?")) return;
    await fetch(`http://localhost:8000/document/${id}`, { method: "DELETE" });
    setDocuments((prev) => prev.filter((d)  => d.id !== id));
    setSelected( (prev) => prev.filter((dId) => dId !== id));
  };

  /* ------------------------- open card ---------------------------- */
  const handleOpen = (id) => router.push(`/document/${id}`);

  /* --------------------- bulk‑override UI ------------------------- */
  const toggleSelect = (docId) =>
    setSelected((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    );

  const handleBulkOverride = () =>
    alert("Bulk override functionality is not yet implemented.");

  /* --------------------------- render ----------------------------- */
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
                    onOpen={handleOpen}
                  />
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}
