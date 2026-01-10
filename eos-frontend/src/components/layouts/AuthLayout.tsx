/**
 * EOS Platform - Auth Layout Component
 */
import { Outlet, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

export default function AuthLayout() {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  // Redirect to dashboard if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen flex flex-col justify-center bg-gradient-to-br from-primary-50 to-primary-100">
      {/* Background pattern */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-200 rounded-full opacity-30 blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-primary-300 rounded-full opacity-30 blur-3xl"></div>
      </div>

      <div className="relative z-10 sm:mx-auto sm:w-full sm:max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-600">EOS Platform</h1>
          <p className="mt-2 text-gray-600">Digital Marketing Campaign Management</p>
        </div>

        {/* Auth card */}
        <div className="bg-white py-8 px-6 shadow-xl rounded-2xl sm:px-10">
          <Outlet />
        </div>

        {/* Footer */}
        <p className="mt-6 text-center text-sm text-gray-500">
          &copy; {new Date().getFullYear()} True Digital Media. All rights reserved.
        </p>
      </div>
    </div>
  );
}
