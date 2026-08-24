import { expect, test } from "@playwright/test";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const directory = path.dirname(fileURLToPath(import.meta.url));
const homeSource = path.resolve(directory, "../src/pages/Home.tsx");

const localizedHomeCopy = {
  en: { path: ".", label: "02 / Field note", evidence: "03 / Evidence before certainty", alt: "A field notebook with abstract contour-map sketches" },
  vi: { path: "vi", label: "02 / Ghi chép thực địa", evidence: "03 / Bằng chứng trước khi kết luận", alt: "Cuốn sổ thực địa với các phác thảo bản đồ đường đồng mức trừu tượng" },
  ko: { path: "ko", label: "02 / 현장 노트", evidence: "03 / 확신보다 근거", alt: "추상적인 등고선 지도 스케치가 있는 현장 노트" },
} as const;

test("i18n contract: Home public field-note copy is resource-backed rather than hard-coded", async () => {
  const source = await readFile(homeSource, "utf8");
  for (const key of ["fieldNoteLabel", "fieldNoteBody", "evidenceLabel", "workingSurface", "fieldImageAlt"]) {
    expect(source).toContain(`t("home.${key}")`);
  }
  expect(source).not.toContain(">02 / Field note<");
  expect(source).not.toContain(">03 / Evidence before certainty<");
});

test("i18n contract: Home field-note labels and image alternative text follow the active locale", async ({ page }) => {
  for (const copy of Object.values(localizedHomeCopy)) {
    await page.goto(copy.path, { waitUntil: "domcontentloaded" });
    await expect(page.getByText(copy.label, { exact: true })).toHaveCount(1);
    await expect(page.getByText(copy.evidence, { exact: true })).toBeVisible();
    await expect(page.getByRole("img", { name: copy.alt })).toBeVisible();
  }
});
