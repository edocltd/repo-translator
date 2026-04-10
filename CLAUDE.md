# CLAUDE.md — repo-translator

This repository is a universal tool for translating GitHub repository documentation into any language.

## What this project does

repo-translator scans a repository, identifies markdown files, and provides tools to translate, validate, and keep translations in sync with the original.

## Project structure

```
scripts/
  scan.py              — Scan repo, classify files, generate translation plan
  validate.py          — Validate translated files against originals
  fix_anchors.py       — Auto-fix broken anchor links and encoding issues
  prompt_generator.py  — Generate translation prompts for copy-paste workflow
  sync_check.py        — Check if translations are outdated

examples/
  glossary-uk.yaml     — Example glossary for Ukrainian

templates/
  (reserved for future prompt templates)
```

## How to use scripts

```bash
# Scan a repo and see what needs translating
python scripts/scan.py --root /path/to/repo --lang uk

# Validate translations
python scripts/validate.py --root /path/to/repo --lang uk

# Auto-fix broken anchors and encoding
python scripts/fix_anchors.py translations/uk/

# Generate a prompt for copy-paste translation
python scripts/prompt_generator.py README.md --lang uk

# Check if translations are up to date
python scripts/sync_check.py --root /path/to/repo --lang uk
```

## Translation workflow

When helping a user translate a repository:

1. Run `scan.py` to understand the repo structure and generate a plan
2. For each file to translate:
   a. Read the original file
   b. Load the glossary for the target language
   c. Translate ONLY prose — preserve code blocks, Mermaid diagrams, URLs, file paths
   d. Write the translated file to `translations/{lang}/` mirroring the original path
   e. Run `validate.py` on the result
   f. If validation fails — run `fix_anchors.py` and re-validate
3. After all files — run `validate.py` on the entire translations directory

## Critical rules for translation

1. Code blocks (``` or ~~~~) must be preserved EXACTLY — never translate code
2. Mermaid diagrams must not be modified
3. URLs and file paths must not change
4. Frontmatter YAML: only translate `description` field, keep `name`, `tools`, etc.
5. Use glossary terms consistently across all files
6. Add i18n metadata header to each translated file:
   ```
   <!-- i18n-source: original/path.md -->
   <!-- i18n-source-sha: abc1234 -->
   <!-- i18n-date: 2026-04-10 -->
   ```
7. Translated file must have ±5% lines compared to original (no shortening)
8. All anchor links (#section) must resolve to actual headings in the translated file
