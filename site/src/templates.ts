/**
 * Page templates.
 *
 * The layout keeps the reference site's structure: sticky header, centred
 * column, hero, card grid, footer. Copy is SoulMap's own and follows the
 * repository's language rules, which forbid guru certainty, support-bot
 * filler, and any promise the product does not make.
 */

import { marked } from "marked";
import type { Skill, SiteContent, SkillDocument } from "./content.js";

const REPO = "https://github.com/tuanductran/soulmap-ai";

/** Escape text for HTML interpolation. */
export function esc(value = ""): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/**
 * Render Markdown to HTML, resolving knowledge-base links to site routes.
 *
 * Links in the knowledge base are relative to the file that holds them, so the
 * same href means different things depending on where it appears. `SOULMAP.md`
 * links to `skills/meta/x.md` from the repository root, while a file inside
 * `skills/spiritual/` links to a sibling as plain `x.md`. Both are resolved
 * against the linking document's own directory first, then mapped once.
 *
 * A link that cannot become a page, such as one into `docs/`, is unwrapped to
 * its text rather than left pointing at nothing.
 *
 * @param body Markdown body with front matter removed.
 * @param baseDir Repository-relative directory of the linking document.
 */
export function renderMarkdown(body: string, baseDir = ""): string {
  const html = marked.parse(body, { async: false }) as string;
  return html.replace(
    /<a href="(?!https?:|#|mailto:)([^"]+)"[^>]*>(.*?)<\/a>/g,
    (_whole, href: string, text: string) => {
      const target = href.split("#")[0] ?? "";
      if (!target.endsWith(".md")) return text;
      const route = routeFor(resolveRepoPath(baseDir, target));
      return route ? `<a href="${route}">${text}</a>` : text;
    },
  );
}

/** Resolve a link target against the linking document's directory. */
function resolveRepoPath(baseDir: string, target: string): string {
  const segments = baseDir ? baseDir.split("/") : [];
  for (const part of target.split("/")) {
    if (part === "" || part === ".") continue;
    if (part === "..") segments.pop();
    else segments.push(part);
  }
  return segments.join("/");
}

/** Map a repository-relative Markdown path to its site route, if it has one. */
function routeFor(repoPath: string): string | null {
  if (repoPath === "SOULMAP.md") return "/doctrine/";
  if (repoPath === "SKILL.md") return "/";
  const match = /^skills\/([^/]+)\/(.+)\.md$/.exec(repoPath);
  if (!match) return null;
  const [, skill, document] = match;
  return document === "SKILL" ? `/skills/${skill}/` : `/skills/${skill}/${document}/`;
}

interface LayoutOptions {
  readonly title: string;
  readonly description: string;
  readonly body: string;
  readonly page: string;
  readonly version: string;
}

