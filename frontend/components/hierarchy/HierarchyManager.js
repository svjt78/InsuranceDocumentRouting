// frontend/components/hierarchy/HierarchyManager.js
import React, { useState, useEffect } from 'react';
import HierarchyTree from './HierarchyTree';
import ImportModal from './ImportModal';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export default function HierarchyManager() {
  const [flatList, setFlatList]           = useState([]);
  const [tree, setTree]                   = useState([]);
  const [showImport, setShowImport]       = useState(false);
  const [importPreview, setImportPreview] = useState(null);

  // Build nested tree from flat list
  const buildTree = (list) => {
    const deptMap = {};
    list.forEach(({ id, department, category, subcategory }) => {
      // Department node
      if (!deptMap[department]) {
        deptMap[department] = {
          id: department,            // grouping node; name is unique
          name: department,
          level: 'department',
          categories: {}
        };
      }
      const dept = deptMap[department];

      // Category node
      if (!dept.categories[category]) {
        dept.categories[category] = {
          id: `${department}>>${category}`,  // grouping node
          name: category,
          level: 'category',
          parent: department,
          subcategories: []
        };
      }
      const cat = dept.categories[category];

      // Subcategory node (actual row)
      cat.subcategories.push({
        id: id,               // use DB primary-key
        name: subcategory,
        level: 'subcategory',
        parent: category
      });
    });

    // Convert map → array
    return Object.values(deptMap).map(dept => ({
      ...dept,
      categories: Object.values(dept.categories)
    }));
  };

  // Fetch the flat list of all hierarchy rows
  const fetchAll = async () => {
    try {
      const res = await fetch(`${API_BASE}/lookup/doc-hierarchy/all`);
      if (!res.ok) throw new Error(res.statusText);
      const list = await res.json();
      setFlatList(list);
      setTree(buildTree(list));
    } catch (err) {
      console.error('Failed to fetch hierarchy', err);
      setFlatList([]);
      setTree([]);
    }
  };

  useEffect(() => {
    fetchAll();
  }, []);

  // Add handler: prompts user and posts a new row
  const handleAdd = async (node) => {
    let department, category, subcategory;
    if (!node) {
      department  = window.prompt('New Department name:');
      if (!department) return;
      category    = window.prompt(`Initial Category for "${department}":`);
      if (!category) return;
      subcategory = window.prompt(`Initial Sub-category for "${category}":`);
      if (!subcategory) return;
    } else if (node.level === 'department') {
      department  = node.name;
      category    = window.prompt(`New Category under "${department}":`);
      if (!category) return;
      subcategory = window.prompt(`Initial Sub-category for "${category}":`);
      if (!subcategory) return;
    } else if (node.level === 'category') {
      department  = node.parent;
      category    = node.name;
      subcategory = window.prompt(`New Sub-category under "${category}":`);
      if (!subcategory) return;
    } else {
      return; // no deeper level
    }

    try {
      const res = await fetch(`${API_BASE}/lookup/doc-hierarchy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ department, category, subcategory })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || res.statusText);
      }
      fetchAll();
    } catch (err) {
      console.error('Add failed', err);
      alert('Failed to add');
    }
  };

  // Rename handler: bulk‐PUT on department/category; single‐PUT on subcategory
  const handleRename = async (node) => {
    const newName = window.prompt(`Rename ${node.level} "${node.name}" to:`, node.name);
    if (!newName || newName === node.name) return;

    try {
      if (node.level === 'department') {
        // Bulk‐rename every row in that department
        const toUpdate = flatList.filter(i => i.department === node.name);
        await Promise.all(
          toUpdate.map(item =>
            fetch(`${API_BASE}/lookup/doc-hierarchy/${item.id}`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ department: newName })
            })
          )
        );
      } else if (node.level === 'category') {
        // Bulk‐rename every row in that department+category
        const toUpdate = flatList.filter(i =>
          i.department === node.parent && i.category === node.name
        );
        await Promise.all(
          toUpdate.map(item =>
            fetch(`${API_BASE}/lookup/doc-hierarchy/${item.id}`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ category: newName })
            })
          )
        );
      } else {
        // Single‐row rename for subcategory
        await fetch(`${API_BASE}/lookup/doc-hierarchy/${node.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ subcategory: newName })
        });
      }

      fetchAll();
    } catch (err) {
      console.error('Rename failed', err);
      alert('Failed to rename');
    }
  };

  // Delete handler: deletes one or multiple rows
  const handleDelete = async (node) => {
    if (!confirm(`Delete ${node.level} "${node.name}"? This cannot be undone.`)) return;

    try {
      let toDelete = [];
      if (node.level === 'department') {
        toDelete = flatList.filter(i => i.department === node.name);
      } else if (node.level === 'category') {
        toDelete = flatList.filter(i =>
          i.department === node.parent && i.category === node.name
        );
      } else {
        toDelete = [node];
      }

      await Promise.all(
        toDelete.map(item =>
          fetch(`${API_BASE}/lookup/doc-hierarchy/${item.id}`, { method: 'DELETE' })
        )
      );

      fetchAll();
    } catch (err) {
      console.error('Delete failed', err);
      alert('Failed to delete');
    }
  };

  // Export JSON
  const onExport = async () => {
    try {
      const res = await fetch(`${API_BASE}/lookup/doc-hierarchy/export?format=json`);
      if (!res.ok) throw new Error(res.statusText);
      const blob = await res.blob();
      const url  = window.URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = 'doc-hierarchy.json';
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error('Export failed', err);
      alert('Failed to export');
    }
  };

  // Import preview (unchanged)
  const handleFileUpload = async (file) => {
    const text = await file.text();
    let preview;
    if (file.name.toLowerCase().endsWith('.json')) {
      preview = JSON.parse(text);
    } else {
      const [hdr, ...lines] = text.split('\n').filter(Boolean);
      const keys = hdr.split(',');
      preview = lines.map(l => {
        const vals = l.split(',');
        return keys.reduce((o, k, i) => ({ ...o, [k]: vals[i] }), {});
      });
    }
    setImportPreview(preview);
  };
  const applyImport = async () => {
    /* calls POST /import?merge=true */
    setShowImport(false);
    fetchAll();
  };

  return (
    <>
      <div className="flex justify-between mb-4">
        <div className="flex space-x-2">
          <button
            onClick={onExport}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Export JSON
          </button>
          <button
            onClick={() => setShowImport(true)}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            Import
          </button>
        </div>
        <button
          onClick={() => handleAdd(null)}
          className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
        >
          Add Department
        </button>
      </div>

      <HierarchyTree
        nodes={tree}
        onAdd={handleAdd}
        onRename={handleRename}
        onDelete={handleDelete}
      />

      {showImport && (
        <ImportModal
          onClose={() => setShowImport(false)}
          onFile={handleFileUpload}
          preview={importPreview}
          onConfirm={applyImport}
        />
      )}
    </>
  );
}
