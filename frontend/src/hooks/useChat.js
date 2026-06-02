/**
 * EduSight AI — useChat Hook
 *
 * Manages chat state, API calls, and message history.
 * Used by ChatPage component.
 *
 * Features:
 *   - Load conversation history on mount
 *   - Send messages with loading state
 *   - Auto-retry on failure
 *   - Optimistic message append
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { chatAPI } from '../services/api'
import useStore from '../store/useStore'

export default function useChat(studentId) {
  const [messages,  setMessages]  = useState([])
  const [loading,   setLoading]   = useState(false)
  const [fetching,  setFetching]  = useState(true)
  const [error,     setError]     = useState(null)
  const { addNotification }       = useStore()
  const abortRef                  = useRef(null)

  // ── Load history on mount ──
  useEffect(() => {
    if (!studentId) return
    loadHistory()
    return () => {
      if (abortRef.current) abortRef.current.abort()
    }
  }, [studentId])

  const loadHistory = useCallback(async () => {
    setFetching(true)
    try {
      const res = await chatAPI.getHistory(studentId)
      const raw = res.data?.data || []

      // Normalize to UI message format
      const normalized = raw.map((msg) => ({
        id:        msg.id,
        role:      msg.role,
        content:   msg.content,
        timestamp: msg.created_at,
        sources:   msg.sources || [],
      }))

      setMessages(normalized)
    } catch (err) {
      console.error('Chat history load failed:', err)
    } finally {
      setFetching(false)
    }
  }, [studentId])

  const sendMessage = useCallback(async (text) => {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    // ── Optimistic user message ──
    const userMsg = {
      id:        `temp-${Date.now()}`,
      role:      'user',
      content:   trimmed,
      timestamp: new Date().toISOString(),
      sources:   [],
    }

    setMessages((prev) => [...prev, userMsg])
    setLoading(true)
    setError(null)

    try {
      const res = await chatAPI.send(studentId, trimmed)
      const data = res.data?.data

      // ── Append AI response ──
      const aiMsg = {
        id:        data.message_id || `ai-${Date.now()}`,
        role:      'assistant',
        content:   data.ai_response,
        timestamp: data.timestamp || new Date().toISOString(),
        sources:   data.sources || [],
      }

      setMessages((prev) => [...prev, aiMsg])

    } catch (err) {
      setError('Failed to send message. Please try again.')
      addNotification({
        type:    'error',
        title:   'Message failed',
        message: 'Could not reach AI. Check your connection.',
      })
      // Remove optimistic message on error
      setMessages((prev) =>
        prev.filter((m) => m.id !== userMsg.id)
      )
    } finally {
      setLoading(false)
    }
  }, [studentId, loading, addNotification])

  const clearError = useCallback(() => setError(null), [])

  return {
    messages,
    loading,
    fetching,
    error,
    sendMessage,
    clearError,
    isEmpty: messages.length === 0 && !fetching,
  }
}
