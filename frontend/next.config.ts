import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: 'standalone',
};

// Only add PWA in production builds
if (process.env.NODE_ENV === 'production') {
  try {
    const withPWA = require('next-pwa')({
      dest: 'public',
      disable: false,
      register: true,
      skipWaiting: true,
    });
    module.exports = withPWA(nextConfig);
  } catch (e) {
    console.log('PWA not available, continuing without it');
    module.exports = nextConfig;
  }
} else {
  module.exports = nextConfig;
}
