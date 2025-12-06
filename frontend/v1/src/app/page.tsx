'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { BarChart3, TrendingUp, Shield, Zap } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Skip auth and go directly to dashboard for testing
    router.push('/dashboard');
  }, [router]);

  // Show loading page while checking authentication
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="max-w-4xl mx-auto text-center px-4">
        <div className="mb-8">
          <div className="mx-auto h-20 w-20 bg-blue-500 rounded-full flex items-center justify-center mb-6">
            <BarChart3 className="h-10 w-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            ETF Analysis Dashboard
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Modern portfolio analysis and optimization platform
          </p>
        </div>

        {/* Loading while redirecting */}
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>

        {/* Features showcase while loading */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
          <div className="bg-white rounded-lg p-6 shadow-lg">
            <TrendingUp className="h-8 w-8 text-blue-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Portfolio Analytics
            </h3>
            <p className="text-gray-600 text-sm">
              Real-time portfolio performance and risk analysis
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-lg">
            <Shield className="h-8 w-8 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Secure API
            </h3>
            <p className="text-gray-600 text-sm">
              JWT authentication with FastAPI backend
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-lg">
            <Zap className="h-8 w-8 text-purple-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Modern Stack
            </h3>
            <p className="text-gray-600 text-sm">
              NextJS, TypeScript, Tailwind CSS
            </p>
          </div>
        </div>

        <div className="mt-8 text-sm text-gray-500">
          Phase 8: Modern Frontend Foundation
        </div>
      </div>
    </div>
  );
}
