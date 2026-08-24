// Atlas Nội Tâm: Router dùng locale prefix tùy chọn qua các route song song, English không mang /en/ và static SPA vẫn giữ URL rõ ràng.
import { createRootRoute, createRoute, createRouter } from "@tanstack/react-router";
import { lazy, Suspense } from "react";
import { SiteShell } from "@/components/SiteShell";

const HomePage = lazy(() => import("@/pages/Home"));
const SkillsPage = lazy(() => import("@/pages/Skills"));
const AboutPage = lazy(() =>
  import("@/pages/Info").then((module) => ({ default: () => <module.InfoPage kind="about" /> })),
);
const DocumentPage = lazy(() =>
  import("@/pages/Documents").then((module) => ({ default: module.DocumentPage })),
);

function RouteChunk({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<div className="min-h-[60vh] bg-[#f7f6ef]" />}>{children}</Suspense>;
}

const rootRoute = createRootRoute({ component: SiteShell });
const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: () => (
    <RouteChunk>
      <HomePage />
    </RouteChunk>
  ),
});
const skillsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "skills",
  component: () => (
    <RouteChunk>
      <SkillsPage />
    </RouteChunk>
  ),
});
const aboutRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "about",
  component: () => (
    <RouteChunk>
      <AboutPage />
    </RouteChunk>
  ),
});
const faqRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "faq",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="faq" />
    </RouteChunk>
  ),
});
const howRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "how-it-works",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="how" />
    </RouteChunk>
  ),
});
const boundariesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "boundaries",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="boundaries" />
    </RouteChunk>
  ),
});
const notesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "notes",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="notes" />
    </RouteChunk>
  ),
});
const downloadRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "download",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="download" />
    </RouteChunk>
  ),
});
const privacyRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "privacy",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="privacy" />
    </RouteChunk>
  ),
});
const localeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "$locale",
  beforeLoad: ({ params }) => {
    if (params.locale !== "vi" && params.locale !== "ko") throw new Error("Unsupported locale");
  },
});
const localeHomeRoute = createRoute({
  getParentRoute: () => localeRoute,
  path: "/",
  component: () => (
    <RouteChunk>
      <HomePage />
    </RouteChunk>
  ),
});
const localeSkillsRoute = createRoute({
  getParentRoute: () => localeRoute,
  path: "skills",
  component: () => (
    <RouteChunk>
      <SkillsPage />
    </RouteChunk>
  ),
});
const localeAboutRoute = createRoute({
  getParentRoute: () => localeRoute,
  path: "about",
  component: () => (
    <RouteChunk>
      <AboutPage />
    </RouteChunk>
  ),
});
const localeFaqRoute = createRoute({
  getParentRoute: () => localeRoute,
  path: "faq",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="faq" />
    </RouteChunk>
  ),
});
const localeHowRoute = createRoute({
  getParentRoute: () => localeRoute,
  path: "how-it-works",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="how" />
    </RouteChunk>
  ),
});
const localeBoundariesRoute = createRoute({
  getParentRoute: () => localeRoute,
  path: "boundaries",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="boundaries" />
    </RouteChunk>
  ),
});
const localeNotesRoute = createRoute({
  getParentRoute: () => localeRoute,
  path: "notes",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="notes" />
    </RouteChunk>
  ),
});
const localeDownloadRoute = createRoute({
  getParentRoute: () => localeRoute,
  path: "download",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="download" />
    </RouteChunk>
  ),
});
const localePrivacyRoute = createRoute({
  getParentRoute: () => localeRoute,
  path: "privacy",
  component: () => (
    <RouteChunk>
      <DocumentPage kind="privacy" />
    </RouteChunk>
  ),
});

const routeTree = rootRoute.addChildren([
  homeRoute,
  skillsRoute,
  aboutRoute,
  faqRoute,
  howRoute,
  boundariesRoute,
  notesRoute,
  downloadRoute,
  privacyRoute,
  localeRoute.addChildren([
    localeHomeRoute,
    localeSkillsRoute,
    localeAboutRoute,
    localeFaqRoute,
    localeHowRoute,
    localeBoundariesRoute,
    localeNotesRoute,
    localeDownloadRoute,
    localePrivacyRoute,
  ]),
]);

export const router = createRouter({
  routeTree,
  basepath: import.meta.env.BASE_URL.replace(/\/$/, "") || "/",
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
