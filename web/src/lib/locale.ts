// Atlas Nội Tâm: Locale được suy ra từ URL, English giữ URL không prefix để bề mặt công khai gọn và ổn định.
import type { Locale } from "@/i18n";

export function localeFromPath(pathname: string): Locale {
  const segment = pathname.split("/").filter(Boolean)[0];
  return segment === "vi" || segment === "ko" ? segment : "en";
}

export function localizedPath(pathname: string, locale: Locale): string {
  const segments = pathname.split("/").filter(Boolean);
  const withoutLocale = segments[0] === "vi" || segments[0] === "ko" ? segments.slice(1) : segments;
  const prefix = locale === "en" ? [] : [locale];
  return `/${[...prefix, ...withoutLocale].join("/")}` || "/";
}
