// src/app/page.tsx
'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { MessageCircle, Brain, Zap, Shield, LogIn, UserPlus, User } from 'lucide-react';
import { api } from '@/services/api';

export default function HomePage() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      await api.me();
      setIsAuthenticated(true);
    } catch (err) {
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      {/* Header */}
      <header className="py-6 px-4 sm:px-6 lg:px-8 bg-white shadow-sm">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <MessageCircle className="h-8 w-8 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">DocBot</h1>
          </div>
          <nav className="flex items-center space-x-4">
            <Link href="/about" className="text-gray-600 hover:text-primary-600 transition-colors font-medium">
              About
            </Link>
            {!loading && (
              <>
                {isAuthenticated ? (
                  <>
                    <Link href="/chat" className="text-gray-600 hover:text-primary-600 transition-colors font-medium">
                      Chat
                    </Link>
                    <Link href="/dashboard" className="btn-primary inline-flex items-center space-x-2">
                      <User className="h-4 w-4" />
                      <span>Dashboard</span>
                    </Link>
                  </>
                ) : (
                  <>
                    <Link href="/login" className="text-gray-600 hover:text-primary-600 transition-colors font-medium flex items-center space-x-1">
                      <LogIn className="h-4 w-4" />
                      <span>Login</span>
                    </Link>
                    <Link href="/register" className="btn-primary inline-flex items-center space-x-2">
                      <UserPlus className="h-4 w-4" />
                      <span>Sign Up</span>
                    </Link>
                  </>
                )}
              </>
            )}
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
            Access Health Insights
            <span className="text-primary-600 block mt-2">Powered by AI</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            DocBot provides preliminary health assessments by analyzing symptoms and medical images, offering accessible and secure health insights for everyone.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            {isAuthenticated ? (
              <>
                <Link href="/chat" className="btn-primary inline-flex items-center justify-center text-lg px-8 py-3">
                  <MessageCircle className="mr-2 h-5 w-5" />
                  Start Chatting
                </Link>
                <Link href="/dashboard" className="btn-secondary inline-flex items-center justify-center text-lg px-8 py-3">
                  <User className="mr-2 h-5 w-5" />
                  My Dashboard
                </Link>
              </>
            ) : (
              <>
                <Link href="/register" className="btn-primary inline-flex items-center justify-center text-lg px-8 py-3">
                  <UserPlus className="mr-2 h-5 w-5" />
                  Get Started Free
                </Link>
                <Link href="/about" className="btn-secondary inline-flex items-center justify-center text-lg px-8 py-3">
                  Learn More
                </Link>
              </>
            )}
          </div>
          {!isAuthenticated && (
            <p className="mt-4 text-sm text-gray-500">
              Already have an account?{' '}
              <Link href="/login" className="text-primary-600 hover:text-primary-700 font-medium">
                Sign in here
              </Link>
            </p>
          )}
        </div>

        {/* Features */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white rounded-xl shadow-sm p-8 text-center hover:shadow-md transition-shadow">
            <div className="bg-primary-100 rounded-full p-4 w-16 h-16 mx-auto mb-4">
              <Brain className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Smart Diagnostics</h3>
            <p className="text-gray-600">
              Advanced AI analyzes symptoms and medical images to provide preliminary disease suggestions.
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-8 text-center hover:shadow-md transition-shadow">
            <div className="bg-primary-100 rounded-full p-4 w-16 h-16 mx-auto mb-4">
              <Zap className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Instant Insights</h3>
            <p className="text-gray-600">
              Fast responses powered by optimized RAG and image classification systems.
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-8 text-center hover:shadow-md transition-shadow">
            <div className="bg-primary-100 rounded-full p-4 w-16 h-16 mx-auto mb-4">
              <Shield className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Secure & Private</h3>
            <p className="text-gray-600">
              Built with data privacy in mind, ensuring user information and medical data are protected.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        {!isAuthenticated && (
          <div className="mt-20 bg-primary-600 rounded-2xl p-12 text-center text-white">
            <h3 className="text-3xl font-bold mb-4">Ready to Get Started?</h3>
            <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
              Join DocBot today and get instant access to AI-powered health insights. No credit card required.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/register" className="bg-white text-primary-600 hover:bg-gray-100 font-medium py-3 px-8 rounded-lg transition-colors inline-flex items-center justify-center">
                <UserPlus className="mr-2 h-5 w-5" />
                Create Free Account
              </Link>
              <Link href="/login" className="bg-primary-700 hover:bg-primary-800 font-medium py-3 px-8 rounded-lg transition-colors inline-flex items-center justify-center">
                <LogIn className="mr-2 h-5 w-5" />
                Sign In
              </Link>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <MessageCircle className="h-6 w-6" />
                <span className="text-lg font-semibold">DocBot</span>
              </div>
              <p className="text-gray-400">
                Powered by advanced AI for accessible and secure preliminary health assessments.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
              <ul className="space-y-2">
                <li>
                  <Link href="/about" className="text-gray-400 hover:text-white transition-colors">
                    About Us
                  </Link>
                </li>
                <li>
                  <Link href="/chat" className="text-gray-400 hover:text-white transition-colors">
                    Chat
                  </Link>
                </li>
                {!isAuthenticated && (
                  <>
                    <li>
                      <Link href="/login" className="text-gray-400 hover:text-white transition-colors">
                        Login
                      </Link>
                    </li>
                    <li>
                      <Link href="/register" className="text-gray-400 hover:text-white transition-colors">
                        Sign Up
                      </Link>
                    </li>
                  </>
                )}
              </ul>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Legal</h4>
              <ul className="space-y-2">
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Privacy Policy
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Terms of Service
                  </a>
                </li>
                <li>
                  <a href="#" className="text-gray-400 hover:text-white transition-colors">
                    Disclaimer
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 DocBot. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}