"use client";
import { useEffect, useState } from "react";
import { getHealth } from "../../lib/api";

export default function AdminPage() {
  const [h, setH] = useState<Record<string, string> | null>(null);
  useEffect(() => { getHealth().then(setH).catch(() => setH(null)); }, []);
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-bold">Admin</h1>
      <div className="bg-white border rounded-2xl p-4 text-sm">
        <p>Backend health: {h ? JSON.stringify(h) : "unreachable (start backend on :8000)"}</p>
        <p className="mt-2">Endpoints: <code>/chat /analyze /recommend /reasoning /reason /impact /upload /ingest /conversation /history /sources /metrics /graph /health</code> — see <code>docs/API_SPEC.md</code>.</p>
      </div>
    </div>
  );
}
