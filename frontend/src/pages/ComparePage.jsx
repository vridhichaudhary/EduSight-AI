/**
 * EduSight AI — Multi-Student Comparison Page
 * Full comparison dashboard with 1/3 selector + 2/3 charts layout.
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Users } from 'lucide-react'
import { comparisonAPI } from '../services/api'
import PageHeader from '../components/layout/PageHeader'
import StudentSelector from '../components/comparison/StudentSelector'
import ComparisonRadar from '../components/comparison/ComparisonRadar'
import ComparisonTrendLine from '../components/comparison/ComparisonTrendLine'
import ComparisonTable from '../components/comparison/ComparisonTable'
import ComparisonSummary from '../components/comparison/ComparisonSummary'
import EmptyState from '../components/ui/EmptyState'
import { SkeletonCard } from '../components/ui/Skeleton'

export default function ComparePage() {
  const [selectedIds, setSelectedIds] = useState([])

  const { data, isLoading } = useQuery({
    queryKey: ['comparison', selectedIds],
    queryFn:  () => comparisonAPI.compare(selectedIds),
    enabled:  selectedIds.length >= 2,
  })

  const comparison = data?.data?.data
  const students   = comparison?.students   || []
  const radarData  = comparison?.radar_data || []
  const trendData  = comparison?.trend_data || []
  const subjects   = comparison?.subjects   || []

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <PageHeader
        badge="Analytics"
        title="Student Comparison"
        description="Compare performance across multiple students side by side."
      />

      <div className="grid grid-cols-3 gap-6 mt-8">
        {/* ── Left: Selector (1/3) ── */}
        <div className="col-span-1 space-y-4">
          <StudentSelector
            selectedIds={selectedIds}
            onChange={setSelectedIds}
            maxStudents={4}
          />

          {selectedIds.length < 2 && (
            <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg px-4 py-4">
              <p className="text-xs text-[#52525b] leading-relaxed">
                Select at least <span className="text-[#a1a1aa] font-medium">2 students</span> from
                the list above to see comparison charts and insights.
              </p>
            </div>
          )}
        </div>

        {/* ── Right: Charts (2/3) ── */}
        <div className="col-span-2 space-y-6">
          {selectedIds.length < 2 ? (
            <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg">
              <EmptyState
                icon={Users}
                title="Select students to compare"
                description="Choose 2–4 students on the left to see their performance compared side by side."
              />
            </div>
          ) : isLoading ? (
            <div className="space-y-4">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : (
            <>
              {/* Summary cards */}
              <ComparisonSummary students={students} />

              {/* Radar chart */}
              <ComparisonRadar data={radarData} students={students} />

              {/* Trend lines */}
              <ComparisonTrendLine data={trendData} students={students} />

              {/* Subject table */}
              <ComparisonTable subjects={subjects} students={students} />
            </>
          )}
        </div>
      </div>
    </div>
  )
}
