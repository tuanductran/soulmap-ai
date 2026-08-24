import AxeBuilder from "@axe-core/playwright";
import { expect, type Page, type TestInfo, test } from "@playwright/test";

const wcagTags = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22a", "wcag22aa"];
const locales = ["", "vi", "ko"] as const;
const routes = [
  "",
  "skills",
  "about",
  "faq",
  "how-it-works",
  "boundaries",
  "notes",
  "download",
  "privacy",
] as const;

function routePath(locale: string, route: string) {
  return [locale, route].filter(Boolean).join("/") || ".";
}

type A11yFinding = { state: string; rule: string; impact: string | null; targets: string[][] };

async function collectA11yViolations(page: Page, state: string): Promise<A11yFinding[]> {
  const results = await new AxeBuilder({ page }).withTags(wcagTags).analyze();
  return results.violations.map((violation) => ({
    state,
    rule: violation.id,
    impact: violation.impact ?? null,
    targets: violation.nodes.map((node) => node.target),
  }));
}

async function expectNoA11yViolations(findings: A11yFinding[], testInfo: TestInfo) {
  await testInfo.attach("axe-audit-findings", {
    body: JSON.stringify(findings, null, 2),
    contentType: "application/json",
  });
  expect(
    findings,
    findings.map((finding) => `${finding.state}: ${finding.rule}`).join("; "),
  ).toEqual([]);
}

test("a11y audit: every public route in every locale has no automatically detectable WCAG A/AA violations", async ({
  page,
}, testInfo) => {
  const findings: A11yFinding[] = [];
  for (const locale of locales) {
    for (const route of routes) {
      const path = routePath(locale, route);
      await test.step(`${locale || "en"}/${route || "home"}`, async () => {
        await page.goto(path, { waitUntil: "domcontentloaded" });
        await expect(page.locator("h1")).toBeVisible();
        findings.push(
          ...(await collectA11yViolations(page, `${locale || "en"}-${route || "home"}`)),
        );
      });
    }
  }
  await expectNoA11yViolations(findings, testInfo);
});

test("a11y audit: menus, disclosure and provider handoff retain WCAG A/AA conformance when open", async ({
  page,
}, testInfo) => {
  const findings: A11yFinding[] = [];
  await page.goto("vi/skills", { waitUntil: "domcontentloaded" });
  await page
    .getByRole("button", { name: /Xem kỹ/ })
    .first()
    .click();
  await expect(page.getByRole("button", { name: /Dùng prompt bắt đầu/ }).first()).toBeVisible();
  findings.push(...(await collectA11yViolations(page, "vi-skill-detail-dialog")));

  await page
    .getByRole("button", { name: /Dùng prompt bắt đầu/ })
    .first()
    .click();
  await expect(page.getByRole("link", { name: /Đọc nguồn chuẩn/ })).toBeVisible();
  findings.push(...(await collectA11yViolations(page, "vi-provider-dialog")));

  await page.keyboard.press("Escape");
  await page.goto("ko/faq", { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: /SoulMap AI란 무엇인가요/ }).click();
  await expect(page.getByText(/외부 AI host/)).toBeVisible();
  findings.push(...(await collectA11yViolations(page, "ko-faq-disclosure")));

  await page.getByRole("button", { name: /더 보기/ }).click();
  await expect(page.getByRole("menu")).toBeVisible();
  findings.push(...(await collectA11yViolations(page, "ko-more-menu")));
  await expectNoA11yViolations(findings, testInfo);
});

test("a11y audit: mobile navigation scroll cue is labelled and leaves a conformant page state", async ({
  page,
}, testInfo) => {
  test.skip(
    testInfo.project.name !== "mobile",
    "This check applies to the mobile navigation rail.",
  );
  await page.goto("vi/skills", { waitUntil: "domcontentloaded" });
  await expect(page.getByRole("button", { name: "Cuộn sang phải để xem thêm mục" })).toBeVisible();
  await expectNoA11yViolations(
    await collectA11yViolations(page, "vi-mobile-navigation-cue"),
    testInfo,
  );
});
