/**
 * EduSight AI — Message Bubble
 *
 * Renders a single chat message.
 * User messages: right-aligned, subtle bg.
 * AI messages: left-aligned, no bg, slightly muted text.
 * Minimal. No avatars, no heavy UI.
 */

import { format, parseISO, isValid } from 'date-fns'
import { Bot, User } from 'lucide-react'

// ── Format timestamp ──
function formatTime(timestamp) {
  try {
    const date = parseISO(timestamp)
    if (!isValid(date)) return ''
    return format(date, 'h:mm a')
  } catch {
    return ''
  }
}

// ── Parse AI message into paragraphs ──
function parseContent(content) {
  if (!content) return []
  return content
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
}

// ── AI Message ──
function AIMessage({ content, timestamp }) {
  const paragraphs = parseContent(content)

  return (
    <div className="flex items-start gap-3 group">
      {/* AI icon */}
      <div
        className="
          w-6 h-6 rounded-md flex-shrink-0
          bg-[#111111] border border-[#1f1f1f]
          flex items-center justify-center mt-0.5
        "
      >
        <div className="w-2 h-2 rounded-sm bg-[#4f46e5]" />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0 max-w-[85%]">
        <div className="space-y-1.5">
          {paragraphs.map((para, i) => {
            // ── Section headers (ALL CAPS: text) ──
            if (/^[A-Z][A-Z\s]+:/.test(para)) {
              const [label, ...rest] = para.split(':')
              return (
                <div key={i}>
                  <span className="text-[11px] font-semibold text-[#52525b] uppercase tracking-wider">
                    {label}:
                  </span>
                  {rest.join(':').trim() && (
                    <p className="text-sm text-[#a1a1aa] leading-relaxed mt-0.5">
                      {rest.join(':').trim()}
                    </p>
                  )}
                </div>
              )
            }

            // ── Bullet point lines ──
            if (para.startsWith('•') || para.startsWith('-')) {
              return (
                <div key={i} className="flex items-start gap-2">
                  <div className="w-1 h-1 rounded-full bg-[#3f3f46] mt-2 flex-shrink-0" />
                  <p className="text-sm text-[#a1a1aa] leading-relaxed">
                    {para.replace(/^[•\-]\s*/, '')}
                  </p>
                </div>
              )
            }

            // ── Regular paragraph ──
            return (
              <p key={i} className="text-sm text-[#a1a1aa] leading-relaxed">
                {para}
              </p>
            )
          })}
        </div>

        {/* Timestamp */}
        {timestamp && (
          <p className="text-[11px] text-[#3f3f46] mt-1.5">
            {formatTime(timestamp)}
          </p>
        )}
      </div>
    </div>
  )
}

// ── User Message ──
function UserMessage({ content, timestamp }) {
  return (
    <div className="flex items-start justify-end gap-3 group">
      {/* Content */}
      <div className="max-w-[75%]">
        <div
          className="
            bg-[#1a1a1a] border border-[#2a2a2a]
            rounded-lg rounded-tr-sm
            px-4 py-2.5
          "
        >
          <p className="text-sm text-[#f5f5f5] leading-relaxed">
            {content}
          </p>
        </div>

        {/* Timestamp */}
        {timestamp && (
          <p className="text-[11px] text-[#3f3f46] mt-1.5 text-right">
            {formatTime(timestamp)}
          </p>
        )}
      </div>

      {/* User icon */}
      <div
        className="
          w-6 h-6 rounded-md flex-shrink-0
          bg-[#1a1a1a] border border-[#2a2a2a]
          flex items-center justify-center mt-0.5
        "
      >
        <User size={11} strokeWidth={1.5} className="text-[#52525b]" />
      </div>
    </div>
  )
}

// ── Main Export ──
export default function MessageBubble({ message }) {
  if (message.role === 'user') {
    return (
      <UserMessage
        content={message.content}
        timestamp={message.timestamp}
      />
    )
  }

  return (
    <AIMessage
      content={message.content}
      timestamp={message.timestamp}
    />
  )
}
