/**
 * Subject-by-subject comparison table.
 * Rows = subjects, Columns = each student.
 * Color-coded cells and rank indicators.
 */

import { Card, CardHeader, CardTitle, CardDescription } from '../ui/Card'

function getCellColor(score) {
  if (score >= 80) return { bg: 'rgba(34,197,94,0.08)',  text: '#22c55e' }
  if (score >= 60) return { bg: 'rgba(245,158,11,0.08)', text: '#f59e0b' }
  return                   { bg: 'rgba(239,68,68,0.08)', text: '#ef4444' }
}

function getRankBadge(rank) {
  const badges = {
    1: { bg: 'rgba(34,197,94,0.12)',  text: '#22c55e', label: '1st' },
    2: { bg: 'rgba(79,70,229,0.12)',  text: '#4f46e5', label: '2nd' },
    3: { bg: 'rgba(245,158,11,0.12)', text: '#f59e0b', label: '3rd' },
    4: { bg: 'rgba(239,68,68,0.08)', text: '#ef4444',  label: '4th' },
  }
  return badges[rank] || badges[4]
}

export default function ComparisonTable({ subjects, students }) {
  if (!subjects.length || !students.length) return null

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Subject-by-Subject Comparison</CardTitle>
          <CardDescription>Ranked performance per subject</CardDescription>
        </div>
      </CardHeader>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-[#1f1f1f]">
              <th className="text-left px-5 py-3 text-[11px] font-medium text-[#52525b] uppercase tracking-wider min-w-[120px]">
                Subject
              </th>
              {students.map((s) => (
                <th
                  key={s.student_id}
                  className="text-center px-4 py-3 text-[11px] font-medium uppercase tracking-wider min-w-[100px]"
                  style={{ color: s.color }}
                >
                  <div className="flex flex-col items-center gap-1">
                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: s.color }} />
                    {s.student_name.split(' ')[0]}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {subjects.map((subject) => {
              const scores = students.map((s) => ({
                id:    s.student_id,
                score: s.subject_averages?.[subject] || 0,
              }))
              const sorted = [...scores].sort((a, b) => b.score - a.score)

              return (
                <tr
                  key={subject}
                  className="border-b border-[#1f1f1f] last:border-b-0 hover:bg-[#161616] transition-colors duration-100"
                >
                  <td className="px-5 py-3 font-medium text-[#a1a1aa]">{subject}</td>
                  {students.map((student) => {
                    const score = student.subject_averages?.[subject]
                    const rank  = score
                      ? sorted.findIndex((s) => s.id === student.student_id) + 1
                      : null
                    const rankInfo    = rank ? getRankBadge(rank) : null
                    const colorScheme = score ? getCellColor(score) : null

                    return (
                      <td key={student.student_id} className="px-4 py-3 text-center">
                        {score ? (
                          <div className="flex flex-col items-center gap-1">
                            <span
                              className="font-semibold text-sm tracking-tight"
                              style={{ color: colorScheme?.text }}
                            >
                              {score.toFixed(1)}%
                            </span>
                            {rankInfo && (
                              <span
                                className="text-[10px] font-medium px-1.5 py-0.5 rounded"
                                style={{ backgroundColor: rankInfo.bg, color: rankInfo.text }}
                              >
                                {rankInfo.label}
                              </span>
                            )}
                          </div>
                        ) : (
                          <span className="text-[#3f3f46]">—</span>
                        )}
                      </td>
                    )
                  })}
                </tr>
              )
            })}

            {/* Overall row */}
            <tr className="bg-[#161616] border-t-2 border-[#2a2a2a]">
              <td className="px-5 py-3 text-[11px] font-semibold text-[#52525b] uppercase tracking-wider">
                Overall Average
              </td>
              {students.map((student) => {
                const avg   = student.overall_avg
                const color = getCellColor(avg)
                return (
                  <td key={student.student_id} className="px-4 py-3 text-center">
                    <span
                      className="font-bold text-sm tracking-tight"
                      style={{ color: color.text }}
                    >
                      {avg.toFixed(1)}%
                    </span>
                  </td>
                )
              })}
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  )
}
