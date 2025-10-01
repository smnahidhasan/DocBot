// src/app/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, User } from '@/services/api';
import { LogOut, User as UserIcon, Mail, Calendar, Shield, MessageCircle, Edit } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [fullName, setFullName] = useState('');

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const userData = await api.me();
      setUser(userData);
      setFullName(userData.full_name);
    } catch (err) {
      router.push('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      router.push('/');
    } catch (err) {
      console.error('Logout failed', err);
    }
  };

  const handleUpdateProfile = async () => {
    if (!user) return;
    try {
      const updated = await api.updateUser(user.id, { full_name: fullName });
      setUser(updated);
      setEditing(false);
    } catch (err) {
      console.error('Update failed', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-primary-600">
            DocBot
          </Link>
          <button onClick={handleLogout} className="btn-secondary flex items-center space-x-2">
            <LogOut className="h-4 w-4" />
            <span>Logout</span>
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Profile Information</h2>
              {!editing && (
                <button onClick={() => setEditing(true)} className="btn-secondary flex items-center space-x-2">
                  <Edit className="h-4 w-4" />
                  <span>Edit</span>
                </button>
              )}
            </div>

            <div className="space-y-6">
              <div className="flex items-start space-x-3">
                <UserIcon className="h-5 w-5 text-gray-400 mt-1" />
                <div className="flex-1">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                  {editing ? (
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                    />
                  ) : (
                    <p className="text-gray-900">{user.full_name}</p>
                  )}
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Mail className="h-5 w-5 text-gray-400 mt-1" />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <p className="text-gray-900">{user.email}</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Shield className="h-5 w-5 text-gray-400 mt-1" />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                    {user.role}
                  </span>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <Calendar className="h-5 w-5 text-gray-400 mt-1" />
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Member Since</label>
                  <p className="text-gray-900">{new Date(user.created_at).toLocaleDateString()}</p>
                </div>
              </div>

              {editing && (
                <div className="flex space-x-3 pt-4">
                  <button onClick={handleUpdateProfile} className="btn-primary">
                    Save Changes
                  </button>
                  <button onClick={() => setEditing(false)} className="btn-secondary">
                    Cancel
                  </button>
                </div>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <Link href="/chat" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition">
                  <MessageCircle className="h-5 w-5 text-primary-600" />
                  <span className="text-gray-700">Start Chat</span>
                </Link>
                {(user.role === 'admin' || user.role === 'moderator') && (
                  <Link href="/users" className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 transition">
                    <UserIcon className="h-5 w-5 text-primary-600" />
                    <span className="text-gray-700">Manage Users</span>
                  </Link>
                )}
              </div>
            </div>

            <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-primary-900 mb-2">Account Status</h3>
              <p className="text-sm text-primary-700">
                {user.is_active ? '✓ Your account is active' : '⚠ Account inactive'}
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}