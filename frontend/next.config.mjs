/** @type {import('next').NextConfig} */
const nextConfig = {
    output: "standalone",
    swcMinify: true,
    reactStrictMode: true,
    experimental: {
        optimizePackageImports: ["recharts", "lucide-react"],
    },
    async rewrites() {
        return [
            {
                source: "/api/:path*",
                destination: "http://localhost:8000/api/:path*",
            },
        ];
    },
};

export default nextConfig;
