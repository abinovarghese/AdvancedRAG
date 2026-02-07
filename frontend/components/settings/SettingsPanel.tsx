"use client";

import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { getSettings, updateSettings } from "@/lib/api";
import type { Settings } from "@/types";
import LoadingSpinner from "../ui/LoadingSpinner";

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function SettingsPanel({ open, onClose }: Props) {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [watsonxKey, setWatsonxKey] = useState("");
  const [watsonxProject, setWatsonxProject] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (open) {
      getSettings().then(setSettings).catch(console.error);
    }
  }, [open]);

  if (!open) return null;

  const handleSave = async () => {
    if (!settings) return;
    setSaving(true);
    try {
      const update: Record<string, any> = { ...settings };
      if (apiKey) update.openai_api_key = apiKey;
      if (watsonxKey) update.watsonx_api_key = watsonxKey;
      if (watsonxProject) update.watsonx_project_id = watsonxProject;
      const updated = await updateSettings(update);
      setSettings(updated);
      onClose();
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-card border border-border rounded-2xl w-full max-w-lg max-h-[85vh] overflow-y-auto shadow-xl">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="font-semibold">Settings</h2>
          <button onClick={onClose} className="p-1 hover:bg-muted rounded-lg">
            <X size={20} />
          </button>
        </div>

        {!settings ? (
          <div className="flex justify-center p-8">
            <LoadingSpinner />
          </div>
        ) : (
          <div className="p-4 space-y-5">
            {/* Provider */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">LLM Provider</label>
              <select
                value={settings.llm_provider}
                onChange={(e) =>
                  setSettings({ ...settings, llm_provider: e.target.value })
                }
                className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
              >
                <option value="openai">OpenAI</option>
                <option value="watsonx">WatsonX</option>
              </select>
            </div>

            {/* OpenAI key */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">OpenAI API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-..."
                className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
              />
            </div>

            {/* WatsonX keys */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">WatsonX API Key</label>
              <input
                type="password"
                value={watsonxKey}
                onChange={(e) => setWatsonxKey(e.target.value)}
                placeholder="WatsonX API key"
                className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">WatsonX Project ID</label>
              <input
                value={watsonxProject}
                onChange={(e) => setWatsonxProject(e.target.value)}
                placeholder="Project ID"
                className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
              />
            </div>

            {/* RAG params */}
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Chunk Size</label>
                <input
                  type="number"
                  value={settings.chunk_size}
                  onChange={(e) =>
                    setSettings({ ...settings, chunk_size: +e.target.value })
                  }
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Chunk Overlap</label>
                <input
                  type="number"
                  value={settings.chunk_overlap}
                  onChange={(e) =>
                    setSettings({ ...settings, chunk_overlap: +e.target.value })
                  }
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Retrieval Top K</label>
                <input
                  type="number"
                  value={settings.retrieval_top_k}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      retrieval_top_k: +e.target.value,
                    })
                  }
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Rerank Top K</label>
                <input
                  type="number"
                  value={settings.rerank_top_k}
                  onChange={(e) =>
                    setSettings({ ...settings, rerank_top_k: +e.target.value })
                  }
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">BM25 Weight</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={settings.bm25_weight}
                  onChange={(e) =>
                    setSettings({ ...settings, bm25_weight: +e.target.value })
                  }
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Vector Weight</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="1"
                  value={settings.vector_weight}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      vector_weight: +e.target.value,
                    })
                  }
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
                />
              </div>
            </div>

            <button
              onClick={handleSave}
              disabled={saving}
              className="w-full py-2.5 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              {saving ? "Saving..." : "Save Settings"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
