import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp } from 'lucide-react'
import { dashboardAPI } from '../../services/api'
import PageHeader from '../../components/layout/PageHeader'
import Badge from '../../components/ui/Badge'
import { Card, CardBody } from '../../components/ui/Card'
import { SkeletonTable } from '../../components/ui/Skeleton'
import EmptyState from '../../components/ui/EmptyState'

export default function PredictionsPage() {
  const { studentId } = useParams()

  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', studentId],
    queryFn: () => dashboardAPI.get(studentId),
    enabled: !!studentId,
  })

  const predictions = data?.data?.data?.predictions || []

  return (
    <div className="space-y-6">
      <PageHeader
        badge="Predictions"
        title="Exam Predictions"
        description="ML-generated forecasts for upcoming assessments."
      />

      <Card>
        {isLoading ? (
          <SkeletonTable rows={6} />
        ) : predictions.length === 0 ? (
          <CardBody>
            <EmptyState
              icon={TrendingUp}
              title="No predictions yet"
              description="Run analysis to generate ML predictions."
            />
          </CardBody>
        ) : (
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-[#1f1f1f]">
                {['Subject', 'Predicted Score', 'Range',
                  'Confidence', 'For Date', 'Risk'].map((h) => (
                  <th key={h}
                    className="text-left px-5 py-3 text-[11px]
                      font-medium text-[#52525b] uppercase tracking-wider"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {predictions.map((p, i) => {
                const isRisk = p.predicted_marks < 60
                return (
                  <tr key={i}
                    className={`hover:bg-[#161616] transition-colors duration-100
                      ${i !== predictions.length - 1 ? 'border-b border-[#1f1f1f]' : ''}
                    `}
                  >
                    <td className="px-5 py-3 font-medium text-[#a1a1aa]">
                      {p.subject_name}
                    </td>
                    <td className="px-5 py-3 font-semibold text-[#f5f5f5]
                      tracking-tight"
                    >
                      {Number(p.predicted_marks).toFixed(1)}%
                    </td>
                    <td className="px-5 py-3 text-[#52525b]">
                      {p.lower_bound && p.upper_bound
                        ? `${Number(p.lower_bound).toFixed(0)}–${Number(p.upper_bound).toFixed(0)}%`
                        : '—'}
                    </td>
                    <td className="px-5 py-3 text-[#52525b]">
                      {Math.round(p.confidence_score * 100)}%
                    </td>
                    <td className="px-5 py-3 text-[#52525b]">
                      {p.prediction_for_date}
                    </td>
                    <td className="px-5 py-3">
                      <Badge variant={isRisk ? 'danger' : 'success'} dot>
                        {isRisk ? 'At Risk' : 'On Track'}
                      </Badge>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  )
}
