// Bản đồ Biên Độ: Documents chia metadata rail và reading field với Info/Skills, nhưng giữ measure đọc riêng cho nội dung dài.
import { Disclosure, DisclosureButton, DisclosurePanel } from "@headlessui/react";
import { useRouterState } from "@tanstack/react-router";
import { ChevronDown, CircleAlert } from "lucide-react";
import { useTranslation } from "react-i18next";
import { type DocumentKind, documentCopy } from "@/content/documents";
import { localeFromPath } from "@/lib/locale";

export function DocumentPage({ kind }: { kind: DocumentKind }) {
  const { t } = useTranslation();
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  const copy = documentCopy[localeFromPath(pathname)][kind];
  return (
    <section className="section-pad bg-[#fbfaf5]">
      <div className="site-frame page-layout">
        <aside className="page-rail">
          <p className="eyebrow">{copy.eyebrow}</p>
          <div className="survey-rule" />
        </aside>
        <article className="page-field max-w-4xl">
          <h1 className="page-title">{copy.title}</h1>
          <p className="reading-lede">{copy.lede}</p>
          {kind === "faq" ? (
            <div className="mt-10 divide-y divide-[#d6ded7] border-y border-[#d6ded7]">
              {copy.faq?.map(([question, answer]) => (
                <Disclosure key={question}>
                  {({ open }) => (
                    <div className="py-4 sm:py-5">
                      <DisclosureButton className="flex w-full items-center justify-between gap-6 text-left text-base font-extrabold text-[#214641]">
                        <span>{question}</span>
                        <ChevronDown
                          className={`size-5 shrink-0 text-[#28756d] transition duration-200 ${open ? "rotate-180" : ""}`}
                        />
                      </DisclosureButton>
                      <DisclosurePanel className="max-w-2xl pt-4 text-sm leading-7 text-[#536965]">
                        {answer}
                      </DisclosurePanel>
                    </div>
                  )}
                </Disclosure>
              ))}
            </div>
          ) : (
            <div className="mt-10 grid gap-3">
              {copy.sections?.map((section) => (
                <div
                  key={section.title}
                  className="surface-card grid gap-4 rounded-xl p-5 sm:grid-cols-[5rem_1fr] sm:p-6"
                >
                  <span className="font-serif text-4xl text-[#5d756b]">{section.label}</span>
                  <div>
                    <h2 className="text-lg font-extrabold tracking-[-0.025em] text-[#244a47]">
                      {section.title}
                    </h2>
                    <p className="mt-3 max-w-2xl text-sm leading-7 text-[#536965]">
                      {section.body}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
          <div className="mt-10 flex gap-3 rounded-xl border border-[#cfded1] bg-[#e8f0e9] p-5 text-sm leading-6 text-[#35544f]">
            <CircleAlert className="mt-0.5 size-5 shrink-0 text-[#267b72]" />
            {t("info.note")}
          </div>
        </article>
      </div>
    </section>
  );
}
