/**
 * EduSight AI — Student Selector for Comparison
 * Select up to 4 students to compare.
 * Each gets a distinct color indicator.
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, X, Plus } from 'lucide-react'
import { studentAPI } from '../../services/api'
import Button from '../ui/Button'

const COLORS = ['#4f46e5', '#22c55e', '#f59e0b', '#ef4444']

export default function StudentSelector({
  selectedIds,
  onChange,
  maxStudents = 4,
}) {
  const [search, setSearch] = useState('')

  const { data } = useQuery({
    queryKey: ['students', search],
    queryFn:  () => studentAPI.list({ search }),
  })

  const students      = data?.data?.data || []
  const selectedCount = selectedIds.length
  const canAddMore    = selectedCount < maxStudents

  const toggleStudent = (id) => {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((s) => s !== id))
    } else if (canAddMore) {
      onChange([...selectedIds, id])
    }
  }

  return (
    <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-[#1f1f1f] flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-[#f5f5f5]">Select Students</h3>
          <p className="text-xs text-[#52525b] mt-0.5">
            Choose up to {maxStudents} students to compare
          </p>
        </div>
        <div className="flex items-center gap-1.5">
          {selectedIds.map((id, i) => (
            <div
              key={id}
              className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white"
              style={{ backgroundColor: COLORS[i % COLORS.length] }}
            >
              {i + 1}
            </div>
          ))}
        </div>
      </div>

      {/* Search */}
      <div className="px-4 py-3 border-b border-[#1f1f1f]">
        <div className="relative">
          <Search
            size={13}
            strokeWidth={1.5}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-[#52525b]"
          />
          <input
            type="text"
            placeholder="Search students..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full h-8 bg-[#0a0a0a] border border-[#1f1f1f] rounded-md pl-8 pr-3 text-xs text-[#f5f5f5] placeholder:text-[#3f3f46] focus:outline-none focus:border-[#4f46e5] transition-colors duration-150"
          />
        </div>
      </div>

      {/* Student List */}
      <div className="max-h-64 overflow-y-auto">
        {students.length === 0 ? (
          <div className="px-5 py-6 text-center">
            <p className="text-xs text-[#52525b]">No students found</p>
          </div>
        ) : (
          students.map((student) => {
            const selectedIndex = selectedIds.indexOf(student.id)
            const isSelected    = selectedIndex !== -1
            const color         = isSelected
              ? COLORS[selectedIndex % COLORS.length]
              : null

            return (
              <div
                key={student.id}
                onClick={() => toggleStudent(student.id)}
                className={`
                  flex items-center justify-between px-4 py-3 cursor-pointer
                  border-b border-[#1f1f1f] last:border-b-0
                  transition-colors duration-100
                  ${isSelected
                    ? 'bg-[#161620]'
                    : canAddMore
                    ? 'hover:bg-[#161616]'
                    : 'opacity-40 cursor-not-allowed'
                  }
                `}
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-2 h-2 rounded-full flex-shrink-0 transition-colors duration-200"
                    style={{ backgroundColor: color || '#3f3f46' }}
                  />
                  <div>
                    <p className="text-xs font-medium text-[#f5f5f5]">
                      {student.name}
                    </p>
                    <p className="text-[11px] text-[#52525b]">
                      Grade {student.grade_level}
                      {student.average_percentage
                        ? ` · ${student.average_percentage.toFixed(1)}% avg`
                        : ''}
                    </p>
                  </div>
                </div>

                {isSelected ? (
                  <div className="flex items-center gap-1.5">
                    <span className="text-[11px] font-medium" style={{ color }}>
                      Student {selectedIndex + 1}
                    </span>
                    <div
                      className="w-4 h-4 rounded-full flex items-center justify-center"
                      style={{ backgroundColor: color }}
                    >
                      <X size={9} className="text-white" />
                    </div>
                  </div>
                ) : (
                  canAddMore && (
                    <Plus size={13} strokeWidth={1.5} className="text-[#52525b]" />
                  )
                )}
              </div>
            )
          })
        )}
      </div>

      {/* Footer */}
      {selectedCount > 0 && (
        <div className="px-4 py-3 border-t border-[#1f1f1f] flex items-center justify-between">
          <span className="text-xs text-[#52525b]">
            {selectedCount} student{selectedCount > 1 ? 's' : ''} selected
          </span>
          <Button variant="ghost" size="sm" onClick={() => onChange([])}>
            Clear all
          </Button>
        </div>
      )}
    </div>
  )
}
