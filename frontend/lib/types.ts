export interface Impact { biodiversity_gain_pct: number; soil_carbon_gain_pct: number; water_retention_gain_pct: number; habitat_quality_gain_pct: number; horizon: string; }
export interface Recommendation { title: string; detail: string; scientific_reasoning: string; impacted_metrics: string[]; estimated_improvement: string; time_horizon: string; confidence: number; dimensions_used: string[]; impact: Impact; }
export interface Source { source: string; publication: string; year: number; topic: string; evidence_strength: string; excerpt: string; }
export interface ChatResponse {
  conversation_id: string; situation_assessment: string; key_risks: string[];
  recommendations: Recommendation[]; scientific_reasoning: string; impacted_metrics: string[];
  estimated_improvement: string; time_horizon: string; confidence: number;
  supporting_sources: Source[]; additional_data_needed: string[]; clarifying_questions: string[];
  reasoning_graph: { nodes: { id: string; label: string }[]; edges: { from: string; to: string; label: string }[] };
  completeness: number;
}
