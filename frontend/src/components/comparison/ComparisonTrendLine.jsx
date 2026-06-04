/**
 * Multi-student trend line comparison.
 * One line per student, same chart.
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts'
import { Card, CardHeader, CardTitle, CardDescription, CardBody } from '../ui/Card'

function TrendTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-[#111111] border border-[#2a2a2a] rounded-lg px-3 py-2.5 shadow-[0_4px_12px_rgba(0,0,0,0.5)]">
      <p className="text-[11px] text-[#52525b] mb-2 font-medium uppercase tracking-wider">
        {label}
      </p>
      {payload.map((entry, i) =>
        entry.value !== null ? (
          <div key={i} className="flex items-center justify-between gap-6">
            <div className="flex items-center gap-1.5">
              <div className="w-3 h-0.5 rounded" style={{ backgroundColor: entry.stroke }} />
              <span className="text-[11px] text-[#a1a1aa]">{entry.name}</span>
            </div>
            <span className="text-xs font-semibold text-[#f5f5f5]">
              {Number(entry.value).toFixed(1)}%
            </span>
          </div>
        ) : null
      )}
    </div>
  )
}

function TrendLegend({ payload }) {
  return (
    <div className="flex flex-wrap items-center gap-4 justify-end px-1 mt-1">
      {payload?.map((entry, i) => (
        <div key={i} className="flex items-center gap-1.5">
          <div className="w-4 h-0.5" style={{ backgroundColor: entry.color }} />
          <span className="text-[11px] text-[#52525b]">{entry.value}</span>
        </div>
      ))}
    </div>
  )
}

export default function ComparisonTrendLine({ data, students }) {
  if (!data || data.length === 0) return null

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Grade Trend Comparison</CardTitle>
          <CardDescription>Monthly average — all selected students</CardDescription>
        </div>
      </CardHeader>
      <CardBody className="pt-0">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data} margin={{ top: 16, right: 16, bottom: 0, left: -10 }}>
            <CartesianGrid stroke="#1f1f1f" strokeWidth={1} vertical={false} />
            <XAxis
              dataKey="month"
              tick={{ fill: '#52525b', fontSize: 11, fontFamily: 'Inter' }}
              axisLine={false}
              tickLine={false}
              dy={8}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: '#52525b', fontSize: 11, fontFamily: 'Inter' }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v) => `${v}%`}
              width={40}
            />
            <ReferenceLine
              y={60}
              stroke="#ef4444"
              strokeDasharray="3 4"
              strokeWidth={1}
              strokeOpacity={0.3}
              label={{
                value: 'Pass',
                position: 'insideTopLeft',
                fill: '#ef4444',
                fontSize: 10,
                opacity: 0.5,
              }}
            />
            <Tooltip content={<TrendTooltip />} />
            <Legend content={<TrendLegend />} />

            {students.map((student) => (
              <Line
                key={student.student_id}
                type="monotone"
                dataKey={student.student_name}
                stroke={student.color}
                strokeWidth={1.5}
                dot={{ r: 3, fill: '#0a0a0a', stroke: student.color, strokeWidth: 1.5 }}
                activeDot={{ r: 4, fill: student.color, strokeWidth: 0 }}
                connectNulls={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardBody>
    </Card>
  )
}
