/**
 * EduSight AI — Students List Page
 * Table-style list. Clean. Fast.
 */

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Users, Search, ArrowRight, GraduationCap } from 'lucide-react'
import { studentAPI } from '../services/api'
import PageHeader from '../components/layout/PageHeader'
import Button from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import Badge from '../components/ui/Badge'
import { SkeletonTable } from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'
import DownloadReportButton from '../components/ui/DownloadReportButton'

function getGradeBadge(avg) {
  if (avg >= 90) return { variant: 'success', label: 'Excellent' }
  if (avg >= 75) return { variant: 'info',    label: 'Good' }
  if (avg >= 60) return { variant: 'warning', label: 'Average' }
  return { variant: 'danger', label: 'Needs Help' }
}

export default function StudentsPage() {
  const [search, setSearch] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['students', search],
    queryFn: () => studentAPI.list({ search }),
  })

  const students = data?.data?.data || []

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <PageHeader
        badge="Students"
        title="All Students"
        description="Select a student to view performance analysis."
        actions={
          <Link to="/upload">
            <Button variant="primary" size="sm">
              Upload CSV
            </Button>
          </Link>
        }
      />

      {/* Search */}
      <div className="mb-4 max-w-xs">
        <Input
          icon={Search}
          placeholder="Search students..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Table */}
      <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg overflow-hidden">
        {/* Table Header */}
        <div className="grid grid-cols-12 px-4 py-2.5 border-b border-[#1f1f1f]">
          <span className="col-span-4 text-[11px] font-medium text-[#52525b] uppercase tracking-wider">Student</span>
          <span className="col-span-2 text-[11px] font-medium text-[#52525b] uppercase tracking-wider">Grade</span>
          <span className="col-span-2 text-[11px] font-medium text-[#52525b] uppercase tracking-wider">Average</span>
          <span className="col-span-2 text-[11px] font-medium text-[#52525b] uppercase tracking-wider">Status</span>
          <span className="col-span-2" />
        </div>

        {/* Rows */}
        {isLoading ? (
          <SkeletonTable rows={6} />
        ) : students.length === 0 ? (
          <EmptyState
            icon={Users}
            title="No students found"
            description="Upload a CSV to add student records."
          />
        ) : (
          students.map((student, i) => {
            const { variant, label } = getGradeBadge(
              student.average_percentage || 0
            )
            return (
              <div
                key={student.id}
                className={`
                  grid grid-cols-12 px-4 py-3
                  items-center
                  hover:bg-[#161616] transition-colors duration-100
                  ${i !== students.length - 1 ? 'border-b border-[#1f1f1f]' : ''}
                `}
              >
                <div className="col-span-4 flex items-center gap-3">
                  <div className="w-7 h-7 rounded-full bg-[#161616]
                    border border-[#1f1f1f] flex items-center justify-center
                    flex-shrink-0"
                  >
                    <span className="text-[11px] font-medium text-[#52525b]">
                      {student.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-[#f5f5f5]">
                      {student.name}
                    </p>
                    <p className="text-[11px] text-[#52525b]">
                      {student.email}
                    </p>
                  </div>
                </div>
                <div className="col-span-2">
                  <span className="text-xs text-[#a1a1aa]">
                    Grade {student.grade_level}
                  </span>
                </div>
                <div className="col-span-2">
                  <span className="text-xs font-medium text-[#f5f5f5]">
                    {student.average_percentage?.toFixed(1) || '0.0'}%
                  </span>
                </div>
                <div className="col-span-2">
                  <Badge variant={variant} dot>{label}</Badge>
                </div>
                <div className="col-span-2 flex justify-end gap-2">
                  <DownloadReportButton
                    studentId={student.id}
                    studentName={student.name}
                    size="sm"
                    variant="ghost"
                    label="PDF"
                  />
                  <Link to={`/dashboard/${student.id}/overview`}>
                    <Button variant="ghost" size="sm" iconRight={ArrowRight}>
                      View
                    </Button>
                  </Link>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
