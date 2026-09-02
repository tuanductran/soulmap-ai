/**
 * The publishable-path boundary is the site's safety-critical rule.
 *
 * Everything else here is presentation. This decides whether a repository-only
 * file can reach a public page, so it is tested directly rather than only
 * through a full build.
 */

import assert from "node:assert/strict";
import { test } from "node:test";

import { isPublishable } from "../src/content.js";
import { esc, firstSentence, renderMarkdown } from "../src/templates.js";

test("the shipped knowledge package is publishable", () => {
  assert.equal(isPublishable("SOULMAP.md"), true);
  assert.equal(isPublishable("SKILL.md"), true);
  assert.equal(isPublishable("skills/safety/SKILL.md"), true);
  assert.equal(isPublishable("skills/meta/quick-reference.md"), true);
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
    assert.equal(isPublishable(path), false, `${path} must not be publishable`);
  }
});

test("traversal cannot escape the repository", () => {
  assert.equal(isPublishable("../secrets.md"), false);
  assert.equal(isPublishable("skills/../docs/ROADMAP.md"), false);
});

test("a link into an internal directory is unwrapped, not left dead", () => {
  const html = renderMarkdown("See [the roadmap](../../docs/ROADMAP.md) for more.", "skills/voice");

  assert.ok(!html.includes("docs/ROADMAP.md"), "internal path must not survive");
  assert.ok(html.includes("the roadmap"), "the words must survive");
});

test("a link to a sibling skill document becomes a site route", () => {
  const html = renderMarkdown("Read [ethics-safety.md](../safety/ethics-safety.md) first.", "skills/voice");

  assert.ok(html.includes('href="/skills/safety/ethics-safety/"'), html);
});

test("a link to the doctrine resolves to the doctrine page", () => {
  const html = renderMarkdown("Read [SOULMAP.md](../../SOULMAP.md) first.", "skills/voice");

  assert.ok(html.includes('href="/doctrine/"'), html);
});

test("external links are left alone", () => {
  const html = renderMarkdown("See [findahelpline](https://findahelpline.com).");

  assert.ok(html.includes('href="https://findahelpline.com"'), html);
});

test("HTML in content is escaped", () => {
  assert.equal(esc('<script>"x"</script>'), "&lt;script&gt;&quot;x&quot;&lt;/script&gt;");
});

test("a card summary stops at the first sentence", () => {
  assert.equal(
    firstSentence("SoulMap safety rules. Relevant for requests involving harm."),
    "SoulMap safety rules.",
  );
  assert.equal(firstSentence("No terminal punctuation here"), "No terminal punctuation here");
  assert.equal(firstSentence(""), "");
});

test("a sibling link resolves inside its own skill", () => {
  // The case the first draft got wrong: without the skill id this produced
  // /skills/spiritual-discernment/, which is not a page. The validator caught
  // 140 of these, so it is pinned here.
  const html = renderMarkdown("Start with [spiritual-discernment.md](spiritual-discernment.md).", "skills/spiritual");

  assert.ok(html.includes('href="/skills/spiritual/spiritual-discernment/"'), html);
});

test("a link to another skill's manifest resolves to that skill page", () => {
  const html = renderMarkdown("See [SKILL.md](../voice/SKILL.md).", "skills/safety");

  assert.ok(html.includes('href="/skills/voice/"'), html);
});
