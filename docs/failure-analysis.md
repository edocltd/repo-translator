# Failure Analysis: 48 Real Problems in Repository Translation

Every problem documented here was encountered during real translation work on [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐). Each entry includes: scenario, risk level, and implemented defense.

---

## Category 1: Scanning & Repo Analysis

### P1.1: Giant repository
**Scenario**: User runs tool on monorepo with 50,000+ files.
**Defense**: File limit (default: 500), depth limit (10 levels), warning with suggestion to narrow scope.

### P1.2: Non-git repository
**Scenario**: Directory without `.git/`.
**Defense**: Tool works without git. Sync-check disabled with warning. Uses file hash instead of commit SHA.

### P1.3: Existing translation structure
**Scenario**: Repo already has `uk/`, `translations/`, `i18n/` directories.
**Defense**: Auto-detect existing translations and exclude from scanning. Report what was found.

### P1.4: Symlinks and circular references
**Defense**: Don't follow symlinks. Track visited paths via `set(realpath)`.

### P1.5: Binary files with .md extension
**Defense**: Check first 8KB for null bytes. If >1% nulls → classify as binary, skip.

### P1.6: Empty .md files
**Defense**: Skip files <10 bytes. Skip files with only frontmatter (no prose).

### P1.7: Same filename in different directories
**Defense**: Always preserve full directory structure. Never flatten.

---

## Category 2: Translation Quality (AI Output)

### P2.1: AI shortens file ⚠️ CRITICAL
**Real case**: Original 1945 lines, AI returned 540 (58% lost).
**Defense**: Check line count after translation. Reject if <85% of original.

### P2.2: AI translates code blocks ⚠️ CRITICAL
**Real case**: `mkdir -p .claude/commands` became `створити_каталог .claude/commands`.
**Defense**: Extract code blocks as placeholders BEFORE sending to AI. Restore AFTER. Code never passes through AI.

### P2.3: AI translates Mermaid labels
**Defense**: Treat Mermaid blocks as code blocks (placeholder extraction).

### P2.4: AI changes Markdown formatting
**Defense**: Validate heading count, table row count, bold/italic markers match original.

### P2.5: AI hallucinated URLs
**Defense**: Extract URLs from original and translation. Report added/removed URLs.

### P2.6: AI removes HTML tags
**Defense**: Extract HTML as placeholders (like code blocks).

### P2.7: AI adds translator notes
**Defense**: Prompt rule: "DO NOT add notes." Validate: scan for "note:", "translator" patterns.

### P2.8: Large file exceeds context ⚠️ CRITICAL
**Real case**: 87KB / 3136 lines file.
**Defense**: Chunk by `##` headings. If section still too large → chunk by `###`. Each chunk gets same glossary and rules.

### P2.9: AI returns truncated response
**Defense**: Check if last line is complete sentence. Check if code fence count is even (all blocks closed).

---

## Category 3: Links & Anchors

### P3.1: Broken anchors after translation ⚠️ CRITICAL
**Real case**: `[See below](#slash-commands)` but heading is now `## Слеш-команди` → anchor is `#слеш-команди`.
**Defense**: After translation, collect all headings → generate anchors → compare with links → auto-fix mismatches.

### P3.2: Apostrophe variants in anchors ⚠️ CRITICAL
**Real case**: Heading uses `'` (U+0027) which is stripped in anchor, but link uses `ʼ` (U+02BC) which is kept → mismatch.
**Defense**: Normalize all apostrophe variants when comparing anchors.

### P3.3: Duplicate headings
**Real case**: Two `## Prompt-хуки` headings. GitHub adds `-1` suffix to second. Validator didn't handle this.
**Defense**: Track heading counter. Generate `-1`, `-2` suffixes for duplicates.

### P3.4: Relative links to untranslated files
**Scenario**: `translations/uk/docs/guide.md` links to `../src/deploy.sh` which doesn't exist at that path.
**Defense**: Rewrite relative links: if target is translated → keep local link. If not → rewrite to original.

### P3.5: Absolute paths
**Defense**: Detect and warn. Don't auto-rewrite (framework-specific behavior).

### P3.6: Cross-file anchor links
**Scenario**: `[See](other.md#section)` where `other.md` is translated → `#section` may become `#секція`.
**Defense**: Resolve target file first, then check anchors in the correct version.

---

## Category 4: Encoding & File Format

### P4.1: File not UTF-8 ⚠️ CRITICAL
**Real case**: AI returned partial CP1251 in UTF-8 file. 240 invalid bytes.
**Defense**: Verify UTF-8 after every write. Auto-repair: detect bad byte ranges, try CP1251 → UTF-8 re-encoding.

### P4.2: BOM (Byte Order Mark)
**Defense**: Ignore BOM on read. Never write BOM.

### P4.3: CRLF vs LF
**Defense**: Match original line endings. Default to LF.

### P4.4: Missing trailing newline
**Defense**: Always add `\n` at end of file.

### P4.5: Invisible Unicode characters
**Defense**: Remove U+200B (zero-width space), U+200C, U+200D, U+200E, U+200F after translation.

---

## Category 5: Language-Specific Issues

### P5.1: RTL languages (Arabic, Hebrew)
**Defense**: Warning at init. Limited Markdown support for RTL.

