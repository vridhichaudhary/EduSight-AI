import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useQueryClient } from '@tanstack/react-query'
import { BookOpen, ExternalLink, Clock, RefreshCw } from 'lucide-react'
import api from '../../services/api'
import PageHeader from '../../components/layout/PageHeader'
import Badge from '../../components/ui/Badge'
import { Card, CardBody } from '../../components/ui/Card'
import EmptyState from '../../components/ui/EmptyState'
import { Skeleton } from '../../components/ui/Skeleton'
import Button from '../../components/ui/Button'

export default function RecommendationsPage() {
  const { studentId } = useParams()
  const queryClient   = useQueryClient()

  // Fetch recommendations directly
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['recommendations', studentId],
    queryFn:  () =>
      api.get(`/api/recommendations/?student_id=${studentId}`),
    enabled: !!studentId,
  })

  // Also fetch from dashboard as fallback
  const { data: dashData } = useQuery({
    queryKey: ['dashboard', studentId],
    queryFn:  () => api.get(`/api/dashboard/${studentId}/`),
    enabled:  !!studentId,
  })

  const directRecs  = data?.data?.data || data?.data?.results || []
  const dashRecs    = dashData?.data?.data?.recommendations || []
  const recs        = directRecs.length > 0 ? directRecs : dashRecs

  return (
    <div className="space-y-6">
      <PageHeader
        badge="AI"
        title="Study Recommendations"
        description="Personalized plans generated from your weak area analysis."
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

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="bg-[#111111] border border-[#1f1f1f]
                rounded-lg p-5"
            >
              <Skeleton className="h-3 w-24 mb-3" />
              <Skeleton className="h-4 w-64 mb-2" />
              <Skeleton className="h-3 w-full" />
            </div>
          ))}
        </div>
      ) : recs.length === 0 ? (
        <Card>
          <CardBody>
            <EmptyState
              icon={BookOpen}
              title="No recommendations yet"
              description="Go to Overview and click Run Analysis to generate AI study recommendations."
            />
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-3">
          {recs.map((rec, i) => (
            <div
              key={i}
              className="bg-[#111111] border border-[#1f1f1f]
                rounded-lg p-5 hover:border-[#2a2a2a]
                transition-colors duration-150"
            >
              {/* Header */}
              <div className="flex items-start justify-between
                gap-4 mb-3"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    <Badge variant="default">
                      {rec.subject_name || rec.subject || '—'}
                    </Badge>
                    {rec.recommendation_type && (
                      <Badge variant="accent">
                        {rec.recommendation_type}
                      </Badge>
                    )}
                  </div>
                  <h3 className="text-sm font-medium text-[#f5f5f5]">
                    {rec.title || 'Study Plan'}
                  </h3>
                </div>
                <div className="flex items-center gap-1.5
                  flex-shrink-0 text-[#52525b]"
                >
                  <Clock size={12} strokeWidth={1.5} />
                  <span className="text-[11px]">
                    {rec.study_hours_suggested || rec.study_hours || 3}h/week
                  </span>
                </div>
              </div>

              {/* Description */}
              {rec.description && (
                <p className="text-xs text-[#71717a]
                  leading-relaxed mb-4"
                >
                  {rec.description}
                </p>
              )}

              {/* Topics */}
              {rec.topics_to_study &&
               rec.topics_to_study.length > 0 && (
                <div className="mb-4">
                  <p className="text-[11px] font-medium
                    text-[#52525b] uppercase tracking-wider mb-2"
                  >
                    Topics to Cover
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {rec.topics_to_study.map((topic, j) => (
                      <Badge key={j} variant="default">
                        {topic}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Resources */}
              {rec.resources && rec.resources.length > 0 && (
                <div className="space-y-1.5">
                  <p className="text-[11px] font-medium
                    text-[#52525b] uppercase tracking-wider mb-2"
                  >
                    Resources
                  </p>
                  {rec.resources.slice(0, 3).map((resource, j) => (
                    <a
                      key={j}
                      href={resource.url || '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 py-2 px-3
                        bg-[#161616] border border-[#1f1f1f]
                        rounded-md hover:border-[#2a2a2a]
                        transition-colors duration-150 group"
                    >
                      <span className="text-xs text-[#a1a1aa]
                        group-hover:text-[#f5f5f5] transition-colors
                        flex-1"
                      >
                        {resource.title || resource.url}
                      </span>
                      {resource.difficulty && (
                        <Badge variant="default">
                          {resource.difficulty}
                        </Badge>
                      )}
                      <ExternalLink
                        size={11}
                        strokeWidth={1.5}
                        className="text-[#3f3f46]
                          group-hover:text-[#52525b] flex-shrink-0"
                      />
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Debug info — remove after fixing */}
      {recs.length === 0 && !isLoading && (
        <div className="bg-[#111111] border border-[#2a2a2a]
          rounded-lg px-4 py-3"
        >
          <p className="text-xs text-[#52525b]">
            No recommendations found for student ID: {studentId}.
            Go to Overview → click Run Analysis → wait 15-30 seconds → return here.
          </p>
        </div>
      )}
    </div>
  )
}
