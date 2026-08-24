// Atlas Nội Tâm: Header giống một masthead atlas, cung cấp đường đi rõ ràng và menu ngôn ngữ accessible.
import { Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/react";
import { ChevronDown, ChevronRight, ExternalLink } from "lucide-react";
import { Link, Outlet, useRouterState } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { BrandMark } from "@/components/BrandMark";
import { supportedLocales, type Locale } from "@/i18n";
import { localeFromPath, localizedPath } from "@/lib/locale";

const labels: Record<Locale, string> = { en: "EN", vi: "VI", ko: "KO" };

export function SiteShell() {
  const { t, i18n } = useTranslation();
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const locale = localeFromPath(pathname);
  const navigationRef = useRef<HTMLElement>(null);
  const [canScrollNavigation, setCanScrollNavigation] = useState(false);
  useEffect(() => { void i18n.changeLanguage(locale); document.documentElement.lang = locale; }, [i18n, locale]);
  useEffect(() => {
    const navigation = navigationRef.current;
    if (!navigation) return;
    const updateScrollCue = () => setCanScrollNavigation(navigation.scrollLeft + navigation.clientWidth < navigation.scrollWidth - 4);
    const frame = window.requestAnimationFrame(updateScrollCue);
    window.addEventListener("resize", updateScrollCue);
    return () => { window.cancelAnimationFrame(frame); window.removeEventListener("resize", updateScrollCue); };
  }, [locale]);
  const scrollNavigation = () => {
    const navigation = navigationRef.current;
    if (!navigation) return;
    const behavior = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";
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
  return (
    <div className="min-h-screen overflow-x-clip bg-[#f7f6ef] text-[#122b2c]">
      <header className="relative z-30 border-b border-[#dfe5dc] bg-[#f7f6ef]/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8 lg:px-12">
          <Link to={localizedPath("/", locale)}><BrandMark /></Link>
          <Menu as="div" className="relative">
            <MenuButton className="inline-flex items-center gap-2 rounded-full border border-[#d8dfd8] bg-white/70 px-4 py-2 text-xs font-bold tracking-[0.08em] text-[#234d4a] transition hover:bg-white">{t("common.language")} {labels[locale]}<ChevronDown className="size-3" /></MenuButton>
            <MenuItems className="absolute right-0 mt-2 w-40 origin-top-right rounded-2xl border border-[#d8dfd8] bg-[#fbfaf5] p-1.5 shadow-xl focus:outline-none">
              {supportedLocales.map((item) => <MenuItem key={item}>{({ focus }) => <Link to={localizedPath(pathname, item)} className={`block rounded-xl px-3 py-2 text-sm font-semibold ${focus ? "bg-[#e5efe8] text-[#1c625b]" : "text-[#284543]"}`}>{labels[item]} <span className="ml-2 text-xs font-normal text-[#6e7d77]">{item === "en" ? "English" : item === "vi" ? "Tiếng Việt" : "한국어"}</span></Link>}</MenuItem>)}
            </MenuItems>
          </Menu>
        </div>
        <div className="relative mx-auto max-w-7xl">
          <nav ref={navigationRef} onScroll={() => { const navigation = navigationRef.current; if (navigation) setCanScrollNavigation(navigation.scrollLeft + navigation.clientWidth < navigation.scrollWidth - 4); }} className="overflow-x-auto px-5 pb-3 pr-14 [scrollbar-width:thin] sm:px-8 sm:pr-8 lg:px-12" aria-label={t("nav.primaryLabel")}>
            <div className="flex min-w-max gap-1">
              {links.map((link) => <Link key={link.key} to={link.to} className="rounded-full px-4 py-2 text-sm font-medium text-[#526565] transition hover:bg-[#e6eee8] hover:text-[#1b5550] active:scale-[0.98]" activeProps={{ className: "bg-[#dcebe2] text-[#1b5550]" }}>{t(`nav.${link.key}`)}</Link>)}
              <Menu as="div" className="relative">
                <MenuButton className="inline-flex items-center gap-1 rounded-full px-4 py-2 text-sm font-medium text-[#526565] transition hover:bg-[#e6eee8] hover:text-[#1b5550]">{t("nav.more")} <ChevronDown className="size-3" /></MenuButton>
                <MenuItems anchor="bottom start" portal className="z-40 w-44 origin-top-left rounded-2xl border border-[#d8dfd8] bg-[#fbfaf5] p-1.5 shadow-xl [--anchor-gap:8px] focus:outline-none">
                  {moreLinks.map((link) => <MenuItem key={link.key}>{({ focus }) => <Link to={link.to} className={`block rounded-xl px-3 py-2 text-sm font-semibold ${focus ? "bg-[#e5efe8] text-[#1c625b]" : "text-[#284543]"}`}>{t(`nav.${link.key}`)}</Link>}</MenuItem>)}
                </MenuItems>
              </Menu>
            </div>
          </nav>
          {canScrollNavigation && <button type="button" onClick={scrollNavigation} className="absolute right-2 top-0 inline-flex size-9 items-center justify-center rounded-full border border-[#cfd9d0] bg-[#f7f6ef]/95 text-[#1e655e] shadow-sm backdrop-blur sm:hidden" aria-label={t("nav.scrollMore")}><ChevronRight className="size-4" /></button>}
        </div>
      </header>
      <main><Outlet /></main>
      <footer className="border-t border-[#dfe5dc] bg-[#f2f1e8] px-5 py-8 sm:px-8 lg:px-12">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-4 text-sm text-[#5d6c67] sm:flex-row sm:items-center"><p>{t("footer")}</p><a href="https://github.com/tuanductran/soulmap-ai" target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-semibold text-[#256a63] hover:underline">{t("common.repository")} <ExternalLink className="size-3" /></a></div>
      </footer>
    </div>
  );
}
