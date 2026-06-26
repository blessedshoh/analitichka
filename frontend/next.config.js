/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Static export so the single-container deploy can serve the UI straight
  // from FastAPI. Set BUILD_STATIC=1 in the deploy build; local dev/build
  // (two services) is unaffected.
  ...(process.env.BUILD_STATIC ? { output: "export", images: { unoptimized: true } } : {}),
};
module.exports = nextConfig;
