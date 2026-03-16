/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    black: "#000000",
                    gold: "#D4AF37",
                    dark: "#1A1A1A",
                }
            },
            fontFamily: {
                mono: ['"JetBrains Mono"', 'monospace'],
            }
        },
    },
    plugins: [],
}
