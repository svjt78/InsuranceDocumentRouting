// frontend/pages/viewer/[id].js
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import Layout from "../../components/Layout";
import { Document, Page, pdfjs } from "react-pdf";

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

export default function PDFViewer() {
  const router = useRouter();
  const { id } = router.query;
  const [url, setUrl] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) return;
    fetch(`http://localhost:8000/documents/${id}/download`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setUrl(data.url);
      })
      .catch((err) => {
        console.error("Failed to fetch download URL:", err);
        setError("Unable to load document.");
      });
  }, [id]);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }

  if (error) {
    return (
      <Layout title="Viewer Error">
        <div className="container mx-auto p-4 text-red-400">
          {error}
        </div>
      </Layout>
    );
  }

  if (!url) {
    return (
      <Layout title="Loading PDF…">
        <div className="container mx-auto p-4">Loading PDF…</div>
      </Layout>
    );
  }

  return (
    <Layout title={`Viewing Document ${id}`}>
      {/* Close button */}
      <button
        onClick={() => router.back()}
        className="fixed top-4 right-4 z-50 text-white bg-black bg-opacity-50 p-2 rounded"
        title="Close viewer"
      >
        ✕
      </button>

      {/* Download button, only when URL ready */}
      {url && (
        <a
          href={url}
          download={`document-${id}.pdf`}
          target="_blank"
          rel="noopener noreferrer"
          className="fixed top-4 left-4 z-50 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Download PDF
        </a>
      )}

      {/* PDF viewer */}
      <div className="w-full h-screen bg-gray-900 flex justify-center items-start overflow-auto pt-16">
        <Document
          file={url}
          onLoadSuccess={onDocumentLoadSuccess}
          loading={<p className="text-white">Loading PDF…</p>}
          error={<p className="text-red-400">Failed to load PDF.</p>}
        >
          {Array.from(new Array(numPages), (_, index) => (
            <Page
              key={`page_${index + 1}`}
              pageNumber={index + 1}
              width={Math.min(typeof window !== 'undefined' ? window.innerWidth * 0.9 : 800, 1200)}
            />
          ))}
        </Document>
      </div>
    </Layout>
  );
}
