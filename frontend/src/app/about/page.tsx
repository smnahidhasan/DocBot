import Link from 'next/link'
import { ArrowLeft, MessageCircle, Database, Cpu, Search } from 'lucide-react'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors"
          >
            <ArrowLeft className="h-5 w-5" />
            <span>Back to Home</span>
          </Link>
          <h1 className="text-xl font-semibold text-gray-900">About DocBot</h1>
          <div className="w-24"></div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Introduction */}
        <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <div className="flex items-center space-x-3 mb-6">
            <MessageCircle className="h-8 w-8 text-primary-600" />
            <h2 className="text-3xl font-bold text-gray-900">What is DocBot?</h2>
          </div>
          <p className="text-lg text-gray-700 leading-relaxed mb-6">
            DocBot is an AI-driven health assistance platform designed to enhance healthcare accessibility. Powered by advanced artificial intelligence, it allows users to interact with a chatbot for preliminary symptom-based disease suggestions and upload medical images for analysis. DocBot aims to provide accessible, preliminary medical assessments for individuals with limited access to healthcare services, ensuring data privacy and a user-friendly experience.
          </p>
          <div className="bg-primary-50 border-l-4 border-primary-600 p-6 rounded-r-lg">
            <p className="text-primary-800 font-medium">
              DocBot empowers users with preliminary health insights, leveraging AI to bridge gaps in healthcare access while prioritizing data security.
            </p>
          </div>
        </div>

        {/* How it Works */}
        <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full p-4 w-16 h-16 mx-auto mb-4">
                <Search className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">1. Symptom Analysis</h3>
              <p className="text-gray-600">
                Users describe symptoms via the chatbot, which uses a Retrieval-Augmented Generation (RAG) system to analyze and retrieve relevant medical information.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-4">
                <Database className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">2. Image Processing</h3>
              <p className="text-gray-600">
                Users can upload medical images, which are analyzed by an open-source image classification model to identify potential diseases.
              </p>
            </div>
            <div className="text-center">
              <div className="bg-purple-100 rounded-full p-4 w-16 h-16 mx-auto mb-4">
                <Cpu className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">3. Health Insights</h3>
              <p className="text-gray-600">
                DocBot synthesizes symptom and image data to provide preliminary disease suggestions, securely stored for user reference.
              </p>
            </div>
          </div>
        </div>

        {/* Use Cases */}
        <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Use Cases</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start space-x-3">
              <div className="bg-primary-100 rounded-lg p-2 mt-1">
                <MessageCircle className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Symptom-Based Guidance</h3>
                <p className="text-gray-600">
                  Users can describe symptoms like fever or rash, and DocBot provides preliminary disease suggestions using its RAG-based chatbot.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="bg-primary-100 rounded-lg p-2 mt-1">
                <Search className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Medical Image Analysis</h3>
                <p className="text-gray-600">
                  Upload images of skin conditions or other visual symptoms, and DocBot’s image classification model identifies potential diseases.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="bg-primary-100 rounded-lg p-2 mt-1">
                <Database className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Accessible Health Insights</h3>
                <p className="text-gray-600">
                  DocBot supports users in remote areas by offering preliminary health assessments, helping them decide when to seek professional care.
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="bg-primary-100 rounded-lg p-2 mt-1">
                <Cpu className="h-5 w-5 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">Secure Health Tracking</h3>
                <p className="text-gray-600">
                  Store chat histories and image metadata securely, allowing users to track their health concerns over time.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Disclaimer</h2>
          <p className="text-gray-600 leading-relaxed">
            DocBot provides preliminary health assessments and is not a substitute for professional medical advice. The platform uses AI to suggest potential diseases based on symptoms and images, but results may not always be accurate. Users should consult a healthcare professional for definitive diagnoses and cross-check all information provided by DocBot.
          </p>
        </div>

        {/* CTA */}
        <div className="text-center mt-8">
          <Link href="/chat" className="btn-primary inline-flex items-center text-lg px-8 py-3">
            <MessageCircle className="mr-2 h-5 w-5" />
            Try DocBot Now
          </Link>
        </div>
      </main>
    </div>
  )
}
