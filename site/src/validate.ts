/**
 * Check the generated site before it is published.
 *
 * The build is only half the guarantee. This inspects what actually landed in
 * `dist/`, because that is what a visitor sees. Two classes of failure matter:
 *
 * - internal content leaking into a public page, which the content layer is
 *   built to prevent but should not be the only thing preventing
 * - an internal link that resolves to nothing, which turns the knowledge base
 *   into a maze of dead ends
 */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const SITE_DIR = dirname(dirname(fileURLToPath(import.meta.url)));
const DIST = join(SITE_DIR, "dist");

/** Paths that must never appear as a link target in a published page. */
const INTERNAL_LINK_ROOTS = [
  "/docs/",
  "/templates/",
  "/.claude",
  "/.github/",
  "/tests/",
  "/scripts/",
  "/src/",
  "/evals/",
  "/library/",
];

function htmlFilesIn(directory: string): string[] {
  const found: string[] = [];
  for (const entry of readdirSync(directory)) {
    const full = join(directory, entry);
    if (statSync(full).isDirectory()) {
      found.push(...htmlFilesIn(full));
    } else if (entry.endsWith(".html")) {
      found.push(full);
    }
  }
  return found;
}

function main(): number {
  const pages = htmlFilesIn(DIST);
  const problems: string[] = [];

  if (pages.length === 0) {
    process.stderr.write("no pages found in dist, did the build run?\n");
    return 1;
  }

  // Every internal href a page offers, so both checks read the same set.
  const routes = new Set(
    pages.map((page) => {
      const rel = relative(DIST, page).split("\\").join("/");
      return "/" + rel.replace(/index\.html$/, "").replace(/\.html$/, "");
    }),
  );

  for (const page of pages) {
    const rel = relative(DIST, page);
    const html = readFileSync(page, "utf8");

    for (const root of INTERNAL_LINK_ROOTS) {
      if (html.includes(`href="${root}`)) {
        problems.push(`${rel}: links to internal path ${root}`);
      }
    }

    for (const [, href] of html.matchAll(/href="(\/[^"#]*)"/g)) {
      if (href === undefined) continue;
      if (href.endsWith(".css") || href.endsWith(".js")) continue;
      const normalised = href.endsWith("/") ? href : `${href}/`;
      if (!routes.has(href) && !routes.has(normalised)) {
        problems.push(`${rel}: dead internal link ${href}`);
      }
    }
  }

  if (problems.length > 0) {
    for (const problem of problems) process.stderr.write(`${problem}\n`);
    process.stderr.write(`\n${problems.length} problem(s) in the generated site.\n`);
    return 1;
  }

  process.stdout.write(`validated ${pages.length} pages, no internal leaks or dead links\n`);
  return 0;
}

process.exit(main());
