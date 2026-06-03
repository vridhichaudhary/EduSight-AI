/**
 * EduSight AI — Manual Marks Entry Form
 * Dynamic spreadsheet-style form for entering marks without a file.
 */

import { useState } from 'react'
import { Plus, Trash2, Send, AlertCircle, CheckCircle } from 'lucide-react'
import Button from '../ui/Button'
import Badge from '../ui/Badge'

const EXAM_TYPES = [
  { value: 'quiz',       label: 'Quiz' },
  { value: 'midterm',    label: 'Midterm' },
  { value: 'final',      label: 'Final Exam' },
  { value: 'assignment', label: 'Assignment' },
  { value: 'practical',  label: 'Practical' },
  { value: 'project',    label: 'Project' },
]

const EMPTY_ROW = {
  subject:        '',
  marks_obtained: '',
  max_marks:      '100',
  exam_type:      'midterm',
  exam_date:      new Date().toISOString().split('T')[0],
  topic:          '',
}

function getPercentage(row) {
  const mo = parseFloat(row.marks_obtained)
  const mm = parseFloat(row.max_marks)
  if (isNaN(mo) || isNaN(mm) || mm === 0) return null
  return ((mo / mm) * 100).toFixed(1)
}

function pctColor(pct) {
  if (!pct) return 'text-[#52525b]'
  const n = parseFloat(pct)
  if (n >= 80) return 'text-[#22c55e]'
  if (n >= 60) return 'text-[#f59e0b]'
  return 'text-[#ef4444]'
}

const cellBase = `
  h-7 w-full bg-[#0a0a0a] border rounded px-2
  text-xs text-[#f5f5f5] placeholder:text-[#3f3f46]
  focus:outline-none focus:border-[#4f46e5]
  transition-colors duration-150
`

