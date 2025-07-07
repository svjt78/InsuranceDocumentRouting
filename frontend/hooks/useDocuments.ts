// frontend/hooks/useDocuments.ts

import { useState, useEffect } from "react";
import { Document } from "../types";

const API_URL = "http://localhost:8000";  // keep your hard-coded URL here

export function useDocuments() {
  const [data, setData]         = useState<Document[]>([]);
  const [loading, setLoading]   = useState<boolean>(true);
  const [error, setError]       = useState<Error | null>(null);

  useEffect(() => {
    let isActive = true;
    async function fetchDocs() {
      try {
        const res = await fetch(`${API_URL}/documents`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const docs: Document[] = await res.json();
        if (isActive) {
          setData(docs);
        }
      } catch (err: any) {
        if (isActive) setError(err);
      } finally {
        if (isActive) setLoading(false);
      }
    }
    fetchDocs();
    return () => { isActive = false; };
  }, []);

  return { data, loading, error };
}
