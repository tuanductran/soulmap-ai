---
name: framework-author
description: Write and maintain framework skill files that define activation signals and response structures for SoulMap's framework system. Relevant for writing or revising a framework file in skills/frameworks/, including its activation signals and response structure.
---

# Framework author

Use this skill when creating new frameworks or substantially updating existing framework skill files.

## Do not use this skill for

- Implementing detectors that identify frameworks, use [`detector-engineer`](../detector-engineer/SKILL.md)
- Writing eval test cases for frameworks, use [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md)
- General documentation editing, use [`docs-and-api-writer`](../docs-and-api-writer/SKILL.md)
- Creating non-framework skill files under `skills/`, reference those in `skills/meta/` instead

## Mission

Framework skill files live in `skills/frameworks/` and define:

1. **When a framework activates**, activation Signals section
2. **How to respond**, response Structure section
3. **Key concepts**, context and framing for users of the framework

This skill helps you author frameworks that are:

- Internally consistent and clear
- Properly integrated with the detector system
- Testable through the eval suite
- Referenced correctly by source markers in eval groups

## Choose the knowledge type first

Before authoring, decide whether the new file is a **primary routed framework** or
**supporting knowledge**.

- A primary routed framework is an independently selectable primary response route. It
  needs a registered detector/routing binding, a priority position, a template mapping,
  and source-backed eval coverage. Check the current Python routing and configuration
  before proposing a new route.
- A supporting lens or secondary layer enriches a primary framework that is already
  active. It does not need its own primary detector, priority row, or template mapping.
  Examples include relationship reflection, money and self-worth, self-compassion,
  numerology connection, and secondary anger or somatic guidance.
- A file's directory or filename does not determine its runtime role. Follow
  [the Library/framework boundary](../../../docs/engineering/library-vs-framework.md)
  and the current runtime mappings.

Do not create a new primary route merely because a topic deserves a useful knowledge file.

## Framework file location

General frameworks usually live under `skills/frameworks/`. Domain-specific primary frameworks
may live in an established domain directory such as `skills/soulmate/`. Follow the current
source registry and neighboring files; use a kebab-case filename matching the front-matter name.

Examples:

- `skills/frameworks/emotional-deescalation.md`, crisis and de-escalation response
- `skills/frameworks/grief-companion.md`, grief support
- `skills/frameworks/inner-parts.md`, inner conflict work

## YAML front matter

Every framework file starts with metadata:

```yaml
---
name: "framework-name"
description: "One-line description of what this framework does"
---
```

Examples:

```yaml
---
name: "crisis"
description: "Safety-first response when a user signals immediate crisis (self-harm, suicidal ideation, abuse)"
---
```

```yaml
---
name: "self-compassion"
description: "Self-compassion language for shame, self-criticism, and the inner critic"
---
```

## Required sections for primary routed frameworks

The following sections define the contract for a new or substantially revised primary
routed framework. Supporting lenses should use the sections that fit their role; do not
force a detector-facing contract onto a file that is not independently routed.

### Activation Signals

Clearly describe what user language or situation triggers this framework.

```markdown
## When to activate this framework

Signals:

- "I don't know who I really am"
- "Nothing I do feels authentic"
- "I'm just pretending to be someone"
- User expressing identity instability or feeling like a "mask"
```

**Rules**:

- Use first-person language ("I" statements from the user)
- Be specific, give examples, not just categories
- Include what NOT to confuse this with (if relevant)
- Keep the signal list concise (5-10 examples, not exhaustive)

### Response Structure

Explain the structure SoulMap uses when this framework activates.

```markdown
## Response structure

1. **Acknowledge**, name the experience without judgment
2. **Explore**, ask what the identity question is really about
3. **Normalize**, this is part of human development, not pathology
4. **Inquiry**, optionally offer at most one open question that turns the user inward when appropriate; a reflection or quiet close is also valid
```

**Rules**:

- Number or bullet the steps
- Include a brief description of each step
- Show how this differs from other frameworks (if applicable)
- Keep it concise (2-4 steps typically)

### Key Concepts

Explain foundational ideas used in this framework.

