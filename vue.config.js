// // vue.config.js
// module.exports = {
//     devServer: {
//       proxy: {
//         '/api': {
//           target: 'http://localhost:5000',  // Your Flask backend URL
//           changeOrigin: true,
//           pathRewrite: { '^/api': '' },  // Remove the /api prefix
//         },
//       },
//     },
//   };
// vue.config.js
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = {
  devServer: {
    '/api': {
      target: 'http://localhost:5000', // Replace with your Python backend URL
      changeOrigin: true,
      pathRewrite: {
        '^/api': '', // Remove the /api prefix when forwarding requests
      },
    },
  },
};

  