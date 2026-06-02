/**
 * EduSight AI — Chat Page (Complete)
 *
 * Conversational AI interface for student performance queries.
 * Connects to LangChain backend with real student data context.
 */

import {
  useEffect,
  useRef,
  useCallback,
  useState,
} from 'react'
import { useParams }     from 'react-router-dom'
import { useQuery }      from '@tanstack/react-query'
import { studentAPI, dashboardAPI } from '../../services/api'
import useChat           from '../../hooks/useChat'
import ChatHeader        from '../../components/chat/ChatHeader'
import ChatInput         from '../../components/chat/ChatInput'
import MessageBubble     from '../../components/chat/MessageBubble'
import TypingIndicator   from '../../components/chat/TypingIndicator'
import StarterSuggestions from '../../components/chat/StarterSuggestions'
import { Skeleton }      from '../../components/ui/Skeleton'

// ── Utilities ──
function isSameDay(d1, d2) {
  try {
    return (
      d1.getFullYear() === d2.getFullYear() &&
      d1.getMonth()    === d2.getMonth() &&
      d1.getDate()     === d2.getDate()
    )
  } catch { return true }
}

function formatDateLabel(timestamp) {
  try {
    const date      = new Date(timestamp)
    const today     = new Date()
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    if (isSameDay(date, today))     return 'Today'
    if (isSameDay(date, yesterday)) return 'Yesterday'
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day:   'numeric',
      year:  date.getFullYear() !== today.getFullYear()
        ? 'numeric' : undefined,
    })
  } catch { return '' }
}

// ── Date separator ──
function DateSeparator({ label }) {
  return (
    <div className="flex items-center gap-3 py-4 px-6">
      <div className="flex-1 h-px bg-[#1f1f1f]" />
      <span className="text-[11px] text-[#3f3f46] flex-shrink-0 select-none">
        {label}
      </span>
      <div className="flex-1 h-px bg-[#1f1f1f]" />
    </div>
  )
}

// ── Scroll to bottom button ──
function ScrollDownButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="
        absolute bottom-4 right-6
        w-8 h-8 rounded-full
        bg-[#111111] border border-[#2a2a2a]
        flex items-center justify-center
        shadow-[0_4px_16px_rgba(0,0,0,0.5)]
        hover:border-[#3f3f46] hover:bg-[#161616]
        transition-all duration-150
        z-10
      "
    >
      <svg
        width="12"
        height="12"
        viewBox="0 0 12 12"
        fill="none"
      >
        <path
          d="M6 2L6 10M6 10L3 7M6 10L9 7"
          stroke="#71717a"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  )
}

// ── Message list ──
function MessageThread({ messages, loading, fetching }) {
  if (fetching) {
    return (
      <div className="px-6 py-6 space-y-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex items-start gap-3">
            <Skeleton className="w-6 h-6 rounded-md flex-shrink-0" />
            <div className="space-y-2 flex-1">
              <Skeleton className="h-3 w-2/3" />
              <Skeleton className="h-3 w-1/2" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  const items = []
  messages.forEach((msg, idx) => {
    const showDate =
      idx === 0 ||
      !isSameDay(
        new Date(msg.timestamp),
        new Date(messages[idx - 1].timestamp)
      )
    if (showDate) {
      items.push(
        <DateSeparator
          key={`date-${idx}`}
          label={formatDateLabel(msg.timestamp)}
        />
      )
    }
    items.push(
      <div key={msg.id} className="px-6">
        <MessageBubble message={msg} />
      </div>
    )
  })

  return (
    <div className="py-4 space-y-3">
      {items}
      {loading && <TypingIndicator />}
    </div>
  )
}

// ── Main Page ──
export default function ChatPage() {
  const { studentId }   = useParams()
  const bottomRef       = useRef(null)
  const containerRef    = useRef(null)
  const [userScrolled, setUserScrolled] = useState(false)

  // ── Data queries ──
  const { data: studentData } = useQuery({
    queryKey: ['student', studentId],
    queryFn:  () => studentAPI.get(studentId),
    enabled:  !!studentId,
  })

  const { data: dashData } = useQuery({
    queryKey: ['dashboard', studentId],
    queryFn:  () => dashboardAPI.get(studentId),
    enabled:  !!studentId,
    staleTime: 1000 * 60 * 5,
  })

  const student      = studentData?.data?.data
  const weakSubjects = (dashData?.data?.data?.weak_areas || [])
    .map((w) => w.subject_name)
    .slice(0, 2)

  // ── Chat state ──
  const {
    messages,
    loading,
    fetching,
    error,
    sendMessage,
    clearError,
    isEmpty,
  } = useChat(studentId)

  // ── Scroll to bottom on new messages ──
  useEffect(() => {
    if (!userScrolled) {
      bottomRef.current?.scrollIntoView({
        behavior: messages.length <= 1 ? 'auto' : 'smooth',
        block: 'end',
      })
    }
  }, [messages.length, loading, userScrolled])

  // ── Detect manual scroll ──
  useEffect(() => {
    const el = containerRef.current
    if (!el) return
    const onScroll = () => {
      const atBottom =
        el.scrollHeight - el.scrollTop - el.clientHeight < 80
      setUserScrolled(!atBottom)
    }
    el.addEventListener('scroll', onScroll, { passive: true })
    return () => el.removeEventListener('scroll', onScroll)
  }, [])

  const handleSend = useCallback(async (text) => {
    setUserScrolled(false)
    await sendMessage(text)
  }, [sendMessage])

  const scrollToBottom = useCallback(() => {
    setUserScrolled(false)
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [])

  return (
    <div
      className="
        flex flex-col
        h-[calc(100vh-3rem)]
        bg-[#0a0a0a]
      "
    >
      {/* Header */}
      <ChatHeader
        studentName={student?.name}
        messageCount={messages.length}
        onRefresh={() => window.location.reload()}
      />

      {/* Body */}
      <div className="flex-1 relative overflow-hidden">

        {isEmpty && !fetching ? (
          // ── Starter screen ──
          <div className="h-full overflow-y-auto">
            <StarterSuggestions
              onSelect={handleSend}
              weakSubjects={weakSubjects}
            />
          </div>
        ) : (
          // ── Message thread ──
          <div
            ref={containerRef}
            className="h-full overflow-y-auto"
            style={{
              scrollbarWidth: 'thin',
              scrollbarColor: '#2a2a2a transparent',
            }}
          >
            <MessageThread
              messages={messages}
              loading={loading}
              fetching={fetching}
            />
            <div ref={bottomRef} className="h-px" />
          </div>
        )}

        {/* Scroll-to-bottom button */}
        {userScrolled && messages.length > 4 && (
          <ScrollDownButton onClick={scrollToBottom} />
        )}
      </div>

      {/* Error banner */}
      {error && (
        <div
          className="
            mx-6 mb-2 px-4 py-2.5
            flex items-center justify-between
            bg-[rgba(239,68,68,0.04)]
            border border-[rgba(239,68,68,0.15)]
            rounded-lg
          "
        >
          <p className="text-xs text-[#ef4444]">{error}</p>
          <button
            onClick={clearError}
            className="text-xs text-[#52525b] hover:text-[#a1a1aa] ml-4 flex-shrink-0"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Input */}
      <ChatInput
        onSend={handleSend}
        loading={loading}
        disabled={fetching}
      />
    </div>
  )
}
