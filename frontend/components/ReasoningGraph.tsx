"use client";

export function ReasoningGraph({ data }: { data: { nodes: { id: string; label: string }[]; edges: { from: string; to: string; label: string }[] } }) {
  return (
    <div className="text-xs space-y-1">
      <div className="flex flex-wrap gap-2">
        {data.nodes.map((n) => (
          <span key={n.id} className="bg-emerald-50 border border-emerald-200 rounded-full px-3 py-1">{n.label}</span>
        ))}
      </div>
      <ul className="text-slate-600">
        {data.edges.map((e, i) => <li key={i}>{e.from} —{e.label || "→"}→ {e.to}</li>)}
      </ul>
    </div>
  );
}
