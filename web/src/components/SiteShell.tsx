// Bản đồ Biên Độ: Masthead desktop dùng một baseline; mobile giữ rail cuộn ngang riêng nhưng dùng cùng gutter/page frame.
import { Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/react";
import { Link, Outlet, useRouterState } from "@tanstack/react-router";
import { ChevronDown, ChevronRight, ExternalLink } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { BrandMark } from "@/components/BrandMark";
import { type Locale, supportedLocales } from "@/i18n";
import { localeFromPath, localizedPath } from "@/lib/locale";

const labels: Record<Locale, string> = { en: "EN", vi: "VI", ko: "KO" };

export function SiteShell() {
  const { t, i18n } = useTranslation();
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const locale = localeFromPath(pathname);
  const navigationRef = useRef<HTMLElement>(null);
  const [canScrollNavigation, setCanScrollNavigation] = useState(false);
  useEffect(() => {
    void i18n.changeLanguage(locale);
    document.documentElement.lang = locale;
  }, [i18n, locale]);
  // biome-ignore lint/correctness/useExhaustiveDependencies: Locale changes link widths, so scroll geometry must be recalculated after the localized navigation commits.
  useEffect(() => {
    const navigation = navigationRef.current;
    if (!navigation) return;
    const updateScrollCue = () =>
      setCanScrollNavigation(
        navigation.scrollLeft + navigation.clientWidth < navigation.scrollWidth - 4,
      );
    const frame = window.requestAnimationFrame(updateScrollCue);
    window.addEventListener("resize", updateScrollCue);
    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener("resize", updateScrollCue);
    };
  }, [locale]);
  const scrollNavigation = () => {
    const navigation = navigationRef.current;
    if (!navigation) return;
    const behavior = window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? "auto"
      : "smooth";
    navigation.scrollBy({ left: navigation.clientWidth * 0.75, behavior });
  };
  const links = [
    { key: "home", to: localizedPath("/", locale) },
    { key: "how", to: localizedPath("/how-it-works", locale) },
    { key: "boundaries", to: localizedPath("/boundaries", locale) },
    { key: "notes", to: localizedPath("/notes", locale) },
    { key: "skills", to: localizedPath("/skills", locale) },
  ];
  const moreLinks = [
    { key: "about", to: localizedPath("/about", locale) },
    { key: "faq", to: localizedPath("/faq", locale) },
    { key: "download", to: localizedPath("/download", locale) },
    { key: "privacy", to: localizedPath("/privacy", locale) },
  ];
  const navigation = (
    <div className="flex min-w-max items-center gap-1">
      {links.map((link) => (
        <Link
          key={link.key}
          to={link.to}
          className="rounded-full px-3 py-2 text-sm font-semibold text-[#5a6d68] transition duration-200 hover:bg-[#e6eee8] hover:text-[#1b5550] active:scale-[0.98]"
          activeProps={{ className: "bg-[#dcebe2] text-[#174943]" }}
        >
          {t(`nav.${link.key}`)}
        </Link>
      ))}
      <Menu as="div" className="relative">
        <MenuButton className="inline-flex items-center gap-1 rounded-full px-3 py-2 text-sm font-semibold text-[#5a6d68] transition duration-200 hover:bg-[#e6eee8] hover:text-[#1b5550]">
          {t("nav.more")} <ChevronDown className="size-3" />
        </MenuButton>
        <MenuItems
          anchor="bottom start"
          portal
          className="z-40 w-48 origin-top-left rounded-xl border border-[#d6ded7] bg-[#fcfbf7] p-1.5 shadow-[0_18px_42px_rgba(20,49,45,0.15)] [--anchor-gap:10px] focus:outline-none"
        >
          {moreLinks.map((link) => (
            <MenuItem key={link.key}>
              {({ focus }) => (
                <Link
                  to={link.to}
                  className={`block rounded-lg px-3 py-2.5 text-sm font-semibold ${focus ? "bg-[#e5efe8] text-[#1c625b]" : "text-[#284543]"}`}
                >
                  {t(`nav.${link.key}`)}
                </Link>
              )}
            </MenuItem>
          ))}
        </MenuItems>
      </Menu>
    </div>
  );
  return (
    <div className="min-h-screen overflow-x-clip bg-[#f7f6ef] text-[#173837]">
      <header className="relative z-30 border-b border-[#d6ded7] bg-[#f7f6ef]/95 backdrop-blur-xl">
        <div className="site-frame">
          <div className="flex min-h-[4.75rem] items-center gap-5">
            <Link to={localizedPath("/", locale)}>
              <BrandMark />
            </Link>
            <nav
              className="hidden min-w-0 flex-1 justify-center lg:flex"
              aria-label={t("nav.primaryLabel")}
            >
              {navigation}
            </nav>
            <Menu as="div" className="relative ml-auto shrink-0">
              <MenuButton className="inline-flex items-center gap-2 rounded-full border border-[#d6ded7] bg-[#fcfbf7] px-3.5 py-2 text-xs font-bold tracking-[0.08em] text-[#234d4a] transition duration-200 hover:border-[#b8c8bc] hover:bg-white">
                {t("common.language")} {labels[locale]}
                <ChevronDown className="size-3" />
              </MenuButton>
              <MenuItems className="absolute right-0 mt-2 w-40 origin-top-right rounded-xl border border-[#d6ded7] bg-[#fcfbf7] p-1.5 shadow-[0_18px_42px_rgba(20,49,45,0.15)] focus:outline-none">
                {supportedLocales.map((item) => (
                  <MenuItem key={item}>
                    {({ focus }) => (
                      <Link
                        to={localizedPath(pathname, item)}
                        className={`block rounded-lg px-3 py-2.5 text-sm font-semibold ${focus ? "bg-[#e5efe8] text-[#1c625b]" : "text-[#284543]"}`}
                      >
                        {labels[item]}{" "}
                        <span className="ml-2 text-xs font-normal text-[#6e7d77]">
                          {item === "en" ? "English" : item === "vi" ? "Tiếng Việt" : "한국어"}
                        </span>
                      </Link>
                    )}
                  </MenuItem>
                ))}
              </MenuItems>
            </Menu>
          </div>
        </div>
        <div className="relative border-t border-[#e1e6df] lg:hidden">
          <nav
            ref={navigationRef}
            data-navigation-rail
            onScroll={() => {
              const navigation = navigationRef.current;
              if (navigation)
                setCanScrollNavigation(
                  navigation.scrollLeft + navigation.clientWidth < navigation.scrollWidth - 4,
                );
            }}
            className="site-frame overflow-x-auto pb-2.5 pr-14 pt-2 [scrollbar-width:thin] sm:pr-8"
            aria-label={t("nav.primaryLabel")}
          >
            {navigation}
          </nav>
          {canScrollNavigation && (
            <button
              type="button"
              onClick={scrollNavigation}
              className="absolute right-2 top-2 inline-flex size-8 items-center justify-center rounded-full border border-[#cfd9d0] bg-[#f7f6ef]/95 text-[#1e655e] shadow-sm backdrop-blur"
              aria-label={t("nav.scrollMore")}
            >
              <ChevronRight className="size-4" />
            </button>
          )}
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="border-t border-[#d6ded7] bg-[#eff1e8] py-8 sm:py-10">
        <div className="site-frame flex flex-col justify-between gap-4 text-sm text-[#5d6c67] sm:flex-row sm:items-center">
          <p>{t("footer")}</p>
          <a
            href="https://github.com/tuanductran/soulmap-ai"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 font-semibold text-[#256a63] hover:underline"
          >
            {t("common.repository")} <ExternalLink className="size-3" />
          </a>
        </div>
      </footer>
    </div>
  );
}