```markdown
## Key concepts

**Authentic Self vs. Performed Self**, humans adapt to contexts. The question isn't which is "real,"
but whether the user can access their own knowing across contexts.

**Identity Development**, identity isn't static. Uncertainty about values or purpose is often a sign
of growth, not collapse.
```

**Rules**:

- Define concepts that might be unfamiliar
- Use bold for concept names
- Keep definitions accessible (not jargon-heavy)
- Limit to 2-4 key concepts

### Practical reflection language

Show examples of how to communicate this framework to users.

```markdown
## Practical reflection language

**Opening lines:**
- "There's a difference between not knowing who you are and not being able to access who you are right now."
- "Something in what you just said feels exploratory, not lost."

**Reflective questions:**
- "When you imagine being fully yourself, what's present?"
- "Who are you when no one's watching?"

**What not to do:**
- Don't tell them who they are
- Don't minimize their confusion
- Don't offer reassurance ("You're fine, just confused")
```

**Rules**:

- Use actual language, not abstract descriptions
- Include examples of what NOT to say
- Show conversational tone
- Make it applicable to real user inputs

### What Not to Do (if relevant)

Explain common mistakes or framework misuse.

```markdown
## What not to do

- **Don't rush to interpretation**, "I'm confused about my identity" isn't yet a clear signal. Let the user describe more first.
- **Don't dismiss the confusion**, "This is just a phase" minimizes real exploration.
- **Don't offer certainty**, "Your values are actually X" centers the wrong person's authority.
```

## Optional sections

Frameworks may also include:

- **Relationship to Other Frameworks**, how this differs from similar frameworks
- **Common Variations**, different ways the signal appears in real conversation
- **Integration with Inner Parts Work**, if this framework relates to inner parts language
- **Ethical Boundaries**, where this framework does and doesn't apply

Example:

```markdown
## Relationship to other frameworks

The standard reflective posture is the default. Use it when the user is exploring
openly. Use direction work when the exploration feels specifically about life purpose
or path.

Inner parts work fits when identity confusion involves conflicting inner voices. But if
the user isn't describing internal conflict, only uncertainty, stay with direction work
rather than shifting into parts language.
```

## Framework integration

### Primary routed framework

For a new independently selectable primary route:

1. Confirm that the need is distinct and not already served by an existing primary
   framework or supporting lens.
2. Add or extend a detector only when the routing contract requires new detection.
   Follow the existing detector-specific callable and output contract; do not assume
   one Markdown file always maps one-to-one to one detector.
3. Keep semantic signals and qualitative guidance in the registered Markdown source.
   Keep executable scoring weights, thresholds, priority values, and routing settings in
   Python-owned runtime configuration.
4. Register the primary route and its detector binding through the existing routing
   and knowledge architecture. Preserve safety priority and the independent safety gate.
5. Add or update the Python-owned template row when the new route needs distinct
   deterministic output constraints, and add source-backed eval coverage.

### Supporting lens or secondary layer

For a supporting knowledge file:

- Do not add a primary detector, priority row, or independent framework-template mapping
  unless the product decision explicitly promotes it to a primary route.
- Link it from the appropriate primary framework, quick reference, or other canonical
  guidance so it can be used when relevant.
- Keep its scope and relationship to existing frameworks explicit.
- Add or update contract/eval coverage only where the file has a testable behavior or
  source-reference requirement.

## Writing quality standards

### Clarity

- Use concrete examples, not abstract concepts
- Keep sentences short and direct
- Avoid clinical language unless it's the framework's voice
- Define any specialized terms

### Consistency

- Match the tone of existing frameworks (`skills/frameworks/`)
- Use the same YAML frontmatter format
- Follow the section structure: Signals, Response, Concepts, Language, and What not to do
- Reference other frameworks using backticks and relative paths

### Completeness

- Activation signals are specific and traceable
- Response structure is clear and actionable
- Examples of what to say and what not to say
- Framework name appears in YAML, headings, and discussions

### Auditability

- Each framework should be testable through `evals/datasets/groups.json`
- Concepts should trace back to SoulMap's brand doctrine (`SOULMAP.md`)
- Language examples should be realistic and gender/culture-neutral

