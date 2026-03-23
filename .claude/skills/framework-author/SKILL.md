---
name: framework-author
description: Write and maintain framework skill files that define activation signals and response structures for SoulMap's framework system.
---

# Framework Author

Use this skill when creating new frameworks or substantially updating existing framework skill files.

## Do not use this skill for

- Implementing detectors that identify frameworks - use [`detector-engineer`](../detector-engineer/SKILL.md)
- Writing eval test cases for frameworks - use [`eval-suite-maintainer`](../eval-suite-maintainer/SKILL.md)
- General documentation editing - use [`docs-and-api-writer`](../docs-and-api-writer/SKILL.md)
- Creating non-framework skill files under `skills/` - reference those in `skills/meta/` instead

## Mission

Framework skill files live in `skills/frameworks/` and define:

1. **When a framework activates** - Activation Signals section
2. **How to respond** - Response Structure section
3. **Key concepts** - context and framing for users of the framework

This skill helps you author frameworks that are:

- Internally consistent and clear
- Properly integrated with the detector system
- Testable through the eval suite
- Referenced correctly by source markers in eval groups

## Framework File Location

New frameworks live here: `skills/frameworks/{framework-name}.md`

Examples:
- `skills/frameworks/mirror.md` - reflective mode
- `skills/frameworks/crisis.md` - crisis response
- `skills/frameworks/grief.md` - grief support

## YAML Frontmatter

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
description: "Safety-first response when user signals Tier 1 crisis (self-harm, suicidal ideation, abuse)"
---
```

```yaml
---
name: "self-compassion"
description: "Self-compassion language for shame, self-criticism, and the inner critic"
---
```

## Required Sections

Every framework must have these sections:

### Activation Signals

Clearly describe what user language or situation triggers this framework.

```markdown
## When to Activate This Framework

Signals:

- "I don't know who I really am"
- "Nothing I do feels authentic"
- "I'm just pretending to be someone"
- User expressing identity instability or feeling like a "mask"
```

**Rules**:
- Use first-person language ("I" statements from the user)
- Be specific - give examples, not just categories
- Include what NOT to confuse this with (if relevant)
- Keep the signal list concise (5-10 examples, not exhaustive)

### Response Structure

Explain the structure SoulMap uses when this framework activates.

```markdown
## Response Structure

1. **Acknowledge** - name the experience without judgment
2. **Explore** - ask what the identity question is really about
3. **Normalize** - this is part of human development, not pathology
4. **Inquiry** - one open question that turns the user inward
```

**Rules**:
- Number or bullet the steps
- Include a brief description of each step
- Show how this differs from other frameworks (if applicable)
- Keep it concise (2-4 steps typically)

### Key Concepts

Explain foundational ideas used in this framework.

```markdown
## Key Concepts

**Authentic Self vs. Performed Self** - humans adapt to contexts. The question isn't which is "real," 
but whether the user can access their own knowing across contexts.

**Identity Development** - identity isn't static. Uncertainty about values or purpose is often a sign 
of growth, not collapse.
```

**Rules**:
- Define concepts that might be unfamiliar
- Use bold for concept names
- Keep definitions accessible (not jargon-heavy)
- Limit to 2-4 key concepts

### Practical Reflection Language

Show examples of how to communicate this framework to users.

```markdown
## Practical Reflection Language

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
## What Not to Do

- **Don't rush to interpretation** - "I'm confused about my identity" isn't yet a clear signal. Let the user describe more first.
- **Don't dismiss the confusion** - "This is just a phase" minimizes real exploration.
- **Don't offer certainty** - "Your values are actually X" centers the wrong person's authority.
```

## Optional Sections

Frameworks may also include:

- **Relationship to Other Frameworks** - how this differs from similar frameworks
- **Common Variations** - different ways the signal appears in real conversation
- **Integration with Inner Parts Work** - if this framework relates to inner parts language
- **Ethical Boundaries** - where this framework does and doesn't apply

Example:

```markdown
## Relationship to Other Frameworks

**MIRROR** - our default. Use MIRROR when the user is exploring openly. Use DIRECTION when the 
exploration feels specifically about life purpose or path.

