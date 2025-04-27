// components/hierarchy/NodeLabel.js
import React, { useState } from 'react';
import {
  FaPlus,
  FaEdit,
  FaTrash,
  FaChevronDown,
  FaChevronRight
} from 'react-icons/fa';
export default function NodeLabel({
  label,
  hasChildren,
  expanded,
  onToggle,
  onAdd,
  onRename,
  onDelete
}) {
  return (
    <div className="flex items-center space-x-2 py-1">
      {hasChildren ? (
        <button onClick={onToggle} className="focus:outline-none">
          {expanded ? <FaChevronDown /> : <FaChevronRight />}
        </button>
      ) : (
        <span className="w-4" />
      )}

      {/* Now `label` is guaranteed to be a string */}
      <span className="flex-1">{label}</span>

      <button onClick={onAdd} title="Add Child">
        <FaPlus />
      </button>
      <button onClick={onRename} title="Rename">
        <FaEdit />
      </button>
      <button onClick={onDelete} title="Delete">
        <FaTrash />
      </button>
    </div>
  );
}
