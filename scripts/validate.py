#!/usr/bin/env python3
"""Validate translated files against originals."""

import argparse
import json
import re
import sys
from pathlib import Path


def heading_to_anchor(heading: str) -> str:
    """Convert heading text to GitHub-style anchor."""
    # Remove emoji
    heading = re.sub(
        r"[\U0001F000-\U0001FFFF\U00002702-\U000027B0"
        r"\U0000FE00-\U0000FE0F\U0000200D"
        r"\U000000A9\U000000AE\U00002000-\U0000206F]",
        "",
        heading,
    )
    # Remove punctuation, keep word chars, spaces, hyphens
    anchor = re.sub(r"[^\w\s-]", "", heading.lower(), flags=re.UNICODE)
    anchor = anchor.replace(" ", "-")
    return anchor.rstrip("-")


def strip_code_blocks(content: str) -> str:
    """Remove fenced code blocks and inline code."""
    content = re.sub(r"```[^\n]*\n.*?```", "", content, flags=re.DOTALL)
    content = re.sub(r"~~~~[^\n]*\n.*?~~~~", "", content, flags=re.DOTALL)
    content = re.sub(r"`[^`\n]+`", "", content)
    return content


def extract_code_blocks(content: str) -> list[str]:
    """Extract all fenced code block contents."""
    blocks = re.findall(r"```[^\n]*\n(.*?)```", content, flags=re.DOTALL)
    blocks += re.findall(r"~~~~[^\n]*\n(.*?)~~~~", content, flags=re.DOTALL)
    return blocks


def extract_urls(content: str) -> set[str]:
    """Extract all URLs from markdown."""
    scannable = strip_code_blocks(content)
    urls = re.findall(r"https?://[^\s\)>]+", scannable)
    return set(urls)


def check_utf8(path: Path) -> dict:
    """Check if file is valid UTF-8."""
    with open(path, "rb") as f:
        raw = f.read()
    try:
        raw.decode("utf-8")
        return {"status": "ok"}
    except UnicodeDecodeError as e:
        return {
            "status": "error",
            "message": f"Invalid UTF-8 at byte {e.start}: {e.reason}",
            "byte_offset": e.start,
        }


def check_structure(original: str, translated: str) -> list[dict]:
    """Check structural parity between original and translated files."""
    issues = []

    # Line count
    orig_lines = original.count("\n") + 1
    trans_lines = translated.count("\n") + 1
    ratio = trans_lines / max(orig_lines, 1)

    if ratio < 0.85:
        issues.append(
            {
                "severity": "error",
                "check": "line_count",
                "message": f"File shortened: {trans_lines} lines vs {orig_lines} original ({ratio:.0%})",
            }
        )
    elif ratio < 0.95:
        issues.append(
            {
                "severity": "warning",
                "check": "line_count",
                "message": f"Line count differs: {trans_lines} vs {orig_lines} ({ratio:.0%})",
            }
        )

    # Code blocks count
    orig_fences = len(re.findall(r"^```", original, re.MULTILINE))
    trans_fences = len(re.findall(r"^```", translated, re.MULTILINE))

    if orig_fences != trans_fences:
        issues.append(
            {
                "severity": "error",
                "check": "code_blocks",
                "message": f"Code block count mismatch: {trans_fences} vs {orig_fences} original",
            }
        )

    # Unmatched fences
    if trans_fences % 2 != 0:
        issues.append(
            {
                "severity": "error",
                "check": "code_fences",
                "message": f"Unmatched code fences (odd count: {trans_fences})",
            }
        )

    # Mermaid blocks
    orig_mermaid = len(re.findall(r"^```mermaid", original, re.MULTILINE))
    trans_mermaid = len(re.findall(r"^```mermaid", translated, re.MULTILINE))

    if orig_mermaid != trans_mermaid:
        issues.append(
            {
                "severity": "error",
                "check": "mermaid",
                "message": f"Mermaid count mismatch: {trans_mermaid} vs {orig_mermaid} original",
            }
        )

    # Heading count
    orig_headings = len(re.findall(r"^#{1,6}\s", original, re.MULTILINE))
    trans_headings = len(re.findall(r"^#{1,6}\s", translated, re.MULTILINE))

    if orig_headings != trans_headings:
        issues.append(
            {
                "severity": "warning",
                "check": "headings",
                "message": f"Heading count differs: {trans_headings} vs {orig_headings} original",
            }
        )

    # Table row count
    orig_tables = len(re.findall(r"^\|", original, re.MULTILINE))
    trans_tables = len(re.findall(r"^\|", translated, re.MULTILINE))

    if orig_tables > 0 and abs(orig_tables - trans_tables) > 2:
        issues.append(
            {
                "severity": "warning",
                "check": "tables",
                "message": f"Table row count differs: {trans_tables} vs {orig_tables}",
            }
        )

    return issues


