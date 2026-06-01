/**
 * EduSight AI — Dashboard Overview
 * Full analytics view for a single student.
 */

import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart2,
  Target,
  TrendingUp,
  BookOpen,
  RefreshCw,
  ArrowRight,
} from 'lucide-react'
import { dashboardAPI, analysisAPI } from '../../services/api'
import useStore from '../../store/useStore'
import PageHeader from '../../components/layout/PageHeader'
import Button from '../../components/ui/Button'
import StatCard from '../../components/ui/StatCard'
import Badge from '../../components/ui/Badge'
import Divider from '../../components/ui/Divider'
import SubjectRadarChart from '../../components/charts/SubjectRadarChart'
import GradeTrendChart from '../../components/charts/GradeTrendChart'
import WeakAreaChart from '../../components/charts/WeakAreaChart'
import { SkeletonCard } from '../../components/ui/Skeleton'

// ─── Predictions Table ───
function PredictionsTable({ predictions = [] }) {
  if (predictions.length === 0) return null
  return (
    <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg overflow-hidden">
      <div className="px-5 py-4 border-b border-[#1f1f1f] flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-[#f5f5f5]">
            Predicted Scores
          </h3>
          <p className="text-xs text-[#52525b] mt-0.5">
            Next exam forecast by ML model
          </p>
        </div>
        <Badge variant="accent" dot>Beta</Badge>
      </div>
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-[#1f1f1f]">
            {['Subject', 'Predicted', 'Confidence', 'Risk'].map((h) => (
              <th
                key={h}
                className="text-left px-5 py-2.5 text-[11px]
                  font-medium text-[#52525b] uppercase tracking-wider"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {predictions.slice(0, 6).map((pred, i) => {
            const isRisk = pred.predicted_marks < 60
            return (
              <tr
                key={i}
                className={`
                  hover:bg-[#161616] transition-colors duration-100
                  ${i !== predictions.length - 1 ? 'border-b border-[#1f1f1f]' : ''}
                `}
              >
                <td className="px-5 py-3 text-[#a1a1aa] font-medium">
                  {pred.subject_name}
                </td>
                <td className="px-5 py-3 text-[#f5f5f5] font-semibold
                  tracking-tight"
                >
                  {Number(pred.predicted_marks).toFixed(1)}%
                </td>
                <td className="px-5 py-3 text-[#52525b]">
                  {Math.round(pred.confidence_score * 100)}%
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
    </div>
  )
}

// ─── Recommendations Preview ───
function RecommendationsPreview({ recommendations = [], studentId }) {
  if (recommendations.length === 0) return null
  return (
    <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg overflow-hidden">
      <div className="px-5 py-4 border-b border-[#1f1f1f]
        flex items-center justify-between"
      >
        <div>
          <h3 className="text-sm font-medium text-[#f5f5f5]">
            Study Recommendations
          </h3>
          <p className="text-xs text-[#52525b] mt-0.5">
            AI-generated based on weak areas
          </p>
        </div>
        <Link to={`/dashboard/${studentId}/recommendations`}>
          <Button variant="ghost" size="sm" iconRight={ArrowRight}>
            View all
          </Button>
        </Link>
      </div>
      <div className="divide-y divide-[#1f1f1f]">
        {recommendations.slice(0, 3).map((rec, i) => (
          <div
            key={i}
            className="px-5 py-4 flex items-start gap-3
              hover:bg-[#161616] transition-colors duration-100"
          >
            <div className="w-7 h-7 rounded-md bg-[#161616]
              border border-[#1f1f1f] flex items-center justify-center
              flex-shrink-0 mt-0.5"
            >
              <BookOpen size={13} strokeWidth={1.5} className="text-[#4f46e5]" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-[#f5f5f5] mb-0.5 truncate">
                {rec.title}
              </p>
              <p className="text-[11px] text-[#52525b] line-clamp-1">
                {rec.description}
              </p>
            </div>
            <Badge variant="default" className="flex-shrink-0 ml-2">
              {rec.subject_name}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  )
}

// ─── Main Component ───
export default function OverviewPage() {
  const { studentId } = useParams()
  const { addNotification } = useStore()
  const [triggering, setTriggering] = useState(false)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['dashboard', studentId],
    queryFn: () => dashboardAPI.get(studentId),
    enabled: !!studentId,
  })

  const dashboard  = data?.data?.data
  const student    = dashboard?.student
  const summary    = dashboard?.summary
  const radarData  = dashboard?.radar_chart    || []
  const trendData  = dashboard?.trend_line     || []
  const weakAreas  = dashboard?.weak_areas     || []
  const predictions = dashboard?.predictions   || []
  const recommendations = dashboard?.recommendations || []

  // ─── Trigger Analysis ───
  const handleTriggerAnalysis = async () => {
    setTriggering(true)
    try {
      await analysisAPI.trigger(studentId)
      addNotification({
        type: 'success',
        title: 'Analysis queued',
        message: 'AI agents are processing your data.',
      })
      setTimeout(refetch, 3000)
    } catch {
      addNotification({
        type: 'error',
        title: 'Analysis failed',
        message: 'Please try again.',
      })
    } finally {
      setTriggering(false)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="h-8 w-48 bg-[#111111] border border-[#1f1f1f]
          rounded-md animate-pulse"
        />
        <div className="grid grid-cols-4 gap-4">
          {[1,2,3,4].map((i) => <SkeletonCard key={i} />)}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">

      {/* ── Page Header ── */}
      <PageHeader
        badge="Overview"
        title={student?.name || 'Student Dashboard'}
        description={`Grade ${student?.grade_level} · ${student?.school || 'EduSight AI'}`}
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              icon={RefreshCw}
              onClick={refetch}
            >
              Refresh
            </Button>
            <Button
              variant="secondary"
              size="sm"
              loading={triggering}
              onClick={handleTriggerAnalysis}
            >
              Run Analysis
            </Button>
          </div>
        }
      />

      {/* ── Stat Cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Average Score"
          value={`${summary?.average_percentage?.toFixed(1) || 0}%`}
          change={2.4}
          changeLabel="vs last month"
          icon={BarChart2}
        />
        <StatCard
          label="Total Exams"
          value={summary?.total_exams || 0}
          icon={BookOpen}
        />
        <StatCard
          label="Highest Score"
          value={`${summary?.highest_score?.toFixed(1) || 0}%`}
          change={1.2}
          changeLabel="vs last exam"
          icon={TrendingUp}
        />
        <StatCard
          label="Weak Areas"
          value={summary?.weak_areas_count || 0}
          change={summary?.weak_areas_count > 2 ? -1 : 0}
          changeLabel="identified"
          icon={Target}
        />
      </div>

      {/* ── Charts Row ── */}
      <div>
        <p className="text-[11px] font-medium text-[#52525b]
          uppercase tracking-widest mb-4"
        >
          Performance Analysis
        </p>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SubjectRadarChart data={radarData} loading={isLoading} />
          <GradeTrendChart   data={trendData} loading={isLoading} />
        </div>
      </div>

      {/* ── Weak Area Chart ── */}
      <div>
        <p className="text-[11px] font-medium text-[#52525b]
          uppercase tracking-widest mb-4"
        >
          Subject Breakdown
        </p>
        <WeakAreaChart
          data={radarData.map((d) => ({
            subject: d.subject,
            score: d.score,
          }))}
          loading={isLoading}
        />
      </div>

      <Divider />

      {/* ── Predictions + Recommendations ── */}
      <div>
        <p className="text-[11px] font-medium text-[#52525b]
          uppercase tracking-widest mb-4"
        >
          AI Insights
        </p>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <PredictionsTable
            predictions={predictions}
          />
          <RecommendationsPreview
            recommendations={recommendations}
            studentId={studentId}
          />
        </div>
      </div>
    </div>
  )
}
