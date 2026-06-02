/**
 * EduSight AI — Chat Input
 *
 * Fixed bottom input area.
 * Auto-resizing textarea.
 * Send on Enter (Shift+Enter for newline).
 * Disabled while loading.
 */

import { useRef, useState, useEffect, useCallback } from 'react'
import { ArrowUp, Square } from 'lucide-react'

export default function ChatInput({ onSend, loading, disabled }) {
  const [value,    setValue]    = useState('')
  const textareaRef             = useRef(null)
  const MAX_HEIGHT              = 160

  // ── Auto-resize textarea ──
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, MAX_HEIGHT) + 'px'
  }, [value])

  // ── Focus on mount ──
  useEffect(() => {
    if (!disabled) {
      textareaRef.current?.focus()
    }
  }, [disabled])

  const handleSend = useCallback(() => {
    const trimmed = value.trim()
    if (!trimmed || loading || disabled) return
    onSend(trimmed)
    setValue('')
    // Reset height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }, [value, loading, disabled, onSend])

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSend()
      }
    },
    [handleSend]
  )

  const canSend = value.trim().length > 0 && !loading && !disabled

  return (
    <div
      className="
        border-t border-[#1f1f1f]
        bg-[#0a0a0a]
        px-6 py-4
      "
    >
      <div
        className="
          flex items-end gap-3
          bg-[#111111]
          border border-[#1f1f1f]
          rounded-lg
          px-4 py-3
          focus-within:border-[#2a2a2a]
          transition-colors duration-150
          max-w-3xl mx-auto
        "
      >
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your performance..."
          disabled={loading || disabled}
          rows={1}
          className="
            flex-1 bg-transparent
            text-sm text-[#f5f5f5]
            placeholder:text-[#3f3f46]
            resize-none outline-none
            leading-relaxed
            disabled:opacity-50
            min-h-[24px]
          "
          style={{ maxHeight: MAX_HEIGHT }}
        />

        {/* Send button */}
        <button
          onClick={handleSend}
          disabled={!canSend}
          className="
            w-7 h-7 rounded-md flex-shrink-0
            flex items-center justify-center
            transition-all duration-150
            disabled:opacity-30 disabled:cursor-not-allowed
            focus:outline-none
            mb-0.5
            bg-[#4f46e5] hover:bg-[#4338ca]
            disabled:bg-[#1f1f1f]
          "
        >
          {loading ? (
            <Square
              size={10}
              strokeWidth={2}
              className="text-white fill-white"
            />
          ) : (
            <ArrowUp size={13} strokeWidth={2} className="text-white" />
          )}
        </button>
      </div>

      {/* Hint */}
      <p className="text-[11px] text-[#3f3f46] text-center mt-2">
        Press Enter to send · Shift+Enter for new line
      </p>
    </div>
  )
}
