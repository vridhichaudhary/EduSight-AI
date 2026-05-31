/**
 * Toast Notification System
 * Appears top-right. Auto-dismisses after duration.
 */

import { CheckCircle, AlertCircle, Info, X, AlertTriangle } from 'lucide-react'
import useStore from '../../store/useStore'

const icons = {
  success: CheckCircle,
  error:   AlertCircle,
  info:    Info,
  warning: AlertTriangle,
}

const styles = {
  success: 'border-l-2 border-[#22c55e]',
  error:   'border-l-2 border-[#ef4444]',
  info:    'border-l-2 border-[#4f46e5]',
  warning: 'border-l-2 border-[#f59e0b]',
}

const iconColors = {
  success: '#22c55e',
  error:   '#ef4444',
  info:    '#4f46e5',
  warning: '#f59e0b',
}

function ToastItem({ id, type, title, message }) {
  const removeNotification = useStore((s) => s.removeNotification)
  const Icon = icons[type] || Info

  return (
    <div
      className={`
        flex items-start gap-3 w-80
        bg-[#111111] border border-[#1f1f1f]
        rounded-lg px-4 py-3
        shadow-[0_4px_12px_rgba(0,0,0,0.5)]
        animate-fade-in
        ${styles[type]}
      `}
    >
      <Icon
        size={15}
        strokeWidth={1.5}
        style={{ color: iconColors[type] }}
        className="flex-shrink-0 mt-0.5"
      />
      <div className="flex-1 min-w-0">
        {title && (
          <p className="text-xs font-medium text-[#f5f5f5] mb-0.5">{title}</p>
        )}
        {message && (
          <p className="text-xs text-[#a1a1aa] leading-relaxed">{message}</p>
        )}
      </div>
      <button
        onClick={() => removeNotification(id)}
        className="text-[#52525b] hover:text-[#a1a1aa] transition-colors flex-shrink-0"
      >
        <X size={13} />
      </button>
    </div>
  )
}

export default function ToastContainer() {
  const notifications = useStore((s) => s.notifications)

  if (!notifications.length) return null

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {notifications.map((n) => (
        <ToastItem key={n.id} {...n} />
      ))}
    </div>
  )
}
