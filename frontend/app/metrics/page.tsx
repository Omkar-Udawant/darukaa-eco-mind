"use client";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const data = [
  { name: "Biodiversity", gain: 18 }, { name: "Soil C", gain: 22 },
  { name: "Water", gain: 16 }, { name: "Habitat", gain: 20 }
];

export default function MetricsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Environmental Metrics & Impact</h1>
      <div className="bg-white border rounded-2xl p-4 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis /><Tooltip />
            <Bar dataKey="gain" fill="#047857" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-sm text-slate-600">Live per-conversation metrics are available at <code>GET /metrics/{"{id}"}</code>; impact per intervention at <code>POST /impact</code>.</p>
    </div>
  );
}