function layout({ title, description, body, page, version }: LayoutOptions): string {
  const nav = (href: string, id: string, label: string): string =>
    `<a href="${href}"${page === id ? ' aria-current="page"' : ""}>${label}</a>`;

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/styles.css">
</head>
<body class="page-${esc(page)}">
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="/">SoulMap<span> AI</span></a>
    <nav>
      ${nav("/", "home", "Overview")}
      ${nav("/skills/", "skills", "Skills")}
      ${nav("/doctrine/", "doctrine", "Doctrine")}
      <a href="${REPO}">GitHub</a>
    </nav>
  </div>
</header>
<main class="wrap">
${body}
</main>
<footer class="site-foot">
  <div class="wrap">
    <p>SoulMap is a reflective companion. It is not therapy, not a crisis service, and not a substitute for a person.</p>
    <p class="muted">Generated from the shipped knowledge package at version ${esc(version)}. Source: <a href="${REPO}">tuanductran/soulmap-ai</a>.</p>
  </div>
</footer>
</body>
</html>`;
}

/** The one notice that appears on every entry page. */
function safetyNotice(): string {
  return `<div class="notice">
  <h2>What this is not</h2>
  <p>SoulMap reflects, it does not decide. It does not diagnose, predict, or confirm who you are. If you are in crisis, contact a local support line. <a href="https://findahelpline.com">findahelpline.com</a> lists services by country.</p>
</div>`;
}

function skillCard(skill: Skill): string {
  return `<a class="card" href="/skills/${esc(skill.id)}/">
  <h3>${esc(skill.name)}</h3>
  <p>${esc(firstSentence(skill.description))}</p>
  <div class="meta">${skill.documents.length + 1} documents</div>
</a>`;
}

/** Return the first sentence, so a card stays a card. */
export function firstSentence(text = ""): string {
  const match = /^(.*?[.!?])(\s|$)/.exec(text.trim());
  return (match?.[1] ?? text.trim()).trim();
}

export function indexPage(content: SiteContent): string {
  const body = `<div class="hero">
  <span class="eyebrow">Version ${esc(content.version)}</span>
  <h1>A mirror, not a guide</h1>
  <p class="lede">SoulMap is a content-first reflective companion: a curated knowledge base of frameworks, safety rules, and voice guidance that helps people stop abandoning themselves.</p>
  <p>Every page here is generated from the same files the package ships, so what you read is what the product actually follows.</p>
</div>

<section>
  <h2>Skills</h2>
  <p class="section-note">Seven layers, each a directory of Markdown the assistant reads at request time.</p>
  <div class="cards">
    ${content.skills.map(skillCard).join("\n    ")}
  </div>
</section>

<section>
  <h2>How it works</h2>
  <p class="section-note">Markdown holds the knowledge. A small deterministic layer routes and enforces, and never writes the words.</p>
  <div class="cards">
    <div class="card"><h3>Knowledge first</h3><p>Frameworks, safety rules, and voice all live in Markdown. Changing behavior means editing content, not code.</p></div>
    <div class="card"><h3>Deterministic safety</h3><p>Crisis detection, scope classification, and response contracts are plain, auditable checks with no model in the loop.</p></div>
    <div class="card"><h3>Verified claims</h3><p>Doctrine rules are pinned by contract tests, so a promise on this page has a check behind it.</p></div>
  </div>
</section>

${safetyNotice()}`;

  return layout({
    title: "SoulMap AI",
    description:
      "A content-first reflective companion. Curated Markdown frameworks with a deterministic safety layer.",
    body,
    page: "home",
    version: content.version,
  });
}

export function skillsIndexPage(content: SiteContent): string {
  const body = `<div class="hero">
  <h1>Skills</h1>
  <p class="lede">Each skill is a directory with a manifest and its supporting documents. The manifest says when to reach for it.</p>
</div>

<section>
  <div class="cards">
    ${content.skills.map(skillCard).join("\n    ")}
  </div>
</section>`;

  return layout({
    title: "Skills - SoulMap AI",
    description: "The seven skill layers that make up the SoulMap knowledge package.",
    body,
    page: "skills",
    version: content.version,
  });
}

export function skillPage(skill: Skill, content: SiteContent): string {
  const documents = skill.documents
    .map(
      (doc) => `<li><a href="/skills/${esc(doc.slug)}/">
      <span class="name">${esc(doc.name)}</span>
      <span class="desc">${esc(firstSentence(doc.description))}</span>
    </a></li>`,
    )
    .join("\n    ");

  const body = `<div class="hero">
  <span class="eyebrow">Skill</span>
  <h1>${esc(skill.name)}</h1>
  <p class="lede">${esc(skill.description)}</p>
  <p><span class="badge">v${esc(skill.version)}</span></p>
</div>

<section class="prose">
  ${renderMarkdown(skill.manifest.body, `skills/${skill.id}`)}
</section>

${
  skill.documents.length > 0
    ? `<section>
  <h2>Documents</h2>
  <p class="section-note">${skill.documents.length} supporting files in this skill.</p>
  <ul class="doc-list">
    ${documents}
  </ul>
</section>`
    : ""
}

<p class="breadcrumb"><a href="/skills/">All skills</a></p>`;

  return layout({
    title: `${skill.name} - SoulMap AI`,
    description: firstSentence(skill.description),
    body,
    page: "skills",
    version: content.version,
  });
}

export function documentPage(doc: SkillDocument, content: SiteContent): string {
  const parent = doc.slug.split("/")[0] ?? "";
  const body = `<div class="hero">
  <span class="eyebrow">${esc(parent)}</span>
  <h1>${esc(doc.name)}</h1>
  ${doc.description ? `<p class="lede">${esc(doc.description)}</p>` : ""}
</div>

<section class="prose">
  ${renderMarkdown(doc.body, `skills/${parent}`)}
</section>

<p class="breadcrumb"><a href="/skills/${esc(parent)}/">Back to ${esc(parent)}</a></p>`;

  return layout({
    title: `${doc.name} - SoulMap AI`,
    description: firstSentence(doc.description) || `${doc.name}, part of the SoulMap knowledge package.`,
    body,
    page: "skills",
    version: content.version,
  });
}

export function doctrinePage(content: SiteContent): string {
  const body = `<div class="hero">
  <span class="eyebrow">Doctrine</span>
  <h1>SOULMAP.md</h1>
  <p class="lede">The baseline doctrine and safety contract. It ships with every package and stands on its own there.</p>
</div>

<section class="prose">
  ${renderMarkdown(content.doctrine.body)}
</section>`;

  return layout({
    title: "Doctrine - SoulMap AI",
    description: "The SoulMap doctrine and non-negotiable safety rules.",
    body,
    page: "doctrine",
    version: content.version,
  });
}

export function notFoundPage(content: SiteContent): string {
  return layout({
    title: "Not found - SoulMap AI",
    description: "That page does not exist.",
    body: `<div class="hero">
  <h1>Not found</h1>
  <p class="lede">That page does not exist. The <a href="/skills/">skills index</a> lists everything the package publishes.</p>
</div>`,
    page: "404",
    version: content.version,
  });
}
