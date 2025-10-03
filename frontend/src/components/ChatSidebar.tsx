'use client'

import React, { useEffect, useState } from 'react'
import { X, Plus, MessageSquare, Trash2, Loader2 } from 'lucide-react'
import { api } from '@/services/api'
import clsx from 'clsx'
import { v4 as uuidv4 } from 'uuid'

// Define ChatSession type explicitly to enforce id as string
interface ChatSession {
  id: string
  title: string
  updated_at: string
  // Add other session properties as needed
}

interface ChatSidebarProps {
  isOpen: boolean
  onClose: () => void
  currentSessionId: string | null
  onNewChat: () => void
  onSelectSession: (sessionId: string) => void
}

export default function ChatSidebar({
  isOpen,
  onClose,
  currentSessionId,
  onNewChat,
  onSelectSession
}: ChatSidebarProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    checkAuth()
  }, [])

  useEffect(() => {
    if (isOpen && isAuthenticated) {
      loadSessions()
    }
  }, [isOpen, isAuthenticated])

  const checkAuth = () => {
    const token = localStorage.getItem('access_token')
    setIsAuthenticated(!!token)
  }

  const loadSessions = async () => {
    setIsLoading(true)
    try {
      const data = await api.getChatSessions()
      // Ensure unique and valid IDs
      const safeSessions = data.map((session: ChatSession) => ({
        ...session,
        id: session.id && typeof session.id === 'string' ? session.id : uuidv4(),
      }))
      // Log sessions for debugging
      console.log('Loaded sessions:', safeSessions)
      // Filter out any sessions with invalid IDs (extra safety)
      const validSessions = safeSessions.filter(
        (session) => session.id && typeof session.id === 'string'
      )
      setSessions(
        validSessions.sort((a, b) =>
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        )
      )
    } catch (error) {
      console.error('Error loading sessions:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteSession = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('Delete this conversation?')) return

    try {
      await api.deleteChatSession(sessionId)
      setSessions((prev) => prev.filter((s) => s.id !== sessionId))
      if (currentSessionId === sessionId) {
        onNewChat()
      }
    } catch (error) {
      console.error('Error deleting session:', error)
      alert('Failed to delete conversation')
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <>
      {/* Overlay */}
      <div
        className={clsx(
          'fixed inset-0 bg-black bg-opacity-50 transition-opacity z-40',
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        )}
        onClick={onClose}
      />

      {/* Sidebar */}
      <div
        className={clsx(
          'fixed top-0 left-0 h-full w-80 bg-white shadow-xl transform transition-transform duration-300 ease-in-out z-50 flex flex-col',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Chat History</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* New Chat Button */}
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={() => {
              onNewChat()
              onClose()
            }}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto p-4">
          {!isAuthenticated ? (
            <div className="text-center text-gray-500 mt-8">
              <MessageSquare className="h-12 w-12 mx-auto mb-3 text-gray-400" />
              <p className="text-sm">Please login to view chat history</p>
            </div>
          ) : isLoading ? (
            <div className="flex justify-center items-center mt-8">
              <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <MessageSquare className="h-12 w-12 mx-auto mb-3 text-gray-400" />
              <p className="text-sm">No chat history yet</p>
              <p className="text-xs mt-1">Start a new conversation!</p>
            </div>
          ) : (
            <div className="space-y-2">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  onClick={() => {
                    onSelectSession(session.id)
                    onClose()
                  }}
                  className={clsx(
                    'group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors',
                    currentSessionId === session.id
                      ? 'bg-blue-50 border border-blue-200'
                      : 'hover:bg-gray-50 border border-transparent'
                  )}
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      <MessageSquare className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {session.title}
                      </h3>
                    </div>
                    <p className="text-xs text-gray-500">
                      {formatDate(session.updated_at)}
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDeleteSession(session.id, e)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity ml-2 p-1 text-gray-400 hover:text-red-600"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
