// Bản đồ Biên Độ: Info dùng cùng metadata rail/reading field với Documents để ranh giới và mô tả không trở thành một layout riêng.

import { Link, useRouterState } from "@tanstack/react-router";
import { ArrowRight, CircleAlert } from "lucide-react";
import { useTranslation } from "react-i18next";
import { localeFromPath, localizedPath } from "@/lib/locale";

export function InfoPage({ kind }: { kind: "about" | "faq" }) {
  const { t } = useTranslation();
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const locale = localeFromPath(pathname);
  const key = `info.${kind}` as const;
  return (
    <section className="section-pad bg-[#fbfaf5]">
      <div className="site-frame page-layout">
        <aside className="page-rail">
          <p className="eyebrow">{t(`${key}.eyebrow`)}</p>
          <div className="survey-rule" />
        </aside>
        <article className="page-field max-w-4xl">
          <h1 className="page-title">{t(`${key}.title`)}</h1>
          <p className="reading-lede">{t(`${key}.body`)}</p>
          <div className="mt-10 rounded-xl border border-[#cfded1] bg-[#e8f0e9] p-6 sm:p-7">
            <CircleAlert className="size-5 text-[#267b72]" />
            <p className="mt-4 max-w-2xl text-base leading-7 text-[#36524d]">{t("info.note")}</p>
          </div>
          <Link
            to={localizedPath("/skills", locale)}
            className="mt-10 inline-flex items-center gap-2 text-sm font-extrabold text-[#1e655e] hover:gap-3"
          >
            {t("common.explore")} <ArrowRight className="size-4" />
          </Link>
        </article>
      </div>
    </section>
  );
}
