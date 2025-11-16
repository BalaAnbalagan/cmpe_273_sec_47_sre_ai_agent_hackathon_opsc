import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL_AZ1: process.env.NEXT_PUBLIC_API_URL_AZ1 || 'https://sre-backend-az1.azurewebsites.net',
    NEXT_PUBLIC_API_URL_AZ2: process.env.NEXT_PUBLIC_API_URL_AZ2 || 'https://sre-backend-az2.azurewebsites.net',
  },
};

export default nextConfig;
