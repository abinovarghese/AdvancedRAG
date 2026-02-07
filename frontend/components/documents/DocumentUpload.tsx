"use client";

import { useState, useRef, useCallback } from "react";
import { Upload, X, FileText, Link } from "lucide-react";
import { uploadDocuments, ingestURL } from "@/lib/api";
import LoadingSpinner from "../ui/LoadingSpinner";

interface Props {
  onUploaded: () => void;
}

export default function DocumentUpload({ onUploaded }: Props) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [urlInput, setUrlInput] = useState("");
  const [error, setError] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    async (files: FileList | File[]) => {
      setError("");
      setUploading(true);
      try {
        await uploadDocuments(Array.from(files));
        onUploaded();
      } catch (e: any) {
        setError(e.message || "Upload failed");
      } finally {
        setUploading(false);
      }
    },
    [onUploaded]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
    },
    [handleFiles]
  );

  const handleURL = async () => {
    if (!urlInput.trim()) return;
    setError("");
    setUploading(true);
    try {
      await ingestURL(urlInput.trim());
      setUrlInput("");
      onUploaded();
    } catch (e: any) {
      setError(e.message || "URL ingestion failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => fileRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
          dragging
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50"
        }`}
      >
        <input
          ref={fileRef}
          type="file"
          multiple
          className="hidden"
          accept=".pdf,.docx,.doc,.pptx,.xlsx,.xls,.md,.csv,.txt,.json"
          onChange={(e) => e.target.files && handleFiles(e.target.files)}
        />
        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <LoadingSpinner size={32} />
            <p className="text-sm text-muted-foreground">Processing...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload size={32} className="text-muted-foreground" />
            <p className="text-sm font-medium">
              Drop files here or click to upload
            </p>
            <p className="text-xs text-muted-foreground">
              PDF, DOCX, PPTX, XLSX, MD, CSV, TXT, JSON
            </p>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <div className="flex items-center gap-2 flex-1 border border-border rounded-lg px-3 py-2">
          <Link size={16} className="text-muted-foreground shrink-0" />
          <input
            type="url"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="Paste a URL to ingest..."
            className="flex-1 text-sm bg-transparent outline-none"
            onKeyDown={(e) => e.key === "Enter" && handleURL()}
          />
        </div>
        <button
          onClick={handleURL}
          disabled={!urlInput.trim() || uploading}
          className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-40 transition-colors"
        >
          Ingest
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-sm text-red-500 bg-red-500/10 px-3 py-2 rounded-lg">
          <X size={16} />
          {error}
        </div>
      )}
    </div>
  );
}
