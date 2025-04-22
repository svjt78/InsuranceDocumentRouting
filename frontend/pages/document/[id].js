// frontend/pages/document/[id].js
import { useRouter } from "next/router";
import { useState, useEffect, useMemo, useCallback } from "react";
import Layout from "../../components/Layout";

export default function DocumentDetail() {
  const router = useRouter();
  const { id } = router.query;
  const API_BASE = "http://localhost:8000";

  /* ─────────────── helper ─────────────── */
  const listToText = (val) => {
    if (!val) return "";
    if (Array.isArray(val)) return val.join("; ");
    try {
      const parsed = JSON.parse(val);
      if (Array.isArray(parsed)) return parsed.join("; ");
    } catch {}
    return String(val);
  };

  /* ─────────────── state ─────────────── */
  const [documentData, setDocumentData] = useState(null);
  const [override, setOverride] = useState({
    department: "",
    category: "",
    subcategory: "",
    summary: "",
    action_items: "",
  });
  const [hierarchy, setHierarchy] = useState([]);

  /* ─────────── load hierarchy ────────── */
  useEffect(() => {
    fetch(`${API_BASE}/lookup`)
      .then(r => r.json())
      .then(raw => {
        const transformed = Object.entries(raw).map(([dept, cats]) => ({
          department: dept,
          categories: Object.entries(cats).map(
            ([cat, subs]) => ({ category: cat, subcategories: subs })
          ),
        }));
        setHierarchy(transformed);
      })
      .catch(() => setHierarchy([]));
  }, []);

  /* ─────────── fetch document ───────── */
  const loadDocument = useCallback(async () => {
    if (!id) return;
    const res = await fetch(`${API_BASE}/document/${id}`);
    const data = await res.json();

    let cleaned = data.extracted_text || "";
    const lower = cleaned.toLowerCase();
    const idxSummary = lower.indexOf("summary:");
    const idxAI = lower.indexOf("action items:");
    const cut = [idxSummary, idxAI].filter(i => i !== -1).sort((a,b) => a - b)[0];
    if (cut !== undefined) cleaned = cleaned.slice(0, cut).trim();

    setDocumentData({ ...data, extracted_text: cleaned });
    setOverride({
      department:   data.department   || "",
      category:     data.category     || "",
      subcategory:  data.subcategory  || "",
      summary:      Array.isArray(data.summary) ? data.summary.join("; ") : data.summary || "",
      action_items: listToText(data.action_items),
    });
  }, [id]);

  useEffect(() => {
    loadDocument();
  }, [loadDocument]);

  /* ───────────── handlers ────────────── */
  const handleRefresh = async () => {
    await loadDocument();
  };

  const handleDelete = async () => {
    if (!confirm("Delete this document?")) return;
    await fetch(`${API_BASE}/document/${id}`, { method: "DELETE" });
    router.replace("/documents");
  };

  const handleCancel = () => {
    router.push("/documents");
  };

  const handleInputChange = (e) =>
    setOverride(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const handleDepartmentChange = (e) =>
    setOverride({
      ...override,
      department:  e.target.value,
      category:    "",
      subcategory: "",
    });

  const handleCategoryChange = (e) =>
    setOverride({
      ...override,
      category:    e.target.value,
      subcategory: "",
    });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!confirm("You should click this button only when you changed any data. Are you sure you want to click this button?")) {
      return;
    }
    const res = await fetch(`${API_BASE}/document/${id}/override`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(override),
    });
    if (!res.ok) {
      alert("Failed to save override");
      return;
    }
    const updated = await res.json();

    setDocumentData(prev => ({
      ...prev,
      department:         updated.department,
      category:           updated.category,
      subcategory:        updated.subcategory,
      summary:            updated.summary,
      action_items:       updated.action_items,
      status:             updated.status,
      destination_bucket: updated.destination_bucket,
      destination_key:    updated.destination_key,
      error_message:      updated.error_message,
    }));

    setOverride({
      department:   updated.department,
      category:     updated.category,
      subcategory:  updated.subcategory,
      summary:      Array.isArray(updated.summary) ? updated.summary.join("; ") : updated.summary,
      action_items: listToText(updated.action_items),
    });
  };

  /* ────────── cascading options ───────── */
  const categoriesForDept = useMemo(() => {
    const dep = hierarchy.find(d => d.department === override.department);
    return dep ? dep.categories : [];
  }, [override.department, hierarchy]);

  const subcategoriesForCat = useMemo(() => {
    const cat = categoriesForDept.find(c => c.category === override.category);
    return cat ? cat.subcategories : [];
  }, [override.category, categoriesForDept]);

  /* ────────── formatting helpers ─────── */
  const formattedSummary = useMemo(() => {
    if (!documentData?.summary) return "—";
    return Array.isArray(documentData.summary)
      ? documentData.summary.join("; ")
      : documentData.summary;
  }, [documentData]);

  const actionArray = useMemo(() => {
    const raw = documentData?.action_items;
    if (!raw) return [];
    if (Array.isArray(raw)) return raw;
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed;
    } catch {}
    return raw
      .split(/[;\n]+/)
      .map(s => s.trim())
      .filter(Boolean);
  }, [documentData]);

  /* ─────────── loading view ──────────── */
  if (!documentData) {
    return (
      <Layout title="Loading…">
        <div className="container mx-auto p-4">Loading…</div>
      </Layout>
    );
  }

  /* ───────────── render ──────────────── */
  return (
    <Layout title={`Document ${documentData.id} Details`}>
      <div className="container mx-auto p-4 space-y-6">

        {/* info header */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Document Details</h1>
          <div>
            <button
              onClick={handleRefresh}
              className="px-3 py-1 mr-2 bg-blue-600 rounded hover:bg-blue-700"
            >
              Refresh
            </button>
            <button
              onClick={handleDelete}
              className="px-3 py-1 bg-red-600 rounded hover:bg-red-700"
            >
              Delete
            </button>
          </div>
        </div>

        {/* metadata */}
        <div>
          <p><strong>Filename:</strong> {documentData.filename}</p>
          <p><strong>Status:</strong> {documentData.status}</p>
          <p><strong>Created:</strong> {new Date(documentData.created_at).toLocaleString()}</p>
          <p><strong>Updated:</strong> {documentData.updated_at ? new Date(documentData.updated_at).toLocaleString() : "—"}</p>
          <p><strong>Destination Bucket:</strong> {documentData.destination_bucket || "N/A"}</p>
          {documentData.error_message && (
            <p className="text-red-400"><strong>Error:</strong> {documentData.error_message}</p>
          )}
        </div>

        {/* extracted text */}
        <div>
          <p className="font-semibold mb-1">Extracted Text:</p>
          <pre className="bg-gray-800 p-2 rounded overflow-auto max-h-64 whitespace-pre-wrap">
            {documentData.extracted_text}
          </pre>
        </div>

        {/* summary & actions */}
        <div>
          <p className="font-semibold mb-1">Summary:</p>
          <p>{formattedSummary}</p>
          {actionArray.length > 0 && (
            <>
              <p className="font-semibold mt-4 mb-1">Action Items:</p>
              <ol className="list-decimal list-inside space-y-1">
                {actionArray.map((it, idx) => <li key={idx}>{it}</li>)}
              </ol>
            </>
          )}
        </div>

        {/* manual override */}
        <hr className="border-gray-600" />
        <h2 className="text-xl font-bold">Manual Override</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Department */}
          <div>
            <label className="block mb-1">Department</label>
            <select
              name="department"
              value={override.department}
              onChange={handleDepartmentChange}
              className="w-full p-2 rounded bg-gray-700 text-white"
            >
              {override.department &&
                !hierarchy.find(d => d.department === override.department) && (
                  <option value={override.department}>{override.department}</option>
              )}
              <option value="">Select Department</option>
              {hierarchy.map(d => (
                <option key={d.department} value={d.department}>{d.department}</option>
              ))}
            </select>
          </div>

          {/* Category */}
          <div>
            <label className="block mb-1">Category</label>
            <select
              name="category"
              value={override.category}
              onChange={handleCategoryChange}
              disabled={!override.department}
              className="w-full p-2 rounded bg-gray-700 text-white"
            >
              {override.category &&
                !categoriesForDept.find(c => c.category === override.category) && (
                  <option value={override.category}>{override.category}</option>
              )}
              <option value="">Select Category</option>
              {categoriesForDept.map(c => (
                <option key={c.category} value={c.category}>{c.category}</option>
              ))}
            </select>
          </div>

          {/* Subcategory */}
          <div>
            <label className="block mb-1">Sub‑category</label>
            <select
              name="subcategory"
              value={override.subcategory}
              onChange={handleInputChange}
              disabled={!override.category}
              className="w-full p-2 rounded bg-gray-700 text-white"
            >
              {override.subcategory &&
                !subcategoriesForCat.includes(override.subcategory) && (
                  <option value={override.subcategory}>{override.subcategory}</option>
              )}
              <option value="">Select Subcategory</option>
              {subcategoriesForCat.map(sc => (
                <option key={sc} value={sc}>{sc}</option>
              ))}
            </select>
          </div>

          {/* Summary */}
          <div>
            <label className="block mb-1">Summary</label>
            <textarea
              name="summary"
              value={override.summary}
              onChange={handleInputChange}
              rows={3}
              className="w-full p-2 rounded bg-gray-700 text-white"
            />
          </div>

          {/* Action items */}
          <div>
            <label className="block mb-1">Action Items</label>
            <textarea
              name="action_items"
              value={override.action_items}
              onChange={handleInputChange}
              rows={3}
              className="w-full p-2 rounded bg-gray-700 text-white"
            />
          </div>

          <div className="flex items-center">
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700"
            >
              Save Override
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 ml-2 bg-gray-600 rounded hover:bg-gray-700"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}
