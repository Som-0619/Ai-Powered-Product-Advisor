/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const backendUrl =
      process.env.INTERNAL_API_URL ||
      (process.env.HOSTNAME === "0.0.0.0"
        ? "http://backend:8000"
        : process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");

    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
