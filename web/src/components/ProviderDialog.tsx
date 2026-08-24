// Atlas Nội Tâm: Dialog chỉ mở tuyến tiếp theo, luôn cho phép copy prompt và quay lại mà không giam người dùng trong UI.
import { Dialog, DialogPanel, DialogTitle } from "@headlessui/react";
import { ArrowUpRight, Check, Copy, X } from "lucide-react";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import type { Skill } from "@/content/skills";
import { rawBundleUrl } from "@/content/skills";
import type { Locale } from "@/i18n";

type ProviderDialogProps = {
  open: boolean;
  skill: Skill | null;
  locale: Locale;
  onClose: () => void;
};

export function ProviderDialog({ open, skill, locale, onClose }: ProviderDialogProps) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  if (!skill) return null;
  const copy = skill.copy[locale];
  const prompt = `Use the SoulMap ${copy.title} layer as a careful reference. Context: ${copy.useWhen}\n\nPlease reflect what I share without diagnosing, predicting, or taking over the meaning.`;
  const copyPrompt = async () => {
    await navigator.clipboard?.writeText(prompt);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  };
  return (
    <Dialog open={open} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-[#122b2c]/45 backdrop-blur-sm" aria-hidden="true" />
      <div className="fixed inset-0 grid place-items-end p-3 sm:place-items-center sm:p-6">
        <DialogPanel className="w-full max-w-xl rounded-[1.75rem] border border-white/70 bg-[#fbfaf5] p-6 shadow-[0_28px_80px_rgba(18,43,44,0.28)] sm:p-8">
          <div className="flex items-start justify-between gap-6">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#1d5f58]">
                {copy.group}
              </p>
              <DialogTitle className="mt-3 font-serif text-3xl leading-none tracking-[-0.045em] text-[#122b2c]">
                {t("skills.dialogTitle")}
              </DialogTitle>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="grid size-10 place-items-center rounded-full border border-[#d8dfd8] text-[#305a58] transition hover:bg-[#eaf0eb]"
              aria-label={t("common.close")}
            >
              <X className="size-4" />
            </button>
          </div>
          <p className="mt-5 max-w-lg text-sm leading-6 text-[#526565]">{t("skills.dialogBody")}</p>
          <p className="mt-4 text-xs font-semibold leading-5 text-[#52706b]">
            {t("skills.promptLanguage")}
          </p>
          <div className="mt-6 rounded-2xl border border-[#dce5de] bg-white/70 p-4 text-sm leading-6 text-[#294242]">
            {prompt}
          </div>
          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={copyPrompt}
              className="inline-flex min-h-12 items-center justify-center gap-2 rounded-full bg-[#267b72] px-5 text-sm font-bold text-white transition hover:bg-[#1c625b] active:scale-[0.98]"
            >
              {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
              {copied ? t("common.copied") : t("common.copy")}
            </button>
            <a
              href={rawBundleUrl(skill, locale)}
              target="_blank"
              rel="noreferrer"
              className="inline-flex min-h-12 items-center justify-center gap-2 rounded-full border border-[#bfcfc4] px-5 text-sm font-bold text-[#1e5550] transition hover:bg-[#eaf0eb]"
            >
              {t("skills.raw")}
              <ArrowUpRight className="size-4" />
            </a>
          </div>
          <div className="mt-4 flex flex-wrap gap-2 text-xs font-semibold text-[#526565]">
            <a
              href="https://claude.ai/new"
              target="_blank"
              rel="noreferrer"
              className="rounded-full border border-[#d8dfd8] px-3 py-2 hover:bg-white"
            >
              Claude <ArrowUpRight className="ml-1 inline size-3" />
            </a>
            <a
              href="https://chatgpt.com/"
              target="_blank"
              rel="noreferrer"
              className="rounded-full border border-[#d8dfd8] px-3 py-2 hover:bg-white"
            >
              ChatGPT <ArrowUpRight className="ml-1 inline size-3" />
            </a>
          </div>
        </DialogPanel>
      </div>
    </Dialog>
  );
}
