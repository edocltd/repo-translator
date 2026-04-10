# repo-translator

Universal tool for translating GitHub repository documentation into any language.

Not an API wrapper — a **framework** for structure, validation, and sync. Translate with any method: Claude Code, Claude.ai, ChatGPT, Ollama, or manually.

## The Problem

You want to translate a repository's documentation. You face:

- **No structure**: Which files to translate? Which to skip? Where to put results?
- **No validation**: Did the AI silently delete half your content? Break anchor links? Corrupt encoding?
- **No consistency**: "hook" translated as "хук" in one file and "гачок" in another.
- **No sync**: Original updated last week — which translations are outdated?

Existing tools (co-op-translator, gpt-translate) handle translation but skip validation entirely.

## What repo-translator Does

```
SCAN → TRANSLATE → VALIDATE → FIX → SYNC
  ↓        ↓           ↓        ↓      ↓
"What    "Any       "Is it   "Auto-  "What's
 files?"  method"   correct?" fix"   outdated?"
```

1. **Scan** — Analyze repo, classify files (translate / copy / skip), estimate effort
2. **Translate** — Use any method (AI, manual, copy-paste). Tool generates prompts and glossary
3. **Validate** — Check structure (line count, code blocks, Mermaid), anchors, encoding, glossary
4. **Fix** — Auto-fix broken anchors, encoding issues, invisible Unicode
5. **Sync** — Track which translations are outdated when originals change

## Quick Start

```bash
# Clone
git clone https://github.com/edocltd/repo-translator.git

# Scan a repo to see what needs translating
python repo-translator/scripts/scan.py --root /path/to/any-repo --lang uk

# Generate a translation prompt (copy-paste into Claude.ai / ChatGPT)
python repo-translator/scripts/prompt_generator.py /path/to/any-repo/README.md --lang uk

# After translating — validate
python repo-translator/scripts/validate.py --root /path/to/any-repo --lang uk

# Auto-fix broken anchors and encoding
python repo-translator/scripts/fix_anchors.py /path/to/any-repo/translations/uk/

# Check what's outdated
python repo-translator/scripts/sync_check.py --root /path/to/any-repo --lang uk
```

## Translation Methods (all supported)

| Method | Cost | Setup | Best for |
|--------|------|-------|----------|
| **Claude Code** | $0 extra | Already installed | Subscribers — fastest workflow |
| **Copy-paste** | $0-20/mo | Any AI chat | Anyone with Claude.ai / ChatGPT |
| **Manual** | $0 | None | Human translators, small repos |
| **Ollama** | $0 | Install Ollama | Privacy-sensitive, offline work |
| **API** | Pay-per-use | API key | Automation, large repos |

The tool doesn't care HOW you translate. It ensures the result is correct.

## Output Structure

```
any-repo/
├── README.md                    ← original
├── docs/
│   └── guide.md
├── src/
│   └── app.py                   ← not touched (code)
│
└── translations/                ← created by repo-translator
    └── uk/
        ├── README.md            ← translated
        ├── docs/
        │   └── guide.md         ← translated
        └── .glossary.yaml       ← project glossary
```

Only `.md` files are translated. Code, images, configs stay in the original location. Links are automatically rewritten to point to originals.

## Validation Checks

| Check | Type | Auto-fix |
|-------|------|----------|
| UTF-8 encoding | Critical | ✅ Yes |
| Line count ±5% of original | Error | ❌ Re-translate |
| Code blocks count = original | Error | ❌ Re-translate |
| Mermaid diagrams count = original | Error | ❌ Re-translate |
| Code block content identical | Warning | ❌ Manual |
| Anchor links resolve | Error | ✅ Yes |
| URLs preserved | Warning | ❌ Manual |
| Glossary consistency | Warning | ❌ Manual |
| Invisible Unicode chars | Warning | ✅ Yes |
| Trailing newline | Warning | ✅ Yes |

## Any Language

Uses ISO 639-1 codes. Any language supported:

```bash
python scripts/scan.py --lang uk     # Ukrainian
python scripts/scan.py --lang ja     # Japanese
python scripts/scan.py --lang ar     # Arabic
python scripts/scan.py --lang pt-br  # Brazilian Portuguese
```

## Configuration (optional)

Works without config. For customization, create `.repo-translator.yaml` in the target repo:

```yaml
source_lang: en
translations_dir: translations
include:
  - "**/*.md"
exclude:
  - "CHANGELOG.md"
  - "node_modules/**"
```

See `.repo-translator.yaml.example` for all options.

## Built from Real Experience

Every feature exists because of a real problem encountered while translating [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐) into Ukrainian:

- AI shortened files by 58% → **line count validation**
- AI translated code blocks → **placeholder extraction**
- Anchors broke after translating headings → **auto-fix anchors**
- Mixed CP1251/UTF-8 encoding → **encoding detection and repair**
- Inconsistent terminology across files → **glossary enforcement**

See [FAILURE-ANALYSIS.md](FAILURE-ANALYSIS.md) for the full 48-problem analysis.

## Requirements

- Python 3.10+
- No external dependencies for core scripts
- Optional: `pyyaml` for config/glossary files (falls back to basic parsing)

## License

MIT
