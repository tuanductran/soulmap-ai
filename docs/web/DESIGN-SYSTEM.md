# Website design system

**Status:** Phase 2 proposal, approved for implementation. **Date:** 2026-08-30.

The design has one job: make a visitor feel they are reading something
considered, honest, and unhurried, and never that they are being sold a
companion.

## Design principles

Each one is traceable to existing doctrine rather than to taste.

| Principle | Source |
| --- | --- |
| Editorial, not promotional | `SOULMAP.md`: SoulMap is not a guru or authority. A page that sells behaves like one |
| Calm density over spectacle | The content is genuinely dense. Respecting the reader means presenting it plainly, not decorating it |
| Restraint as a signal of trust | `skills/brand/competitive-differentiation.md` positions SoulMap against engagement-optimized companions. The interface should not use engagement patterns |
| Quiet by default | Motion, color, and emphasis are used sparingly, so that when something is emphasized it means something |
| Legible before beautiful | Long-form reflective prose in two languages is the primary content type |

Explicitly avoided, because each would contradict the product: AI gradients,
neon purple, glassmorphism, galaxy or nebula imagery, crystal and chakra
iconography, testimonial walls, usage counters, streak indicators, and any
call-to-action implying the visitor should come back often.

## Relationship to the reference CSS

`caezium/skills/site/style.css` is MIT licensed and structurally sound. What
carries over is **architecture**: a `:root` custom-property token block, a
three-role type system, a `prefers-color-scheme` override that redefines only
tokens, `clamp()` for fluid display type, `color-mix()` for derived states, and
`[hidden]` for filtering that degrades without JavaScript.

What does not carry over is every value that constitutes its identity: the
`#9a3412` burnt-orange accent, the Newsreader and Inter and JetBrains Mono
pairing, the `.brand` treatment, and all source-specific copy and class naming.

Because structural patterns are borrowed from an MIT-licensed project, the
website source carries a short attribution notice naming the project and its
license. This is recorded here so the obligation is not lost later.

## Tokens

All tokens are CSS custom properties on `:root`, prefixed `--sm-`. Dark mode
redefines only the color tokens.

### Color

A warm-neutral paper ground with a single desaturated accent. The accent is deep
teal: it reads as considered and credible, it is far from both the AI-purple
cliche and the reference site's orange, and it holds contrast well in both
schemes.

```text
--sm-bg              #faf9f6   warm paper, not clinical white
--sm-surface         #ffffff
--sm-ink             #1c1b18   near-black with warmth
--sm-ink-soft        #4a4740   body prose
--sm-muted           #86827a   metadata, counts
--sm-line            #e5e1d8
--sm-line-soft       #f0ede5
--sm-accent          #1f5f5b   deep teal
--sm-accent-soft     #2d7d78
--sm-accent-wash     color-mix(in srgb, var(--sm-accent) 8%, transparent)
```

Dark scheme redefines the same nine names against a warm near-black
(`#15140f` ground, `#1d1c16` surface), lifting the accent to `#5fb3ac` so it
keeps contrast without glowing.

Contrast targets: body text at or above 7:1 (WCAG AAA), secondary text and the
accent on ground at or above 4.5:1 (AA). Verified during Phase 8, not assumed.

### Typography

The type choice is where the Vietnamese requirement is decided, so it is
decided first rather than last.

```text
--sm-font-display    "Source Serif 4", Georgia, serif
--sm-font-ui         "Be Vietnam Pro", system-ui, -apple-system, sans-serif
--sm-font-mono       "JetBrains Mono", ui-monospace, SFMono-Regular, monospace
```

**Be Vietnam Pro** for UI and body text is the deliberate choice. It was
designed by a Vietnamese foundry specifically for Vietnamese typesetting, so
stacked diacritics render at their intended height rather than colliding with
ascenders or being clipped at small sizes. For a product whose founder is
Vietnamese and whose first listed crisis line is Vietnam's, using a typeface
built for the language is a substantive decision, not decoration.

**Source Serif 4** for display carries a complete Vietnamese range with properly
drawn diacritics, and its editorial warmth suits reflective prose better than a
neutral grotesque.

Both are open-licensed and self-hosted as subset `woff2`, so the site makes no
third-party font request and adds no external dependency.

The required render test, run on real text at 14px, 17px, and display size, in
both schemes:

```text
Tôi không cần biết hết mọi thứ.
Điều gì đang thực sự xảy ra bên trong tôi?
```

Checked for: `ố` and `ữ` diacritic collision with the line above, `ề` and `ế`
distinguishability at 14px, even color in a full paragraph, and no fallback
substitution. This is a Phase 8 gate, not a nicety.

### Spacing, radius, motion

A 4px base scale (`--sm-space-1` through `--sm-space-12`) rather than arbitrary
values. Radius stays modest, 6px to 12px, never pill-shaped on containers.
Motion is limited to 120-180ms on color and border, plus a 2px card lift.

`prefers-reduced-motion: reduce` disables transform and animation entirely while
keeping focus and hover color changes, so the interface stays legible without
motion.

## Components

Small and semantic. Each earns its place.

| Component | Purpose |
| --- | --- |
| `SiteShell` | Header, skip link, main landmark, footer |
| `FrameworkIndex` | Priority-tiered listing with filter and count |
| `FrameworkCard` | Name, description, tier, one link |
| `FrameworkDetail` | Public prose, section anchors, source link |
| `SafetyRule` | One numbered doctrine rule, stated plainly |
| `ArchitectureFlow` | The real request path, as semantic HTML, not an image |
| `Prose` | Rendered Markdown, the site's primary reading surface |
| `SearchField` | Progressive enhancement over the static index |
| `SourceLink` | "Read this in the repository", on every derived page |

No `GenericCard`, `Wrapper`, or `Section2`. A component that only groups markup
is a class name, not a component.

`SourceLink` on every derived page is a design decision with a doctrinal
purpose: it keeps the site honest about being generated from a public
repository, and it sends a curious reader to the source rather than asking them
to trust the page.

## Layout

A single reading column, 680px for prose and 1080px for index pages, on a
12-column grid used loosely. Two breakpoints, 860px and 640px, matching the
reference architecture's proven behavior rather than inventing a new scale.

Long-form pages keep the measure near 70 characters, which matters more for
Vietnamese than for English because diacritics increase visual line density.

## Accessibility floor

Not aspirational. These are build gates.

- Semantic landmarks, one `h1` per page, no skipped heading levels
- A visible skip-to-content link as the first focusable element
- Focus rings on every interactive element, never `outline: none` without a
  replacement
- Filtering and search reachable and operable by keyboard alone
- No information conveyed by color alone
- `prefers-reduced-motion` respected
- Search results announced through a polite live region
- The site fully readable and navigable with JavaScript disabled

## Tone rules for site copy

Site copy is subject to the same language rules as the rest of the repository,
including `.claude/rules/language-and-grammar.md` and the forbidden-phrase list
in `SOULMAP.md`.

Specifically for public pages: no second-person promises, no "your companion",
no "always here", no invented metrics, no testimonials, and no claim that
SoulMap understands the reader. Describe the mechanism and let it be
interesting on its own.

The homepage states what SoulMap refuses to do as prominently as what it does.
That is the product's actual differentiator, and a page that hides it would be
selling something the repository does not build.
