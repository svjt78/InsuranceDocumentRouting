export default function DocumentCard({ document }) {
    return (
      <div className="border rounded p-4 shadow hover:shadow-lg">
        <h2 className="text-xl font-bold">{document.filename}</h2>
        <p>Status: {document.status}</p>
        <p>Department: {document.department || "N/A"}</p>
      </div>
    );
  }
  