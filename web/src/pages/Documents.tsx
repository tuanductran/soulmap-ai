// Atlas Nội Tâm: Các route văn bản dùng document rail và Disclosure accessible, giữ nội dung dài có cấu trúc thay vì card-grid lặp lại.
import { Disclosure, DisclosureButton, DisclosurePanel } from "@headlessui/react";
import { ChevronDown, CircleAlert } from "lucide-react";
import { useRouterState } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { documentCopy, type DocumentKind } from "@/content/documents";
import { localeFromPath } from "@/lib/locale";

export function DocumentPage({ kind }: { kind: DocumentKind }) {
  const { t } = useTranslation();
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const copy = documentCopy[localeFromPath(pathname)][kind];
  return <section className="relative overflow-hidden bg-[#fbfaf5] px-5 py-20 sm:px-8 lg:px-12 lg:py-28"><div className="mx-auto grid max-w-7xl gap-16 lg:grid-cols-[0.65fr_1.35fr]"><aside><p className="text-xs font-extrabold uppercase tracking-[0.2em] text-[#327d75]">{copy.eyebrow}</p><div className="mt-8 h-px w-24 bg-[#b46d4c]" /></aside><article className="max-w-4xl"><h1 className="font-serif text-6xl leading-[0.86] tracking-[-0.065em] text-[#173837] sm:text-7xl">{copy.title}</h1><p className="mt-10 max-w-2xl text-xl leading-9 text-[#516863]">{copy.lede}</p>{kind === "faq" ? <div className="mt-14 divide-y divide-[#dfe5dc] border-y border-[#dfe5dc]">{copy.faq?.map(([question, answer]) => <Disclosure key={question}>{({ open }) => <div className="py-5"><DisclosureButton className="flex w-full items-center justify-between gap-6 text-left text-base font-extrabold text-[#214641]"><span>{question}</span><ChevronDown className={`size-5 shrink-0 text-[#28756d] transition ${open ? "rotate-180" : ""}`} /></DisclosureButton><DisclosurePanel className="max-w-2xl pt-4 text-sm leading-7 text-[#536965]">{answer}</DisclosurePanel></div>}</Disclosure>)}</div> : <div className="mt-14 grid gap-4">{copy.sections?.map((section) => <div key={section.title} className="grid gap-4 rounded-[1.5rem] border border-[#dfe5dc] bg-white/70 p-6 sm:grid-cols-[6rem_1fr]"><span className="font-serif text-4xl text-[#9caf9f]">{section.label}</span><div><h2 className="text-lg font-extrabold tracking-[-0.025em] text-[#244a47]">{section.title}</h2><p className="mt-3 max-w-2xl text-sm leading-7 text-[#536965]">{section.body}</p></div></div>)}</div>}<div className="mt-10 flex gap-3 rounded-2xl border border-[#dfe5dc] bg-[#eaf0eb] p-5 text-sm leading-6 text-[#35544f]"><CircleAlert className="mt-0.5 size-5 shrink-0 text-[#267b72]" />{t("info.note")}</div></article></div></section>;
}
