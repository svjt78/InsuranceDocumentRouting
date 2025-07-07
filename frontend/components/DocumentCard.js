import React from 'react';
import PropTypes from 'prop-types';

export default function DocumentCard({ document, onDelete, onOpen }) {
  // Format creation and update timestamps
  const createdAt = new Date(document.created_at).toLocaleString();
  const updatedAt = document.updated_at
    ? new Date(document.updated_at).toLocaleString()
    : '—';

  // Helper to display metadata or fallback to "N/A"
  const showField = (value) =>
    value && value !== 'XXXX' ? value : 'N/A';

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
          e.preventDefault(); // ⬅ stops navigation
          onDelete(document.id);
        }}
      >
        ✕
      </button>

      <h2 className="text-xl font-bold mb-2 break-all">{document.filename}</h2>

      {/* Metadata fields */}
      <p><strong>Account #:</strong> {showField(document.account_number)}</p>
      <p><strong>Policy #:</strong>  {showField(document.policy_number)}</p>
      <p><strong>Policyholder:</strong> {showField(document.policyholder_name)}</p>
      {document.department?.toLowerCase() === 'claims' && (
        <p><strong>Claim #:</strong>   {showField(document.claim_number)}</p>
      )}

      <p className="mt-2"><strong>Status:</strong>     {document.status}</p>
      <p><strong>Department:</strong> {showField(document.department)}</p>
      <p><strong>Created:</strong>    {createdAt}</p>
      <p><strong>Updated:</strong>    {updatedAt}</p>
      <p><strong>Destination:</strong> {showField(document.destination_bucket)}</p>

      {document.error_message && (
        <p className="text-red-400 mt-1"><strong>Error:</strong> {document.error_message}</p>
      )}
    </div>
  );
}

DocumentCard.propTypes = {
  document: PropTypes.shape({
    id:                 PropTypes.number.isRequired,
    filename:           PropTypes.string.isRequired,
    s3_key:             PropTypes.string,
    extracted_text:     PropTypes.string,
    department:         PropTypes.string,
    category:           PropTypes.string,
    subcategory:        PropTypes.string,
    summary:            PropTypes.string,
    action_items:       PropTypes.string,
    status:             PropTypes.string.isRequired,
    destination_bucket: PropTypes.string,
    destination_key:    PropTypes.string,
    error_message:      PropTypes.string,
    email_error:        PropTypes.string,

    // metadata fields
    account_number:     PropTypes.string,
    policyholder_name:  PropTypes.string,
    policy_number:      PropTypes.string,
    claim_number:       PropTypes.string,

    created_at:         PropTypes.string.isRequired,
    updated_at:         PropTypes.string,
  }).isRequired,
  onDelete: PropTypes.func.isRequired,
  onOpen:   PropTypes.func.isRequired,
};
