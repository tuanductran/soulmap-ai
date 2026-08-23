// Atlas Nội Tâm: Static generator phát hành raw bundle đã sanitize từ canonical skills, giữ GitHub Pages không cần Python web server.
import { cp, mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(webRoot, "..");
const distRoot = path.join(webRoot, "dist");
const catalog = JSON.parse(await readFile(path.join(webRoot, "content/catalog_data.json"), "utf8"));
const prompts = JSON.parse(await readFile(path.join(webRoot, "content/prompt_data.json"), "utf8"));
const siteUrl = "https://tuanductran.github.io/soulmap-ai";

function sanitize(markdown, labels) {
  return markdown
    .replace(/\[([^\]]+)\]\((?:\.\.\/)+AGENTS\.md\)/g, "$1")
    .replace(/\[AGENTS\.md\]\([^)]*\)/g, labels.behavioral_contract)
    .replaceAll("AGENTS.md", labels.behavioral_contract)
    .replace(/(?<!\w)(?:\.claude\/|\.github\/|src\/|tests\/|pyproject\.toml|uv\.lock)(?:[A-Za-z0-9_./-]*)/g, labels.repository_internals);
}

async function rawMarkdown(entry, locale) {
  const labels = { ...catalog.raw_copy.en, ...catalog.raw_copy[locale] };
  const fields = entry.locales[locale] || entry.locales.en;
  const skillsDir = path.join(repoRoot, "skills", entry.directory);
  let names = [];
  try { names = (await readdir(skillsDir)).filter((name) => name.endsWith(".md")).sort(); } catch { /* missing source renders a clear bundle message */ }
  const parts = [`# ${labels.bundle_title}: ${fields.title}\n\n`, `> ${labels.canonical_bundle} \`${entry.slug}\`.\n\n`];
  if (!names.length) return `${parts.join("")}${labels.unavailable}\n`;
  for (const name of names) {
    parts.push(`\n---\n\n## ${name}\n\n`, sanitize(await readFile(path.join(skillsDir, name), "utf8"), labels), "\n");
  }
  const scenarios = prompts.packs?.[entry.slug]?.scenarios ?? [];
  if (scenarios.length) {
    const prefix = locale === "en" ? "" : `/${locale}`;
    const source = `${siteUrl}${prefix}/api/raw/${entry.slug}.md`;
    parts.push(`\n---\n\n## ${labels.suggested_prompts}\n\n${labels.use_one}\n\n`);
    for (const scenario of scenarios) {
      const copy = scenario.locales?.[locale] ?? scenario.locales?.en;
      if (!copy) continue;
      parts.push(`### ${copy.title}\n\n**${labels.when}:** ${copy.when}\n\n**${labels.prompt}:** ${copy.prompt}\n\n**${labels.source_bundle}:** ${source}\n\n**${labels.starter_question}:** ${copy.question}\n\n`);
    }
  }
  return parts.join("");
}

for (const locale of ["en", "vi", "ko"]) {
  const prefix = locale === "en" ? "" : locale;
  const target = path.join(distRoot, prefix, "api", "raw");
  await mkdir(target, { recursive: true });
  for (const entry of catalog.entries) await writeFile(path.join(target, `${entry.slug}.md`), await rawMarkdown(entry, locale), "utf8");
}

await cp(path.join(distRoot, "index.html"), path.join(distRoot, "404.html"));
