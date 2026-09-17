"use client";
import { useState } from "react";
import { postChat } from "../../lib/api";
import type { ChatResponse } from "../../lib/types";
import { ConfidenceBadge } from "../../components/ConfidenceBadge";
import { RecommendationCard } from "../../components/RecommendationCard";
import { ReasoningGraph } from "../../components/ReasoningGraph";

export default function ChatPage() {
  const [msg, setMsg] = useState("Biodiversity is declining on my cropland near Nashik. SOC 0.6%, rainfall 520mm, 34C, heavy pesticide, few bees.");
  const [cid, setCid] = useState<string | null>(null);
  const [resp, setResp] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function send() {
    setLoading(true); setErr("");
    try {
      const r = await postChat(msg, cid);
      setCid(r.conversation_id); setResp(r);
    } catch (e: unknown) {
      setErr(e instanceof Error ? e.message : "request failed");
    } finally { setLoading(false); }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">AI Environmental Scientist</h1>
      <div className="bg-white border rounded-2xl p-4 space-y-3">
        <textarea value={msg} onChange={(e) => setMsg(e.target.value)} rows={3} className="w-full border rounded-xl p-3 text-sm" />
        <button onClick={send} disabled={loading} className="bg-emerald-700 text-white px-4 py-2 rounded-xl text-sm disabled:opacity-50">
          {loading ? "Reasoning…" : "Assess ecosystem"}
        </button>
        {err && <p className="text-red-600 text-sm">{err} — is the backend running on :8000?</p>}
      </div>
      {resp && (
        <div className="space-y-4">
          <section className="bg-white border rounded-2xl p-4">
            <div className="flex items-center gap-3"><h2 className="font-semibold">Situation Assessment</h2><ConfidenceBadge value={resp.confidence} /></div>
            <p className="text-sm mt-2">{resp.situation_assessment}</p>
            <p className="text-xs text-slate-500 mt-1">Completeness {(resp.completeness * 100).toFixed(0)}% · Horizon {resp.time_horizon}</p>
          </section>
          {resp.clarifying_questions.length > 0 && (
            <section className="bg-amber-50 border border-amber-200 rounded-2xl p-4">
              <h2 className="font-semibold text-sm">🔎 Additional data needed</h2>
              <ul className="list-disc ml-5 text-sm">{resp.clarifying_questions.map((q, i) => <li key={i}>{q}</li>)}</ul>
            </section>
          )}
          <section className="bg-white border rounded-2xl p-4">
            <h2 className="font-semibold mb-1">Key Risks</h2>
            <ul className="list-disc ml-5 text-sm">{resp.key_risks.map((r, i) => <li key={i}>{r}</li>)}</ul>
          </section>
          <section className="grid md:grid-cols-2 gap-3">
            {resp.recommendations.map((r, i) => <RecommendationCard key={i} rec={r} />)}
          </section>
          <section className="bg-white border rounded-2xl p-4">
            <h2 className="font-semibold mb-1">Scientific Reasoning</h2>
            <p className="text-sm">{resp.scientific_reasoning}</p>
          </section>
          <section className="bg-white border rounded-2xl p-4">
            <h2 className="font-semibold mb-2">Reasoning Graph</h2>
            <ReasoningGraph data={resp.reasoning_graph} />
          </section>
          <section className="bg-white border rounded-2xl p-4">
            <h2 className="font-semibold mb-1">Supporting Sources</h2>
            <ul className="text-sm space-y-1">{resp.supporting_sources.map((s, i) => (
              <li key={i} className="border-b pb-1">[{s.source} {s.year}] <b>{s.publication}</b> <span className="text-slate-500">({s.evidence_strength})</span><br /><span className="text-slate-600">{s.excerpt}</span></li>
            ))}</ul>
          </section>
        </div>
      )}
    </div>
  );
}
