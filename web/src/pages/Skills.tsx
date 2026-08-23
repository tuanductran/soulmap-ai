// Atlas Nội Tâm: Skills page giữ catalog ở một rails layout, không tái sử dụng hero hay centered grid của landing page.
import { useRouterState } from "@tanstack/react-router";
import { SkillPanel } from "@/components/SkillPanel";
import { localeFromPath } from "@/lib/locale";

export default function SkillsPage() {
  const pathname = useRouterState({ select: (state) => state.location.pathname });
  return <SkillPanel locale={localeFromPath(pathname)} />;
}
