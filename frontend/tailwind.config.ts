import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#f0f4ff",
          100: "#dbe4ff",
          200: "#bac8ff",
          300: "#91a7ff",
          400: "#748ffc",
          500: "#5c7cfa",
          600: "#4c6ef5",
          700: "#4263eb",
          800: "#3b5bdb",
          900: "#364fc7",
        },
        spirit: {
          50: "#f8f6f3",
          100: "#ede8e0",
          200: "#d9cfc2",
          300: "#c2b09c",
          400: "#a98f78",
          500: "#967a64",
          600: "#816455",
          700: "#6a5148",
          800: "#59443f",
          900: "#4d3b38",
        },
      },
    },
  },
  plugins: [],
};

export default config;
