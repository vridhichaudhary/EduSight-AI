import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { TrendingUp, RefreshCw } from 'lucide-react'
import { useQueryClient } from '@tanstack/react-query'
import api from '../../services/api'
import PageHeader from '../../components/layout/PageHeader'
import Badge from '../../components/ui/Badge'
import { Card, CardBody } from '../../components/ui/Card'
import { SkeletonTable } from '../../components/ui/Skeleton'
import EmptyState from '../../components/ui/EmptyState'
import Button from '../../components/ui/Button'

export default function PredictionsPage() {
  const { studentId }  = useParams()
  const queryClient    = useQueryClient()

  // Fetch predictions directly from predictions endpoint
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['predictions', studentId],
    queryFn:  () => api.get(`/api/predictions/?student_id=${studentId}`),
    enabled:  !!studentId,
  })

  // Also fetch from dashboard as fallback
  const { data: dashData } = useQuery({
    queryKey: ['dashboard', studentId],
    queryFn:  () => api.get(`/api/dashboard/${studentId}/`),
    enabled:  !!studentId,
  })

  // Use direct predictions first, fall back to dashboard predictions
  const directPreds    = data?.data?.data || data?.data?.results || []
  const dashPreds      = dashData?.data?.data?.predictions || []
  const predictions    = directPreds.length > 0 ? directPreds : dashPreds

  return (
    <div className="space-y-6">
      <PageHeader
        badge="Predictions"
        title="Exam Predictions"
        description="ML-generated forecasts for upcoming assessments."
        actions={
          <Button
            variant="ghost"
            size="sm"
            icon={RefreshCw}
            onClick={() => {
              refetch()
              queryClient.invalidateQueries(['dashboard', studentId])
            }}
          >
            Refresh
          </Button>
        }
      />

      <Card>
        {isLoading ? (
          <SkeletonTable rows={6} />
        ) : predictions.length === 0 ? (
          <CardBody>
            <EmptyState
              icon={TrendingUp}
              title="No predictions yet"
              description="Click Run Analysis on the Overview page to generate ML predictions."
            />
          </CardBody>
        ) : (
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-[#1f1f1f]">
                {[
                  'Subject',
                  'Predicted Score',
                  'Range',
                  'Confidence',
                  'For Date',
                  'Risk',
                ].map((h) => (
                  <th
                    key={h}
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
                const predicted  = Number(p.predicted_marks || 0)
                const isRisk     = predicted < 60
                const confidence = p.confidence_score
                  ? Math.round(Number(p.confidence_score) * 100)
                  : null

                return (
                  <tr
                    key={i}
                    className={`
                      hover:bg-[#161616] transition-colors duration-100
                      ${i !== predictions.length - 1
                        ? 'border-b border-[#1f1f1f]'
                        : ''
                      }
                    `}
                  >
                    <td className="px-5 py-3 font-medium text-[#a1a1aa]">
                      {p.subject_name || p.subject?.name || '—'}
                    </td>
                    <td className="px-5 py-3 font-semibold
                      text-[#f5f5f5] tracking-tight"
                    >
                      {predicted.toFixed(1)}%
                    </td>
                    <td className="px-5 py-3 text-[#52525b]">
                      {p.lower_bound && p.upper_bound
                        ? `${Number(p.lower_bound).toFixed(0)}–${Number(p.upper_bound).toFixed(0)}%`
                        : '—'
                      }
                    </td>
                    <td className="px-5 py-3 text-[#52525b]">
                      {confidence !== null ? `${confidence}%` : '—'}
                    </td>
                    <td className="px-5 py-3 text-[#52525b]">
                      {p.prediction_for_date || '—'}
                    </td>
                    <td className="px-5 py-3">
                      <Badge
                        variant={isRisk ? 'danger' : 'success'}
                        dot
                      >
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

      {/* Debug info — remove after fixing */}
      {predictions.length === 0 && !isLoading && (
        <div className="bg-[#111111] border border-[#2a2a2a]
          rounded-lg px-4 py-3"
        >
          <p className="text-xs text-[#52525b]">
            No predictions found for student ID: {studentId}.
            Go to Overview → click Run Analysis → wait 15-30 seconds → refresh this page.
          </p>
        </div>
      )}
    </div>
  )
}
