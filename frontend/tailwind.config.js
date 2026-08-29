/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#071016",
        panel: "#101a22",
        line: "#22313b",
        mint: "#39d98a",
        cyan: "#4cc9f0",
        amber: "#f7b955",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(76,201,240,.18), 0 18px 70px rgba(0,0,0,.35)",
      },
    },
  },
  plugins: [],
};

