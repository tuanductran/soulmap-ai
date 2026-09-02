/**
 * Read SoulMap content for the public site.
 *
 * The site publishes the shipped knowledge package and nothing else. That set
 * is the root `SKILL.md`, `SOULMAP.md`, and everything under `skills/`, which
 * is exactly what the Python packager puts in the distribution archives.
 * `docs/`, `templates/`, `.claude/`, `tests/`, `scripts/`, and `src/` are
 * repository-only and must never reach a public page.
 *
 * The boundary is enforced here rather than trusted to the templates: every
 * document this module returns has already been checked against the allowed
 * roots, so a page cannot render something the packager would not ship.
 */

import { readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative, sep } from "node:path";
import matter from "gray-matter";

/** Directories and files the site is allowed to publish. */
const PUBLISHABLE_ROOTS = ["skills"] as const;
const PUBLISHABLE_FILES = ["SKILL.md", "SOULMAP.md"] as const;

/** Repository-only paths. Present for an explicit check, not just omission. */
const INTERNAL_ROOTS = [
  "docs",
  "templates",
  ".claude",
  ".claude-plugin",
  ".github",
  "tests",
  "scripts",
  "src",
  "library",
  "evals",
  "dist",
] as const;

export interface SkillDocument {
  /** Repository-relative POSIX path, for example `skills/safety/SKILL.md`. */
  readonly path: string;
  /** URL slug, for example `safety/boundaries-safety`. */
  readonly slug: string;
  /** Front-matter `name`. */
  readonly name: string;
  /** Front-matter `description`. */
  readonly description: string;
  /** Markdown body with the front matter removed. */
  readonly body: string;
}

export interface Skill {
  /** Directory name, which the front matter `name` must match. */
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly version: string;
  /** The skill's own `SKILL.md`. */
  readonly manifest: SkillDocument;
  /** Supporting documents inside the skill, excluding the manifest. */
  readonly documents: readonly SkillDocument[];
}

export interface SiteContent {
  readonly version: string;
  readonly doctrine: SkillDocument;
  readonly rootManifest: SkillDocument;
  readonly skills: readonly Skill[];
}

/**
 * Report whether a repository-relative path may be published.
 *
 * Exported because the boundary deserves a direct test rather than only being
 * exercised through a full build.
 */
export function isPublishable(relativePath: string): boolean {
  const normalised = relativePath.split(sep).join("/");
  if (normalised.startsWith("../") || normalised.includes("/../")) return false;

  const [head] = normalised.split("/");
  if (head === undefined) return false;
  if (INTERNAL_ROOTS.includes(head as (typeof INTERNAL_ROOTS)[number])) {
    return false;
  }
  if (PUBLISHABLE_FILES.includes(normalised as (typeof PUBLISHABLE_FILES)[number])) {
    return true;
  }
  return PUBLISHABLE_ROOTS.includes(head as (typeof PUBLISHABLE_ROOTS)[number]);
}

function readDocument(repoRoot: string, relativePath: string): SkillDocument {
  if (!isPublishable(relativePath)) {
    throw new Error(
      `Refusing to publish a repository-only path: ${relativePath}. ` +
        `The site may only render the shipped knowledge package.`,
    );
  }
  const raw = readFileSync(join(repoRoot, relativePath), "utf8");
  const { data, content } = matter(raw);
  const slug = relativePath.replace(/^skills\//, "").replace(/\.md$/, "");
  return {
    path: relativePath,
    slug,
    name: String(data["name"] ?? "").trim(),
    description: String(data["description"] ?? "").trim(),
    body: content.trim(),
  };
}

function markdownFilesIn(directory: string): string[] {
  return readdirSync(directory)
    .filter((entry) => entry.endsWith(".md"))
    .sort();
}

/** Read the package version from `pyproject.toml`, the single source of truth. */
function packageVersion(repoRoot: string): string {
  const text = readFileSync(join(repoRoot, "pyproject.toml"), "utf8");
  const match = /^version\s*=\s*"([^"]+)"/m.exec(text);
  if (!match?.[1]) {
    throw new Error("pyproject.toml does not declare project.version");
  }
  return match[1];
}

/** Load every publishable document, grouped by skill. */
export function loadContent(repoRoot: string): SiteContent {
  const skillsDir = join(repoRoot, "skills");
  const skills: Skill[] = readdirSync(skillsDir)
    .filter((entry) => statSync(join(skillsDir, entry)).isDirectory())
    .sort()
    .map((id) => {
      const manifest = readDocument(repoRoot, `skills/${id}/SKILL.md`);
      const documents = markdownFilesIn(join(skillsDir, id))
        .filter((file) => file !== "SKILL.md")
        .map((file) => readDocument(repoRoot, `skills/${id}/${file}`));

      const raw = readFileSync(join(skillsDir, id, "SKILL.md"), "utf8");
      const version = String(matter(raw).data["version"] ?? "").trim();

      return { id, name: manifest.name, description: manifest.description, version, manifest, documents };
    });

  return {
    version: packageVersion(repoRoot),
    doctrine: readDocument(repoRoot, "SOULMAP.md"),
    rootManifest: readDocument(repoRoot, "SKILL.md"),
    skills,
  };
}

/** Resolve the repository root from this file's location. */
export function repositoryRoot(fromUrl: string): string {
  const here = new URL(".", fromUrl).pathname;
  return relative(process.cwd(), join(here, "..", "..")) || ".";
}
