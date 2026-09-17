export default function ReasoningPage() {
  return (
    <div className="space-y-3">
      <h1 className="text-xl font-bold">Reasoning Visualization</h1>
      <div className="bg-white border rounded-2xl p-4 text-sm space-y-2">
        <p><b>Example causal chain:</b> Low Soil Carbon → Reduced Microbial Activity → Lower Plant Diversity → Reduced Pollinator Population → Biodiversity Loss</p>
        <p>Full interactive graph renders on the Chat page from <code>reasoning_graph</code> in every <code>/chat</code> response, and raw chains via <code>POST /reasoning</code>.</p>
      </div>
    </div>
  );
}
