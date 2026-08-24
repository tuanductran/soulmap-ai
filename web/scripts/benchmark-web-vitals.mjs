// Atlas Nội Tâm: Benchmark chỉ đo lab metrics trên static preview; không suy diễn Core Web Vitals field data hay hiệu năng thiết bị thật.

import { spawn } from "node:child_process";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const basePath = "/soulmap-ai";
const port = Number(process.env.PERFORMANCE_PORT ?? "4174");
const runs = Number(process.env.PERFORMANCE_RUNS ?? "3");
const outputDir = process.env.PERFORMANCE_OUTPUT_DIR ?? "/tmp/soulmap-lighthouse";
const chromePath = process.env.CHROME_PATH ?? "/usr/bin/chromium";
const routes = [
  { id: "home-en", path: "/" },
  { id: "skills-en", path: "/skills" },
  { id: "faq-vi", path: "/vi/faq" },
];
const profiles = [
  { id: "mobile", flags: [] },
  { id: "desktop", flags: ["--preset=desktop"] },
];

function execute(command, args, { quiet = false, env = {} } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: webRoot,
      env: { ...process.env, ...env },
      stdio: quiet ? "ignore" : "inherit",
    });
    child.once("error", reject);
    child.once("exit", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${command} ${args.join(" ")} exited with ${code}`));
    });
  });
}

async function waitForPreview(url) {
  const deadline = Date.now() + 30_000;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) return;
    } catch {
      // The preview has not opened its listening socket yet.
    }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error(`Preview did not become ready at ${url}`);
}

function median(values) {
  const sorted = [...values].sort((left, right) => left - right);
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function round(value, digits = 0) {
  return Number(value.toFixed(digits));
}

function metricsFrom(report) {
  const audit = (id) => report.audits[id]?.numericValue ?? null;
  return {
    performance: round((report.categories.performance.score ?? 0) * 100),
    fcpMs: round(audit("first-contentful-paint")),
    lcpMs: round(audit("largest-contentful-paint")),
    tbtMs: round(audit("total-blocking-time")),
    cls: round(audit("cumulative-layout-shift"), 3),
    inpMs:
      audit("interaction-to-next-paint") === null
        ? null
        : round(audit("interaction-to-next-paint")),
    speedIndexMs: round(audit("speed-index")),
  };
}

function summarize(samples) {
  const numberKeys = ["performance", "fcpMs", "lcpMs", "tbtMs", "cls", "speedIndexMs"];
  const result = { samples: samples.length };
  for (const key of numberKeys) result[key] = median(samples.map((sample) => sample[key]));
  const inp = samples.map((sample) => sample.inpMs).filter((value) => value !== null);
  result.inpMs = inp.length ? median(inp) : null;
  return result;
}

async function runLighthouse(url, route, profile, run) {
  const prefix = `${route.id}-${profile.id}-${run}`;
  const destination = path.join(outputDir, `${prefix}.json`);
  await execute(
    "pnpm",
    [
      "exec",
      "lighthouse",
      url,
      "--only-categories=performance",
      "--throttling-method=simulate",
      "--output=json",
      `--output-path=${destination}`,
      "--quiet",
      "--disable-full-page-screenshot",
      "--chrome-flags=--headless --no-sandbox --disable-dev-shm-usage",
      ...profile.flags,
    ],
    { quiet: true, env: { CHROME_PATH: chromePath } },
  );
  return metricsFrom(JSON.parse(await readFile(destination, "utf8")));
}

await rm(outputDir, { recursive: true, force: true });
await mkdir(outputDir, { recursive: true });
await execute("pnpm", ["build"], { env: { SITE_BASE_PATH: `${basePath}/` } });

const preview = spawn(
  "pnpm",
  ["exec", "vite", "preview", "--host", "127.0.0.1", "--port", String(port), "--strictPort"],
  { cwd: webRoot, env: { ...process.env, SITE_BASE_PATH: `${basePath}/` }, stdio: "ignore" },
);

try {
  const origin = `http://127.0.0.1:${port}${basePath}`;
  await waitForPreview(`${origin}/`);
  const summary = [];
  for (const route of routes) {
    for (const profile of profiles) {
      const samples = [];
      for (let run = 1; run <= runs; run += 1) {
        const url = `${origin}${route.path}`;
        samples.push(await runLighthouse(url, route, profile, run));
      }
      summary.push({
        route: route.id,
        profile: profile.id,
        url: `${origin}${route.path}`,
        ...summarize(samples),
      });
    }
  }
  await writeFile(path.join(outputDir, "summary.json"), `${JSON.stringify(summary, null, 2)}\n`);
  console.table(summary);
  console.log(`Lighthouse lab reports: ${outputDir}`);
} finally {
  preview.kill("SIGTERM");
}
