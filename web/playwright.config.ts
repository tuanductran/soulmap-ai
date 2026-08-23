import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  retries: 1,
  use: { baseURL: "http://127.0.0.1:4173/soulmap-ai/", trace: "retain-on-failure", screenshot: "only-on-failure" },
  webServer: { command: "SITE_BASE_PATH=/soulmap-ai/ pnpm vite preview --host 127.0.0.1 --port 4173", port: 4173, reuseExistingServer: !process.env.CI },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }, { name: "mobile", use: { ...devices["iPhone 13"] } }],
});
