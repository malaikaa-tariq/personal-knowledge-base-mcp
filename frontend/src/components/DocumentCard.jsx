import {
  FileText,
  MoreVertical,
  Trash2,
} from "lucide-react";

function formatDate(value) {
  if (!value) return "Unknown date";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unknown date";
  }

  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function getExtension(title = "") {
  const extension = title.split(".").pop()?.toUpperCase();

  return extension || "FILE";
}

export default function DocumentCard({
  document,
  onDelete,
  onOpen,
}) {
  return (
    <article className="document-card">
      <div className="document-main">
        <div className="document-icon">
          <FileText size={22} />
        </div>

        <div className="document-details">
          <h3 title={document.title}>
            {document.title}
          </h3>

          <div className="document-meta">
            <span>{getExtension(document.title)}</span>
            <span>•</span>
            <span>
              Added {formatDate(document.created_at)}
            </span>
          </div>
        </div>
      </div>

      <div className="document-actions">
        <button
          className="document-open"
          onClick={() => onOpen(document.id)}
        >
          Open
        </button>

        <button
          className="delete-button"
          onClick={() => onDelete(document.id)}
          title="Delete document"
        >
          <Trash2 size={17} />
        </button>

        <button className="more-button">
          <MoreVertical size={18} />
        </button>
      </div>
    </article>
  );
}