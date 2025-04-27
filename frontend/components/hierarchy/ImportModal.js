// components/hierarchy/ImportModal.js
import React, { useState } from 'react';

export default function ImportModal({ onClose, onFile, preview, onConfirm }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = e => {
    const file = e.target.files[0];
    setSelectedFile(file);
    onFile(file);
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-[#051530] text-white rounded-lg p-6 w-full max-w-lg">
        <h2 className="text-xl font-bold mb-4">Import Hierarchy</h2>

        <input
          type="file"
          accept=".json,.csv"
          onChange={handleFileChange}
          className="mb-4"
        />

        {preview && (
          <div className="mb-4 max-h-60 overflow-auto bg-gray-800 p-2 rounded">
            <h3 className="font-semibold mb-2">Preview</h3>
            <pre className="whitespace-pre-wrap text-sm">
              {JSON.stringify(preview, null, 2)}
            </pre>
          </div>
        )}

        <div className="flex justify-end space-x-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-600 rounded hover:bg-gray-700"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={!selectedFile}
            className={`px-4 py-2 rounded ${
              selectedFile
                ? 'bg-green-600 hover:bg-green-700'
                : 'bg-gray-500 cursor-not-allowed'
            }`}
          >
            Merge
          </button>
        </div>
      </div>
    </div>
  );
}
