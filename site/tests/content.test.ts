/**
 * The publishable-path boundary is the site's safety-critical rule.
 *
 * Everything else here is presentation. This decides whether a repository-only
 * file can reach a public page, so it is tested directly rather than only
 * through a full build.
 */

import { expect, test } from "vitest";

import { isPublishable } from "../src/content.js";
import { esc, firstSentence, renderMarkdown } from "../src/templates.js";

test("the shipped knowledge package is publishable", () => {
  expect(isPublishable("SOULMAP.md")).toBe(true);
  expect(isPublishable("SKILL.md")).toBe(true);
  expect(isPublishable("skills/safety/SKILL.md")).toBe(true);
  expect(isPublishable("skills/meta/quick-reference.md")).toBe(true);
});

test("repository-only paths are refused", () => {
  for (const path of [
    "docs/ROADMAP.md",
    "templates/brand-copy.md",
    ".claude/settings.json",
    ".claude-plugin/marketplace.json",
    "tests/contract/test_response_validators.py",
    "scripts/verify_artifact_hashes.py",
    "src/soulmap/cli.py",
    "evals/datasets/groups.json",
    "library/catalog.json",
  ]) {
    expect(isPublishable(path), `${path} must not be publishable`).toBe(false);
  }
});

test("traversal cannot escape the repository", () => {
  expect(isPublishable("../secrets.md")).toBe(false);
  expect(isPublishable("skills/../docs/ROADMAP.md")).toBe(false);
});

test("a link into an internal directory is unwrapped, not left dead", () => {
  const html = renderMarkdown("See [the roadmap](../../docs/ROADMAP.md) for more.", "skills/voice");

  expect(html, "internal path must not survive").not.toContain("docs/ROADMAP.md");
  expect(html, "the words must survive").toContain("the roadmap");
});

test("a link to a sibling skill document becomes a site route", () => {
  const html = renderMarkdown("Read [ethics-safety.md](../safety/ethics-safety.md) first.", "skills/voice");

  expect(html).toContain('href="/skills/safety/ethics-safety/"');
});

test("a link to the doctrine resolves to the doctrine page", () => {
  const html = renderMarkdown("Read [SOULMAP.md](../../SOULMAP.md) first.", "skills/voice");

  expect(html).toContain('href="/doctrine/"');
});

test("external links are left alone", () => {
  const html = renderMarkdown("See [findahelpline](https://findahelpline.com).");

  expect(html).toContain('href="https://findahelpline.com"');
});

test("HTML in content is escaped", () => {
  expect(esc('<script>"x"</script>')).toBe("&lt;script&gt;&quot;x&quot;&lt;/script&gt;");
});

test("a card summary stops at the first sentence", () => {
  expect(firstSentence("SoulMap safety rules. Relevant for requests involving harm.")).toBe("SoulMap safety rules.");
  expect(firstSentence("No terminal punctuation here")).toBe("No terminal punctuation here");
  expect(firstSentence("")).toBe("");
});

test("a sibling link resolves inside its own skill", () => {
  // The case the first draft got wrong: without the skill id this produced
  // /skills/spiritual-discernment/, which is not a page. The validator caught
  // 140 of these, so it is pinned here.
  const html = renderMarkdown("Start with [spiritual-discernment.md](spiritual-discernment.md).", "skills/spiritual");

  expect(html).toContain('href="/skills/spiritual/spiritual-discernment/"');
});

test("a link to another skill's manifest resolves to that skill page", () => {
  const html = renderMarkdown("See [SKILL.md](../voice/SKILL.md).", "skills/safety");

  expect(html).toContain('href="/skills/voice/"');
});

test("a root in neither list is refused, so a new directory is not published by default", () => {
  // The denylist names today's internal directories. A directory added later
  // will be in neither list, and the allowlist is what refuses it. Mutation
  // testing showed the two gates are independent: removing `docs` from the
  // denylist leaves it refused, because `skills` is still the only allowed
  // root. This pins the case the allowlist alone has to carry.
  expect(isPublishable("benchmarks/results.md")).toBe(false);
  expect(isPublishable("node_modules/pkg/readme.md")).toBe(false);
  expect(isPublishable("SECURITY.md")).toBe(false);
});
