/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1890ff',
        success: '#52c41a',
        warning: '#faad14',
        error: '#f5222d',
      },
      boxShadow: {
        card: '0 2px 8px rgba(0, 0, 0, 0.09)',
      },
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false, // 禁用默认样式重置，与Ant Design兼容
  },
}
