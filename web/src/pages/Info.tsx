// Atlas Nội Tâm: Trang thông tin dùng một document rail thoáng, phục vụ clarity thay vì thêm nhiều khuôn card.
import { ArrowRight, CircleAlert } from "lucide-react";
import { Link, useRouterState } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";
import { localeFromPath, localizedPath } from "@/lib/locale";

export function InfoPage({ kind }: { kind: "about" | "faq" }) {
  const { t } = useTranslation();
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const locale = localeFromPath(pathname);
  const key = `info.${kind}` as const;
  return <section className="relative overflow-hidden bg-[#fbfaf5] px-5 py-20 sm:px-8 lg:px-12 lg:py-28"><div className="mx-auto grid max-w-7xl gap-16 lg:grid-cols-[0.65fr_1.35fr]"><aside><p className="text-xs font-extrabold uppercase tracking-[0.2em] text-[#327d75]">{t(`${key}.eyebrow`)}</p><div className="mt-8 h-px w-24 bg-[#b46d4c]" /></aside><article className="max-w-4xl"><h1 className="font-serif text-6xl leading-[0.86] tracking-[-0.065em] text-[#173837] sm:text-7xl">{t(`${key}.title`)}</h1><p className="mt-10 max-w-2xl text-xl leading-9 text-[#516863]">{t(`${key}.body`)}</p><div className="mt-12 rounded-[1.75rem] border border-[#dfe5dc] bg-[#eaf0eb] p-7"><CircleAlert className="size-5 text-[#267b72]" /><p className="mt-4 max-w-2xl text-base leading-7 text-[#36524d]">{t("info.note")}</p></div><Link to={localizedPath("/skills", locale)} className="mt-10 inline-flex items-center gap-2 text-sm font-extrabold text-[#1e655e] hover:gap-3">{t("common.explore")} <ArrowRight className="size-4" /></Link></article></div></section>;
}
