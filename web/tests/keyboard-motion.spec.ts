import { expect, test } from "@playwright/test";

test("keyboard contract: language and More menus open, navigate and restore focus with Escape", async ({
  page,
}) => {
  await page.goto("vi/skills", { waitUntil: "domcontentloaded" });

  const language = page.getByRole("button", { name: /Ngôn ngữ/ });
  await language.focus();
  await page.keyboard.press("Enter");
  const languageMenu = page.getByRole("menu");
  await expect(languageMenu).toBeVisible();
  await page.keyboard.press("ArrowDown");
  await expect
    .poll(() =>
      languageMenu.evaluate((menu) => {
        const activeId = menu.getAttribute("aria-activedescendant");
        return Boolean(
          activeId && document.getElementById(activeId)?.getAttribute("role") === "menuitem",
        );
      }),
    )
    .toBe(true);
  await page.keyboard.press("Escape");
  await expect(language).toBeFocused();

  const more = page.getByRole("button", { name: "Thêm", exact: true });
  await more.focus();
  await page.keyboard.press("Enter");
  const moreMenu = page.getByRole("menu");
  await expect(moreMenu).toBeVisible();
  await page.keyboard.press("ArrowDown");
  await expect
    .poll(() =>
      moreMenu.evaluate((menu) => {
        const activeId = menu.getAttribute("aria-activedescendant");
        return Boolean(
          activeId && document.getElementById(activeId)?.getAttribute("role") === "menuitem",
        );
      }),
    )
    .toBe(true);
  await page.keyboard.press("Escape");
  await expect(more).toBeFocused();
});

test("keyboard contract: skill dialog traps keyboard focus and restores it on Escape", async ({
  page,
}) => {
  await page.goto("vi/skills", { waitUntil: "domcontentloaded" });
  const inspect = page.getByRole("button", { name: /Xem kỹ/ }).first();
  await inspect.focus();
  await page.keyboard.press("Enter");
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByRole("button", { name: /Dùng prompt bắt đầu/ })).toBeVisible();
  await page.keyboard.press("Shift+Tab");
  await expect
    .poll(() =>
      page.evaluate(() => {
        const activeDialog = document.querySelector<HTMLElement>('[role="dialog"][data-open]');
        return Boolean(activeDialog?.contains(document.activeElement));
      }),
    )
    .toBe(true);
  await page.keyboard.press("Escape");
  await expect(inspect).toBeFocused();
});

test("reduced-motion contract: navigation cue avoids smooth scrolling and focus remains visibly outlined", async ({
  page,
}, testInfo) => {
  test.skip(testInfo.project.name !== "mobile", "The navigation cue is mobile-only.");
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("vi/skills", { waitUntil: "domcontentloaded" });
  const cue = page.getByRole("button", { name: "Cuộn sang phải để xem thêm mục" });
  await expect(cue).toBeVisible();
  await cue.focus();
  await expect(cue).toHaveCSS("outline-style", "solid");
  await expect(cue).toHaveCSS("outline-width", "3px");
  await page.evaluate(() => {
    const navigation = document.querySelector("nav");
    if (!(navigation instanceof HTMLElement)) throw new Error("Expected a navigation rail.");
    const calls: ScrollToOptions[] = [];
    navigation.scrollBy = (options?: ScrollToOptions | number, y?: number) => {
      if (typeof options === "object") calls.push(options);
      else calls.push({ left: options, top: y });
    };
    Object.assign(window, { __soulmapScrollCalls: calls });
  });
  await cue.click();
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          (window as Window & { __soulmapScrollCalls?: ScrollToOptions[] })
            .__soulmapScrollCalls?.[0]?.behavior,
      ),
    )
    .toBe("auto");
});
