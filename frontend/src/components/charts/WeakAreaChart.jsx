/**
 * Weak Area Horizontal Bar Chart
 * Ranked subjects by performance gap.
 * Color: red/amber/green by score.
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardDescription, CardBody }
  from '../ui/Card'
import { Skeleton } from '../ui/Skeleton'
import EmptyState from '../ui/EmptyState'
import Badge from '../ui/Badge'
import { Target } from 'lucide-react'

// ─── Get color by score ───
function getBarColor(score) {
  if (score >= 75) return '#22c55e'
  if (score >= 60) return '#f59e0b'
  if (score >= 40) return '#f97316'
  return '#ef4444'
}

function getSeverityBadge(score) {
  if (score >= 75) return { variant: 'success', label: 'Good' }
  if (score >= 60) return { variant: 'warning', label: 'Moderate' }
  if (score >= 40) return { variant: 'danger',  label: 'Severe' }
  return { variant: 'danger', label: 'Critical' }
}

// ─── Custom YAxis Label ───
function CustomYAxisTick({ x, y, payload }) {
  return (
    <text
      x={x - 8}
      y={y}
      textAnchor="end"
      dominantBaseline="middle"
      fill="#a1a1aa"
      fontSize={12}
      fontFamily="Inter, sans-serif"
    >
      {payload.value}
    </text>
  )
}

// ─── Custom Tooltip ───
function WeakAreaTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const score = payload[0]?.value
  const { variant, label: sevLabel } = getSeverityBadge(score)
  return (
    <div className="bg-[#111111] border border-[#2a2a2a]
      rounded-lg px-3 py-2.5 shadow-[0_4px_12px_rgba(0,0,0,0.5)]"
    >
      <p className="text-xs font-medium text-[#f5f5f5] mb-1">{label}</p>
      <p className="text-lg font-semibold text-[#f5f5f5] tracking-tight">
        {Number(score).toFixed(1)}%
      </p>
      <p className="text-[11px] text-[#52525b] mt-0.5">
        {sevLabel} performance
      </p>
    </div>
  )
}

// ─── Main Component ───
export default function WeakAreaChart({ data, loading }) {

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Subject Breakdown</CardTitle>
        </CardHeader>
        <CardBody>
          <Skeleton className="h-64 w-full" />
        </CardBody>
      </Card>
    )
  }

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Subject Breakdown</CardTitle>
        </CardHeader>
        <CardBody>
          <EmptyState
            icon={Target}
            title="No weak area data"
            description="Analysis will identify subjects after upload."
          />
        </CardBody>
      </Card>
    )
  }

  // Sort ascending (worst first)
  const sorted = [...data].sort((a, b) => a.score - b.score)

  const classAvg = sorted.reduce((s, d) => s + d.score, 0) / sorted.length

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Subject Breakdown</CardTitle>
          <CardDescription>
            Sorted by performance — class avg {classAvg.toFixed(1)}%
          </CardDescription>
        </div>
      </CardHeader>
      <CardBody className="pt-0">
        <ResponsiveContainer width="100%" height={Math.max(200, sorted.length * 48)}>
          <BarChart
            data={sorted}
            layout="vertical"
            margin={{ top: 8, right: 16, bottom: 0, left: 80 }}
            barSize={10}
          >
            <CartesianGrid
              strokeDasharray="0"
              stroke="#1f1f1f"
              horizontal={false}
              vertical={true}
            />
            <XAxis
              type="number"
              domain={[0, 100]}
              tick={{
                fill: '#52525b',
                fontSize: 11,
                fontFamily: 'Inter',
              }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${v}%`}
            />
            <YAxis
              type="category"
              dataKey="subject"
              tick={<CustomYAxisTick />}
              axisLine={false}
              tickLine={false}
              width={76}
            />

            {/* Class average reference */}
            <ReferenceLine
              x={classAvg}
              stroke="#52525b"
              strokeDasharray="3 4"
              strokeWidth={1}
              label={{
                value: 'Avg',
                position: 'top',
                fill: '#52525b',
                fontSize: 10,
                fontFamily: 'Inter',
              }}
            />

            <Tooltip
              content={<WeakAreaTooltip />}
              cursor={{ fill: 'rgba(255,255,255,0.02)' }}
            />
            <Bar dataKey="score" radius={[0, 3, 3, 0]}>
              {sorted.map((entry, i) => (
                <Cell
                  key={`cell-${i}`}
                  fill={getBarColor(entry.score)}
                  fillOpacity={0.85}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        {/* Legend */}
        <div className="flex items-center gap-4 mt-4 pt-4
          border-t border-[#1f1f1f]"
        >
          {[
            { label: 'Critical  < 40%',  color: '#ef4444' },
            { label: 'Severe  40–60%',   color: '#f97316' },
            { label: 'Moderate  60–75%', color: '#f59e0b' },
            { label: 'Good  > 75%',      color: '#22c55e' },
          ].map(({ label, color }) => (
            <div key={label} className="flex items-center gap-1.5">
              <div
                className="w-2 h-2 rounded-sm"
                style={{ backgroundColor: color, opacity: 0.85 }}
              />
              <span className="text-[11px] text-[#52525b]">{label}</span>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  )
}
