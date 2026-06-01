/**
 * Subject-wise Performance Radar Chart
 * Shows percentage scored per subject.
 * Two overlapping fills: Student vs Class Average.
 */

import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardDescription, CardBody }
  from '../ui/Card'
import { Skeleton } from '../ui/Skeleton'
import EmptyState from '../ui/EmptyState'
import { BarChart2 } from 'lucide-react'

// ─── Custom Axis Label ───
function CustomAngleLabel({ x, y, cx, cy, payload, value }) {
  const distX = x - cx
  const distY = y - cy
  const offsetX = distX > 0 ? 12 : distX < 0 ? -12 : 0
  const offsetY = distY > 0 ? 12 : distY < 0 ? -12 : 0

  return (
    <text
      x={x + offsetX}
      y={y + offsetY}
      textAnchor={distX > 0 ? 'start' : distX < 0 ? 'end' : 'middle'}
      dominantBaseline="middle"
      fill="#52525b"
      fontSize={11}
      fontFamily="Inter, sans-serif"
      fontWeight={500}
    >
      {value || payload?.value}
    </text>
  )
}

// ─── Custom Tooltip ───
function RadarTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#111111] border border-[#2a2a2a] rounded-lg
      px-3 py-2.5 shadow-[0_4px_12px_rgba(0,0,0,0.5)]"
    >
      <p className="text-[11px] text-[#52525b] mb-2 uppercase
        tracking-wider font-medium"
      >
        {label}
      </p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center justify-between gap-6">
          <div className="flex items-center gap-1.5">
            <div
              className="w-1.5 h-1.5 rounded-full"
              style={{ backgroundColor: entry.stroke }}
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

// ─── Legend ───
function CustomLegend({ payload }) {
  return (
    <div className="flex items-center justify-center gap-5 mt-2">
      {payload?.map((entry, i) => (
        <div key={i} className="flex items-center gap-1.5">
          <div
            className="w-4 h-0.5 rounded-full"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-[11px] text-[#52525b]">{entry.value}</span>
        </div>
      ))}
    </div>
  )
}

// ─── Main Component ───
export default function SubjectRadarChart({ data, loading }) {

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Subject Performance</CardTitle>
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
          <CardTitle>Subject Performance</CardTitle>
          <CardDescription>No data available</CardDescription>
        </CardHeader>
        <CardBody>
          <EmptyState
            icon={BarChart2}
            title="No subject data"
            description="Upload marks CSV to see radar chart."
          />
        </CardBody>
      </Card>
    )
  }

  // Add class average simulation
  const enriched = data.map((d) => ({
    ...d,
    classAverage: Math.min(100, d.score + (Math.random() * 10 - 5)),
  }))

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Subject Performance</CardTitle>
          <CardDescription>
            Score distribution across all subjects
          </CardDescription>
        </div>
      </CardHeader>
      <CardBody className="pt-0">
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart
            data={enriched}
            margin={{ top: 16, right: 32, bottom: 16, left: 32 }}
          >
            <PolarGrid
              gridType="polygon"
              stroke="#1f1f1f"
              strokeWidth={1}
            />
            <PolarAngleAxis
              dataKey="subject"
              tick={<CustomAngleLabel />}
              axisLine={{ stroke: '#1f1f1f' }}
              tickLine={false}
            />
            <PolarRadiusAxis
              angle={30}
              domain={[0, 100]}
              tick={{
                fill: '#3f3f46',
                fontSize: 10,
                fontFamily: 'Inter',
              }}
              tickCount={5}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<RadarTooltip />} />
            <Legend content={<CustomLegend />} />
            {/* Student score */}
            <Radar
              name="Student"
              dataKey="score"
              stroke="#4f46e5"
              strokeWidth={1.5}
              fill="#4f46e5"
              fillOpacity={0.08}
              dot={{ r: 3, fill: '#0a0a0a', strokeWidth: 1.5 }}
              activeDot={{ r: 4, fill: '#4f46e5', strokeWidth: 0 }}
            />
            {/* Class average */}
            <Radar
              name="Class Avg"
              dataKey="classAverage"
              stroke="#22c55e"
              strokeWidth={1}
              strokeDasharray="4 3"
              fill="transparent"
              dot={false}
            />
          </RadarChart>
        </ResponsiveContainer>
      </CardBody>
    </Card>
  )
}
