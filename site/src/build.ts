/**
 * Generate the static site into `dist/`.
 *
 * Every page comes from the shipped knowledge package. Nothing is authored
 * here, so the site cannot drift from what SoulMap actually says: correcting a
 * page means correcting the doctrine or the skill it came from.
 */

import { cpSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
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

function writePage(relativePath: string, html: string): void {
  const target = join(DIST, relativePath);
  mkdirSync(dirname(target), { recursive: true });
  writeFileSync(target, html, "utf8");
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

  return { pages };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const { pages } = build();
  process.stdout.write(`built ${pages} pages into site/dist\n`);
}
