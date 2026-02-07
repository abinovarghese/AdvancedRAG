"use client";

import { FileText, Trash2, Globe } from "lucide-react";
import type { Document } from "@/types";

interface Props {
  documents: Document[];
  onDelete: (id: string) => void;
}

function formatSize(bytes: number | null): string {
  if (!bytes) return "--";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentList({ documents, onDelete }: Props) {
  if (documents.length === 0) {
    return (
      <p className="text-sm text-muted-foreground text-center py-4">
        No documents uploaded yet
      </p>
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center gap-3 p-3 rounded-lg border border-border bg-card group"
        >
          {doc.file_type === "url" ? (
            <Globe size={18} className="text-primary shrink-0" />
          ) : (
            <FileText size={18} className="text-primary shrink-0" />
          )}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{doc.filename}</p>
            <p className="text-xs text-muted-foreground">
              {formatSize(doc.file_size)} &middot; {doc.chunk_count} chunks
            </p>
          </div>
          <button
            onClick={() => onDelete(doc.id)}
            className="opacity-0 group-hover:opacity-100 p-1.5 hover:text-red-500 transition-all"
          >
            <Trash2 size={16} />
          </button>
        </div>
      ))}
    </div>
  );
}
