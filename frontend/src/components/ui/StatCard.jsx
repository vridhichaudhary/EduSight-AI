/**
 * StatCard — KPI display card for dashboard metrics
 * Minimal. Number prominent. Label small.
 */

import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Skeleton } from './Skeleton'

export default function StatCard({
  label,
  value,
  change,
  changeLabel,
  icon: Icon,
  loading = false,
}) {
  if (loading) {
    return (
      <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-5">
        <Skeleton className="h-3 w-20 mb-3" />
        <Skeleton className="h-7 w-28 mb-2" />
        <Skeleton className="h-3 w-24" />
      </div>
    )
  }

  const trendPositive = change > 0
  const trendNeutral  = change === 0

  return (
    <div className="
      bg-[#111111] border border-[#1f1f1f] rounded-lg p-5
      hover:border-[#2a2a2a] transition-colors duration-150
    ">
      {/* Label row */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-[11px] font-medium text-[#52525b] uppercase tracking-widest">
          {label}
        </span>
        {Icon && (
          <div className="w-7 h-7 rounded-md bg-[#161616] border border-[#1f1f1f]
            flex items-center justify-center">
            <Icon size={13} strokeWidth={1.5} className="text-[#52525b]" />
          </div>
        )}
      </div>

      {/* Value */}
      <div className="text-2xl font-semibold text-[#f5f5f5] tracking-tight mb-2">
        {value}
      </div>

      {/* Trend */}
      {change !== undefined && (
        <div className="flex items-center gap-1.5">
          {trendNeutral ? (
            <Minus size={12} className="text-[#52525b]" />
          ) : trendPositive ? (
            <TrendingUp size={12} className="text-[#22c55e]" />
          ) : (
            <TrendingDown size={12} className="text-[#ef4444]" />
          )}
          <span
            className={`text-xs font-medium ${
              trendNeutral
                ? 'text-[#52525b]'
                : trendPositive
                ? 'text-[#22c55e]'
                : 'text-[#ef4444]'
            }`}
          >
            {trendPositive ? '+' : ''}{change}%
          </span>
          {changeLabel && (
            <span className="text-xs text-[#52525b]">{changeLabel}</span>
          )}
        </div>
      )}
    </div>
  )
}
