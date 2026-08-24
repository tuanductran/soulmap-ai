import { expect, test } from "@playwright/test";

test("performance contract: Home chooses the compact hero candidate for default desktop and mobile viewports", async ({
  page,
}) => {
  await page.goto("");
  const hero = page.locator("main > section:first-of-type img").first();
  await expect(hero).toHaveAttribute("srcset", /hero-1280\.webp 1280w.*hero\.webp 1920w/);
  await expect(hero).toHaveAttribute("sizes", "100vw");
  await expect(hero.evaluate((image) => image.currentSrc)).resolves.toMatch(/hero-1280\.webp/);
});
