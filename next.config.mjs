/** @type {import('next').NextConfig} */
const nextConfig = {};
/*module.exports = {
    webpack: (config, { isServer }) => {
      if (!isServer) {
        // Fixes npm packages that depend on `fs`, `net`, or `tls` modules in client side
        config.resolve.fallback = {
          fs: false,
          net: false,
          tls: false,
          tty: false,
        };
      }
      return config;
    },
  };*/
export default nextConfig;
