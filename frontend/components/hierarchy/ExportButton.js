// components/hierarchy/ExportButton.js
import React from 'react';

export default function ExportButton({ format = 'json' }) {
  const handleExport = () => {
    fetch(`/lookup/doc-hierarchy/export?format=${format}`)
      .then(res => {
        if (!res.ok) throw new Error('Export failed');
        return res.blob();
      })
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `doc-hierarchy.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
      })
      .catch(err => {
        console.error(err);
        alert('Failed to export hierarchy');
      });
  };

  return (
    <button
      onClick={handleExport}
      className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
    >
      Export {format.toUpperCase()}
    </button>
  );
}
