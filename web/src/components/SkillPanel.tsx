// Atlas Nội Tâm: Catalog tải card/search trước, còn dialog detail/provider chỉ tải sau một thao tác chủ động.
import { ArrowRight, Search } from "lucide-react";
import { lazy, Suspense, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { skills, type Skill } from "@/content/skills";
import type { Locale } from "@/i18n";

const accentClass: Record<string, string> = { Moss: "bg-[#dcebe2] text-[#1f655e]", Clay: "bg-[#f1e0d2] text-[#9b583b]", Ink: "bg-[#dce5e6] text-[#234a50]" };
const SkillDetailDialog = lazy(() => import("@/components/SkillDetailDialog").then((module) => ({ default: module.SkillDetailDialog })));
const ProviderDialog = lazy(() => import("@/components/ProviderDialog").then((module) => ({ default: module.ProviderDialog })));

export function SkillPanel({ locale }: { locale: Locale }) {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Skill | null>(null);
  const [providerSkill, setProviderSkill] = useState<Skill | null>(null);
  const triggers = useRef<Record<string, HTMLButtonElement | null>>({});
  const filtered = useMemo(() => skills.filter((skill) => Object.values(skill.copy[locale]).join(" ").toLocaleLowerCase().includes(query.toLocaleLowerCase())), [locale, query]);
  const openProvider = (skill: Skill) => { setSelected(null); window.setTimeout(() => setProviderSkill(skill), 0); };
  const restoreTrigger = (slug: string | undefined) => { if (slug) window.requestAnimationFrame(() => triggers.current[slug]?.focus()); };
  const closeDetail = () => { const slug = selected?.slug; setSelected(null); restoreTrigger(slug); };
  const closeProvider = () => { const slug = providerSkill?.slug; setProviderSkill(null); restoreTrigger(slug); };
  return (
    <section className="mx-auto max-w-7xl px-5 py-14 sm:px-8 lg:px-12 lg:py-20">
      <div className="grid gap-10 lg:grid-cols-[0.72fr_1.6fr] lg:gap-20">
        <aside className="lg:sticky lg:top-8 lg:self-start">
          <p className="text-xs font-extrabold uppercase tracking-[0.2em] text-[#327d75]">{t("common.coordinates")} / 06</p>
          <h1 className="mt-4 max-w-md font-serif text-5xl leading-[0.93] tracking-[-0.06em] text-[#122b2c] sm:text-6xl">{t("skills.title")}</h1>
          <p className="mt-5 max-w-sm text-base leading-7 text-[#546865]">{t("skills.body")}</p>
          <div className="relative mt-8"><Search className="pointer-events-none absolute left-4 top-1/2 size-4 -translate-y-1/2 text-[#5a776f]" /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t("skills.search")} className="h-13 w-full rounded-2xl border border-[#cfd9d0] bg-white/75 pl-11 pr-4 text-sm outline-none transition placeholder:text-[#85938e] focus:border-[#267b72] focus:ring-4 focus:ring-[#267b72]/10" /></div>
          <p className="mt-3 text-xs font-bold uppercase tracking-[0.14em] text-[#6e7d77]">{filtered.length} {t("skills.count")}</p>
        </aside>
        <div className="grid gap-4 sm:grid-cols-2">
          {filtered.map((skill, index) => {
            const copy = skill.copy[locale];
            return <article key={skill.slug} className="group relative flex min-h-72 flex-col overflow-hidden rounded-[1.5rem] border border-[#dfe5dc] bg-[#fcfbf7] p-6 shadow-[0_12px_30px_rgba(20,49,45,0.05)] transition duration-200 hover:-translate-y-1 hover:shadow-[0_22px_44px_rgba(20,49,45,0.11)]">
              <div className="flex items-start justify-between gap-3"><span className={`rounded-full px-3 py-1 text-[0.68rem] font-extrabold uppercase tracking-[0.16em] ${accentClass[skill.accent]}`}>{copy.group}</span><span className="font-serif text-sm text-[#95a39c]">0{index + 1}</span></div>
              <h2 className="mt-6 font-serif text-3xl leading-[0.98] tracking-[-0.045em] text-[#163736]">{copy.title}</h2>
              <p className="mt-4 text-sm leading-6 text-[#5a6d68]">{copy.summary}</p>
              <button ref={(element) => { triggers.current[skill.slug] = element; }} onClick={() => setSelected(skill)} className="mt-auto inline-flex items-center gap-2 pt-6 text-sm font-extrabold text-[#1e655e] transition group-hover:gap-3">{t("common.inspect")} <ArrowRight className="size-4" /></button>
            </article>;
          })}
          {!filtered.length && <div className="rounded-[1.5rem] border border-dashed border-[#bdcbc0] p-8 text-sm leading-6 text-[#5a6d68]">{t("skills.noResults")}</div>}
        </div>
      </div>
      <Suspense fallback={null}>
        {selected && <SkillDetailDialog skill={selected} locale={locale} onClose={closeDetail} onOpenProvider={openProvider} />}
        {providerSkill && <ProviderDialog open skill={providerSkill} locale={locale} onClose={closeProvider} />}
      </Suspense>
    </section>
  );
}
