/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#05050a",
                surface: "#0f111a",
                primary: "#00f2ff", // Neon Cyan
                secondary: "#ff0055", // Neon Red
                accent: "#7000ff", // Neon Purple
                success: "#00ff9d",
                warning: "#ffb800",
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
                display: ['Orbitron', 'sans-serif'],
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
            },
            keyframes: {
                glow: {
                    '0%': { boxShadow: '0 0 5px #00f2ff20' },
                    '100%': { boxShadow: '0 0 20px #00f2ff60, 0 0 10px #00f2ff' },
                }
            }
        },
    },
    plugins: [],
}
