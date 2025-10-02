'use client'

import { useState } from 'react'
import ChatBox from '@/components/ChatBox'
import ChatSidebar from '@/components/ChatSidebar'
import Link from 'next/link'
import { ArrowLeft, Menu } from 'lucide-react'

export default function ChatPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)

  const handleNewChat = () => {
    setCurrentSessionId(null)
  }

  const handleSelectSession = (sessionId: string) => {
    setCurrentSessionId(sessionId)
  }

  const handleSessionUpdate = () => {
    // This will trigger sidebar to refresh its session list
    setIsSidebarOpen(false)
    setTimeout(() => setIsSidebarOpen(true), 100)
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Sidebar */}
      <ChatSidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        currentSessionId={currentSessionId}
        onNewChat={handleNewChat}
        onSelectSession={handleSelectSession}
      />

      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Open chat history"
            >
              <Menu className="h-5 w-5" />
            </button>
            <Link
              href="/"
              className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
            >
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Home</span>
            </Link>
          </div>
          <h1 className="text-xl font-semibold text-gray-900">DocBot AI</h1>
          <div className="w-32"></div> {/* Spacer for centering */}
        </div>
      </header>

      {/* Chat Interface */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 max-w-4xl mx-auto w-full px-4 py-6">
          <ChatBox
            sessionId={currentSessionId}
            onSessionUpdate={handleSessionUpdate}
          />
        </div>
      </main>
    </div>
  )
}