def check_code_preserved(original: str, translated: str) -> list[dict]:
    """Check that code blocks are preserved identically."""
    issues = []
    orig_blocks = extract_code_blocks(original)
    trans_blocks = extract_code_blocks(translated)

    if len(orig_blocks) != len(trans_blocks):
        # Already caught by structure check
        return issues

    for i, (orig, trans) in enumerate(zip(orig_blocks, trans_blocks)):
        if orig.strip() != trans.strip():
            # Show first difference
            orig_lines = orig.strip().split("\n")
            trans_lines = trans.strip().split("\n")
            for j, (ol, tl) in enumerate(zip(orig_lines, trans_lines)):
                if ol != tl:
                    issues.append(
                        {
                            "severity": "warning",
                            "check": "code_content",
                            "message": (
                                f"Code block #{i + 1} modified at line {j + 1}: "
                                f"'{tl[:50]}...' vs '{ol[:50]}...'"
                            ),
                        }
                    )
                    break

    return issues


def check_anchors(translated: str) -> list[dict]:
    """Check that all in-page anchor links resolve to headings."""
    issues = []
    scannable = strip_code_blocks(translated)

    # Collect all headings and generate anchors
    headings = re.findall(r"^#{1,6}\s+(.+)$", translated, re.MULTILINE)
    anchor_counts: dict[str, int] = {}
    valid_anchors = set()

    for h in headings:
        anchor = heading_to_anchor(h)
        if anchor in anchor_counts:
            anchor_counts[anchor] += 1
            valid_anchors.add(f"{anchor}-{anchor_counts[anchor]}")
        else:
            anchor_counts[anchor] = 0
            valid_anchors.add(anchor)

    # Find all in-page anchor links
    anchors = re.findall(r"\[[^\]]+\]\(#([^)]+)\)", scannable)

    for anchor in anchors:
        if anchor not in valid_anchors:
            # Try to find best match
            best = find_best_anchor(anchor, valid_anchors)
            issues.append(
                {
                    "severity": "error",
                    "check": "anchor",
                    "message": f"Broken anchor: #{anchor}",
                    "suggested_fix": f"#{best}" if best else None,
                    "auto_fixable": best is not None,
                }
            )

    return issues


def find_best_anchor(broken: str, valid: set[str]) -> str | None:
    """Find the closest matching valid anchor for a broken one."""
    # Normalize: remove apostrophes, convert to lowercase
    broken_norm = re.sub(r"[\u0027\u02bc\u2019\u2018]", "", broken.lower())

    for v in valid:
        v_norm = re.sub(r"[\u0027\u02bc\u2019\u2018]", "", v.lower())
        if broken_norm == v_norm:
            return v

    # Fuzzy: check if one contains the other
    for v in valid:
        if broken.lower() in v.lower() or v.lower() in broken.lower():
            return v

    return None


def check_urls_preserved(original: str, translated: str) -> list[dict]:
    """Check that URLs are not modified in translation."""
    issues = []
    orig_urls = extract_urls(original)
    trans_urls = extract_urls(translated)

    added = trans_urls - orig_urls
    removed = orig_urls - trans_urls

    for url in removed:
        issues.append(
            {
                "severity": "warning",
                "check": "url_removed",
                "message": f"URL removed: {url[:80]}",
            }
        )

    for url in added:
        issues.append(
            {
                "severity": "warning",
                "check": "url_added",
                "message": f"URL added: {url[:80]}",
            }
        )

    return issues


def check_encoding_issues(content: str) -> list[dict]:
    """Check for invisible Unicode characters and encoding artifacts."""
    issues = []

    # Invisible characters
    invisible = {
        "\u200b": "Zero-width space",
        "\u200c": "Zero-width non-joiner",
        "\u200d": "Zero-width joiner",
        "\u200e": "Left-to-right mark",
        "\u200f": "Right-to-left mark",
        "\ufeff": "BOM (not at start)",
    }

    for char, name in invisible.items():
        positions = [i for i, c in enumerate(content) if c == char]
        # Allow BOM only at position 0
        if char == "\ufeff":
            positions = [p for p in positions if p > 0]
        if positions:
            issues.append(
                {
                    "severity": "warning",
                    "check": "invisible_unicode",
                    "message": f"Found {name} (U+{ord(char):04X}) at {len(positions)} positions",
                    "auto_fixable": True,
                }
            )

    # Missing newline at end
    if content and not content.endswith("\n"):
        issues.append(
            {
                "severity": "warning",
                "check": "trailing_newline",
                "message": "Missing newline at end of file",
                "auto_fixable": True,
            }
        )

    return issues


def check_glossary(content: str, glossary: dict | None) -> list[dict]:
    """Check glossary consistency."""
    if not glossary:
        return []

    issues = []
    terms = glossary.get("terms", {})
    scannable = strip_code_blocks(content).lower()

    for eng_term, expected_translation in terms.items():
        # This is a simplified check — look for known bad translations
        # A full implementation would do NLP-based matching
        pass

    return issues


