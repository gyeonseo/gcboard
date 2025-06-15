const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  console.log("🔥 setupProxy.js loaded");

  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      pathRewrite: {
        '^/api': '/api'  // ✅ 패턴 기반으로 명시적으로 다시 써줘야 유지됨
      }
    })
  );
};