export default function ManualEntryForm({ onSubmit, loading = false }) {
  const [studentName, setStudentName] = useState('')
  const [gradeLevel,  setGradeLevel]  = useState('10')
  const [rows,        setRows]        = useState([{ ...EMPTY_ROW }])
  const [errors,      setErrors]      = useState({})

  const addRow    = () => setRows((p) => [...p, { ...EMPTY_ROW }])
  const removeRow = (i) => { if (rows.length > 1) setRows((p) => p.filter((_, idx) => idx !== i)) }

  const updateRow = (idx, field, val) => {
    setRows((p) => p.map((r, i) => i === idx ? { ...r, [field]: val } : r))
    const key = `${idx}_${field}`
    if (errors[key]) setErrors((p) => { const n = { ...p }; delete n[key]; return n })
  }

  const validate = () => {
    const e = {}
    if (!studentName.trim()) e['student_name'] = 'Student name is required'
    rows.forEach((row, i) => {
      if (!row.subject.trim())                             e[`${i}_subject`]        = 'Required'
      const mo = parseFloat(row.marks_obtained)
      const mm = parseFloat(row.max_marks)
      if (isNaN(mo) || mo < 0)                            e[`${i}_marks_obtained`] = 'Invalid marks'
      if (isNaN(mm) || mm <= 0)                           e[`${i}_max_marks`]      = 'Invalid total'
      if (!isNaN(mo) && !isNaN(mm) && mo > mm)            e[`${i}_marks_obtained`] = 'Exceeds total'
      if (!row.exam_date)                                  e[`${i}_exam_date`]      = 'Required'
    })
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = () => {
    if (!validate()) return
    onSubmit({
      student_name: studentName.trim(),
      grade_level:  parseInt(gradeLevel) || 10,
      entries: rows.map((r) => ({
        subject:        r.subject.trim(),
        marks_obtained: parseFloat(r.marks_obtained),
        max_marks:      parseFloat(r.max_marks),
        exam_type:      r.exam_type,
        exam_date:      r.exam_date,
        topic:          r.topic.trim(),
      })),
    })
  }

  const errCount = Object.keys(errors).length
  const validRows = rows.filter((r) => r.subject && r.marks_obtained).length

  return (
    <div className="space-y-5">

      {/* ── Student Info ── */}
      <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-5">
        <p className="text-[11px] font-medium text-[#52525b] uppercase tracking-widest mb-4">
          Student Information
        </p>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-[#a1a1aa]">
              Student Name <span className="text-[#ef4444]">*</span>
            </label>
            <input
              type="text"
              placeholder="e.g. John Doe"
              value={studentName}
              onChange={(e) => { setStudentName(e.target.value); if (errors.student_name) setErrors((p) => { const n = {...p}; delete n.student_name; return n }) }}
              className={`h-8 bg-[#0a0a0a] border rounded-md px-3 text-sm text-[#f5f5f5] placeholder:text-[#3f3f46] focus:outline-none focus:border-[#4f46e5] transition-colors ${errors.student_name ? 'border-[#ef4444]' : 'border-[#1f1f1f]'}`}
            />
            {errors.student_name && <p className="text-[11px] text-[#ef4444]">{errors.student_name}</p>}
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-[#a1a1aa]">Grade Level</label>
            <select
              value={gradeLevel}
              onChange={(e) => setGradeLevel(e.target.value)}
              className="h-8 bg-[#0a0a0a] border border-[#1f1f1f] rounded-md px-3 text-sm text-[#f5f5f5] focus:outline-none focus:border-[#4f46e5] transition-colors"
            >
              {Array.from({ length: 12 }, (_, i) => i + 1).map((g) => (
                <option key={g} value={g}>Grade {g}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* ── Marks Table ── */}
      <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg overflow-hidden">
        {/* Header */}
        <div
          className="grid gap-2 px-4 py-2.5 border-b border-[#1f1f1f] bg-[#0d0d0d]"
          style={{ gridTemplateColumns: '2fr 80px 80px 120px 130px 1.4fr 44px 32px' }}
        >
          {['Subject', 'Marks', 'Total', 'Exam Type', 'Date', 'Topic (opt.)', '%', ''].map((h) => (
            <span key={h} className="text-[10px] font-semibold text-[#52525b] uppercase tracking-wider">{h}</span>
          ))}
        </div>

        {/* Rows */}
        <div className="divide-y divide-[#161616]">
          {rows.map((row, idx) => {
            const pct = getPercentage(row)
            return (
              <div
                key={idx}
                className="grid gap-2 px-4 py-2 hover:bg-[#0d0d0d] transition-colors items-center group"
                style={{ gridTemplateColumns: '2fr 80px 80px 120px 130px 1.4fr 44px 32px' }}
              >
                {/* Subject */}
                <input type="text" placeholder="Mathematics" value={row.subject}
                  onChange={(e) => updateRow(idx, 'subject', e.target.value)}
                  className={`${cellBase} ${errors[`${idx}_subject`] ? 'border-[#ef4444]' : 'border-[#1f1f1f]'}`}
                />
                {/* Marks Obtained */}
                <input type="number" placeholder="85" min="0" value={row.marks_obtained}
                  onChange={(e) => updateRow(idx, 'marks_obtained', e.target.value)}
                  className={`${cellBase} ${errors[`${idx}_marks_obtained`] ? 'border-[#ef4444]' : 'border-[#1f1f1f]'}`}
                />
                {/* Max Marks */}
                <input type="number" placeholder="100" min="1" value={row.max_marks}
                  onChange={(e) => updateRow(idx, 'max_marks', e.target.value)}
                  className={`${cellBase} ${errors[`${idx}_max_marks`] ? 'border-[#ef4444]' : 'border-[#1f1f1f]'}`}
                />
                {/* Exam Type */}
                <select value={row.exam_type} onChange={(e) => updateRow(idx, 'exam_type', e.target.value)}
                  className="h-7 bg-[#0a0a0a] border border-[#1f1f1f] rounded px-2 text-xs text-[#f5f5f5] focus:outline-none focus:border-[#4f46e5] transition-colors"
                >
                  {EXAM_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                </select>
                {/* Date */}
                <input type="date" value={row.exam_date}
                  onChange={(e) => updateRow(idx, 'exam_date', e.target.value)}
                  className={`${cellBase} ${errors[`${idx}_exam_date`] ? 'border-[#ef4444]' : 'border-[#1f1f1f]'}`}
                />
                {/* Topic */}
                <input type="text" placeholder="Optional topic..." value={row.topic}
                  onChange={(e) => updateRow(idx, 'topic', e.target.value)}
                  className={`${cellBase} border-[#1f1f1f]`}
                />
                {/* % Preview */}
                <span className={`text-xs font-semibold tabular-nums ${pctColor(pct)}`}>
                  {pct ? `${pct}%` : '—'}
                </span>
                {/* Delete */}
                <button onClick={() => removeRow(idx)} disabled={rows.length === 1}
                  className="w-6 h-6 flex items-center justify-center text-[#3f3f46] hover:text-[#ef4444] transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-20 disabled:cursor-not-allowed"
                >
                  <Trash2 size={12} strokeWidth={1.5} />
                </button>
              </div>
            )
          })}
        </div>

        {/* Add Row */}
        <div className="px-4 py-3 border-t border-[#161616]">
          <Button variant="ghost" size="sm" icon={Plus} onClick={addRow}>
            Add Row
          </Button>
        </div>
      </div>

      {/* ── Error Summary ── */}
      {errCount > 0 && (
        <div className="flex items-start gap-2.5 bg-[rgba(239,68,68,0.05)] border border-[rgba(239,68,68,0.15)] rounded-lg px-4 py-3">
          <AlertCircle size={14} strokeWidth={1.5} className="text-[#ef4444] flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-xs font-medium text-[#ef4444] mb-1">Fix {errCount} error{errCount > 1 ? 's' : ''} before submitting</p>
            <ul className="space-y-0.5">
              {Object.values(errors).slice(0, 3).map((v, i) => (
                <li key={i} className="text-[11px] text-[#a1a1aa]">{v}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* ── Submit Row ── */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <Badge variant="default">{rows.length} row{rows.length !== 1 ? 's' : ''}</Badge>
          {validRows > 0 && <Badge variant="accent" dot>{validRows} ready</Badge>}
          {studentName && (
            <span className="text-xs text-[#52525b]">for <span className="text-[#a1a1aa]">{studentName}</span></span>
          )}
        </div>
        <Button
          variant="primary"
          size="md"
          icon={Send}
          loading={loading}
          onClick={handleSubmit}
          disabled={!studentName.trim()}
        >
          Submit Marks
        </Button>
      </div>
    </div>
  )
}
