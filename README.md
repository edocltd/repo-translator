# repo-translator

🌐 [English](README.md) | [Українська](translations/uk/README.md) | [Español](translations/es/README.md) | [Français](translations/fr/README.md) | [Deutsch](translations/de/README.md) | [Português](translations/pt-br/README.md) | [中文](translations/zh/README.md) | [日本語](translations/ja/README.md)

**Universal tool for translating GitHub repository documentation into any language.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GitHub Stars](https://img.shields.io/github/stars/edocltd/repo-translator?style=flat&color=gold)](https://github.com/edocltd/repo-translator/stargazers)

Not an API wrapper — a **framework** for structure, validation, and sync. Translate using any method: Claude Code, Claude.ai, ChatGPT, Ollama, or manually. The tool ensures the result is correct.

> **Built from real experience**: Every feature exists because of a real problem encountered while translating [claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐) into Ukrainian. See [docs/failure-analysis.md](docs/failure-analysis.md) for the full 48-problem breakdown.

---

## Table of Contents

- [The Problem](#the-problem)
- [How It Works](#how-it-works)
- [Quick Start](#quick-start)
- [Translation Methods](#translation-methods)
- [Scripts Reference](#scripts-reference)
- [Output Structure](#output-structure)
- [Validation Checks](#validation-checks)
- [Any Language](#any-language)
- [Configuration](#configuration)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

---

## The Problem

You want to translate a repository's documentation. You face:

- **No structure** — Which files to translate? Which to skip? Where to put results?
- **No validation** — Did the AI silently delete half your content? Break anchor links? Corrupt encoding?
- **No consistency** — "hook" translated as "хук" in one file and "гачок" in another
- **No sync** — Original updated last week. Which translations are outdated?

Existing tools (co-op-translator, gpt-translate) handle translation but skip validation entirely.

## How It Works

```
SCAN  →  TRANSLATE  →  VALIDATE  →  FIX  →  SYNC
  ↓         ↓            ↓          ↓        ↓
"What     "Any        "Is it     "Auto-   "What's
 files?"   method"    correct?"   fix"    outdated?"
```

1. **Scan** — Analyze repo, classify files (translate / copy / skip), auto-detect existing translations, estimate effort
2. **Translate** — Use any method. Tool generates prompts with glossary and rules
3. **Validate** — Check structure (line count, code blocks, Mermaid), anchors, encoding, glossary
4. **Fix** — Auto-fix broken anchors, encoding issues, invisible Unicode
5. **Sync** — Track which translations are outdated when originals change

Each step is an independent script. Use them together or separately.

## Quick Start

```bash
git clone https://github.com/edocltd/repo-translator.git
```

```bash
# Scan any repo to see what needs translating
python repo-translator/scripts/scan.py --root /path/to/any-repo --lang uk

# Generate a translation prompt (copy-paste into Claude.ai / ChatGPT)
python repo-translator/scripts/prompt_generator.py /path/to/any-repo/README.md --lang uk

# After translating — validate the result
python repo-translator/scripts/validate.py --root /path/to/any-repo --lang uk

# Auto-fix broken anchors and encoding
python repo-translator/scripts/fix_anchors.py /path/to/any-repo/translations/uk/

# Check what's outdated after original changes
python repo-translator/scripts/sync_check.py --root /path/to/any-repo --lang uk
```

## Translation Methods

The tool doesn't care HOW you translate. It ensures the result is correct.

| Method | Cost | Setup | Best For |
|--------|------|-------|----------|
| **Claude Code** | $0 extra | Already installed | Fastest workflow for subscribers |
| **Copy-paste** (Claude.ai / ChatGPT) | $0–20/mo | Any AI chat | Anyone with a subscription |
| **Manual** | $0 | None | Human translators, small repos |
| **Ollama** | $0 | Install Ollama | Privacy-sensitive, offline work |
| **API** (Anthropic / OpenAI) | Pay-per-use | API key | Automation, large repos |

## Scripts Reference

### `scan.py` — Scan & Classify

Analyzes a repository and determines what to do with each file.

```bash
python scripts/scan.py --root /path/to/repo --lang uk
python scripts/scan.py --root /path/to/repo --lang de --json
python scripts/scan.py --root /path/to/repo --lang fr --output plan.json
```

Key features:
- Auto-detects existing translations (`uk/`, `vi/`, `translations/`, `i18n/`, etc.) and excludes them
- Classifies files: `translate` (prose .md) / `copy` (CHANGELOG, code-heavy .md) / `skip` (LICENSE, binary)
- Estimates token count and API cost

### `validate.py` — Validate Translations

Checks translated files against originals with 12 validation checks.

```bash
python scripts/validate.py --root /path/to/repo --lang uk
python scripts/validate.py --root /path/to/repo --lang uk --file README.md
```

### `fix_anchors.py` — Auto-Fix Issues

Automatically fixes common translation problems.

```bash
python scripts/fix_anchors.py translations/uk/
python scripts/fix_anchors.py --dry-run translations/uk/
```

Fixes: broken anchor links, mixed encoding (CP1251/UTF-8), invisible Unicode characters, missing trailing newlines.

### `prompt_generator.py` — Generate Translation Prompts

Creates ready-to-paste prompts with rules and glossary for any AI chat.

```bash
python scripts/prompt_generator.py README.md --lang uk
python scripts/prompt_generator.py large-file.md --lang uk --chunk --max-tokens 4000
python scripts/prompt_generator.py README.md --lang uk --glossary examples/glossary-uk.yaml
```

### `sync_check.py` — Track Outdated Translations

Detects which translations are outdated after the original changes.

```bash
python scripts/sync_check.py --root /path/to/repo --lang uk
```

Uses `i18n-source-sha` metadata in translated files to compare against current git SHA.

## Output Structure

```
any-repo/
├── README.md                    ← original
├── docs/
│   └── guide.md
├── src/
│   └── app.py                   ← not touched
└── translations/                ← created by repo-translator
    └── uk/
        ├── README.md            ← translated
        └── docs/
            └── guide.md         ← translated
```

Only `.md` files are translated. Code, images, and configs stay in the original location. Links are rewritten to point to originals where needed.

## Validation Checks

| Check | Type | Auto-Fix |
|-------|------|----------|
| UTF-8 encoding | Critical | ✅ |
| Line count ≥85% of original | Error | ❌ Re-translate |
| Code block count = original | Error | ❌ Re-translate |
| Mermaid diagram count = original | Error | ❌ Re-translate |
| Unmatched code fences | Error | ❌ Re-translate |
| Code block content preserved | Warning | ❌ Manual |
| Heading count matches | Warning | ❌ Manual |
| Table row count matches | Warning | ❌ Manual |
| Anchor links resolve | Error | ✅ |
| URLs preserved | Warning | ❌ Manual |
| Invisible Unicode chars | Warning | ✅ |
| Trailing newline | Warning | ✅ |

## Any Language

Uses ISO 639-1 codes. 35+ languages built-in, any code accepted:

```bash
python scripts/scan.py --lang uk      # Ukrainian
python scripts/scan.py --lang ja      # Japanese
python scripts/scan.py --lang ar      # Arabic
python scripts/scan.py --lang pt-br   # Brazilian Portuguese
python scripts/scan.py --lang de      # German
```

## Configuration

Works without any config. For customization, create `.repo-translator.yaml` in the target repo:

```yaml
source_lang: en
translations_dir: translations

include:
  - "**/*.md"
  - "**/*.mdx"

exclude:
  - "CHANGELOG.md"
  - "node_modules/**"
```

See [.repo-translator.yaml.example](.repo-translator.yaml.example) for all options.

## Requirements

- Python 3.10+
- No external dependencies for core scripts
- Optional: `pyyaml` for config/glossary files (falls back to basic parsing)
- Optional: `git` for sync-check functionality

## Contributing

Contributions welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting PRs.

## License

MIT License — see [LICENSE](LICENSE) for details.

---

Built by [@edocltd](https://github.com/edocltd)
