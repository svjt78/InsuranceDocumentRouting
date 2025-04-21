// frontend/pages/document/[id].js
import { useRouter } from "next/router";
import { useState, useEffect, useMemo } from "react";
import Layout from "../../components/Layout";

export default function DocumentDetail() {
  const router = useRouter();
  const { id } = router.query;

  /* ─────────────── helper ─────────────── */
  // Normalize any list or JSON string into a "; "-separated string
  const listToText = (val) => {
    if (!val) return "";
    if (Array.isArray(val)) return val.join("; ");
    try {
      const parsed = JSON.parse(val);
      if (Array.isArray(parsed)) return parsed.join("; ");
    } catch {
      // not valid JSON
    }
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

  /* ──────────── fetch document ───────── */
  useEffect(() => {
    if (!id) return;
    (async () => {
      const res = await fetch(`http://localhost:8000/document/${id}`);
      const data = await res.json();

      /* strip trailing “Summary:” or “Action Items:” blocks */
      let cleaned = data.extracted_text || "";
      const lower = cleaned.toLowerCase();
      const idxSummary = lower.indexOf("summary:");
      const idxAI = lower.indexOf("action items:");
      const cut = [idxSummary, idxAI].filter((i) => i !== -1).sort((a, b) => a - b)[0];
      if (cut !== undefined) cleaned = cleaned.slice(0, cut).trim();

      setDocumentData({ ...data, extracted_text: cleaned });
      setOverride({
        department: data.department || "",
        category:   data.category   || "",
        subcategory:data.subcategory|| "",
        summary:    Array.isArray(data.summary)
                      ? data.summary.join("; ")
                      : data.summary || "",
        action_items: listToText(data.action_items),
      });
    })();
  }, [id]);

  /* ──────────── fetch hierarchy ───────── */
  useEffect(() => {
    fetch("http://localhost:8000/lookup")
      .then((r) => r.json())
      .then((raw) => {
        const transformed = Object.entries(raw).map(([dept, cats]) => ({
          department: dept,
          categories: Object.entries(cats).map(([cat, subs]) => ({
            category: cat,
            subcategories: subs,
          })),
        }));
        setHierarchy(transformed);
      })
      .catch(() => setHierarchy([]));
  }, []);

  /* ────────── cascading options ───────── */
  const categoriesForDept = useMemo(() => {
    const dep = hierarchy.find((d) => d.department === override.department);
    return dep ? dep.categories : [];
  }, [override.department, hierarchy]);

  const subcategoriesForCat = useMemo(() => {
    const cat = categoriesForDept.find((c) => c.category === override.category);
    return cat ? cat.subcategories : [];
  }, [override.category, categoriesForDept]);

  /* ───────────── handlers ────────────── */
  const handleDelete = async () => {
    if (!confirm("Delete this document?")) return;
    await fetch(`http://localhost:8000/document/${id}`, { method: "DELETE" });
    router.replace("/documents");
  };

  const handleInputChange = (e) =>
    setOverride((prev) => ({ ...prev, [e.target.name]: e.target.value }));

  const handleDepartmentChange = (e) =>
    setOverride({
      ...override,
      department: e.target.value,
      category: "",
      subcategory: "",
    });

  const handleCategoryChange = (e) =>
    setOverride({
      ...override,
      category: e.target.value,
      subcategory: "",
    });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await fetch(`http://localhost:8000/document/${id}/override`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(override),
    });
    alert("Document override saved!");
    const res = await fetch(`http://localhost:8000/document/${id}`);
    setDocumentData(await res.json());
  };

  /* ────────── formatting helpers ─────── */
  const formattedSummary = useMemo(() => {
    if (!documentData?.summary) return "—";
    return Array.isArray(documentData.summary)
      ? documentData.summary.join("; ")
      : documentData.summary;
  }, [documentData]);

  /* turn any representation into array for numbered list */
  const actionArray = useMemo(() => {
    const raw = documentData?.action_items;
    if (!raw) return [];
    if (Array.isArray(raw)) return raw;
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) return parsed;
    } catch {/* fall‑through */}
    return raw
      .split(/[;\n]+/)
      .map((s) => s.trim())
      .filter(Boolean);
  }, [documentData]);

  /* ─────────── loading view ──────────── */
  if (!documentData)
    return (
      <Layout title="Loading…">
        <div className="container mx-auto p-4">Loading…</div>
      </Layout>
    );

  /* ───────────── render ──────────────── */
  return (
    <Layout title={`Document ${documentData.id} Details`}>
      <div className="container mx-auto p-4 space-y-6">
        {/* info header */}
        <div>
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">Document Details</h1>
            <button
              onClick={handleDelete}
              className="px-3 py-1 bg-red-600 rounded hover:bg-red-700"
            >
              Delete
            </button>
          </div>
          <p><strong>Filename:</strong> {documentData.filename}</p>
          <p><strong>Status:</strong> {documentData.status}</p>
          <p><strong>Created:</strong> {new Date(documentData.created_at).toLocaleString()}</p>
          <p>
            <strong>Updated:</strong>{" "}
            {documentData.updated_at ? new Date(documentData.updated_at).toLocaleString() : "—"}
          </p>
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

        {/* summary & action items */}
        <div>
          <p className="font-semibold mb-1">Summary:</p>
          <p>{formattedSummary}</p>

          {actionArray.length > 0 && (
            <>
              <p className="font-semibold mt-4 mb-1">Action Items:</p>
              <ol className="list-decimal list-inside space-y-1">
                {actionArray.map((it, idx) => (
                  <li key={idx}>{it}</li>
                ))}
              </ol>
            </>
          )}
        </div>

        {/* manual override form */}
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
              !hierarchy.find((d) => d.department === override.department) && (
                <option value={override.department}>{override.department}</option>
              )}
              <option value="">Select Department</option>
              {hierarchy.map((d) => (
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
              !categoriesForDept.find((c) => c.category === override.category) && (
                <option value={override.category}>{override.category}</option>
              )}
              <option value="">Select Category</option>
              {categoriesForDept.map((c) => (
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
              {subcategoriesForCat.map((sc) => (
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

          <button type="submit" className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">
            Save Override
          </button>
        </form>
      </div>
    </Layout>
  );
}
