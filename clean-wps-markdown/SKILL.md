---
name: clean-wps-markdown
description: Clean Markdown exported from WPS collaborative documents or Kingsoft Docs for use in code repositories, including broken heading numbering and permission-bound images. Use when an exported .md file contains list-wrapped headings such as `1. ##`, repeated or reset section numbers, excessive indentation or blank lines, image-only tables, long kdocs.cn image URLs, or when a user asks to normalize or import WPS Markdown without rewriting its meaning.
---

# Clean WPS Markdown

Use the bundled deterministic script before making manual edits. Preserve wording and document structure unless the user explicitly asks for editorial rewriting.

## Workflow

1. Inspect the source file, especially its heading levels and numbering, and the target repository's Markdown conventions.
2. Resolve `<skill-dir>` to the directory containing this `SKILL.md`.
3. Preview the cleaned output without writing a file:

   ```bash
   python3 <skill-dir>/scripts/clean_wps_markdown.py source.md
   ```

4. Review the diff or rendered Markdown.
5. Write to a new target path:

   ```bash
   python3 <skill-dir>/scripts/clean_wps_markdown.py source.md \
     --output docs/design/source.md
   ```

6. Use `--force` only after confirming that replacing an existing target is intended.

Do not assume that ordered-list numbers attached by WPS are valid section numbers. Preview the heading outline first. Keep them only when they are continuous and match the intended hierarchy.

- Use `--strip-heading-numbers` when the target document does not use numbered headings.
- Use `--renumber-headings` when primary sections should use `一、二、三……`, secondary sections should restart as `1、2、3……` in each primary section, and deeper headings should continue as `1.1、1.2……`.
- If the desired numbering style is unclear and the WPS numbers repeat or reset unexpectedly, ask the user before writing the final file.

Example:

```bash
python3 <skill-dir>/scripts/clean_wps_markdown.py source.md \
  --output docs/design/source.md \
  --renumber-headings
```

## Image handling

- Remove standalone images and image-only WPS tables by default. Do not request remote image URLs; they commonly require document permissions or expire outside WPS.
- Use `--keep-images` only when the user explicitly wants the original remote links.
- Use `--download-images <directory>` only when the user explicitly wants repository-local images and the URLs are accessible. Resolve a relative directory from the output file's parent and keep an inaccessible remote URL unchanged with a warning.
- Do not use `--keep-images` and `--download-images` together.

Example:

```bash
python3 <skill-dir>/scripts/clean_wps_markdown.py source.md \
  --output docs/design/source.md \
  --download-images assets/source
```

## Title handling

Add an H1 inferred from the source filename when the export has no H1. Use `--title` to override it or `--no-title` when the repository intentionally omits document titles.

## Verification

After conversion:

- confirm there are no list-wrapped headings such as `1. ##`;
- print the heading outline and confirm primary, secondary, and deeper numbering separately;
- confirm nested lists still have the intended hierarchy and were not mistaken for headings;
- confirm image-only WPS tables became ordinary image lines;
- confirm local image paths resolve when images were downloaded;
- compare source and output to ensure wording was not silently rewritten.

Run `python3 <skill-dir>/scripts/clean_wps_markdown.py --help` for all options.
