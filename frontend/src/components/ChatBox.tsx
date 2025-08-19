'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, RotateCcw } from 'lucide-react'
import MessageBubble from './MessageBubble'
import Loader from './Loader'
import { sendMessageStream } from '@/services/api'

interface Message {
  id: string
  text: string
  isBot: boolean
  timestamp: Date
}

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your RAG-powered assistant. I can stream responses token by token. What would you like to know?",
      isBot: true,
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText.trim(),
      isBot: false,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentQuery = inputText.trim()
    setInputText('')
    setIsLoading(true)

    const botMessageId = (Date.now() + 1).toString()
    setMessages(prev => [
      ...prev,
      { id: botMessageId, text: '', isBot: true, timestamp: new Date() }
    ])

    let firstTokenReceived = false // reset per message

    try {
      await sendMessageStream(currentQuery, (token: string) => {
        // Hide loader on first token
        if (!firstTokenReceived) {
          setIsLoading(false)
          firstTokenReceived = true
        }

        // Append token with a space for proper word spacing
        setMessages(prev =>
          prev.map(msg =>
            msg.id === botMessageId
              ? { ...msg, text: msg.text + token + " " }
              : msg
          )
        )
      })
    } catch (error) {
      console.error('Streaming error:', error)
      setMessages(prev =>
        prev.map(msg =>
          msg.id === botMessageId
            ? { ...msg, text: "⚠️ Error streaming response. Please try again." }
            : msg
        )
      )
    } finally {
      setIsLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([{
      id: '1',
      text: "Chat cleared! Ready to stream a fresh response.",
      isBot: true,
      timestamp: new Date()
    }])
  }

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-120px)] bg-white rounded-lg shadow-lg">
      {/* Chat Header */}
      <div className="flex justify-between items-center p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Chat with RAG Bot (Streaming)</h2>
        <button
          onClick={clearChat}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors"
          title="Clear chat"
        >
          <RotateCcw className="h-4 w-4" />
          <span className="text-sm">Clear</span>
        </button>
      </div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 chat-scrollbar">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message.text.trim()} // trim trailing spaces
            isBot={message.isBot}
            timestamp={message.timestamp}
          />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="message-bubble bot-message">
              <Loader />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type your message here..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-2 text-xs text-gray-500 text-center">
          Powered by Retrieval-Augmented Generation (Streaming)
        </div>
      </form>
    </div>
  )
}
