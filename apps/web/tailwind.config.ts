import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202A",
        line: "#D8DEE8",
        panel: "#F7F9FC",
        brand: "#0E7C86",
        accent: "#E36B2C",
        ok: "#1E8A5A",
        warn: "#B7791F",
        danger: "#C2413D"
      }
    }
  },
  plugins: []
} satisfies Config;
