import { expect, test } from "@playwright/test";

const locales = [
  { prefix: "", trigger: "More", about: "About", destination: "/about" },
  { prefix: "/vi", trigger: "Thêm", about: "Giới thiệu", destination: "/about" },
  { prefix: "/ko", trigger: "더 보기", about: "소개", destination: "/about" },
] as const;

test("More menu pointer flow: every locale opens, routes and closes", async ({ page }) => {
  for (const locale of locales) {
    await page.goto(locale.prefix ? `${locale.prefix.slice(1)}/faq` : "faq", {
      waitUntil: "domcontentloaded",
    });
    const trigger = page.getByRole("button", { name: locale.trigger, exact: true });
    await trigger.click();
    const menu = page.getByRole("menu");
    await expect(menu).toBeVisible();
    const about = page.getByRole("menuitem", { name: locale.about, exact: true });
    await expect(about).toBeVisible();
    await about.click();
    await expect(page).toHaveURL(new RegExp(`${locale.prefix || ""}${locale.destination}$`));
    await expect(menu).toHaveCount(0);
  }
});

test("More menu pointer flow: outside activation closes the open panel", async ({ page }) => {
  await page.goto("vi/faq", { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Thêm", exact: true }).click();
  await expect(page.getByRole("menu")).toBeVisible();
  await page.mouse.click(1100, 300);
  await expect(page.getByRole("menu")).toHaveCount(0);
});

test("More menu mobile geometry: panel remains visible and item hit targets stay inside the viewport", async ({
  page,
}, testInfo) => {
  test.skip(
    testInfo.project.name !== "mobile",
    "Geometry is specific to the mobile navigation rail.",
  );
  await page.goto("vi/faq", { waitUntil: "domcontentloaded" });
  await page.getByRole("button", { name: "Thêm", exact: true }).click();
  const menu = page.getByRole("menu");
  await expect(menu).toBeVisible();
  const result = await page.evaluate(() => {
    const menu = document.querySelector<HTMLElement>('[role="menu"]');
    if (!menu) throw new Error("Expected More menu.");
    const rect = menu.getBoundingClientRect();
    const items = [...menu.querySelectorAll<HTMLElement>('[role="menuitem"]')].map((item) => {
      const itemRect = item.getBoundingClientRect();
      const midpoint = document.elementFromPoint(
        itemRect.left + itemRect.width / 2,
        itemRect.top + itemRect.height / 2,
      );
      return {
        bottom: itemRect.bottom,
        top: itemRect.top,
        hit: midpoint === item || item.contains(midpoint),
      };
    });
    return {
      bottom: rect.bottom,
      top: rect.top,
      viewportHeight: window.innerHeight,
      items,
    };
  });
  expect(result.top).toBeGreaterThanOrEqual(0);
  expect(result.bottom).toBeLessThanOrEqual(result.viewportHeight);
  expect(result.items).toHaveLength(4);
  expect(
    result.items.every((item) => item.top >= 0 && item.bottom <= result.viewportHeight && item.hit),
    JSON.stringify(result),
  ).toBe(true);
});