**INNER_PARTS** - some identity confusion involves conflicting inner voices. But if the user isn't 
describing internal conflict (just uncertainty), stay with DIRECTION rather than shifting to inner parts.
```

## Framework Integration

### Register in Detector System

Your framework needs a detector that identifies when to activate it. After writing the framework file:

1. Create or update a detector in `modules/your_framework_detector.py`
2. Add it to the framework selector in `modules/framework_selector.py`
3. Reference it from `detector-engineer` skill if creating new detector patterns

### Add Test Coverage

Create eval test cases in `evals/groups.json`:

```json
{
  "g": "Your Framework - Core Signal",
  "cat": "your_cat",
  "sources": [
    "skills/frameworks/your_framework.md",
    "templates/quick-reference.md"
  ],
  "source_markers": {
    "skills/frameworks/your_framework.md": "Signal from 'Activation Signals' section"
  },
  "items": [
    {
      "t": "user input that triggers your framework",
      "note": "Testing core signal",
      "expect_primary_framework": "YOUR_FRAMEWORK_NAME",
      "expect_mode": "YOUR_FRAMEWORK_NAME",
      "expect_safety_status": "PASS",
      "expect_safety_reason": "no_override"
    }
  ]
}
```

### Update Quick Reference (if applicable)

If the framework should appear in `templates/quick-reference.md`, add an entry:

```markdown
| Your Framework | Signal | Example |
|---|---|---|
| Your Framework | User describes [signal] | "I don't know what my life is for" |
```

## Writing Quality Standards

### Clarity

- Use concrete examples, not abstract concepts
- Keep sentences short and direct
- Avoid clinical language unless it's the framework's voice
- Define any specialized terms

### Consistency

- Match the tone of existing frameworks (`skills/frameworks/`)
- Use the same YAML frontmatter format
- Follow the section structure (Signals, Response, Concepts, Language, What Not To Do)
- Reference other frameworks using backticks and relative paths

### Completeness

- Activation signals are specific and traceable
- Response structure is clear and actionable
- Examples of what to say and what not to say
- Framework name appears in YAML, headings, and discussions

### Auditability

- Each framework should be testable through `evals/groups.json`
- Concepts should trace back to SoulMap's brand doctrine (`AGENTS.md`)
- Language examples should be realistic and gender/culture-neutral

## Example Framework Template

Use this as a starting point:

```markdown
---
name: "framework-name"
description: "One-line description of what this framework does"
---

# Framework Name

Brief intro explaining the framework's purpose.

## When to Activate This Framework

Signals:

- "Example signal 1"
- "Example signal 2"
- "Example signal 3"
- User describing [specific condition]

## Response Structure

1. **Step 1** - Brief description
2. **Step 2** - Brief description
3. **Step 3** - Brief description
4. **Step 4** - Brief description

## Key Concepts

**Concept 1** - Definition and context.

**Concept 2** - Definition and context.

## Practical Reflection Language

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

**FRAMEWORK_A** - How this differs.

**FRAMEWORK_B** - How this differs.
```

## Testing Your Framework

### Schema Check

Ensure YAML frontmatter is valid:

```bash
python3 -c "import yaml; yaml.safe_load(open('skills/frameworks/your_framework.md'))"
```

### Run Evals

After adding test cases to `evals/groups.json`:

```bash
python3 -m soulmap_ai.tools.eval_groups
```

Verify all test cases for your framework pass.

### Manual Review

Have another contributor review:
- Clarity of activation signals
- Practical applicability of response structure
- Quality of reflection language examples
- Consistency with other frameworks

## Naming Conventions

- Framework file name: lowercase with hyphens (`skills/frameworks/framework-name.md`)
- Framework constant name: uppercase with underscores (`FRAMEWORK_NAME`)
- Category code in evals: short, memorable (`wl1`, `crisis`, `existential`)

Examples:

| File | Constant | Category |
|------|----------|----------|
| `inner-parts.md` | `INNER_PARTS` | `wl6` |
| `shadow-patterns.md` | `SHADOW` | `wl8` |
| `crisis.md` | `CRISIS` | `crisis` |

## Relationship to Other Skills

- **detector-engineer** implements the code that detects when this framework should activate
- **eval-suite-maintainer** writes test cases that validate your framework works correctly
- **research-and-gap-analysis** identifies which frameworks are missing or need updating