### P5.2: CJK languages (Chinese, Japanese, Korean)
**Defense**: Adjust line count tolerance (CJK text is shorter). Use code block count as primary structural check.

### P5.3: Special character casing (Turkish İ/ı)
**Defense**: Use Unicode-aware comparison (`str.casefold()`).

### P5.4: Per-language glossary
**Defense**: Glossary generated per language. Built-in term database for 10-15 popular languages.

---

## Category 6: Frontmatter & Metadata

### P6.1: YAML frontmatter breaks on translation
**Defense**: Parse YAML separately. Translate only `description` field. Always quote values after translation.

### P6.2: Double frontmatter
**Defense**: Only first `---...---` block at file start is frontmatter.

### P6.3: Tilde-fenced blocks (`~~~~`)
**Defense**: Handle both ` ``` ` and `~~~~` as code block markers.

---

## Category 7: Filesystem

### P7.1: No write permissions
**Defense**: Check write access before starting.

### P7.2: Disk full
**Defense**: Estimate required space (2× source .md size). Check free space.

### P7.3: Long paths (Windows 260 char limit)
**Defense**: Warn if resulting path >250 chars.

### P7.4: Special characters in filenames
**Defense**: Preserve original names. Use `Path` objects, not string concatenation.

### P7.5: Case sensitivity
**Defense**: Use exact original filenames. Warn on case-only duplicates.

---

## Category 8: Git & Version Control

### P8.1: Huge diff
**Defense**: Recommend splitting into batch PRs by priority.

### P8.2: Merge conflicts
**Defense**: Each language is a separate subdirectory → no conflicts between languages.

### P8.3: Squash merge loses SHA tracking
**Defense**: Fallback to date-based lookup when SHA not found in history.

---

## Category 9: Configuration

### P9.1: Invalid YAML in config
**Defense**: Validate on load. Fallback to defaults with warning.

### P9.2: Unknown language code
**Defense**: Validate against ISO 639-1. Fuzzy match: "ukr" → "Did you mean uk?"

### P9.3: Glossary conflicts
**Defense**: Check for conflicting root-word translations on load. Warn.

---

## Category 10: Edge Cases

### P10.1: File that is only tables
**Defense**: Process tables row-by-row. Verify `|` count per line matches.

### P10.2: Markdown with inline HTML
**Defense**: HTML tags → placeholders. Translate text between tags, not attributes.

### P10.3: LaTeX formulas
**Defense**: Detect `$...$` and `$$...$$`. Extract as placeholders.

### P10.4: Emoji in headings
**Defense**: Strip emoji when generating anchors (matches GitHub behavior).

### P10.5: File without headings
**Defense**: Chunk by blank lines instead of `##`. If <4000 tokens → translate whole file.

### P10.6: Duplicate i18n metadata
**Defense**: Check for existing metadata before adding. Update, don't duplicate.

### P10.7: Translating translations ⚠️ CRITICAL
**Defense**: ALWAYS exclude `translations_dir` from scanning. Verify source ≠ target directory.

### P10.8: Recursive include/exclude
**Defense**: `exclude: ["**/CHANGELOG.md"]` excludes in any directory. `exclude: ["CHANGELOG.md"]` only in root.

---

## Defense Summary

### Automatic (no user action):
| Defense | When | Action |
|---------|------|--------|
| UTF-8 check | After every write | Auto-repair or reject |
| Code block placeholders | During translation | Code never passes through AI |
| Line count check | After translation | Reject if <85% |
| Anchor fix | After translation | Auto-replace broken anchors |
| Link rewriting | During file creation | Auto-rewrite relative paths |
| Trailing newline | On write | Auto-add |
| Invisible Unicode removal | After translation | Auto-remove |
| Metadata dedup | On header add | Update instead of duplicate |

### Warnings (need user attention):
| Defense | When | Message |
|---------|------|---------|
| Large repo | On scan | "12,847 files, recommend narrowing scope" |
| Existing translations | On init | "Found uk/, importing?" |
| Glossary mismatch | On validate | "hook translated as гачок (1x)" |
| RTL language | On init | "Needs extra attention" |
| Absolute paths | On scan | "Cannot be auto-rewritten" |

### Blocking (stop process):
| Defense | When | Reason |
|---------|------|--------|
| File shortened >15% | After translation | AI lost content |
| Code block count mismatch | After translation | Structure broken |
| Source = target directory | On init | Would translate translations |
| No write permissions | On init | Cannot save |

---

## Implementation Priority

### MVP (implemented):
1. ✅ UTF-8 validation (P4.1)
2. ✅ Line count check (P2.1)
3. ✅ Code block count check (P2.1)
4. ✅ Anchor auto-fix (P3.1, P3.2, P3.3)
5. ✅ Translation dir exclusion (P10.7)
6. ✅ Auto-detect existing translations (P1.3)

### Next (planned):
7. Code block placeholder extraction (P2.2)
8. HTML placeholder extraction (P2.6)
9. Glossary checking (P5.4)
10. Frontmatter handling (P6.1)
11. Large file chunking (P2.8)
12. Relative link rewriting (P3.4)

### Future:
13. RTL support (P5.1)
14. CJK coefficients (P5.2)
15. LaTeX placeholders (P10.3)
16. Translation memory
