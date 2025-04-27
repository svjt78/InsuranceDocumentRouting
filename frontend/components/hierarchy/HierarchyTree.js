// frontend/components/hierarchy/HierarchyTree.js
import React, { useState } from 'react';
import NodeLabel from './NodeLabel';

export default function HierarchyTree({ nodes, onAdd, onRename, onDelete }) {
  const [expandedIds, setExpandedIds] = useState(new Set());

  const toggle = (id) => {
    setExpandedIds(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  return (
    <div>
      {nodes.map(dept => (
        <div key={dept.id}>
          {/* Department */}
          <NodeLabel
            label={dept.name}
            hasChildren={dept.categories.length > 0}
            expanded={expandedIds.has(dept.id)}
            onToggle={() => toggle(dept.id)}
            onAdd={() => onAdd(dept)}
            onRename={() => onRename(dept)}
            onDelete={() => onDelete(dept)}
          />

          {expandedIds.has(dept.id) &&
            dept.categories.map(cat => (
              <div key={cat.id} className="pl-4">
                {/* Category */}
                <NodeLabel
                  label={cat.name}
                  hasChildren={cat.subcategories.length > 0}
                  expanded={expandedIds.has(cat.id)}
                  onToggle={() => toggle(cat.id)}
                  onAdd={() => onAdd(cat)}
                  onRename={() => onRename(cat)}
                  onDelete={() => onDelete(cat)}
                />

                {expandedIds.has(cat.id) &&
                  cat.subcategories.map(sub => (
                    <div key={sub.id} className="pl-8">
                      {/* Sub-category */}
                      <NodeLabel
                        label={sub.name}
                        hasChildren={false}
                        expanded={false}
                        onAdd={() => onAdd(sub)}
                        onRename={() => onRename(sub)}
                        onDelete={() => onDelete(sub)}
                      />
                    </div>
                  ))}
              </div>
            ))}
        </div>
      ))}
    </div>
  );
}
