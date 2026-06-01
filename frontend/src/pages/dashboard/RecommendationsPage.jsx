import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { BookOpen, ExternalLink, Clock } from 'lucide-react'
import { dashboardAPI } from '../../services/api'
import PageHeader from '../../components/layout/PageHeader'
import Badge from '../../components/ui/Badge'
import { Card, CardBody } from '../../components/ui/Card'
import EmptyState from '../../components/ui/EmptyState'
import { Skeleton } from '../../components/ui/Skeleton'

export default function RecommendationsPage() {
  const { studentId } = useParams()

  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', studentId],
    queryFn: () => dashboardAPI.get(studentId),
    enabled: !!studentId,
  })

  const recs = data?.data?.data?.recommendations || []

  return (
    <div className="space-y-6">
      <PageHeader
        badge="AI"
        title="Study Recommendations"
        description="Personalized plans generated from your weak area analysis."
      />

      {isLoading ? (
        <div className="space-y-3">
          {[1,2,3].map((i) => (
            <div key={i}
              className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-5"
            >
              <Skeleton className="h-3 w-32 mb-3" />
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
              description="Run analysis to generate AI study recommendations."
            />
          </CardBody>
        </Card>
      ) : (
        <div className="space-y-3">
          {recs.map((rec, i) => (
            <div
              key={i}
              className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-5
                hover:border-[#2a2a2a] transition-colors duration-150"
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-4 mb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    <Badge variant="default">{rec.subject_name}</Badge>
                    <Badge variant="accent">{rec.recommendation_type}</Badge>
                  </div>
                  <h3 className="text-sm font-medium text-[#f5f5f5]">
                    {rec.title}
                  </h3>
                </div>
                <div className="flex items-center gap-1.5 flex-shrink-0
                  text-[#52525b]"
                >
                  <Clock size={12} strokeWidth={1.5} />
                  <span className="text-[11px]">
                    {rec.study_hours_suggested}h/week
                  </span>
                </div>
              </div>

              {/* Description */}
              <p className="text-xs text-[#71717a] leading-relaxed mb-4">
                {rec.description}
              </p>

              {/* Resources */}
              {rec.resources && rec.resources.length > 0 && (
                <div className="space-y-1.5">
                  <p className="text-[11px] font-medium text-[#52525b]
                    uppercase tracking-wider mb-2"
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
                        bg-[#161616] border border-[#1f1f1f] rounded-md
                        hover:border-[#2a2a2a] transition-colors duration-150
                        group"
                    >
                      <span className="text-xs text-[#a1a1aa]
                        group-hover:text-[#f5f5f5] transition-colors flex-1"
                      >
                        {resource.title}
                      </span>
                      <ExternalLink
                        size={11}
                        strokeWidth={1.5}
                        className="text-[#3f3f46] group-hover:text-[#52525b]
                          flex-shrink-0"
                      />
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
