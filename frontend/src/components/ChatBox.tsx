'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, RotateCcw, Image as ImageIcon, X } from 'lucide-react'
import MessageBubble from './MessageBubble'
import Loader from './Loader'
import { sendMessageStream } from '@/services/api'

interface Message {
  id: string
  text: string
  isBot: boolean
  timestamp: Date
  image?: string // base64 or URL
}

export default function ChatBox() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm DocBot, your AI-driven health assistant. I can analyze symptoms and medical images to provide preliminary health assessments. Describe your symptoms or upload an image to get started!",
      isBot: true,
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      setImageFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setSelectedImage(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const clearImage = () => {
    setSelectedImage(null)
    setImageFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if ((!inputText.trim() && !selectedImage) || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText.trim() || 'Uploaded an image',
      isBot: false,
      timestamp: new Date(),
      image: selectedImage || undefined
    }

    setMessages(prev => [...prev, userMessage])
    const currentQuery = inputText.trim()
    const currentImage = imageFile  // Capture before clearing

    // Clear input and image
    setInputText('')
    clearImage()
    setIsLoading(true)

    // Debug log
    console.log('Submitting with image:', currentImage ? 'YES' : 'NO')
    console.log('Image file:', currentImage)

    const botMessageId = (Date.now() + 1).toString()
    setMessages(prev => [
      ...prev,
      { id: botMessageId, text: '', isBot: true, timestamp: new Date() }
    ])

    let firstTokenReceived = false

    try {
      // Pass the image file to the API
      await sendMessageStream(
        currentQuery || 'Analyze this image',
        (token: string) => {
          if (!firstTokenReceived) {
            setIsLoading(false)
            firstTokenReceived = true
          }

          setMessages(prev =>
            prev.map(msg =>
              msg.id === botMessageId
                ? { ...msg, text: msg.text + token + " " }
                : msg
            )
          )
        },
        currentImage // Pass the image file
      )
    } catch (error) {
      console.error('Streaming error:', error)
      setMessages(prev =>
        prev.map(msg =>
          msg.id === botMessageId
            ? { ...msg, text: "⚠️ Error processing health query. Please try again." }
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
      text: "Chat cleared! Ready to analyze your symptoms or medical images for preliminary health assessments.",
      isBot: true,
      timestamp: new Date()
    }])
    clearImage()
  }

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-120px)] bg-white rounded-lg shadow-lg">
      {/* Chat Header */}
      <div className="flex justify-between items-center p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Chat with DocBot</h2>
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
            message={message.text.trim()}
            isBot={message.isBot}
            timestamp={message.timestamp}
            image={message.image}
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
        {/* Image Preview */}
        {selectedImage && (
          <div className="mb-3 relative inline-block">
            <img
              src={selectedImage}
              alt="Selected"
              className="max-h-32 rounded-lg border border-gray-300"
            />
            <button
              type="button"
              onClick={clearImage}
              className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        <div className="flex space-x-2">
          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
          />

          {/* Image Upload Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            title="Upload image"
          >
            <ImageIcon className="h-5 w-5 text-gray-600" />
          </button>

          {/* Text Input */}
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Describe your symptoms or ask a health question..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={isLoading}
          />

          {/* Send Button */}
          <button
            type="submit"
            disabled={(!inputText.trim() && !selectedImage) || isLoading}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-2 text-xs text-gray-500 text-center">
          Powered by DocBot for preliminary health assessments
        </div>
      </form>
    </div>
  )
}
