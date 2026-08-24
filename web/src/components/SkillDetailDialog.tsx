// Atlas Nội Tâm: Detail dialog là nhánh tương tác hiếm; chỉ tải khi người dùng chọn một Skill.
import { Dialog, DialogPanel, DialogTitle } from "@headlessui/react";
import { Compass, X } from "lucide-react";
import { useTranslation } from "react-i18next";
import type { Skill } from "@/content/skills";
import type { Locale } from "@/i18n";

type SkillDetailDialogProps = {
  skill: Skill;
  locale: Locale;
  onClose: () => void;
  onOpenProvider: (skill: Skill) => void;
};

export function SkillDetailDialog({
  skill,
  locale,
  onClose,
  onOpenProvider,
}: SkillDetailDialogProps) {
  const { t } = useTranslation();
  const copy = skill.copy[locale];

  return (
    <Dialog open onClose={onClose} className="relative z-40">
      <div className="fixed inset-0 bg-[#122b2c]/45 backdrop-blur-sm" />
      <div className="fixed inset-0 overflow-y-auto p-3 sm:p-6">
        <div className="grid min-h-full place-items-end sm:place-items-center">
          <DialogPanel className="w-full max-w-2xl rounded-[1.75rem] border border-white/70 bg-[#fbfaf5] p-6 shadow-2xl sm:p-9">
            <div className="flex items-start justify-between gap-6">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#1d5f58]">
                  {copy.group}
                </p>
                <DialogTitle className="mt-3 font-serif text-4xl leading-none tracking-[-0.055em] text-[#122b2c]">
                  {copy.title}
                </DialogTitle>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="grid size-10 place-items-center rounded-full border border-[#d8dfd8] hover:bg-[#eaf0eb]"
                aria-label={t("common.close")}
              >
                <X className="size-4" />
              </button>
            </div>
            <div className="mt-8 grid gap-6 border-t border-[#dfe5dc] pt-7 sm:grid-cols-2">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#1d5f58]">
                  {t("skills.useWhen")}
                </p>
                <p className="mt-3 text-sm leading-6 text-[#445a56]">{copy.useWhen}</p>
              </div>
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#7f3e29]">
                  {t("skills.boundary")}
                </p>
                <p className="mt-3 text-sm leading-6 text-[#445a56]">{copy.boundary}</p>
              </div>
            </div>
            <div className="mt-6 rounded-2xl bg-[#e8f0ea] p-5">
              <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#1d5f58]">
                {t("skills.bestFor")}
              </p>
              <p className="mt-2 text-sm leading-6 text-[#35544f]">{copy.bestFor}</p>
            </div>
            <button
              type="button"
              onClick={() => onOpenProvider(skill)}
              className="mt-7 inline-flex min-h-12 items-center gap-2 rounded-full bg-[#267b72] px-5 text-sm font-bold text-white transition hover:bg-[#1c625b] active:scale-[0.98]"
            >
              <Compass className="size-4" />
              {t("skills.openPrompt")}
            </button>
          </DialogPanel>
        </div>
      </div>
    </Dialog>
  );
}
