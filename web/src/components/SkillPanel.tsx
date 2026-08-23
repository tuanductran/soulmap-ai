// Atlas Nội Tâm: Catalog ưu tiên mô tả scope/boundary và thao tác tại chỗ, thay vì biến skill thành card marketing đồng nhất.
import { Dialog, DialogPanel, DialogTitle } from "@headlessui/react";
import { ArrowRight, Compass, Search, X } from "lucide-react";
import { useMemo, useState } from "react";
import { useTranslation } from "react-i18next";
import { ProviderDialog } from "@/components/ProviderDialog";
import { skills, type Skill } from "@/content/skills";
import type { Locale } from "@/i18n";

const accentClass: Record<string, string> = { Moss: "bg-[#dcebe2] text-[#1f655e]", Clay: "bg-[#f1e0d2] text-[#9b583b]", Ink: "bg-[#dce5e6] text-[#234a50]" };

export function SkillPanel({ locale }: { locale: Locale }) {
  const { t } = useTranslation();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Skill | null>(null);
  const [providerSkill, setProviderSkill] = useState<Skill | null>(null);
  const filtered = useMemo(() => skills.filter((skill) => Object.values(skill.copy[locale]).join(" ").toLocaleLowerCase().includes(query.toLocaleLowerCase())), [locale, query]);
  const openProvider = (skill: Skill) => { setSelected(null); window.setTimeout(() => setProviderSkill(skill), 0); };
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
              <button onClick={() => setSelected(skill)} className="mt-auto inline-flex items-center gap-2 pt-6 text-sm font-extrabold text-[#1e655e] transition group-hover:gap-3">{t("common.inspect")} <ArrowRight className="size-4" /></button>
            </article>;
          })}
          {!filtered.length && <div className="rounded-[1.5rem] border border-dashed border-[#bdcbc0] p-8 text-sm leading-6 text-[#5a6d68]">{t("skills.noResults")}</div>}
        </div>
      </div>
      <Dialog open={Boolean(selected)} onClose={() => setSelected(null)} className="relative z-40">
        <div className="fixed inset-0 bg-[#122b2c]/45 backdrop-blur-sm" />
        <div className="fixed inset-0 overflow-y-auto p-3 sm:p-6"><div className="grid min-h-full place-items-end sm:place-items-center"><DialogPanel className="w-full max-w-2xl rounded-[1.75rem] border border-white/70 bg-[#fbfaf5] p-6 shadow-2xl sm:p-9">{selected && <>
          <div className="flex items-start justify-between gap-6"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-[#327d75]">{selected.copy[locale].group}</p><DialogTitle className="mt-3 font-serif text-4xl leading-none tracking-[-0.055em] text-[#122b2c]">{selected.copy[locale].title}</DialogTitle></div><button onClick={() => setSelected(null)} className="grid size-10 place-items-center rounded-full border border-[#d8dfd8] hover:bg-[#eaf0eb]" aria-label={t("common.close")}><X className="size-4" /></button></div>
          <div className="mt-8 grid gap-6 border-t border-[#dfe5dc] pt-7 sm:grid-cols-2"><div><p className="text-xs font-bold uppercase tracking-[0.15em] text-[#327d75]">{t("skills.useWhen")}</p><p className="mt-3 text-sm leading-6 text-[#445a56]">{selected.copy[locale].useWhen}</p></div><div><p className="text-xs font-bold uppercase tracking-[0.15em] text-[#9b583b]">{t("skills.boundary")}</p><p className="mt-3 text-sm leading-6 text-[#445a56]">{selected.copy[locale].boundary}</p></div></div>
          <div className="mt-6 rounded-2xl bg-[#e8f0ea] p-5"><p className="text-xs font-bold uppercase tracking-[0.15em] text-[#327d75]">{t("skills.bestFor")}</p><p className="mt-2 text-sm leading-6 text-[#35544f]">{selected.copy[locale].bestFor}</p></div>
          <button onClick={() => openProvider(selected)} className="mt-7 inline-flex min-h-12 items-center gap-2 rounded-full bg-[#267b72] px-5 text-sm font-bold text-white transition hover:bg-[#1c625b] active:scale-[0.98]"><Compass className="size-4" />{t("skills.openPrompt")}</button>
        </>}</DialogPanel></div></div>
      </Dialog>
      <ProviderDialog open={Boolean(providerSkill)} skill={providerSkill} locale={locale} onClose={() => setProviderSkill(null)} />
    </section>
  );
}
