export default function DocumentCard({ document }) {
  return (
    <div className="bg-[#1e1e2f] border border-gray-700 rounded p-4 shadow hover:shadow-lg transition-shadow">
      <h2 className="text-xl font-bold mb-2">{document.filename}</h2>
      <p>Status: {document.status}</p>
      <p>Department: {document.department || "N/A"}</p>
    </div>
  );
}
