/**
 * EduSight AI — Upload Page
 * CSV drag-and-drop, validation, preview, upload.
 */

import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import Papa from 'papaparse'
import {
  Upload,
  FileText,
  X,
  CheckCircle,
  AlertCircle,
  Download,
  ArrowRight,
  ChevronRight,
} from 'lucide-react'
import { marksAPI } from '../services/api'
import useStore from '../store/useStore'
import PageHeader from '../components/layout/PageHeader'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Divider from '../components/ui/Divider'

// ─── CSV Template Download ───
function downloadTemplate() {
  const headers = [
    'student_name',
    'subject',
    'marks_obtained',
    'max_marks',
    'exam_type',
    'exam_date',
  ]
  const rows = [
    ['John Doe', 'Mathematics', '85', '100', 'midterm', '2024-01-15'],
    ['John Doe', 'Science',     '78', '100', 'midterm', '2024-01-16'],
    ['John Doe', 'English',     '92', '100', 'midterm', '2024-01-17'],
    ['Jane Smith','Mathematics','72', '100', 'midterm', '2024-01-15'],
    ['Jane Smith','Science',    '88', '100', 'midterm', '2024-01-16'],
  ]
  const csv = [headers, ...rows].map((r) => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = 'edusight_template.csv'
  a.click()
  URL.revokeObjectURL(url)
}

// ─── Validation ───
const REQUIRED_COLS = [
  'student_name',
  'subject',
  'marks_obtained',
  'max_marks',
  'exam_type',
  'exam_date',
]

const COLUMN_ALIASES = {
  'name': 'student_name',
  'student': 'student_name',
  'studentname': 'student_name',
  'course': 'subject',
  'class': 'subject',
  'marks': 'marks_obtained',
  'score': 'marks_obtained',
  'obtained': 'marks_obtained',
  'max': 'max_marks',
  'total': 'max_marks',
  'total_marks': 'max_marks',
  'type': 'exam_type',
  'exam': 'exam_type',
  'date': 'exam_date',
  'time': 'exam_date',
}

function normalizeHeader(header) {
  const clean = header.toLowerCase().trim().replace(/ /g, '_')
  return COLUMN_ALIASES[clean] || clean
}

function validateCSV(data, fields) {
  const normalized = fields.map(normalizeHeader)
  const missing = REQUIRED_COLS.filter((c) => !normalized.includes(c))
  const errors  = []

  if (missing.length > 0) {
    errors.push(`Missing columns: ${missing.join(', ')}`)
    return errors
  }

  data.slice(0, 50).forEach((row, i) => {
    const mo = parseFloat(row.marks_obtained)
    const mm = parseFloat(row.max_marks)
    if (isNaN(mo) || isNaN(mm)) {
      errors.push(`Row ${i + 2}: marks_obtained and max_marks must be numbers`)
    }
    if (mo > mm) {
      errors.push(`Row ${i + 2}: marks_obtained cannot exceed max_marks`)
    }
    if (!row.student_name?.trim()) {
      errors.push(`Row ${i + 2}: student_name is empty`)
    }
  })
  return errors
}

// ─── Step Indicator ───
function StepIndicator({ steps, current }) {
  return (
    <div className="flex items-center gap-0 mb-10">
      {steps.map((step, i) => {
        const done    = i < current
        const active  = i === current
        return (
          <div key={step} className="flex items-center">
            <div className="flex items-center gap-2">
              <div
                className={`
                  w-5 h-5 rounded-full flex items-center justify-center
                  text-[10px] font-semibold transition-all duration-200
                  ${done   ? 'bg-[#22c55e] text-white' :
                    active ? 'bg-[#4f46e5] text-white' :
                             'bg-[#161616] border border-[#1f1f1f] text-[#52525b]'}
                `}
              >
                {done ? <CheckCircle size={11} /> : i + 1}
              </div>
              <span
                className={`text-xs font-medium transition-colors duration-200
                  ${active ? 'text-[#f5f5f5]' :
                    done   ? 'text-[#52525b]'  : 'text-[#3f3f46]'}
                `}
              >
                {step}
              </span>
            </div>
            {i < steps.length - 1 && (
              <ChevronRight
                size={14}
                strokeWidth={1.5}
                className="text-[#2a2a2a] mx-3"
              />
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── Upload Progress Bar ───
function ProgressBar({ progress, label }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-xs text-[#a1a1aa]">{label}</span>
        <span className="text-xs font-medium text-[#f5f5f5]">
          {progress}%
        </span>
      </div>
      <div className="h-1 bg-[#1f1f1f] rounded-full overflow-hidden">
        <div
          className="h-full bg-[#4f46e5] rounded-full transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}

// ─── Main Component ───
export default function UploadPage() {
  const navigate = useNavigate()
  const { addNotification } = useStore()

  const [step,             setStep]             = useState(0)
  const [file,             setFile]             = useState(null)
  const [preview,          setPreview]          = useState([])
  const [fields,           setFields]           = useState([])
  const [validationErrors, setValidationErrors] = useState([])
  const [uploading,        setUploading]        = useState(false)
  const [progress,         setProgress]         = useState(0)
  const [progressLabel,    setProgressLabel]    = useState('')
  const [result,           setResult]           = useState(null)

  const steps = ['Select File', 'Preview & Validate', 'Upload']

  // ─── Dropzone ───
  const onDrop = useCallback((accepted, rejected) => {
    if (rejected.length > 0) {
      addNotification({
        type: 'error',
        title: 'Invalid file',
        message: 'Only CSV files are accepted.',
      })
      return
    }

    const f = accepted[0]
    setFile(f)

    Papa.parse(f, {
      header: true,
      skipEmptyLines: true,
      transformHeader: normalizeHeader,
      complete: (results) => {
        const errors = validateCSV(results.data, results.meta.fields)
        setFields(results.meta.fields)
        setPreview(results.data.slice(0, 8))
        setValidationErrors(errors)
        setStep(1)
      },
    })
  }, [addNotification])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'text/csv': ['.csv'] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  })

  // ─── Upload ───
  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setStep(2)

    const fakeSteps = [
      [20,  'Uploading file...'],
      [50,  'Validating data...'],
      [75,  'Creating records...'],
      [90,  'Finalizing...'],
    ]

    for (const [p, label] of fakeSteps) {
      await new Promise((r) => setTimeout(r, 400))
      setProgress(p)
      setProgressLabel(label)
    }

    try {
      const res = await marksAPI.uploadCSV(file)
      setProgress(100)
      setProgressLabel('Complete')
      setResult(res.data?.data)

      addNotification({
        type: 'success',
        title: 'Upload successful',
        message: `${res.data?.data?.records_created} records created.`,
      })

      await new Promise((r) => setTimeout(r, 600))
      navigate('/students')
    } catch (err) {
      setUploading(false)
      setStep(1)
      setProgress(0)
      addNotification({
        type: 'error',
        title: 'Upload failed',
        message: err.message || 'Please check your CSV and try again.',
      })
    }
  }

  // ─── Reset ───
  const handleReset = () => {
    setFile(null)
    setPreview([])
    setFields([])
    setValidationErrors([])
    setStep(0)
    setProgress(0)
    setResult(null)
    setUploading(false)
  }

  const hasErrors = validationErrors.length > 0

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <PageHeader
        badge="Data"
        title="Upload Marks CSV"
        description="Upload student marks data to begin performance analysis."
        actions={
          <Button
            variant="ghost"
            size="sm"
            icon={Download}
            onClick={downloadTemplate}
          >
            Download Template
          </Button>
        }
      />

      <StepIndicator steps={steps} current={step} />

      {/* ── STEP 0: Drop Zone ── */}
      {step === 0 && (
        <div
          {...getRootProps()}
          className={`
            border border-dashed rounded-lg
            flex flex-col items-center justify-center
            h-52 cursor-pointer
            transition-all duration-150
            ${isDragActive
              ? 'border-[#4f46e5] bg-[rgba(79,70,229,0.04)]'
              : 'border-[#2a2a2a] hover:border-[#3f3f46] bg-[#111111]'
            }
          `}
        >
          <input {...getInputProps()} />
          <div className={`
            w-10 h-10 rounded-lg mb-4
            flex items-center justify-center
            border transition-colors duration-150
            ${isDragActive
              ? 'bg-[rgba(79,70,229,0.08)] border-[rgba(79,70,229,0.2)]'
              : 'bg-[#161616] border-[#1f1f1f]'
            }
          `}>
            <Upload
              size={18}
              strokeWidth={1.5}
              className={isDragActive ? 'text-[#4f46e5]' : 'text-[#52525b]'}
            />
          </div>

          {isDragActive ? (
            <p className="text-sm font-medium text-[#4f46e5]">
              Drop your CSV here
            </p>
          ) : (
            <>
              <p className="text-sm font-medium text-[#f5f5f5] mb-1">
                Drag & drop your CSV file
              </p>
              <p className="text-xs text-[#52525b]">
                or{' '}
                <span className="text-[#4f46e5] hover:underline cursor-pointer">
                  browse files
                </span>
                {' '}— max 10MB
              </p>
            </>
          )}
        </div>
      )}

      {/* ── STEP 1: Preview ── */}
      {step === 1 && file && (
        <div className="space-y-4">
          {/* File info bar */}
          <div className="flex items-center justify-between
            bg-[#111111] border border-[#1f1f1f] rounded-lg px-4 py-3"
          >
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-md bg-[#161616]
                border border-[#1f1f1f] flex items-center justify-center"
              >
                <FileText size={13} strokeWidth={1.5} className="text-[#52525b]" />
              </div>
              <div>
                <p className="text-xs font-medium text-[#f5f5f5]">
                  {file.name}
                </p>
                <p className="text-[11px] text-[#52525b]">
                  {(file.size / 1024).toFixed(1)} KB
                  {' · '}
                  {preview.length}+ rows detected
                </p>
              </div>
            </div>
            <button
              onClick={handleReset}
              className="text-[#52525b] hover:text-[#a1a1aa]
                transition-colors duration-150"
            >
              <X size={14} strokeWidth={1.5} />
            </button>
          </div>

          {/* Validation Errors */}
          {hasErrors && (
            <div className="bg-[rgba(239,68,68,0.04)] border
              border-[rgba(239,68,68,0.15)] rounded-lg p-4 space-y-1.5"
            >
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle size={13} strokeWidth={1.5}
                  className="text-[#ef4444]" />
                <span className="text-xs font-medium text-[#ef4444]">
                  {validationErrors.length} validation error
                  {validationErrors.length > 1 ? 's' : ''} found
                </span>
              </div>
              {validationErrors.slice(0, 5).map((e, i) => (
                <p key={i} className="text-xs text-[#a1a1aa] pl-5">
                  {e}
                </p>
              ))}
            </div>
          )}

          {/* Column check */}
          <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-4">
            <p className="text-[11px] font-medium text-[#52525b]
              uppercase tracking-widest mb-3"
            >
              Detected Columns
            </p>
            <div className="flex flex-wrap gap-1.5">
              {REQUIRED_COLS.map((col) => {
                const found = fields.includes(col)
                return (
                  <Badge
                    key={col}
                    variant={found ? 'success' : 'danger'}
                    dot
                  >
                    {col}
                  </Badge>
                )
              })}
            </div>
          </div>

          {/* Preview Table */}
          <div className="bg-[#111111] border border-[#1f1f1f]
            rounded-lg overflow-hidden"
          >
            <div className="px-4 py-3 border-b border-[#1f1f1f]">
              <p className="text-[11px] font-medium text-[#52525b]
                uppercase tracking-widest"
              >
                Data Preview — First 8 Rows
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-[#1f1f1f]">
                    {REQUIRED_COLS.map((col) => (
                      <th
                        key={col}
                        className="text-left px-4 py-2.5
                          text-[11px] font-medium text-[#52525b]
                          uppercase tracking-wider whitespace-nowrap"
                      >
                        {col.replace(/_/g, ' ')}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {preview.map((row, i) => (
                    <tr
                      key={i}
                      className={`
                        transition-colors duration-100
                        hover:bg-[#161616]
                        ${i !== preview.length - 1
                          ? 'border-b border-[#1f1f1f]'
                          : ''
                        }
                      `}
                    >
                      {REQUIRED_COLS.map((col) => (
                        <td
                          key={col}
                          className="px-4 py-2.5 text-[#a1a1aa]
                            whitespace-nowrap"
                        >
                          {row[col] || row[col.replace(/_/g, ' ')] || '—'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between pt-2">
            <Button variant="ghost" size="sm" onClick={handleReset}>
              Choose different file
            </Button>
            <Button
              variant="primary"
              size="md"
              iconRight={ArrowRight}
              onClick={handleUpload}
              disabled={hasErrors}
            >
              {hasErrors ? 'Fix errors to continue' : 'Upload & Analyze'}
            </Button>
          </div>
        </div>
      )}

      {/* ── STEP 2: Uploading ── */}
      {step === 2 && (
        <div className="bg-[#111111] border border-[#1f1f1f]
          rounded-lg p-8 space-y-6"
        >
          <div className="space-y-1">
            <h3 className="text-sm font-medium text-[#f5f5f5]">
              {progress === 100
                ? 'Upload complete'
                : 'Processing your data'
              }
            </h3>
            <p className="text-xs text-[#52525b]">
              {progress === 100
                ? 'Redirecting to students list...'
                : 'This will take a few seconds.'
              }
            </p>
          </div>

          <ProgressBar progress={progress} label={progressLabel} />

          {result && (
            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="bg-[#0a0a0a] border border-[#1f1f1f]
                rounded-lg p-4 text-center"
              >
                <div className="text-2xl font-semibold text-[#22c55e]
                  tracking-tight"
                >
                  {result.records_created}
                </div>
                <div className="text-[11px] text-[#52525b] mt-1 uppercase
                  tracking-wider"
                >
                  Records Created
                </div>
              </div>
              {result.records_failed > 0 && (
                <div className="bg-[#0a0a0a] border border-[#1f1f1f]
                  rounded-lg p-4 text-center"
                >
                  <div className="text-2xl font-semibold text-[#ef4444]
                    tracking-tight"
                  >
                    {result.records_failed}
                  </div>
                  <div className="text-[11px] text-[#52525b] mt-1 uppercase
                    tracking-wider"
                  >
                    Records Skipped
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Format guide ── */}
      {step === 0 && (
        <>
          <Divider className="my-8" />
          <div className="space-y-3">
            <p className="text-[11px] font-medium text-[#52525b]
              uppercase tracking-widest"
            >
              Expected Format
            </p>
            <div className="bg-[#111111] border border-[#1f1f1f]
              rounded-lg overflow-hidden"
            >
              <div className="overflow-x-auto">
                <table className="w-full text-[11px]">
                  <thead>
                    <tr className="border-b border-[#1f1f1f]">
                      {REQUIRED_COLS.map((col) => (
                        <th
                          key={col}
                          className="text-left px-3 py-2.5
                            font-medium text-[#52525b] whitespace-nowrap"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      {[
                        'John Doe','Mathematics',
                        '85','100','midterm','2024-01-15',
                      ].map((val, i) => (
                        <td
                          key={i}
                          className="px-3 py-2.5 text-[#3f3f46]
                            font-mono whitespace-nowrap"
                        >
                          {val}
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <p className="text-[11px] text-[#3f3f46]">
              exam_type: quiz · midterm · final · assignment · practical · project
            </p>
          </div>
        </>
      )}
    </div>
  )
}
