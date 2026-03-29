# Markdown portability rules

Keep Markdown compatible across AI tools and OS editors.

## Portability rules

- Use UTF-8 text files with LF line endings.
- Keep a single trailing newline at end of file.
- Do not add trailing spaces.
- Use only fenced code blocks, not indented code blocks.
- Use relative Markdown links for repo files unless an external URL is required.
- Keep YAML front matter valid when a file already uses it.
- Do not add HTML-only constructs unless the file already depends on them and the repo
  contract allows them.

## Lint-sensitive rules

Follow `.pymarkdown.json` and the repo contract exactly.

Key reminders:

- **MD001 / MD003 / MD022:** Keep headings consistent, sentence case where the repo
  uses it, and surrounded by blank lines.
- **MD013:** Respect configured line length by wrapping prose cleanly.
- **MD024:** Avoid duplicate headings at the same level unless the file's structure
  requires it.
- **MD025:** Keep exactly one top-level heading when the file type expects it.
- **MD026:** Do not end headings with stray punctuation.
- **MD029:** Use sequential ordered lists (`1.`, `2.`, `3.`), not repeated `1.`.
- **MD031:** Surround fenced code blocks with blank lines.
- **MD032:** Surround lists with blank lines.
- **MD034:** Wrap bare URLs in angle brackets when not using link syntax.
- **MD040:** Always specify a language tag for fenced code blocks, for example
  `python`, `json`, `yaml`, `text`, or `markdown`.

## Formatting loop

After changing Markdown files, run:

```bash
python -m tools.format
python -m tools.lint
```

If a Markdown change also affects docs contracts, packaging text, or eval references,
run the narrower checks that cover that surface too.
