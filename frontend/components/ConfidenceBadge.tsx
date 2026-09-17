export function ConfidenceBadge({ value }: { value: number }) {
  const c = value >= 80 ? "bg-emerald-100 text-emerald-800" : value >= 60 ? "bg-amber-100 text-amber-800" : "bg-red-100 text-red-800";
  return <span className={`text-xs font-bold px-2 py-1 rounded-full ${c}`}>Confidence {value}%</span>;
}
