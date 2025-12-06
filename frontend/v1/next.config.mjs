/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable experimental features
  experimental: {
    // Enable React compiler if needed
  },
  
  // Turbopack configuration for Base UI optimization (Next.js 16+)
  turbopack: {
    // Enable tree-shaking for Base UI components
    resolveAlias: {
      '@base-ui-components/react': '@base-ui-components/react',
    },
  },
  
  // Optimize bundle size for Base UI
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // API rewrites for development
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*', // FastAPI backend
      },
    ];
  },
  
  // Environment variables
  env: {
    API_BASE_URL: process.env.NODE_ENV === 'production' 
      ? 'https://your-api-domain.com' 
      : 'http://localhost:8000',
  },
};

export default nextConfig;