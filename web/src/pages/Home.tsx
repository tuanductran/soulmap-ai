// Bản đồ Biên Độ: Home dùng editorial split-field, coordinate rail và nhịp section cố định thay vì hero/card system riêng lẻ.

import { Link, useRouterState } from "@tanstack/react-router";
import { ArrowDownRight, ArrowRight, MapPinned } from "lucide-react";
import { useTranslation } from "react-i18next";
import { localeFromPath, localizedPath } from "@/lib/locale";

const asset = (file: string) => `${import.meta.env.BASE_URL}images/${file}`;
const heroImage = asset("hero.webp");
const fieldImage = asset("field-notes.webp");
const textureImage = asset("contours.webp");

export default function HomePage() {
  const { t } = useTranslation();
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const locale = localeFromPath(pathname);
  return (
    <>
      <section className="border-b border-[#d6ded7] bg-[#fbfaf5]">
        <div className="site-frame grid lg:min-h-[41rem] lg:grid-cols-12">
          <div className="flex flex-col justify-end py-16 sm:py-20 lg:col-span-7 lg:py-24 lg:pr-12">
            <p className="eyebrow flex items-center gap-2">
              <MapPinned className="size-4" /> {t("home.eyebrow")}
            </p>
            <h1 className="mt-6 max-w-3xl font-serif text-[clamp(3.5rem,6.7vw,7.25rem)] leading-[0.87] tracking-[-0.075em] text-[#173837]">
              {t("home.title")}
            </h1>
            <p className="mt-7 max-w-xl text-[1.0625rem] leading-8 text-[#506863]">
              {t("home.body")}
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Link to={localizedPath("/skills", locale)} className="action-primary">
                {t("home.primary")} <ArrowRight className="size-4" />
              </Link>
              <Link to={localizedPath("/about", locale)} className="action-secondary">
                {t("home.secondary")}
              </Link>
            </div>
          </div>
          <div className="relative min-h-72 overflow-hidden border-t border-[#d6ded7] lg:col-span-5 lg:min-h-0 lg:border-l lg:border-t-0">
            <img
              src={heroImage}
              alt=""
              className="absolute inset-0 h-full w-full object-cover object-right"
            />
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-[#173837]/75 via-[#173837]/20 to-transparent p-6 sm:p-8 lg:p-10">
              <span className="block text-[0.6875rem] font-extrabold uppercase tracking-[0.18em] text-[#d7eee2]">
                {t("home.fieldNoteLabel")}
              </span>
              <p className="mt-3 max-w-xs text-sm leading-6 text-white/90">
                {t("home.fieldNoteBody")}
              </p>
            </div>
          </div>
        </div>
      </section>
      <section className="relative overflow-hidden border-b border-[#d6ded7] bg-[#f7f6ef]">
        <img
          src={textureImage}
          alt=""
          className="pointer-events-none absolute right-[-5%] top-0 h-full w-1/2 object-cover opacity-35"
        />
        <div className="site-frame relative section-pad">
          <div className="page-layout">
            <div className="page-rail">
              <p className="eyebrow text-[#9b5540]">01 / Orientation</p>
              <div className="survey-rule" />
            </div>
            <div className="page-field">
              <h2 className="section-title max-w-2xl">{t("home.mapTitle")}</h2>
              <p className="reading-lede max-w-xl">{t("home.mapBody")}</p>
              <div className="mt-10 grid overflow-hidden rounded-xl border border-[#d6ded7] bg-[#d6ded7] sm:grid-cols-3">
                {(t("home.steps", { returnObjects: true }) as string[]).map((step, index) => (
                  <div key={step} className="min-h-36 bg-[#fbfaf5] p-5 sm:min-h-44 sm:p-6">
                    <span className="font-serif text-3xl text-[#6a8178]">0{index + 1}</span>
                    <p className="mt-7 text-base font-extrabold tracking-[-0.02em] text-[#244a47] sm:mt-9">
                      {step}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
      <section className="border-b border-[#d6ded7] bg-[#e7efe8]">
        <div className="site-frame section-pad">
          <div className="page-layout">
            <div className="page-rail">
              <p className="eyebrow">{t("home.evidenceLabel")}</p>
              <div className="survey-rule bg-[#1d6a62]" />
            </div>
            <div className="page-field grid gap-10 lg:grid-cols-2 lg:items-center">
              <div>
                <p className="eyebrow">{t("home.workingSurface")}</p>
                <h2 className="section-title mt-5">{t("home.fieldTitle")}</h2>
                <p className="reading-lede mt-6 text-[#526965]">{t("home.fieldBody")}</p>
                <Link
                  to={localizedPath("/skills", locale)}
                  className="mt-8 inline-flex items-center gap-2 text-sm font-extrabold text-[#1d655d] transition hover:gap-3"
                >
                  {t("common.explore")} <ArrowDownRight className="size-4" />
                </Link>
              </div>
              <div className="relative overflow-hidden rounded-xl border border-[#c7d7ca] bg-[#f7f6ef] shadow-[0_18px_46px_rgba(20,49,45,0.1)]">
                <img
                  src={fieldImage}
                  alt={t("home.fieldImageAlt")}
                  className="aspect-[3/2] w-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
