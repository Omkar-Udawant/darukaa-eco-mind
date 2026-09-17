"use client";
import { useEffect, useState } from "react";
import { getSources } from "../../lib/api";

export default function SourcesPage() {
  const [rows, setRows] = useState<{ source: string; publication: string; year: number; topic: string }[]>([]);
  useEffect(() => { getSources().then(setRows).catch(() => setRows([])); }, []);
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-bold">Knowledge Sources</h1>
      <div className="bg-white border rounded-2xl p-4 text-sm">
        {rows.length === 0 ? <p>Backend not reachable or KB empty — seed via <code>knowledge/seed_sources.json</code>.</p> :
          <ul className="space-y-1">{rows.map((r, i) => <li key={i}>[{r.source} {r.year}] {r.publication} <span className="text-slate-500">({r.topic})</span></li>)}</ul>}
      </div>
    </div>
  );
}
