import type { NextConfig } from "next";

const API = process.env.BHAVA_API_ORIGIN ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  transpilePackages: ["@bhava/ui"],
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: false },
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
