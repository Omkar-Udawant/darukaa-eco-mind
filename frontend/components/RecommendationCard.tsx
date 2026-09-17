import type { Recommendation } from "../lib/types";
import { ConfidenceBadge } from "./ConfidenceBadge";

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <div className="bg-white border rounded-2xl p-4 space-y-2">
      <div className="flex justify-between items-start gap-2">
        <h3 className="font-semibold text-sm">{rec.title}</h3>
        <ConfidenceBadge value={rec.confidence} />
      </div>
      <p className="text-sm">{rec.detail}</p>
      <p className="text-xs text-slate-600"><b>Why:</b> {rec.scientific_reasoning}</p>
      <p className="text-xs"><b>Impacts:</b> {rec.impacted_metrics.join(" · ")}</p>
      <p className="text-xs"><b>Est.:</b> {rec.estimated_improvement} ({rec.time_horizon})</p>
      <p className="text-xs text-slate-500">Dimensions: {rec.dimensions_used.join(", ")} · +{rec.impact.biodiversity_gain_pct}% biodiversity</p>
    </div>
  );
}
