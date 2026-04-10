# CLAUDE.md

> Single source of truth for this project. Read this file completely before making any changes.

## What This Project Is

Universal tool for translating GitHub repository markdown documentation into any language. Not an API wrapper — a framework for structure, validation, and sync. Translation itself can be done by any method (Claude Code, copy-paste, Ollama, manually, API).

## Project Structure

```
repo-translator/
├── scripts/
│   ├── scan.py              # Scan repo, classify files, generate plan
│   ├── validate.py          # Validate translations (12 checks)
│   ├── fix_anchors.py       # Auto-fix anchors, encoding, invisible Unicode
│   ├── prompt_generator.py  # Generate prompts for copy-paste workflow
│   └── sync_check.py        # Check sync status with originals
├── examples/
│   └── glossary-uk.yaml     # Example glossary (Ukrainian)
├── templates/
│   └── .gitkeep
├── .repo-translator.yaml.example
├── .gitignore
├── CLAUDE.md                # THIS FILE
├── README.md                # User-facing documentation
├── CONTRIBUTING.md           # Contribution guidelines
├── SECURITY.md              # Security policy
├── CODE_OF_CONDUCT.md       # Community standards
├── FAILURE-ANALYSIS.md      # 48 real problems analysis
├── REPO-TRANSLATOR-SPEC.md  # Full specification
└── LICENSE                  # MIT
```

## Architecture

Five-stage pipeline, each stage is an independent script:

```
SCAN → TRANSLATE → VALIDATE → FIX → SYNC
```

### Data Flow

```
Repository (any)
    │
    ▼
[scan.py] → Plan: which files to translate/copy/skip
    │
    ▼
[Human/AI translates] → Files in translations/{lang}/
    │
    ▼
[validate.py] → Checks: lines, code blocks, anchors, encoding
    │
    ├── Errors? → [fix_anchors.py] → Auto-fix
    └── All OK? → git commit
    │
    ▼
[sync_check.py] → "File X is outdated" (when original changes)
```

## Scripts: Exact Behavior

### scan.py

**Purpose**: Analyze repository and classify every file.

**Auto-detection**: Automatically finds and excludes existing translation directories:
- Language code dirs: `uk/`, `vi/`, `zh/`, etc. (verified by checking for .md files inside)
- Container dirs: `translations/`, `i18n/`, `l10n/`, `lang/`, `locales/`

**Classification logic** (priority order):
1. File in `SKIP_FILENAMES` (LICENSE, .gitignore) → skip
2. Binary file (null bytes > 1%) → skip
3. File in `COPY_FILENAMES` (CHANGELOG.md) → copy
4. .md with < 10% prose (mostly code/config) → copy
5. All other .md files → translate

**Exclude pattern matching**: Uses `Path.match()` with fallback to `str.startswith()` for `**` patterns on Windows.

**CLI**: `python scripts/scan.py --root PATH --lang CODE [--translations-dir NAME] [--json] [--output FILE] [--max-files N]`

### validate.py

**Purpose**: Check translation quality against original.

**12 checks**: UTF-8, line count (±15%), code blocks count, unmatched fences, Mermaid count, heading count, table rows, code content preserved, anchor links resolve, URLs preserved, invisible Unicode, trailing newline.

**Anchor generation**: GitHub-style — remove emoji, remove non-word chars (except Unicode letters), lowercase, spaces→hyphens. Supports duplicate heading numbering (-1, -2).

**Known issue**: Apostrophe variants (U+0027 vs U+02BC) produce different anchors. `find_best_anchor()` normalizes them for comparison.

**CLI**: `python scripts/validate.py --root PATH --lang CODE [--translations-dir NAME] [--file FILE] [--json]`

### fix_anchors.py

**Purpose**: Auto-fix common translation problems.

**Fixes**:
1. Broken anchor links → fuzzy match to correct anchor
2. Mixed encoding (CP1251 blocks in UTF-8) → byte-level repair
3. Invisible Unicode (U+200B, U+200C, U+200D, U+200E, U+200F) → remove
4. Missing trailing newline → add

**CLI**: `python scripts/fix_anchors.py PATH [--dry-run]`

### prompt_generator.py

**Purpose**: Generate ready-to-paste translation prompts.

**Includes**: 11 translation rules, glossary terms, do-not-translate list, original file content.

**Chunking**: Files > max_tokens split by `##` headings. Each chunk gets same rules and glossary.

**Glossary search** (priority): `--glossary` flag → `{dir}/.glossary-{lang}.yaml` → `translations/{lang}/.glossary.yaml`

**CLI**: `python scripts/prompt_generator.py FILE --lang CODE [--glossary FILE] [--chunk] [--max-tokens N] [--output FILE]`

### sync_check.py

**Purpose**: Detect outdated translations.

**Logic**: Reads `<!-- i18n-source-sha: ... -->` from translated files, compares with current `git log` SHA. Different SHA = outdated.

**Auto-detection**: Excludes language code directories and translation container directories from "not yet translated" list.

**CLI**: `python scripts/sync_check.py --root PATH --lang CODE [--translations-dir NAME] [--json]`

## Key Design Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Output directory | `translations/{lang}/` | Clear to everyone, unlike `i18n/` |
| What to copy | Only .md files | Code/images stay in original location |
| API dependency | None required | Core value is validation, not translation |
| Config file | Optional | Works with sensible defaults |
| Language codes | ISO 639-1 | Industry standard |
| Exclude detection | Automatic | Scans for existing translation dirs |

## Translation Rules (for AI prompts)

1. Code blocks (``` and ~~~~) — DO NOT translate or modify
2. Mermaid diagrams — DO NOT modify
3. URLs and file paths — DO NOT change
4. YAML frontmatter — translate only `description` field
5. HTML tags — translate text between tags, NOT attributes
6. Preserve Markdown formatting 1:1
7. Line count of translation ±5% of original
8. DO NOT add translator notes or comments
9. DO NOT shorten or summarize — translate EVERYTHING

## Commit Conventions

```
type(scope): description
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

Examples:
```
feat(scan): add auto-detection of existing translations
fix(validate): handle apostrophe variants in anchors
docs(readme): add badges and quick start section
```

## Known Issues

1. **Glossary checking**: `check_glossary()` in validate.py is a stub (not implemented)
2. **Code block placeholder extraction**: Not yet implemented — AI still sees code blocks
3. **Relative link rewriting**: Not automated when creating translations
4. **RTL language support**: Not tested
5. **CJK line count coefficients**: Not implemented (CJK text is shorter)

## Testing

Tested on two real repositories:

| Repo | Stars | Files | Result |
|------|-------|-------|--------|
| luongnv89/claude-howto | 22K+ | 103 | ✅ scan, validate (4 real errors found), sync |
| AgriciDaniel/claude-seo | new | 101 | ✅ scan, prompt generation, chunking |
