import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  timeout: 120_000,
  expect: { timeout: 5_000 },
  // Three browser engines are intentionally audited serially to keep the small
  // static-site regression suite stable on constrained CI runners.
  workers: 1,
  use: { baseURL: "http://127.0.0.1:4173/soulmap-ai/", trace: "retain-on-failure", screenshot: "only-on-failure" },
  webServer: { command: "SITE_BASE_PATH=/soulmap-ai/ pnpm build && SITE_BASE_PATH=/soulmap-ai/ pnpm vite preview --host 127.0.0.1 --port 4173", port: 4173, reuseExistingServer: !process.env.CI },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "mobile", use: { ...devices["iPhone 13"] } },
  ],
});
