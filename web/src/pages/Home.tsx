// Atlas Nội Tâm: Home page dùng hero có trọng tâm lệch và các coordinate block thay cho landing-page card grid mặc định.

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
      <section className="relative isolate overflow-hidden border-b border-[#d7dfd5] bg-[#e8eee8]">
        <img
          src={heroImage}
          alt=""
          className="absolute inset-0 -z-10 h-full w-full object-cover object-right opacity-80"
        />
        <div className="absolute inset-0 -z-10 bg-gradient-to-r from-[#f8f7f0] via-[#f8f7f0]/85 to-transparent" />
        <div className="mx-auto grid min-h-[620px] max-w-7xl items-end px-5 py-16 sm:px-8 sm:py-20 lg:grid-cols-[1.15fr_0.85fr] lg:px-12 lg:py-24">
          <div className="max-w-3xl">
            <p className="flex items-center gap-2 text-xs font-extrabold uppercase tracking-[0.2em] text-[#1d5f58]">
              <MapPinned className="size-4" /> {t("home.eyebrow")}
            </p>
            <h1 className="mt-6 font-serif text-[clamp(3.5rem,8vw,7.75rem)] leading-[0.84] tracking-[-0.075em] text-[#112f30]">
              {t("home.title")}
            </h1>
            <p className="mt-8 max-w-xl text-lg leading-8 text-[#405c58]">{t("home.body")}</p>
            <div className="mt-10 flex flex-wrap gap-3">
              <Link
                to={localizedPath("/skills", locale)}
                className="inline-flex min-h-13 items-center gap-2 rounded-full bg-[#23786f] px-6 text-sm font-extrabold text-white transition hover:bg-[#195b55] active:scale-[0.98]"
              >
                {t("home.primary")} <ArrowRight className="size-4" />
              </Link>
              <Link
                to={localizedPath("/about", locale)}
                className="inline-flex min-h-13 items-center gap-2 rounded-full border border-[#b7c9bd] bg-[#f8f7f0]/80 px-6 text-sm font-extrabold text-[#225b55] transition hover:bg-white active:scale-[0.98]"
              >
                {t("home.secondary")}
              </Link>
            </div>
          </div>
          <div className="hidden justify-self-end lg:block">
            <div className="w-52 border-l border-[#5a877d] pl-5 text-sm leading-6 text-[#3e6660]">
              <span className="block text-xs font-bold uppercase tracking-[0.18em] text-[#1d5f58]">
                {t("home.fieldNoteLabel")}
              </span>
              <p className="mt-3">{t("home.fieldNoteBody")}</p>
            </div>
          </div>
        </div>
      </section>
      <section className="relative overflow-hidden bg-[#fbfaf5] py-20 sm:py-28">
        <img
          src={textureImage}
          alt=""
          className="pointer-events-none absolute right-[-5%] top-0 h-full w-1/2 object-cover opacity-35"
        />
        <div className="relative mx-auto max-w-7xl px-5 sm:px-8 lg:px-12">
          <div className="grid gap-12 lg:grid-cols-[0.8fr_1.2fr]">
            <div>
              <p className="text-xs font-extrabold uppercase tracking-[0.2em] text-[#7f3e29]">
                01 — Orientation
              </p>
              <h2 className="mt-5 max-w-md font-serif text-5xl leading-[0.92] tracking-[-0.055em] text-[#173837]">
                {t("home.mapTitle")}
              </h2>
              <p className="mt-6 max-w-md text-base leading-7 text-[#59706b]">
                {t("home.mapBody")}
              </p>
            </div>
            <div className="grid gap-px overflow-hidden rounded-[1.75rem] border border-[#dfe5dc] bg-[#dfe5dc] sm:grid-cols-3">
              {(t("home.steps", { returnObjects: true }) as string[]).map((step, index) => (
                <div key={step} className="min-h-48 bg-[#fbfaf5] p-6">
                  <span className="font-serif text-4xl text-[#5d756b]">0{index + 1}</span>
                  <p className="mt-12 text-lg font-bold tracking-[-0.025em] text-[#244a47]">
                    {step}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
      <section className="bg-[#e7eee8] py-20 sm:py-28">
        <div className="mx-auto grid max-w-7xl gap-10 px-5 sm:px-8 lg:grid-cols-[1fr_1fr] lg:items-center lg:px-12">
          <div className="relative overflow-hidden rounded-[2rem] border border-[#cad8cf] bg-[#f7f6ef] shadow-[0_26px_70px_rgba(20,49,45,0.13)]">
            <img
              src={fieldImage}
              alt={t("home.fieldImageAlt")}
              className="aspect-[3/2] w-full object-cover"
            />
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#123433]/80 to-transparent p-7 text-white">
              <p className="text-xs font-bold uppercase tracking-[0.18em]">
                {t("home.evidenceLabel")}
              </p>
            </div>
          </div>
          <div className="lg:pl-10">
            <p className="text-xs font-extrabold uppercase tracking-[0.2em] text-[#1d5f58]">
              {t("home.workingSurface")}
            </p>
            <h2 className="mt-5 max-w-lg font-serif text-5xl leading-[0.92] tracking-[-0.055em] text-[#173837]">
              {t("home.fieldTitle")}
            </h2>
            <p className="mt-6 max-w-xl text-base leading-7 text-[#526965]">
              {t("home.fieldBody")}
            </p>
            <Link
              to={localizedPath("/skills", locale)}
              className="mt-8 inline-flex items-center gap-2 text-sm font-extrabold text-[#1d655d] hover:gap-3"
            >
              {t("common.explore")} <ArrowDownRight className="size-4" />
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
