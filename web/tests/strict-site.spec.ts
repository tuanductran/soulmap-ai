import { expect, test } from "@playwright/test";

const locales = [
  { code: "en", prefix: "", navigation: "Primary navigation" },
  { code: "vi", prefix: "vi", navigation: "Điều hướng chính" },
  { code: "ko", prefix: "ko", navigation: "주요 탐색" },
] as const;

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
const skillSlugs = ["meta", "frameworks", "safety", "spiritual", "voice", "brand"] as const;

function routePath(prefix: string, route: string) {
  return [prefix, route].filter(Boolean).join("/") || ".";
}

test("strict audit: every public route renders in every locale without overflow or page errors", async ({
  page,
}) => {
  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));

  for (const locale of locales) {
    for (const route of routes) {
      const path = routePath(locale.prefix, route);
      await test.step(`${locale.code}/${route || "home"}`, async () => {
        await page.goto(path, { waitUntil: "domcontentloaded" });
        await expect(page.locator("html")).toHaveAttribute("lang", locale.code);
        await expect(page.getByRole("navigation", { name: locale.navigation })).toBeVisible();
        await expect(page.locator("h1")).toBeVisible();
        await expect(page.getByRole("contentinfo")).toBeVisible();
        expect(
          await page.evaluate(
            () =>
              document.documentElement.scrollWidth <= window.innerWidth &&
              document.body.scrollWidth <= window.innerWidth,
          ),
        ).toBeTruthy();
      });
    }
  }

  expect(pageErrors).toEqual([]);
});

test("strict audit: every localized raw bundle is available and does not expose repository-only markers", async ({
  request,
}) => {
  for (const prefix of ["", "vi/", "ko/"]) {
    for (const slug of skillSlugs) {
      const response = await request.get(`${prefix}api/raw/${slug}.md`);
      expect(response.status()).toBe(200);
      const body = await response.text();
      expect(body.length).toBeGreaterThan(500);
      expect(body).not.toMatch(/\.claude\/|\.github\/|pyproject\.toml|uv\.lock/);
    }
  }
});

test("strict audit: skills search, lazy dialogs, locale prompt explanation and focus restoration work", async ({
  page,
}) => {
  await page.goto("vi/skills", { waitUntil: "networkidle" });
  const search = page.getByPlaceholder(/Tìm theo lớp/);
  await search.fill("không-tồn-tại");
  await expect(page.getByText(/Không có lớp phù hợp/)).toBeVisible();
  await search.fill("an toàn");
  await expect(page.locator("article")).toHaveCount(3);

  const inspect = page.getByRole("button", { name: /Xem kỹ/ }).first();
  await inspect.click();
  const usePrompt = page.getByRole("button", { name: /Dùng prompt bắt đầu/ }).first();
  await expect(usePrompt).toBeVisible();
  await usePrompt.click();
  await expect(page.getByText(/Prompt khởi đầu được giữ bằng tiếng Anh/)).toBeVisible();
  const raw = page.getByRole("link", { name: /Đọc nguồn chuẩn/ });
  await expect(raw).toHaveAttribute("href", /\/soulmap-ai\/vi\/api\/raw\/safety\.md$/);
  await page.keyboard.press("Escape");
  await expect(raw).not.toBeVisible();
  await expect(inspect).toBeFocused();
});

test("strict audit: locale menu and FAQ disclosure preserve direct route semantics", async ({
  page,
}) => {
  await page.goto("ko/faq", { waitUntil: "networkidle" });
  await page.getByRole("button", { name: /SoulMap AI란 무엇인가요/ }).click();
  await expect(page.getByText(/외부 AI host/)).toBeVisible();
  await page.getByRole("button", { name: /언어 KO/ }).click();
  await page.getByRole("menuitem", { name: /English/ }).click();
  await expect(page).toHaveURL(/\/soulmap-ai\/faq$/);
});

test("strict audit: mobile navigation exposes a scroll affordance and advances the navigation rail", async ({
  page,
}, testInfo) => {
  test.skip(
    testInfo.project.name !== "mobile",
    "This check applies to the mobile navigation rail.",
  );
  await page.goto("vi/skills", { waitUntil: "networkidle" });
  const navigation = page.getByRole("navigation", { name: "Điều hướng chính" });
  const cue = page.getByRole("button", { name: "Cuộn sang phải để xem thêm mục" });
  await expect(cue).toBeVisible();
  const before = await navigation.evaluate((element) => element.scrollLeft);
  await cue.click();
  await expect
    .poll(() => navigation.evaluate((element) => element.scrollLeft))
    .toBeGreaterThan(before);
});
