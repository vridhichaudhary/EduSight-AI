/**
 * EduSight AI — Custom Recharts Tooltip
 * Shared across all chart components.
 */

export default function ChartTooltip({ active, payload, label, formatter }) {
  if (!active || !payload || !payload.length) return null

  return (
    <div
      className="
        bg-[#111111] border border-[#2a2a2a]
        rounded-lg px-3 py-2.5
        shadow-[0_4px_12px_rgba(0,0,0,0.5)]
        min-w-[120px]
      "
    >
      {label && (
        <p className="text-[11px] text-[#52525b] mb-2 font-medium
          uppercase tracking-wider"
        >
          {label}
        </p>
      )}
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-1.5">
            <div
              className="w-1.5 h-1.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-[11px] text-[#a1a1aa]">
              {entry.name}
            </span>
          </div>
          <span className="text-xs font-semibold text-[#f5f5f5]">
            {formatter ? formatter(entry.value, entry.name) : entry.value}
          </span>
        </div>
      ))}
    </div>
  )
}
