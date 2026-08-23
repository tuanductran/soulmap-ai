// Atlas Nội Tâm: Vite chỉ build static SPA; GitHub Pages base path được truyền rõ từ workflow, không suy luận runtime backend.
import { fileURLToPath, URL } from "node:url";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  base: process.env.SITE_BASE_PATH || "/",
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          "react-runtime": ["react", "react-dom"],
          "router-runtime": ["@tanstack/react-router"],
          "i18n-runtime": ["i18next", "react-i18next"],
          icons: ["lucide-react"],
        },
      },
    },
  },
});
