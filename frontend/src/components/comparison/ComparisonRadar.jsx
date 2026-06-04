/**
 * Overlapping Radar Chart for student comparison.
 * Each student = one filled + stroked shape.
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
import { Card, CardHeader, CardTitle, CardDescription, CardBody } from '../ui/Card'

function CustomLegend({ payload }) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-4 mt-2">
      {payload?.map((entry, i) => (
        <div key={i} className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
          <span className="text-[11px] text-[#a1a1aa]">{entry.value}</span>
        </div>
      ))}
    </div>
  )
}

function ComparisonTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#111111] border border-[#2a2a2a] rounded-lg px-3 py-2.5 shadow-[0_4px_12px_rgba(0,0,0,0.5)]">
      <p className="text-[11px] text-[#52525b] mb-2 uppercase tracking-wider font-medium">
        {label}
      </p>
      {payload.map((entry, i) => (
        <div key={i} className="flex items-center justify-between gap-6">
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: entry.stroke }} />
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

export default function ComparisonRadar({ data, students }) {
  if (!data || data.length === 0) return null

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Subject Performance Comparison</CardTitle>
          <CardDescription>Overlapping radar — each shape = one student</CardDescription>
        </div>
      </CardHeader>
      <CardBody className="pt-0">
        <ResponsiveContainer width="100%" height={320}>
          <RadarChart data={data} margin={{ top: 20, right: 40, bottom: 20, left: 40 }}>
            <PolarGrid stroke="#1f1f1f" strokeWidth={1} gridType="polygon" />
            <PolarAngleAxis
              dataKey="subject"
              tick={{ fill: '#52525b', fontSize: 11, fontFamily: 'Inter' }}
              axisLine={{ stroke: '#1f1f1f' }}
              tickLine={false}
            />
            <PolarRadiusAxis
              angle={30}
              domain={[0, 100]}
              tick={{ fill: '#3f3f46', fontSize: 10 }}
              tickCount={5}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<ComparisonTooltip />} />
            <Legend content={<CustomLegend />} />

            {students.map((student, i) => (
              <Radar
                key={student.student_id}
                name={student.student_name}
                dataKey={student.student_name}
                stroke={student.color}
                strokeWidth={1.5}
                fill={student.color}
                fillOpacity={0.06 + i * 0.02}
                dot={{ r: 3, fill: '#0a0a0a', strokeWidth: 1.5 }}
                activeDot={{ r: 4, fill: student.color, strokeWidth: 0 }}
              />
            ))}
          </RadarChart>
        </ResponsiveContainer>
      </CardBody>
    </Card>
  )
}
