import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Target } from 'lucide-react'
import { dashboardAPI } from '../../services/api'
import PageHeader from '../../components/layout/PageHeader'
import Badge from '../../components/ui/Badge'
import { Card, CardBody } from '../../components/ui/Card'
import WeakAreaChart from '../../components/charts/WeakAreaChart'
import { SkeletonCard } from '../../components/ui/Skeleton'
import EmptyState from '../../components/ui/EmptyState'

export default function WeakAreasPage() {
  const { studentId } = useParams()

  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', studentId],
    queryFn: () => dashboardAPI.get(studentId),
    enabled: !!studentId,
  })

  const weakAreas = data?.data?.data?.weak_areas     || []
  const radarData = data?.data?.data?.radar_chart    || []

  return (
    <div className="space-y-6">
      <PageHeader
        badge="Analysis"
        title="Weak Areas"
        description="Subjects identified as needing improvement, ranked by priority."
      />

      <WeakAreaChart
        data={radarData.map((d) => ({
          subject: d.subject,
          score: d.score,
        }))}
        loading={isLoading}
      />

      {/* Weak Area Detail Cards */}
      {weakAreas.length > 0 && (
        <div className="space-y-3">
          <p className="text-[11px] font-medium text-[#52525b]
            uppercase tracking-widest"
          >
            Detailed Breakdown
          </p>
          {weakAreas.map((area, i) => (
            <div
              key={i}
              className="bg-[#111111] border border-[#1f1f1f]
                rounded-lg px-5 py-4
                flex items-center justify-between
                hover:border-[#2a2a2a] transition-colors duration-150"
            >
              <div className="flex items-center gap-4">
                <div
                  className="w-1 h-8 rounded-full flex-shrink-0"
                  style={{ backgroundColor: area.color_code || '#ef4444' }}
                />
                <div>
                  <p className="text-xs font-medium text-[#f5f5f5]">
                    {area.subject_name}
                  </p>
                  <p className="text-[11px] text-[#52525b] mt-0.5">
                    {area.reason || 'Below expected performance level'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4 flex-shrink-0">
                <div className="text-right">
                  <p className="text-sm font-semibold text-[#f5f5f5]
                    tracking-tight"
                  >
                    {Number(area.current_percentage).toFixed(1)}%
                  </p>
                  <p className="text-[11px] text-[#52525b]">current</p>
                </div>
                <Badge variant={
                  area.severity === 'critical' ? 'danger' :
                  area.severity === 'severe'   ? 'danger' :
                  area.severity === 'moderate' ? 'warning' : 'default'
                } dot>
                  {area.severity}
                </Badge>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
