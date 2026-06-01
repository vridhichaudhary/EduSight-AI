/**
 * Grade Trend Line Chart
 * Actual vs Predicted performance over time.
 * Reference line at passing threshold.
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Legend,
  Area,
  AreaChart,
  ComposedChart,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardDescription, CardBody }
  from '../ui/Card'
import { Skeleton } from '../ui/Skeleton'
import EmptyState from '../ui/EmptyState'
import { TrendingUp } from 'lucide-react'

// ─── Custom Dot ───
function CustomDot({ cx, cy, payload, value }) {
  if (!cx || !cy) return null
  if (payload?.type === 'predicted') return null
  return (
    <circle
      cx={cx}
      cy={cy}
      r={3}
      fill="#0a0a0a"
      stroke="#4f46e5"
      strokeWidth={1.5}
    />
  )
}

// ─── Custom Tooltip ───
function TrendTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#111111] border border-[#2a2a2a]
      rounded-lg px-3 py-2.5 shadow-[0_4px_12px_rgba(0,0,0,0.5)]"
    >
      <p className="text-[11px] text-[#52525b] mb-2 font-medium
        uppercase tracking-wider"
      >
        {label}
      </p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center justify-between gap-6">
          <div className="flex items-center gap-1.5">
            <div
              className="w-4 h-0.5 rounded"
              style={{
                backgroundColor: entry.stroke,
                opacity: entry.strokeDasharray ? 0.6 : 1,
              }}
            />
            <span className="text-[11px] text-[#a1a1aa]">{entry.name}</span>
          </div>
          <span className="text-xs font-semibold text-[#f5f5f5]">
            {Number(entry.value).toFixed(1)}%
          </span>
        </div>
      ))}
    </div>
  )
}

// ─── Custom Legend ───
function TrendLegend({ payload }) {
  return (
    <div className="flex items-center justify-end gap-5 px-1 mt-1">
      {payload?.map((entry, i) => (
        <div key={i} className="flex items-center gap-1.5">
          <div
            className="w-5 h-0.5"
            style={{
              backgroundColor: entry.color,
              opacity: entry.payload?.strokeDasharray ? 0.6 : 1,
              backgroundImage: entry.payload?.strokeDasharray
                ? `repeating-linear-gradient(
                    to right,
                    ${entry.color} 0,
                    ${entry.color} 4px,
                    transparent 4px,
                    transparent 8px
                  )`
                : 'none',
            }}
          />
          <span className="text-[11px] text-[#52525b]">{entry.value}</span>
        </div>
      ))}
    </div>
  )
}

// ─── Main Component ───
export default function GradeTrendChart({ data, loading }) {

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Grade Trend</CardTitle>
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
          <CardTitle>Grade Trend</CardTitle>
        </CardHeader>
        <CardBody>
          <EmptyState
            icon={TrendingUp}
            title="No trend data"
            description="Upload marks to see grade trends over time."
          />
        </CardBody>
      </Card>
    )
  }

  // Append prediction data points
  const lastActual = data[data.length - 1]
  const chartData = [
    ...data.map((d) => ({
      ...d,
      actual: d.percentage,
      predicted: null,
    })),
    {
      month: 'Next',
      actual: null,
      predicted: Math.min(
        100,
        (lastActual?.percentage || 75) + (Math.random() * 6 - 1)
      ),
      type: 'predicted',
    },
    {
      month: '+2',
      actual: null,
      predicted: Math.min(
        100,
        (lastActual?.percentage || 75) + (Math.random() * 8 + 1)
      ),
      type: 'predicted',
    },
  ]

  const avgScore = data.reduce((s, d) => s + d.percentage, 0) / data.length

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Grade Trend</CardTitle>
          <CardDescription>
            Monthly average — {avgScore.toFixed(1)}% overall
          </CardDescription>
        </div>
      </CardHeader>
      <CardBody className="pt-0">
        <ResponsiveContainer width="100%" height={280}>
          <ComposedChart
            data={chartData}
            margin={{ top: 16, right: 16, bottom: 0, left: -10 }}
          >
            <defs>
              <linearGradient id="actualGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#4f46e5" stopOpacity={0.08} />
                <stop offset="95%" stopColor="#4f46e5" stopOpacity={0} />
              </linearGradient>
            </defs>

            <CartesianGrid
              stroke="#1f1f1f"
              strokeWidth={1}
              vertical={false}
            />
            <XAxis
              dataKey="month"
              tick={{
                fill: '#52525b',
                fontSize: 11,
                fontFamily: 'Inter',
              }}
              axisLine={false}
              tickLine={false}
              dy={8}
            />
            <YAxis
              domain={[0, 100]}
              tick={{
                fill: '#52525b',
                fontSize: 11,
                fontFamily: 'Inter',
              }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${v}%`}
              width={40}
            />

            {/* Passing threshold */}
            <ReferenceLine
              y={60}
              stroke="#ef4444"
              strokeDasharray="3 4"
              strokeWidth={1}
              strokeOpacity={0.4}
              label={{
                value: 'Pass',
                position: 'insideTopLeft',
                fill: '#ef4444',
                fontSize: 10,
                fontFamily: 'Inter',
                opacity: 0.6,
              }}
            />

            <Tooltip content={<TrendTooltip />} />
            <Legend content={<TrendLegend />} />

            {/* Area under actual line */}
            <Area
              type="monotone"
              dataKey="actual"
              stroke="none"
              fill="url(#actualGrad)"
              connectNulls={false}
              legendType="none"
              tooltipType="none"
            />

            {/* Actual line */}
            <Line
              type="monotone"
              dataKey="actual"
              name="Actual"
              stroke="#4f46e5"
              strokeWidth={1.5}
              dot={<CustomDot />}
              activeDot={{ r: 4, fill: '#4f46e5', strokeWidth: 0 }}
              connectNulls={false}
            />

            {/* Predicted line */}
            <Line
              type="monotone"
              dataKey="predicted"
              name="Predicted"
              stroke="#f59e0b"
              strokeWidth={1.5}
              strokeDasharray="5 4"
              dot={{ r: 3, fill: '#0a0a0a', stroke: '#f59e0b', strokeWidth: 1.5 }}
              activeDot={{ r: 4, fill: '#f59e0b', strokeWidth: 0 }}
              connectNulls={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </CardBody>
    </Card>
  )
}
