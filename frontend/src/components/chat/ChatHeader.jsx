/**
 * EduSight AI — Chat Header
 * Shows student name, status, and clear button.
 */

import { Trash2, RefreshCw } from 'lucide-react'
import Button from '../ui/Button'
import Badge from '../ui/Badge'

export default function ChatHeader({
  studentName,
  messageCount,
  onRefresh,
}) {
  return (
    <div
      className="
        flex items-center justify-between
        px-6 py-4
        border-b border-[#1f1f1f]
        bg-[#0a0a0a]
        flex-shrink-0
      "
    >
      {/* Left */}
      <div className="flex items-center gap-3">
        {/* Status dot */}
        <div className="flex items-center gap-2">
          <div
            className="
              w-1.5 h-1.5 rounded-full bg-[#22c55e]
            "
            style={{
              boxShadow: '0 0 6px rgba(34,197,94,0.4)',
            }}
          />
          <span className="text-xs font-medium text-[#f5f5f5]">
            EduSight AI
          </span>
        </div>

        {/* Divider */}
        <div className="w-px h-3 bg-[#2a2a2a]" />

        {/* Student context */}
        <span className="text-xs text-[#52525b]">
          {studentName || 'Student'}
        </span>

        {/* Message count */}
        {messageCount > 0 && (
          <Badge variant="default">
            {messageCount} message{messageCount !== 1 ? 's' : ''}
          </Badge>
        )}
      </div>

      {/* Right */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="sm"
          icon={RefreshCw}
          onClick={onRefresh}
        >
          Refresh
        </Button>
      </div>
    </div>
  )
}
