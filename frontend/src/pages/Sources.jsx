import { useEffect, useState } from "react";
import {
  ArrowLeft,
  FileText,
  Search,
} from "lucide-react";
import { Link } from "react-router-dom";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import DocumentCard from "../components/DocumentCard";
import UploadZone from "../components/UploadZone";

import {
  deleteDocument,
  getDocuments,
  uploadDocument,
} from "../services/api";

export default function Sources() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDocuments() {
    setLoading(true);

    try {
      const data = await getDocuments();

      setDocuments(Array.isArray(data) ? data : []);
      setError("");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load sources."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function handleUpload(file) {
    const result = await uploadDocument(file);

    await loadDocuments();

    return result;
  }

  async function handleDelete(id) {
    const confirmed = window.confirm(
      "Delete this document?"
    );

    if (!confirmed) return;

    try {
      await deleteDocument(id);

      setDocuments((current) =>
        current.filter((document) => document.id !== id)
      );
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to delete the document."
      );
    }
  }

  const filteredDocuments = documents.filter(
    (document) =>
      document.title
        ?.toLowerCase()
        .includes(query.toLowerCase())
  );

  return (
    <div className="app-shell">
      <Sidebar
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="main-area">
        <Topbar
          onMenuClick={() => setSidebarOpen(true)}
        />

        <main className="dashboard-page">
          <div className="page-header">
            <div>
              <Link to="/dashboard" className="back-link">
                <ArrowLeft size={16} />
                Dashboard
              </Link>

              <h1>Your sources</h1>

              <p>
                Manage the documents inside your personal
                knowledge base.
              </p>
            </div>

            <div className="source-count">
              {documents.length}{" "}
              {documents.length === 1
                ? "document"
                : "documents"}
            </div>
          </div>

          <UploadZone onUpload={handleUpload} />

          <div className="sources-toolbar">
            <div className="source-search">
              <Search size={18} />

              <input
                type="search"
                placeholder="Filter your sources..."
                value={query}
                onChange={(event) =>
                  setQuery(event.target.value)
                }
              />
            </div>
          </div>

          {error && (
            <div className="page-alert">
              {error}
            </div>
          )}

          <section className="sources-list">
            {loading ? (
              <div className="sources-loading">
                Loading your sources...
              </div>
            ) : filteredDocuments.length === 0 ? (
              <div className="empty-state large">
                <div className="empty-icon">
                  <FileText size={26} />
                </div>

                <h3>
                  {query
                    ? "No matching sources"
                    : "Your library is empty"}
                </h3>

                <p>
                  {query
                    ? "Try a different document name."
                    : "Upload a document above to start building your library."}
                </p>
              </div>
            ) : (
              filteredDocuments.map((document) => (
                <DocumentCard
                  key={document.id}
                  document={document}
                  onDelete={handleDelete}
                  onOpen={(id) => {
  window.location.href = `/sources/${id}`;
}}
                />
              ))
            )}
          </section>
        </main>
      </div>
    </div>
  );
}