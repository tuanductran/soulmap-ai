import { expect, type Page, test } from "@playwright/test";

const clipboardPromptSuffix =
  "Please reflect what I share without diagnosing, predicting, or taking over the meaning.";

function observeClientErrors(page: Page) {
  const pageErrors: string[] = [];
  const consoleErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  return { consoleErrors, pageErrors };
}

async function openVietnameseProviderDialog(page: Page) {
  await page.goto("vi/skills");
  await page
    .getByRole("button", { name: /Xem kỹ/ })
    .first()
    .click();
  await page
    .getByRole("button", { name: /Dùng prompt bắt đầu/ })
    .first()
    .click();
  return page.getByRole("dialog");
}

test("localized catalog opens an accessible provider dialog and exposes a raw bundle", async ({
  page,
}) => {
  await page.goto("vi/skills");
  await expect(page.getByRole("heading", { name: /Chọn một lớp/ })).toBeVisible();
  const inspect = page.getByRole("button", { name: /Xem kỹ/ }).first();
  const initialChunks = await page.evaluate(() =>
    performance.getEntriesByType("resource").map((entry) => entry.name),
  );
  expect(
    initialChunks.some((url) => /SkillDetailDialog|ProviderDialog|dialog-/.test(url)),
  ).toBeFalsy();
  await inspect.click();
  await expect(page.getByRole("button", { name: /Dùng prompt bắt đầu/ }).first()).toBeVisible();
  const detailChunks = await page.evaluate(() =>
    performance.getEntriesByType("resource").map((entry) => entry.name),
  );
  expect(detailChunks.some((url) => /SkillDetailDialog|dialog-/.test(url))).toBeTruthy();
  expect(detailChunks.some((url) => /ProviderDialog/.test(url))).toBeFalsy();
  await page
    .getByRole("button", { name: /Dùng prompt bắt đầu/ })
    .first()
    .click();
  const raw = page.getByRole("link", { name: /Đọc nguồn chuẩn/ });
  await expect(raw).toBeVisible();
  const providerChunks = await page.evaluate(() =>
    performance.getEntriesByType("resource").map((entry) => entry.name),
  );
  expect(providerChunks.some((url) => /ProviderDialog/.test(url))).toBeTruthy();
  await expect(raw).toHaveAttribute("href", /\/soulmap-ai\/vi\/api\/raw\/meta\.md$/);
  await page.keyboard.press("Escape");
  await expect(raw).not.toBeVisible();
  await expect(inspect).toBeFocused();
});

test("provider dialog handles clipboard denial without leaving an exception state", async ({
  page,
}) => {
  const errors = observeClientErrors(page);
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: { writeText: async () => Promise.reject(new Error("Permission denied")) },
    });
  });
  const dialog = await openVietnameseProviderDialog(page);
  await dialog.getByRole("button", { name: /Sao chép prompt/ }).click();
  await expect(dialog.getByRole("button", { name: /Không thể sao chép/ })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("link", { name: /Đọc nguồn chuẩn/ })).not.toBeVisible();
  expect(errors.pageErrors).toEqual([]);
  expect(errors.consoleErrors).toEqual([]);
});

test("provider dialog copies the canonical prompt and confirms success", async ({ page }) => {
  await page.addInitScript(() => {
    const target = window as typeof window & { __soulmapClipboardWrites: string[] };
    Object.defineProperty(target, "__soulmapClipboardWrites", {
      configurable: true,
      value: [],
    });
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: {
        writeText: async (text: string) => {
          target.__soulmapClipboardWrites.push(text);
        },
      },
    });
  });
  const dialog = await openVietnameseProviderDialog(page);
  await dialog.getByRole("button", { name: /Sao chép prompt/ }).click();
  await expect(dialog.getByRole("button", { name: /Đã sao chép/ })).toBeVisible();
  const writes = await page.evaluate(
    () =>
      (window as typeof window & { __soulmapClipboardWrites: string[] }).__soulmapClipboardWrites,
  );
  expect(writes).toHaveLength(1);
  expect(writes[0]).toMatch(
    /^Use the SoulMap Điều phối cốt lõi layer as a careful reference\. Context: Bắt đầu từ đây /,
  );
  expect(writes[0]).toContain(clipboardPromptSuffix);
});

test("provider dialog handles a missing Clipboard API without client errors", async ({ page }) => {
  const errors = observeClientErrors(page);
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: undefined,
    });
  });
  const dialog = await openVietnameseProviderDialog(page);
  await dialog.getByRole("button", { name: /Sao chép prompt/ }).click();
  await expect(dialog.getByRole("button", { name: /Không thể sao chép/ })).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.getByRole("link", { name: /Đọc nguồn chuẩn/ })).not.toBeVisible();
  expect(errors.pageErrors).toEqual([]);
  expect(errors.consoleErrors).toEqual([]);
});

test("direct route, language switch and FAQ disclosure preserve a usable static surface", async ({
  page,
}) => {
  await page.goto("ko/faq");
  await page.getByRole("button", { name: /SoulMap AI란 무엇인가요/ }).click();
  await expect(page.getByText(/외부 AI host/)).toBeVisible();
  await page.getByRole("button", { name: /언어 KO/ }).click();
  await page.getByRole("menuitem", { name: /English/ }).click();
  await expect(page).toHaveURL(/\/soulmap-ai\/faq$/);
});