def validate_file(
    original_path: Path,
    translated_path: Path,
    glossary: dict | None = None,
) -> dict:
    """Run all validation checks on a translated file."""

    result = {
        "original": str(original_path),
        "translated": str(translated_path),
        "issues": [],
        "summary": {"errors": 0, "warnings": 0},
    }

    # Check UTF-8
    utf8 = check_utf8(translated_path)
    if utf8["status"] != "ok":
        result["issues"].append(
            {
                "severity": "error",
                "check": "utf8",
                "message": utf8["message"],
            }
        )
        result["summary"]["errors"] += 1
        return result  # Can't do further checks if encoding is broken

    # Read files
    try:
        original = original_path.read_text(encoding="utf-8")
        translated = translated_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        result["issues"].append(
            {"severity": "error", "check": "read", "message": str(e)}
        )
        result["summary"]["errors"] += 1
        return result

    # Run all checks
    all_checks = [
        check_structure(original, translated),
        check_code_preserved(original, translated),
        check_anchors(translated),
        check_urls_preserved(original, translated),
        check_encoding_issues(translated),
    ]

    if glossary:
        all_checks.append(check_glossary(translated, glossary))

    for check_issues in all_checks:
        result["issues"].extend(check_issues)

    # Count severities
    for issue in result["issues"]:
        if issue["severity"] == "error":
            result["summary"]["errors"] += 1
        elif issue["severity"] == "warning":
            result["summary"]["warnings"] += 1

    return result


def validate_directory(
    original_root: Path,
    translations_dir: Path,
    glossary: dict | None = None,
) -> dict:
    """Validate all translated files in a directory."""

    results = {
        "files": [],
        "summary": {
            "total_files": 0,
            "passed": 0,
            "errors": 0,
            "warnings": 0,
        },
    }

    for trans_path in sorted(translations_dir.rglob("*.md")):
        # Find corresponding original
        rel = trans_path.relative_to(translations_dir)
        orig_path = original_root / rel

        if not orig_path.exists():
            # Translation-specific file (e.g., TRANSLATION_NOTES.md) — skip
            continue

        file_result = validate_file(orig_path, trans_path, glossary)
        results["files"].append(file_result)
        results["summary"]["total_files"] += 1

        if file_result["summary"]["errors"] > 0:
            results["summary"]["errors"] += 1
        elif file_result["summary"]["warnings"] > 0:
            results["summary"]["warnings"] += 1
        else:
            results["summary"]["passed"] += 1

    return results


def print_results(results: dict) -> None:
    """Print validation results in human-readable format."""
    s = results["summary"]
    total = s["total_files"]

    print(f"\n{'='*60}")
    print(f"  repo-translator — Validation Report")
    print(f"{'='*60}\n")

    for file_result in results["files"]:
        issues = file_result["issues"]
        trans = file_result["translated"]
        errors = file_result["summary"]["errors"]
        warnings = file_result["summary"]["warnings"]

        if errors == 0 and warnings == 0:
            continue  # Don't print clean files

        icon = "❌" if errors > 0 else "⚠️"
        print(f"  {icon} {trans}")

        for issue in issues:
            sev = "🔴" if issue["severity"] == "error" else "🟡"
            print(f"     {sev} [{issue['check']}] {issue['message']}")
            if issue.get("suggested_fix"):
                print(f"        → Suggested fix: {issue['suggested_fix']}")

        print()

    # Summary
    print(f"  {'='*56}")
    print(f"  Total files:  {total}")
    print(f"  ✅ Passed:     {s['passed']}")
    if s["warnings"] > 0:
        print(f"  ⚠️  Warnings:   {s['warnings']}")
    if s["errors"] > 0:
        print(f"  ❌ Errors:     {s['errors']}")
    print()

    if s["errors"] > 0:
        print(f"  Result: FAILED — {s['errors']} file(s) with errors")
    elif s["warnings"] > 0:
        print(f"  Result: PASSED with {s['warnings']} warning(s)")
    else:
        print(f"  Result: ALL PASSED ✅")
    print()


def main():
    parser = argparse.ArgumentParser(description="Validate translated files")
    parser.add_argument(
        "--root", "-r", default=".", help="Repository root (default: current dir)"
    )
    parser.add_argument("--lang", "-l", required=True, help="Target language code")
    parser.add_argument(
        "--translations-dir",
        "-d",
        default="translations",
        help="Translations directory name",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--file", "-f", default=None, help="Validate single file (relative path)"
    )

    args = parser.parse_args()
    root = Path(args.root).resolve()
    trans_dir = root / args.translations_dir / args.lang

    if not trans_dir.exists():
        print(f"Error: {trans_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    if args.file:
        orig = root / args.file
        trans = trans_dir / args.file
        if not orig.exists():
            print(f"Error: original {orig} not found", file=sys.stderr)
            sys.exit(1)
        if not trans.exists():
            print(f"Error: translation {trans} not found", file=sys.stderr)
            sys.exit(1)
        result = validate_file(orig, trans)
        results = {
            "files": [result],
            "summary": {
                "total_files": 1,
                "passed": 1 if result["summary"]["errors"] == 0 else 0,
                "errors": 1 if result["summary"]["errors"] > 0 else 0,
                "warnings": 1 if result["summary"]["warnings"] > 0 else 0,
            },
        }
    else:
        results = validate_directory(root, trans_dir)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_results(results)

    sys.exit(1 if results["summary"]["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
