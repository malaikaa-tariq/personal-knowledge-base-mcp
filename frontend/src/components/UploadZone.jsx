import { useRef, useState } from "react";
import {
  CheckCircle2,
  FileUp,
  Loader2,
  UploadCloud,
  X,
} from "lucide-react";

const MAX_SIZE = 10 * 1024 * 1024;

export default function UploadZone({ onUpload }) {
  const inputRef = useRef(null);

  const [dragging, setDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState("");

  function validateFile(file) {
    if (!file) return false;

    const extension =
      "." + file.name.split(".").pop().toLowerCase();

    if (![".pdf", ".md", ".txt"].includes(extension)) {
      setError("Only PDF, Markdown, and TXT files are supported.");
      return false;
    }

    if (file.size > MAX_SIZE) {
      setError("File is too large. Maximum size is 10 MB.");
      return false;
    }

    setError("");
    setSuccess("");
    setSelectedFile(file);

    return true;
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragging(false);

    const file = event.dataTransfer.files?.[0];

    validateFile(file);
  }

  async function handleUpload() {
    if (!selectedFile) return;

    setUploading(true);
    setError("");
    setSuccess("");

    try {
      const result = await onUpload(selectedFile);

      setSuccess(
        result?.message || "Document uploaded successfully."
      );

      setSelectedFile(null);

      if (inputRef.current) {
        inputRef.current.value = "";
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Upload failed. Please try again."
      );
    } finally {
      setUploading(false);
    }
  }

  function removeFile() {
    setSelectedFile(null);
    setError("");
    setSuccess("");

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  return (
    <div className="upload-section">
      <div
        className={`upload-zone ${
          dragging ? "dragging" : ""
        }`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.md,.txt"
          hidden
          onChange={(event) =>
            validateFile(event.target.files?.[0])
          }
        />

        {!selectedFile ? (
          <>
            <div className="upload-icon">
              <UploadCloud size={28} />
            </div>

            <h3>Upload your knowledge</h3>

            <p>
              Drag and drop a document here, or click to
              browse.
            </p>

            <span className="upload-types">
              PDF · Markdown · TXT · Max 10 MB
            </span>
          </>
        ) : (
          <div
            className="selected-file"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="file-icon">
              <FileUp size={22} />
            </div>

            <div className="selected-file-info">
              <strong>{selectedFile.name}</strong>
              <span>
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </span>
            </div>

            <button
              type="button"
              className="remove-file"
              onClick={removeFile}
            >
              <X size={17} />
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="upload-message error">
          <X size={17} />
          {error}
        </div>
      )}

      {success && (
        <div className="upload-message success">
          <CheckCircle2 size={17} />
          {success}
        </div>
      )}

      {selectedFile && !uploading && (
        <button
          className="upload-button"
          onClick={handleUpload}
        >
          <UploadCloud size={18} />
          Index document
        </button>
      )}

      {uploading && (
        <div className="uploading-state">
          <Loader2 className="spin" size={18} />
          Processing and indexing your document...
        </div>
      )}
    </div>
  );
}