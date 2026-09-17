import { ConfidenceBadge } from "../components/ConfidenceBadge";
import { MetricCard } from "../components/MetricCard";
import { ReasoningGraph } from "../components/ReasoningGraph";
import { RecommendationCard } from "../components/RecommendationCard";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div className="bg-emerald-900 text-white rounded-2xl p-6">
        <h1 className="text-2xl font-bold">Environmental Intelligence Dashboard</h1>
        <p className="text-emerald-100 text-sm mt-1">
          Multi-variable ecological reasoning across soil · climate · biodiversity · land-use · human impact.
          Every recommendation uses ≥3 dimensions with cited evidence.
        </p>
      </div>
      <div className="grid md:grid-cols-4 gap-4">
        <MetricCard label="Soil Carbon" value="0.6 %" hint="degraded (<1%)" />
        <MetricCard label="Rainfall" value="520 mm" hint="water-stressed" />
        <MetricCard label="Pollinators" value="low" hint="deficit risk" />
        <MetricCard label="Confidence" value="—" hint="run a chat assessment" />
      </div>
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl p-4 border">
          <h2 className="font-semibold mb-2">Reasoning flow (7 stages)</h2>
          <ReasoningGraph
            data={{ nodes: [
              { id: "input", label: "1 · Input analysis" }, { id: "complete", label: "2 · Completeness" },
              { id: "retrieval", label: "3 · Retrieval (FAO/IPCC/UNEP)" }, { id: "eco", label: "4 · Ecological reasoning" },
              { id: "interv", label: "5 · Interventions" }, { id: "impact", label: "6 · Impact" },
              { id: "conf", label: "7 · Confidence" }],
              edges: [
                { from: "input", to: "complete", label: "" }, { from: "complete", to: "retrieval", label: "" },
                { from: "retrieval", to: "eco", label: "" }, { from: "eco", to: "interv", label: "" },
                { from: "interv", to: "impact", label: "" }, { from: "impact", to: "conf", label: "" }] }}
          />
        </div>
        <div className="bg-white rounded-2xl p-4 border space-y-2">
          <h2 className="font-semibold">Try the scientist</h2>
          <p className="text-sm text-slate-600">Open Chat and paste: “Biodiversity is declining on my cropland. SOC 0.6%, rainfall 520mm, 34°C, heavy pesticide, few bees.”</p>
          <div className="flex gap-2 items-center"><ConfidenceBadge value={84} /><span className="text-xs text-slate-500">target confidence with complete data</span></div>
          <RecommendationCard
            rec={{ title: "Legume-based cover cropping", detail: "Sow nitrogen-fixing legumes off-season; terminate as mulch.", scientific_reasoning: "Legumes fix N, raise SOC, feed microbes and pollinators.", impacted_metrics: ["Soil Organic Carbon", "Pollinator Presence"], estimated_improvement: "15–25% SOC gain in 2–3 years", time_horizon: "Medium Term", confidence: 84, dimensions_used: ["soil", "biodiversity", "human_impact"], impact: { biodiversity_gain_pct: 14, soil_carbon_gain_pct: 22, water_retention_gain_pct: 16, habitat_quality_gain_pct: 12, horizon: "Medium Term" } }}
          />
        </div>
      </div>
    </div>
  );
}
