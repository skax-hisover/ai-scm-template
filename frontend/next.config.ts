import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Docker 배포 시 standalone 모드로 빌드 (server.js 단독 실행 가능)
  output: "standalone",
  // 백엔드 API 프록시 (CORS 문제 방지)
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },
  // 환경 변수
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};

export default nextConfig;
