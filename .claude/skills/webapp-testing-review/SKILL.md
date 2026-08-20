---
name: webapp-testing-review
description: Audit and test SoulMap AI web surfaces with rendered-browser evidence. Use for responsive, accessibility, i18n, htmx, Alpine, Search/Ask, static-export, and interaction regressions.
---

# Webapp testing review

Use this skill when a change affects the SoulMap website, static export, shared HTML head, CSS, htmx partials, Alpine state, or browser interactions. Treat rendered behavior as the contract rather than trusting template markup alone.

## Boundaries

This is a local repository workflow skill. It does not define SoulMap conversational doctrine or shipped product knowledge. Keep product truth in `AGENTS.md` and `skills/`, and keep this skill focused on browser verification.

## Workflow

1. Read the changed template, stylesheet, script, and nearest server/test contracts first.
2. If the page is static HTML, inspect the generated artifact directly before interacting.
3. If JavaScript state or server interaction is involved, start the correct local/static server and wait for the page to reach a stable loaded state before inspecting DOM or console output.
4. Use discovered semantic selectors, labels, roles, IDs, and visible text. Do not rely on coordinates when a stable selector exists.
5. Capture evidence for the initial state and every meaningful state transition: screenshots, visible panels, URL, console errors, network/runtime errors, and key computed dimensions.
6. Test the supported browser matrix: 390px mobile, 768px tablet, and 1440px desktop unless the change has a narrower justified scope.
7. For EN/VI surfaces, verify localized labels, placeholders, headings, empty states, errors, modal copy, and internal links in both locales.
8. For Search/Ask or other mode controls, assert that only the active result surface is visible, mode-specific copy changes, Enter does not cause an unsafe navigation, and no stale results remain.
9. For htmx, verify the request target, swap region, loading state, focus behavior, and graceful static fallback. For Alpine, verify initialization, `x-cloak`/conditional visibility, keyboard interaction, Escape/return-focus behavior, and no console errors.
10. Re-export static output with the repository command and run the static verifier whenever a website or asset path changes.

## Accessibility checks

Check keyboard reachability, visible focus, accessible names, landmarks, heading order, form labels, dialog semantics, and live/error regions. Test at least one keyboard-only path for each changed interaction. Confirm there is no horizontal overflow at the mobile width.

## Evidence standard

Report findings before fixes with severity, exact route/viewport/state, observed behavior, expected behavior, and reproduction evidence. Fix only confirmed defects. Add the smallest regression contract that would catch the same defect again, then rerun the browser check and repository validation.

## Completion checklist

- [ ] Initial and changed states were inspected after JavaScript settled.
- [ ] 390px, 768px, and 1440px layouts were checked where applicable.
- [ ] EN and VI copy and routes were checked where applicable.
- [ ] Console, network/runtime, focus, and overflow checks passed.
- [ ] Static export and verifier passed for website changes.
- [ ] Evidence and limitations are recorded without claiming unsupported browser coverage.
