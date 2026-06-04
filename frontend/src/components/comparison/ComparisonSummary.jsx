/**
 * Summary cards for comparison insights.
 * Top performer, most subjects, needs attention.
 */

import { Trophy, TrendingUp, AlertTriangle } from 'lucide-react'

export default function ComparisonSummary({ students }) {
  if (!students || students.length < 2) return null

  const sorted  = [...students].sort((a, b) => b.overall_avg - a.overall_avg)
  const leader  = sorted[0]
  const weakest = sorted[sorted.length - 1]

  const mostSubjectsStudent = students.reduce((a, b) =>
    Object.keys(a.subject_averages || {}).length >
    Object.keys(b.subject_averages || {}).length
      ? a
      : b
  )

  const summaries = [
    {
      icon:   Trophy,
      label:  'Top Performer',
      name:   leader.student_name,
      value:  `${leader.overall_avg.toFixed(1)}% avg`,
      color:  leader.color,
      bg:     'rgba(34,197,94,0.04)',
      border: 'rgba(34,197,94,0.15)',
    },
    {
      icon:   TrendingUp,
      label:  'Most Subjects',
      name:   mostSubjectsStudent.student_name,
      value:  `${Object.keys(mostSubjectsStudent.subject_averages || {}).length} subjects`,
      color:  '#4f46e5',
      bg:     'rgba(79,70,229,0.04)',
      border: 'rgba(79,70,229,0.15)',
    },
    {
      icon:   AlertTriangle,
      label:  'Needs Attention',
      name:   weakest.student_name,
      value:  `${weakest.overall_avg.toFixed(1)}% avg`,
      color:  weakest.color,
      bg:     'rgba(245,158,11,0.04)',
      border: 'rgba(245,158,11,0.15)',
    },
  ]

  return (
    <div className="grid grid-cols-3 gap-4">
      {summaries.map(({ icon: Icon, label, name, value, color, bg, border }) => (
        <div
          key={label}
          className="rounded-lg px-5 py-4 border transition-all duration-200"
          style={{ backgroundColor: bg, borderColor: border }}
        >
          <div className="flex items-center gap-2 mb-2">
            <Icon size={13} strokeWidth={1.5} style={{ color }} />
            <span className="text-[11px] font-medium text-[#52525b] uppercase tracking-widest">
              {label}
            </span>
          </div>
          <p className="text-sm font-semibold text-[#f5f5f5] tracking-tight">{name}</p>
          <p className="text-xs mt-0.5" style={{ color }}>{value}</p>
        </div>
      ))}
    </div>
  )
}
