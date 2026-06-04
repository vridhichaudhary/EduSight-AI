/**
 * EduSight AI — PDF Report Download Button
 * Reusable button that triggers PDF download.
 * Shows loading state while generating.
 */

import { useState } from 'react'
import { FileDown, CheckCircle } from 'lucide-react'
import Button from './Button'
import { analysisAPI } from '../../services/api'
import useStore from '../../store/useStore'

export default function DownloadReportButton({
  studentId,
  studentName,
  variant = 'secondary',
  size    = 'sm',
  label   = 'Download Report',
}) {
  const [downloading, setDownloading] = useState(false)
  const [done,        setDone]        = useState(false)
  const { addNotification }           = useStore()

  const handleDownload = async () => {
    if (downloading) return
    setDownloading(true)

    try {
      await analysisAPI.downloadReport(studentId, studentName)
      setDone(true)
      addNotification({
        type:    'success',
        title:   'Report downloaded',
        message: `${studentName} performance report saved.`,
      })
      setTimeout(() => setDone(false), 3000)
    } catch (err) {
      addNotification({
        type:    'error',
        title:   'Download failed',
        message: (
          err.message ||
          'Run analysis first to generate report.'
        ),
      })
    } finally {
      setDownloading(false)
    }
  }

  return (
    <Button
      variant={variant}
      size={size}
      icon={done ? CheckCircle : FileDown}
      loading={downloading}
      onClick={handleDownload}
      className={done ? 'text-[#22c55e]' : ''}
    >
      {downloading
        ? 'Generating...'
        : done
        ? 'Downloaded'
        : label
      }
    </Button>
  )
}
