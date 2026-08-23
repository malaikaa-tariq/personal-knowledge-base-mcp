import { useEffect, useMemo, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  FileCheck2,
  FileText,
  Layers3,
  Sparkles,
} from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";
import StatCard from "../components/StatCard";
import UploadZone from "../components/UploadZone";
import DocumentCard from "../components/DocumentCard";

import {
  deleteDocument,
  getDocuments,
  getDocument,
  uploadDocument,
} from "../services/api";

import { useAuth } from "../context/AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pageError, setPageError] = useState("");

  async function loadDocuments() {
    setLoading(true);
    setPageError("");

    try {
      const data = await getDocuments();

      setDocuments(Array.isArray(data) ? data : []);
    } catch (err) {
      setPageError(
        err.response?.data?.detail ||
          "Unable to load your documents."
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
      "Are you sure you want to delete this document? This will remove its indexed vectors too."
    );

    if (!confirmed) return;

    try {
      await deleteDocument(id);

      setDocuments((current) =>
        current.filter((document) => document.id !== id)
      );
    } catch (err) {
      setPageError(
        err.response?.data?.detail ||
          "Unable to delete this document."
      );
    }
  }

  async function handleOpen(id) {
    try {
      const document = await getDocument(id);

      navigate(`/sources/${id}`, {
        state: { document },
      });
    } catch (err) {
      setPageError(
        err.response?.data?.detail ||
          "Unable to open this document."
      );
    }
  }

  const recentDocuments = useMemo(
    () => documents.slice(0, 5),
    [documents]
  );

  const userName =
    user?.full_name ||
    user?.email?.split("@")[0] ||
    "there";

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
          <section className="hero-section">
            <div>
              <div className="eyebrow">
                <Sparkles size={15} />
                PERSONAL KNOWLEDGE SYSTEM
              </div>

              <h1>
                Good to see you,{" "}
                <span>{userName}</span> 👋
              </h1>

              <p>
                Organize your documents and turn your
                knowledge into an intelligent, searchable
                library.
              </p>
            </div>

            <Link
              to="/sources"
              className="secondary-button"
            >
              View all sources
              <ArrowRight size={17} />
            </Link>
          </section>

          {pageError && (
            <div className="page-alert">
              {pageError}
            </div>
          )}

          <section className="stats-grid">
            <StatCard
              icon={<FileText size={21} />}
              label="Documents"
              value={documents.length}
              description="Your indexed sources"
              variant="purple"
            />

            <StatCard
              icon={<Layers3 size={21} />}
              label="Knowledge sources"
              value={documents.length}
              description="Available for retrieval"
              variant="blue"
            />

            <StatCard
              icon={<FileCheck2 size={21} />}
              label="Supported formats"
              value="3"
              description="PDF · MD · TXT"
              variant="green"
            />

            <StatCard
              icon={<BookOpen size={21} />}
              label="Workspace"
              value="Active"
              description="Your private library"
              variant="orange"
            />
          </section>

          <section className="content-grid">
            <div className="main-column">
              <div className="section-heading">
                <div>
                  <h2>Add knowledge</h2>
                  <p>
                    Upload documents to index them into
                    your personal knowledge base.
                  </p>
                </div>
              </div>

              <UploadZone onUpload={handleUpload} />

              <div className="section-heading recent-heading">
                <div>
                  <h2>Recent sources</h2>
                  <p>
                    Your latest documents and knowledge
                    sources.
                  </p>
                </div>

                <Link to="/sources">
                  View all
                  <ArrowRight size={16} />
                </Link>
              </div>

              <div className="documents-list">
                {loading ? (
                  <>
                    <DocumentSkeleton />
                    <DocumentSkeleton />
                    <DocumentSkeleton />
                  </>
                ) : recentDocuments.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">
                      <FileText size={25} />
                    </div>

                    <h3>No sources yet</h3>

                    <p>
                      Upload your first PDF, Markdown, or
                      TXT document to start building your
                      knowledge base.
                    </p>
                  </div>
                ) : (
                  recentDocuments.map((document) => (
                    <DocumentCard
                      key={document.id}
                      document={document}
                      onDelete={handleDelete}
                      onOpen={handleOpen}
                    />
                  ))
                )}
              </div>
            </div>

            <aside className="side-column">
              <div className="info-card">
                <div className="info-card-icon">
                  <Sparkles size={20} />
                </div>

                <h3>Semantic search</h3>

                <p>
                  Once your documents are indexed, the
                  retrieval engine can find relevant
                  knowledge based on meaning—not just
                  exact keywords.
                </p>

                <Link to="/search">
                  Search your knowledge
                  <ArrowRight size={16} />
                </Link>
              </div>

              <div className="quick-card">
                <h3>Workspace limits</h3>

                <div className="limit-row">
                  <span>Maximum file size</span>
                  <strong>10 MB</strong>
                </div>

                <div className="limit-row">
                  <span>Supported formats</span>
                  <strong>3</strong>
                </div>

                <div className="limit-row">
                  <span>Indexed documents</span>
                  <strong>{documents.length}</strong>
                </div>
              </div>
            </aside>
          </section>
        </main>
      </div>
    </div>
  );
}

function DocumentSkeleton() {
  return (
    <div className="document-skeleton">
      <div className="skeleton-icon" />

      <div className="skeleton-lines">
        <div />
        <div />
      </div>
    </div>
  );
}