/**
 * Generate the static site into `dist/`.
 *
 * Every page comes from the shipped knowledge package. Nothing is authored
 * here, so the site cannot drift from what SoulMap actually says: correcting a
 * page means correcting the doctrine or the skill it came from.
 */

import { cpSync, mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

import { loadContent } from "./content.js";
import {
  doctrinePage,
  documentPage,
  indexPage,
  notFoundPage,
  skillPage,
  skillsIndexPage,
} from "./templates.js";

const SITE_DIR = dirname(dirname(fileURLToPath(import.meta.url)));
const REPO_ROOT = dirname(SITE_DIR);
const DIST = join(SITE_DIR, "dist");
const DEFAULT_ORIGIN = "https://tuanductran.github.io";

function basePath(): string {
  const value = process.env["SOULMAP_BASE_PATH"]?.trim() || "/";
  return `/${value.replace(/^\/+|\/+$/g, "")}/`.replace(/^\/\/+/g, "/");
}

function origin(): string {
  return (process.env["SOULMAP_SITE_ORIGIN"]?.trim() || DEFAULT_ORIGIN).replace(/\/+$/, "");
}

function routeForFile(file: string): string {
  const rel = relative(DIST, file).split("\\").join("/");
  if (rel === "index.html") return "/";
  return `/${rel.replace(/\/index\.html$/, "")}/`;
}

function htmlFilesIn(directory: string): string[] {
  const found: string[] = [];
  for (const entry of readdirSync(directory)) {
    const full = join(directory, entry);
    if (statSync(full).isDirectory()) found.push(...htmlFilesIn(full));
    else if (entry.endsWith(".html")) found.push(full);
  }
  return found.sort();
}

function xml(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;");
}

function writePage(relativePath: string, html: string): void {
  const target = join(DIST, relativePath);
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, html, "utf8");
}

function finalisePublicMetadata(): void {
  const root = basePath();
  const siteOrigin = origin();
  const imageUrl = `${siteOrigin}${root}og-image.svg`;
  const pages = htmlFilesIn(DIST);

  for (const file of pages) {
    const route = routeForFile(file);
    const canonical = `${siteOrigin}${root.replace(/\/$/, "")}${route}`.replace(/([^:]\/)\/{2,}/g, "$1");
    let html = readFileSync(file, "utf8");

    html = html.replace(/href="\//g, `href="${root}`);
    html = html.replace(/src="\//g, `src="${root}`);
    html = html.replace(
      "</head>",
      `  <link rel="icon" href="${root}favicon.svg" type="image/svg+xml">\n` +
        `  <link rel="canonical" href="${canonical}">\n` +
        `  <meta property="og:url" content="${canonical}">\n` +
        `  <meta property="og:image" content="${imageUrl}">\n` +
        "</head>",
    );

    writeFileSync(file, html, "utf8");
  }

  const sitemap = pages
    .filter((file) => !file.endsWith("/404.html") && !file.endsWith("\\404.html"))
    .map((file) => `  <url><loc>${xml(`${siteOrigin}${root.replace(/\/$/, "")}${routeForFile(file)}`)}</loc></url>`)
    .join("\n");
  writeFileSync(
    join(DIST, "sitemap.xml"),
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sitemap}\n</urlset>\n`,
    "utf8",
  );
  writeFileSync(join(DIST, "robots.txt"), `User-agent: *\nAllow: /\n\nSitemap: ${siteOrigin}${root}sitemap.xml\n`, "utf8");
  writeFileSync(
    join(DIST, "favicon.svg"),
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#3f6f5e"/><path d="M18 21h28v6H18zm0 10h28v6H18zm0 10h18v6H18z" fill="#fff"/></svg>\n`,
    "utf8",
  );
  writeFileSync(
    join(DIST, "og-image.svg"),
    `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="#fcfcfa"/><rect x="72" y="72" width="1056" height="486" rx="28" fill="#fff" stroke="#e6e3dc"/><text x="120" y="270" fill="#1c1b19" font-family="system-ui,sans-serif" font-size="72" font-weight="600">SoulMap AI</text><text x="120" y="350" fill="#4b4945" font-family="system-ui,sans-serif" font-size="34">A mirror, not a guide.</text><rect x="120" y="410" width="120" height="8" rx="4" fill="#3f6f5e"/></svg>\n`,
    "utf8",
  );
}

export function build(): { pages: number } {
  rmSync(DIST, { recursive: true, force: true });
  mkdirSync(DIST, { recursive: true });

  const content = loadContent(REPO_ROOT);
  let pages = 0;

  writePage("index.html", indexPage(content));
  pages += 1;

  writePage("skills/index.html", skillsIndexPage(content));
  pages += 1;

  writePage("doctrine/index.html", doctrinePage(content));
  pages += 1;

  for (const skill of content.skills) {
    writePage(join("skills", skill.id, "index.html"), skillPage(skill, content));
    pages += 1;
    for (const doc of skill.documents) {
      writePage(join("skills", doc.slug, "index.html"), documentPage(doc, content));
      pages += 1;
    }
  }

  writePage("404.html", notFoundPage(content));
  pages += 1;

  cpSync(join(SITE_DIR, "src", "styles.css"), join(DIST, "styles.css"));
  finalisePublicMetadata();

  return { pages };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const { pages } = build();
  process.stdout.write(`built ${pages} pages into site/dist\n`);
}
