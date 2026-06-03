/**
 * EduSight AI — Enhanced Upload Page
 * Supports: CSV, Excel (.xlsx), PDF upload
 * Plus: Manual marks entry form
 */

import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import Papa from 'papaparse'
import {
  Upload, FileText, X, CheckCircle,
  AlertCircle, Download, ArrowRight,
  ChevronRight, FileSpreadsheet, FileType,
} from 'lucide-react'
import { marksAPI } from '../services/api'
import api from '../services/api'
import useStore from '../store/useStore'
import PageHeader from '../components/layout/PageHeader'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import Divider from '../components/ui/Divider'
import UploadTabs from '../components/upload/UploadTabs'
import ManualEntryForm from '../components/upload/ManualEntryForm'
import { parseExcelFile } from '../components/upload/ExcelParser'
import { parsePDFFile } from '../components/upload/PDFParser'

// ── Constants ──
const REQUIRED_COLS = [
  'student_name', 'subject', 'marks_obtained',
  'max_marks', 'exam_type', 'exam_date',
]

const FILE_ICONS = {
  csv:  { icon: FileText,        color: '#22c55e', label: 'CSV' },
  xlsx: { icon: FileSpreadsheet, color: '#4f46e5', label: 'Excel' },
  xls:  { icon: FileSpreadsheet, color: '#4f46e5', label: 'Excel' },
  pdf:  { icon: FileType,        color: '#f59e0b', label: 'PDF' },
}

