import path from "node:path";
import type { NextConfig } from "next";

function apiOrigin(): string {
  if (process.env.BHAVA_API_ORIGIN?.trim()) {
    return process.env.BHAVA_API_ORIGIN.trim().replace(/\/$/, "");
  }
  const url = process.env.BHAVA_API_URL?.trim();
  if (url) return url.replace(/\/api\/v1\/?$/, "").replace(/\/$/, "");
  return "http://127.0.0.1:8000";
}

const API = apiOrigin();

const nextConfig: NextConfig = {
  output: "standalone",
  outputFileTracingRoot: path.resolve(process.cwd(), "../.."),
  poweredByHeader: false,
  productionBrowserSourceMaps: false,
  transpilePackages: ["@bhava/ui"],
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: false },
  webpack: (config) => {
    // pdfjs-dist optional Node canvas binding is unused in the browser viewer.
    config.resolve.alias = {
      ...config.resolve.alias,
      canvas: false,
    };
    return config;
  },
  async redirects() {
    return [
      { source: "/vanani", destination: "/prabhupada-vani", permanent: true },
      { source: "/vani", destination: "/prabhupada-vani", permanent: true },
      { source: "/blog", destination: "/knowledge", permanent: true },
      { source: "/blog/:path*", destination: "/knowledge/:path*", permanent: true },
    ];
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
