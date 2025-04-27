// frontend/metrics/widgets/BacklogBig.js
import React from 'react';

export default function BacklogBig({ value }) {
  return (
    <div className="bg-[#051530] p-6 rounded-lg flex flex-col items-center shadow-lg">
      <h3 className="text-lg font-medium mb-2">Backlog</h3>
      <span className="text-4xl font-bold">{value} docs</span>
      <p className="text-sm text-gray-400">Pending documents</p>
    </div>
  );
}