// ── Template Download ──
function downloadTemplate() {
  const headers = REQUIRED_COLS
  const rows = [
    ['John Doe','Mathematics','85','100','midterm','2024-01-15'],
    ['John Doe','Science',    '78','100','midterm','2024-01-16'],
    ['John Doe','English',    '92','100','midterm','2024-01-17'],
    ['Jane Smith','Mathematics','72','100','midterm','2024-01-15'],
    ['Jane Smith','Science',   '88','100','midterm','2024-01-16'],
  ]

  const csv  = [headers, ...rows].map((r) => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url  = URL.createObjectURL(blob)
  const a    = Object.assign(document.createElement('a'), {
    href: url, download: 'edusight_template.csv'
  })
  a.click()
  URL.revokeObjectURL(url)
}

// ── Step Indicator ──
function StepIndicator({ steps, current }) {
  return (
    <div className="flex items-center gap-0 mb-10">
      {steps.map((step, i) => {
        const done   = i < current
        const active = i === current
        return (
          <div key={step} className="flex items-center">
            <div className="flex items-center gap-2">
              <div className={`
                w-5 h-5 rounded-full flex items-center justify-center
                text-[10px] font-semibold transition-all duration-200
                ${done   ? 'bg-[#22c55e] text-white'  :
                  active ? 'bg-[#4f46e5] text-white'  :
                           'bg-[#161616] border border-[#1f1f1f] text-[#52525b]'}
              `}>
                {done ? <CheckCircle size={11} /> : i + 1}
              </div>
              <span className={`text-xs font-medium ${
                active ? 'text-[#f5f5f5]' :
                done   ? 'text-[#52525b]' : 'text-[#3f3f46]'
              }`}>{step}</span>
            </div>
            {i < steps.length - 1 && (
              <ChevronRight size={14} strokeWidth={1.5}
                className="text-[#2a2a2a] mx-3" />
            )}
          </div>
        )
      })}
    </div>
  )
}

// ── Progress Bar ──
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
          className="h-full bg-[#4f46e5] rounded-full
            transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────
// MAIN COMPONENT
// ─────────────────────────────────────────────
export default function UploadPage() {
  const navigate        = useNavigate()
  const { addNotification } = useStore()

  // Tabs
  const [activeTab, setActiveTab] = useState('file')

  // File upload state
  const [step,             setStep]      = useState(0)
  const [file,             setFile]      = useState(null)
  const [preview,          setPreview]   = useState([])
  const [fields,           setFields]    = useState([])
  const [validationErrors, setValErrors] = useState([])
  const [fileType,         setFileType]  = useState('')
  const [pdfNote,          setPdfNote]   = useState('')

  // Upload state
  const [uploading,     setUploading]  = useState(false)
  const [progress,      setProgress]  = useState(0)
  const [progressLabel, setProgLabel] = useState('')
  const [result,        setResult]    = useState(null)
  const [resultStudentId, setResultStudentId] = useState(null)

  const steps = ['Select File', 'Preview & Validate', 'Upload']

  // ── File Parsing ──
  const parseFile = useCallback(async (f) => {
    const ext = f.name.split('.').pop().toLowerCase()
    setFileType(ext)

    try {
      if (ext === 'csv') {
        Papa.parse(f, {
          header:         true,
          skipEmptyLines: true,
          complete: (results) => {
            const normalized = results.meta.fields.map((h) =>
              h.toLowerCase().trim().replace(/\s+/g, '_')
            )
            const missing = REQUIRED_COLS.filter(
              (c) => !normalized.includes(c)
            )
            setFields(normalized)
            setPreview(results.data.slice(0, 8))
            setValErrors(
              missing.length > 0
                ? [`Missing columns: ${missing.join(', ')}`]
                : []
            )
          },
        })
      } else if (ext === 'xlsx' || ext === 'xls') {
        const result = await parseExcelFile(f)
        setFields(result.fields)
        setPreview(result.data.slice(0, 8))
        setValErrors(result.errors)
      } else if (ext === 'pdf') {
        const result = await parsePDFFile(f)
        setFields([])
        setPreview([])
        setValErrors(result.errors)
        if (result.note) setPdfNote(result.note)
      }
    } catch (err) {
      setValErrors([`Parse error: ${err.message}`])
    }
  }, [])

  // ── Dropzone ──
  const onDrop = useCallback(async (accepted, rejected) => {
    if (rejected.length > 0) {
      addNotification({
        type:    'error',
        title:   'Invalid file',
        message: 'Only CSV, Excel (.xlsx), and PDF files accepted.',
      })
      return
    }
    const f = accepted[0]
    setFile(f)
    await parseFile(f)
    setStep(1)
  }, [addNotification, parseFile])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv':                          ['.csv'],
      'application/vnd.ms-excel':          ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                                           ['.xlsx'],
      'application/pdf':                   ['.pdf'],
    },
    maxFiles: 1,
    maxSize:  10 * 1024 * 1024,
  })

  // ── File Upload ──
  const handleFileUpload = async () => {
    if (!file) return
    setUploading(true)
    setStep(2)

    const fakeSteps = [
      [20, 'Uploading file...'],
      [50, 'Parsing data...'],
      [75, 'Creating records...'],
      [90, 'Finalizing...'],
    ]

    for (const [p, label] of fakeSteps) {
      await new Promise((r) => setTimeout(r, 400))
      setProgress(p)
      setProgLabel(label)
    }

    try {
      const res = await marksAPI.uploadCSV(file)
      setProgress(100)
      setProgLabel('Complete')
      const data = res.data?.data
      setResult(data)
      setResultStudentId(data?.student_id)

      addNotification({
        type:    'success',
        title:   'Upload successful',
        message: `${data?.records_created} records created.`,
      })

      await new Promise((r) => setTimeout(r, 800))

      if (data?.student_id) {
        navigate(`/dashboard/${data.student_id}/overview`)
      } else {
        navigate('/students')
      }
    } catch (err) {
      setUploading(false)
      setStep(1)
      setProgress(0)
      addNotification({
        type:    'error',
        title:   'Upload failed',
        message: err.message || 'Please check your file and try again.',
      })
    }
  }

  // ── Manual Submit ──
  const handleManualSubmit = async (payload) => {
    setUploading(true)
    try {
      const res = await api.post('/api/marks/bulk/', payload)
      const data = res.data?.data

      addNotification({
        type:    'success',
        title:   'Marks submitted',
        message: `${data?.records_created} entries saved for ${data?.student_name}.`,
      })

      if (data?.student_id) {
        navigate(`/dashboard/${data.student_id}/overview`)
      } else {
        navigate('/students')
      }
    } catch (err) {
      setUploading(false)
      addNotification({
        type:    'error',
        title:   'Submission failed',
        message: err.message || 'Please check your entries.',
      })
    }
  }

  // ── Reset ──
  const handleReset = () => {
    setFile(null)
    setPreview([])
    setFields([])
    setValErrors([])
    setFileType('')
    setPdfNote('')
    setStep(0)
    setProgress(0)
    setResult(null)
    setUploading(false)
  }

  const hasErrors = validationErrors.length > 0
  const FileIcon  = FILE_ICONS[fileType]?.icon || FileText
  const iconColor = FILE_ICONS[fileType]?.color || '#52525b'

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <PageHeader
        badge="Data Input"
        title="Upload Student Marks"
        description="Add student performance data via file upload or manual entry."
        actions={
          activeTab === 'file' && (
            <Button
              variant="ghost"
              size="sm"
              icon={Download}
              onClick={downloadTemplate}
            >
              CSV Template
            </Button>
          )
        }
      />

      <UploadTabs activeTab={activeTab} onChange={setActiveTab} />

      {/* ───────────────────────────────────────────── */}
      {/* TAB: FILE UPLOAD */}
      {/* ───────────────────────────────────────────── */}
      {activeTab === 'file' && (
        <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
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
                  Drop your file here
                </p>
              ) : (
                <>
                  <p className="text-sm font-medium text-[#f5f5f5] mb-1">
                    Drag & drop your file
                  </p>
                  <p className="text-xs text-[#52525b]">
                    or{' '}
                    <span className="text-[#4f46e5] hover:underline cursor-pointer">
                      browse files
                    </span>
                    {' '}— max 10MB
                  </p>
                  <div className="flex items-center gap-2 mt-4 text-[11px] font-medium">
                    <Badge variant="success">.CSV</Badge>
                    <Badge variant="accent">.XLSX</Badge>
                    <Badge variant="warning">.PDF</Badge>
                  </div>
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
                  <div className="w-8 h-8 rounded-md bg-[#161616]
                    border border-[#1f1f1f] flex items-center justify-center"
                  >
                    <FileIcon size={14} strokeWidth={1.5} color={iconColor} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-xs font-medium text-[#f5f5f5]">
                        {file.name}
                      </p>
                      <Badge variant="default" className="text-[9px] px-1.5 py-0">
                        {FILE_ICONS[fileType]?.label || 'File'}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-[#52525b] mt-0.5">
                      {(file.size / 1024).toFixed(1)} KB
                      {preview.length > 0 && ` · ${preview.length}+ rows detected`}
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

              {/* PDF Note */}
              {fileType === 'pdf' && pdfNote && (
                <div className="bg-[rgba(245,158,11,0.05)] border border-[rgba(245,158,11,0.2)] rounded-lg p-4">
                  <div className="flex items-center gap-2">
                    <FileType size={14} className="text-[#f59e0b]" />
                    <p className="text-xs text-[#f59e0b] font-medium">{pdfNote}</p>
                  </div>
                </div>
              )}

              {/* Column check (if we have fields) */}
              {fields.length > 0 && (
                <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-4">
                  <p className="text-[11px] font-medium text-[#52525b] uppercase tracking-widest mb-3">
                    Required Columns
                  </p>
                  <div className="flex flex-wrap gap-1.5">
                    {REQUIRED_COLS.map((col) => {
                      const found = fields.includes(col)
                      return (
                        <Badge key={col} variant={found ? 'success' : 'danger'} dot>
                          {col}
                        </Badge>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Preview Table */}
              {preview.length > 0 && (
                <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg overflow-hidden">
                  <div className="px-4 py-3 border-b border-[#1f1f1f]">
                    <p className="text-[11px] font-medium text-[#52525b] uppercase tracking-widest">
                      Data Preview — First 8 Rows
                    </p>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-[#1f1f1f] bg-[#0d0d0d]">
                          {REQUIRED_COLS.map((col) => (
                            <th
                              key={col}
                              className="text-left px-4 py-2.5 text-[10px] font-semibold text-[#52525b] uppercase tracking-wider whitespace-nowrap"
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
                            className={`transition-colors duration-100 hover:bg-[#161616] ${i !== preview.length - 1 ? 'border-b border-[#1f1f1f]' : ''}`}
                          >
                            {REQUIRED_COLS.map((col) => (
                              <td key={col} className="px-4 py-2.5 text-[#a1a1aa] whitespace-nowrap">
                                {row[col] || row[col.replace(/_/g, ' ')] || '—'}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-2">
                <Button variant="ghost" size="sm" onClick={handleReset}>
                  Choose different file
                </Button>
                <Button
                  variant="primary"
                  size="md"
                  iconRight={ArrowRight}
                  onClick={handleFileUpload}
                  disabled={hasErrors}
                >
                  {hasErrors ? 'Fix errors to continue' : 'Upload & Process'}
                </Button>
              </div>
            </div>
          )}

          {/* ── STEP 2: Uploading ── */}
          {step === 2 && (
            <div className="bg-[#111111] border border-[#1f1f1f] rounded-lg p-8 space-y-6">
              <div className="space-y-1">
                <h3 className="text-sm font-medium text-[#f5f5f5]">
                  {progress === 100 ? 'Upload complete' : 'Processing your data'}
                </h3>
                <p className="text-xs text-[#52525b]">
                  {progress === 100 ? 'Redirecting...' : 'This will take a few seconds.'}
                </p>
              </div>

              <ProgressBar progress={progress} label={progressLabel} />

              {result && (
                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className="bg-[#0a0a0a] border border-[#1f1f1f] rounded-lg p-4 text-center">
                    <div className="text-2xl font-semibold text-[#22c55e] tracking-tight">
                      {result.records_created}
                    </div>
                    <div className="text-[11px] text-[#52525b] mt-1 uppercase tracking-wider">
                      Records Created
                    </div>
                  </div>
                  {result.records_failed > 0 && (
                    <div className="bg-[#0a0a0a] border border-[#1f1f1f] rounded-lg p-4 text-center">
                      <div className="text-2xl font-semibold text-[#ef4444] tracking-tight">
                        {result.records_failed}
                      </div>
                      <div className="text-[11px] text-[#52525b] mt-1 uppercase tracking-wider">
                        Records Skipped
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ───────────────────────────────────────────── */}
      {/* TAB: MANUAL ENTRY */}
      {/* ───────────────────────────────────────────── */}
      {activeTab === 'manual' && (
        <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
          <ManualEntryForm onSubmit={handleManualSubmit} loading={uploading} />
        </div>
      )}

    </div>
  )
}
