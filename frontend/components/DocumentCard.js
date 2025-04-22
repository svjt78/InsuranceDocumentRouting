import React from 'react';

export default function DocumentCard({ document, onDelete, onOpen }) {
  // Format creation and update timestamps
  const createdAt = new Date(document.created_at).toLocaleString();
  const updatedAt = document.updated_at
    ? new Date(document.updated_at).toLocaleString()
    : '—';

  return (
    <div
      className="relative bg-[#1e1e2f] border border-gray-700 rounded p-4 shadow transition transform duration-200 hover:-translate-y-1 hover:scale-105 hover:shadow-lg cursor-pointer"
      onClick={() => onOpen(document.id)}
    >
      {/* Delete icon */}
      <button
        title="Delete record"
        className="absolute top-2 right-2 text-red-400 hover:text-red-600"
        onClick={(e) => {
          e.stopPropagation();
          e.preventDefault(); // ⬅ stops <Link> navigation
          onDelete(document.id);
        }}
      >
        ✕
      </button>

      <h2 className="text-xl font-bold mb-2 break-all">{document.filename}</h2>
      <p>Status: {document.status}</p>
      <p>Department: {document.department || "N/A"}</p>
      <p>Created: {createdAt}</p>
      <p>Updated: {updatedAt}</p>
      <p>Destination Bucket: {document.destination_bucket || "N/A"}</p>
      {document.error_message && (
        <p className="text-red-400">Error: {document.error_message}</p>
      )}
    </div>
  );
}