## Example framework template

Use this as a starting point:

```markdown
---
name: "framework-name"
description: "One-line description of what this framework does"
---

# Framework name

Brief intro explaining the framework's purpose.

## When to Activate This Framework

Signals:

- "Example signal 1"
- "Example signal 2"
- "Example signal 3"
- User describing [specific condition]

## Response Structure

1. **Step 1**, brief description
2. **Step 2**, brief description
3. **Step 3**, brief description
4. **Step 4**, brief description

## Key Concepts

**Concept 1**, definition and context.

**Concept 2**, definition and context.

## Practical reflection language

**Opening lines:**
- "Quote that opens with this framework"
- "Another opening approach"

**Reflective questions:**
- "Question 1"
- "Question 2"

**What not to do:**
- Don't do this (and why)
- Don't do that (and why)

## Relationship to Other Frameworks

**FRAMEWORK_A**, how this differs.

**FRAMEWORK_B**, how this differs.
```

## Testing your framework

### Schema check

Ensure YAML frontmatter is valid:

```bash
python3 -c "import yaml; yaml.safe_load(open('skills/frameworks/your_framework.md'))"
```

### Run evals

After adding test cases to `evals/datasets/groups.json`:

```bash
uv run soulmap eval-groups
```

Verify all test cases for your framework pass.

### Manual review

Have another contributor review:

- Clarity of activation signals
- Practical applicability of response structure
- Quality of reflection language examples
- Consistency with other frameworks

## Naming conventions

- Use a lowercase kebab-case Markdown filename.
- Keep the front-matter `name` aligned with the filename stem.
- Use reader-facing framework labels in Markdown; machine identifiers and routing
  mappings belong in Python.
- Do not infer primary-route status from the directory name alone.

Examples:

| File | Role |
|------|------|
| `emotional-deescalation.md` | Crisis and de-escalation knowledge |
| `grief-companion.md` | Primary grief framework |
| `relationship-reflection.md` | Supporting relationship lens |

## Workflow

1. Read `SOULMAP.md` Section 2 (Framework Selection) to verify priority placement.
2. Read an existing framework file in `skills/frameworks/` for structural reference.
3. Create the knowledge file in the appropriate `skills/` location with sections that fit its role.
4. For a primary routed framework only, update the Python-owned priority and routing configuration.
5. When the route needs deterministic output constraints, update `FRAMEWORK_TEMPLATE_ROWS`
   in `src/soulmap/runtime/knowledge/runtime_config.py`. Add or update qualitative,
   AI-facing response guidance in `skills/meta/framework-template-map.md` only when the
   prose guidance itself needs to change. A supporting lens does not get an independent
   runtime template row by default.
6. For a primary routed framework only, work with [`detector-engineer`](../detector-engineer/SKILL.md) on any required detector and routing changes.
7. Work with [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md) on the appropriate source-backed coverage.
8. Run `uv run soulmap build` and `uv run soulmap test -n auto -q` before committing.

## Definition of done

A primary routed framework is done when:

- YAML front matter has a valid `name` matching the filename stem
- `## Activation Signals` describes observable detection language
- `## Response Structure` defines the response arc and appropriate length boundaries
- `## Paired template` references the correct template and inquiry-bank section
- Its detector/routing binding and priority are present and verified
- Any required deterministic output constraints are represented in Python-owned
  `FRAMEWORK_TEMPLATE_ROWS`; qualitative guidance is updated separately in Markdown
- At least one eval group covers its primary activation signal
- `uv run soulmap build` and the relevant tests pass

A supporting lens or secondary layer is done when:

- Its scope and relationship to existing primary frameworks are explicit
- It is linked from the appropriate canonical guidance
- It does not claim or imply an independent primary route without a routing contract
- Any source-reference or behavior contract it owns is covered by the relevant checks
- `uv run soulmap build` and relevant Markdown QA checks pass

## Relationship to other skills

- **detector-engineer** implements the code that detects when this framework should activate
- **eval-suite-maintainer** writes test cases that validate your framework works correctly
- **research-and-gap-analysis** identifies which frameworks are missing or need updating
