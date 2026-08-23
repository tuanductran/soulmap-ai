import { expect, test } from "@playwright/test";

test("localized catalog opens an accessible provider dialog and exposes a raw bundle", async ({ page }) => {
  await page.goto("vi/skills");
  await expect(page.getByRole("heading", { name: /Chọn một lớp/ })).toBeVisible();
  const inspect = page.getByRole("button", { name: /Xem kỹ/ }).first();
  const initialChunks = await page.evaluate(() => performance.getEntriesByType("resource").map((entry) => entry.name));
  expect(initialChunks.some((url) => /SkillDetailDialog|ProviderDialog|dialog-/.test(url))).toBeFalsy();
  await inspect.click();
  await expect(page.getByRole("button", { name: /Dùng prompt bắt đầu/ }).first()).toBeVisible();
  const detailChunks = await page.evaluate(() => performance.getEntriesByType("resource").map((entry) => entry.name));
  expect(detailChunks.some((url) => /SkillDetailDialog|dialog-/.test(url))).toBeTruthy();
  expect(detailChunks.some((url) => /ProviderDialog/.test(url))).toBeFalsy();
  await page.getByRole("button", { name: /Dùng prompt bắt đầu/ }).first().click();
  const raw = page.getByRole("link", { name: /Đọc nguồn chuẩn/ });
  await expect(raw).toBeVisible();
  const providerChunks = await page.evaluate(() => performance.getEntriesByType("resource").map((entry) => entry.name));
  expect(providerChunks.some((url) => /ProviderDialog/.test(url))).toBeTruthy();
  await expect(raw).toHaveAttribute("href", /\/soulmap-ai\/vi\/api\/raw\/meta\.md$/);
  await page.keyboard.press("Escape");
  await expect(raw).not.toBeVisible();
  await expect(inspect).toBeFocused();
});

test("direct route, language switch and FAQ disclosure preserve a usable static surface", async ({ page }) => {
  await page.goto("ko/faq");
  await page.getByRole("button", { name: /SoulMap AI란 무엇인가요/ }).click();
  await expect(page.getByText(/외부 AI host/)).toBeVisible();
  await page.getByRole("button", { name: /언어 KO/ }).click();
  await page.getByRole("menuitem", { name: /English/ }).click();
  await expect(page).toHaveURL(/\/soulmap-ai\/faq$/);
});
