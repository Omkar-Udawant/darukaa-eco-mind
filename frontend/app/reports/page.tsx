"use client";
import { useEffect, useState } from "react";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface HistRow { id: string; title: string; region: string; turns: number; }
interface Report {
  conversation: { id: string; title: string; region: string };
  memory: { role: string; content: string }[];
  recommendations: { title: string; detail: string; confidence: number }[];
}

/** Environmental Reports: longitudinal landscape record per conversation. */
export default function ReportsPage() {
  const [rows, setRows] = useState<HistRow[]>([]);
  const [sel, setSel] = useState<string>("");
  const [rep, setRep] = useState<Report | null>(null);
  const [metrics, setMetrics] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    fetch(`${BASE}/history`).then((r) => r.json()).then(setRows).catch(() => setRows([]));
  }, []);

  async function load(id: string) {
    setSel(id);
    const [c, m] = await Promise.all([
      fetch(`${BASE}/conversation/${id}`).then((r) => r.json()),
      fetch(`${BASE}/metrics/${id}`).then((r) => r.json())
    ]);
    setRep(c); setMetrics(m);
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Environmental Reports</h1>
      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-white border rounded-2xl p-4 text-sm space-y-1">
          <h2 className="font-semibold">Assessments</h2>
          {rows.length === 0 && <p className="text-slate-500">No history yet — run a Chat assessment first.</p>}
          {rows.map((h) => (
            <button key={h.id} onClick={() => load(h.id)}
              className={`block w-full text-left border rounded-xl px-3 py-2 ${sel === h.id ? "border-emerald-600 bg-emerald-50" : ""}`}>
              <b>{h.title.slice(0, 60)}</b><br />
              <span className="text-slate-500">{h.region} · {h.turns} turns</span>
            </button>
          ))}
        </div>
        <div className="md:col-span-2 bg-white border rounded-2xl p-4 text-sm space-y-2">
          {!rep && <p className="text-slate-500">Select an assessment to view its report.</p>}
          {rep && (
            <>
              <h2 className="font-semibold">{rep.conversation.title}</h2>
              <p><b>Region:</b> {rep.conversation.region || "—"}</p>
              <p><b>Latest metrics:</b> <code>{JSON.stringify(metrics)}</code></p>
              <h3 className="font-semibold mt-2">Recommendations</h3>
              <ul className="list-disc ml-5">
                {rep.recommendations.map((r, i) => <li key={i}>{r.title} <span className="text-slate-500">({r.confidence}%)</span></li>)}
              </ul>
              <h3 className="font-semibold mt-2">Dialogue memory</h3>
              <ul className="space-y-1 max-h-64 overflow-auto">
                {rep.memory.map((t, i) => <li key={i} className="border-b pb-1"><b>{t.role}:</b> {t.content.slice(0, 280)}</li>)}
              </ul>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
