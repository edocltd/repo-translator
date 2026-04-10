#!/usr/bin/env python3
"""Auto-fix broken anchor links in translated markdown files."""

import argparse
import re
import sys
from pathlib import Path


def heading_to_anchor(heading: str) -> str:
    """Convert heading text to GitHub-style anchor."""
    heading = re.sub(
        r"[\U0001F000-\U0001FFFF\U00002702-\U000027B0"
        r"\U0000FE00-\U0000FE0F\U0000200D"
        r"\U000000A9\U000000AE\U00002000-\U0000206F]",
        "",
        heading,
    )
    anchor = re.sub(r"[^\w\s-]", "", heading.lower(), flags=re.UNICODE)
    anchor = anchor.replace(" ", "-")
    return anchor.rstrip("-")


def strip_code_blocks(content: str) -> str:
    """Remove fenced code blocks for scanning (not modifying)."""
    content = re.sub(r"```[^\n]*\n.*?```", "", content, flags=re.DOTALL)
    content = re.sub(r"~~~~[^\n]*\n.*?~~~~", "", content, flags=re.DOTALL)
    content = re.sub(r"`[^`\n]+`", "", content)
    return content


def normalize_anchor(anchor: str) -> str:
    """Normalize anchor for comparison (remove all apostrophe variants)."""
    return re.sub(r"[\u0027\u02bc\u2019\u2018]", "", anchor.lower())


def collect_valid_anchors(content: str) -> dict[str, str]:
    """Collect all valid anchors from headings, handling duplicates."""
    headings = re.findall(r"^#{1,6}\s+(.+)$", content, re.MULTILINE)
    anchor_counts: dict[str, int] = {}
    valid: dict[str, str] = {}  # normalized -> actual

    for h in headings:
        anchor = heading_to_anchor(h)
        if anchor in anchor_counts:
            anchor_counts[anchor] += 1
            suffixed = f"{anchor}-{anchor_counts[anchor]}"
            valid[normalize_anchor(suffixed)] = suffixed
        else:
            anchor_counts[anchor] = 0
            valid[normalize_anchor(anchor)] = anchor

    return valid


def find_best_match(broken: str, valid: dict[str, str]) -> str | None:
    """Find best matching valid anchor for a broken one."""
    broken_norm = normalize_anchor(broken)

    # Exact match after normalization
    if broken_norm in valid:
        return valid[broken_norm]

    # Substring match
    for norm, actual in valid.items():
        if broken_norm in norm or norm in broken_norm:
            return actual

    return None


def fix_anchors_in_file(path: Path, dry_run: bool = False) -> list[dict]:
    """Fix broken anchor links in a single file."""
    content = path.read_text(encoding="utf-8")
    scannable = strip_code_blocks(content)
    valid = collect_valid_anchors(content)

    fixes = []

    # Find all in-page anchor links (outside code blocks)
    # We need to find them in original content but only fix those outside code blocks
    for match in re.finditer(r"(\[[^\]]+\])\(#([^)]+)\)", content):
        full_match = match.group(0)
        link_text = match.group(1)
        anchor = match.group(2)

        # Check if this match is inside a code block
        pos = match.start()
        before = content[:pos]
        open_fences = len(re.findall(r"^```", before, re.MULTILINE))
        if open_fences % 2 != 0:
            continue  # Inside code block, skip

        anchor_norm = normalize_anchor(anchor)
        if anchor_norm not in valid:
            best = find_best_match(anchor, valid)
            if best and best != anchor:
                fixes.append(
                    {
                        "line": content[:pos].count("\n") + 1,
                        "old": f"#{anchor}",
                        "new": f"#{best}",
                        "context": full_match,
                    }
                )

    if fixes and not dry_run:
        fixed_content = content
        # Apply fixes in reverse order to preserve positions
        for fix in reversed(fixes):
            fixed_content = fixed_content.replace(
                f"]({fix['old']})", f"]({fix['new']})", 1
            )
        path.write_text(fixed_content, encoding="utf-8")

    return fixes


def fix_encoding(path: Path, dry_run: bool = False) -> dict | None:
    """Fix mixed encoding issues (e.g., CP1251 blocks in UTF-8 file)."""
    with open(path, "rb") as f:
        raw = f.read()

    try:
        raw.decode("utf-8")
        return None  # File is valid UTF-8
    except UnicodeDecodeError:
        pass

    # Find bad zones and try to fix
    fixed = bytearray()
    i = 0
    fixes_count = 0

    while i < len(raw):
        b = raw[i]
        if b < 0x80:
            fixed.append(b)
            i += 1
        elif b < 0xC0:
            # Invalid continuation byte — try CP1251
            try:
                char = bytes([b]).decode("cp1251")
                fixed.extend(char.encode("utf-8"))
                fixes_count += 1
            except (UnicodeDecodeError, ValueError):
                fixed.append(b)
            i += 1
        elif b < 0xE0:
            if i + 1 < len(raw) and 0x80 <= raw[i + 1] < 0xC0:
                fixed.extend(raw[i : i + 2])
                i += 2
            else:
                try:
                    char = bytes([b]).decode("cp1251")
                    fixed.extend(char.encode("utf-8"))
                    fixes_count += 1
                except (UnicodeDecodeError, ValueError):
                    fixed.append(b)
                i += 1
        elif b < 0xF0:
            if i + 2 < len(raw) and all(0x80 <= raw[i + j] < 0xC0 for j in range(1, 3)):
                fixed.extend(raw[i : i + 3])
                i += 3
            else:
                try:
                    char = bytes([b]).decode("cp1251")
                    fixed.extend(char.encode("utf-8"))
                    fixes_count += 1
                except (UnicodeDecodeError, ValueError):
                    fixed.append(b)
                i += 1
        else:
            if i + 3 < len(raw) and all(0x80 <= raw[i + j] < 0xC0 for j in range(1, 4)):
                fixed.extend(raw[i : i + 4])
                i += 4
            else:
                fixed.append(b)
                i += 1

    # Verify fix
    try:
        bytes(fixed).decode("utf-8")
    except UnicodeDecodeError:
        return {"status": "failed", "message": "Could not auto-fix encoding"}

    if fixes_count > 0 and not dry_run:
        with open(path, "wb") as f:
            f.write(bytes(fixed))

    return {"status": "fixed", "bytes_fixed": fixes_count}


def remove_invisible_unicode(path: Path, dry_run: bool = False) -> int:
    """Remove invisible Unicode characters from file."""
    content = path.read_text(encoding="utf-8")
    invisible = "\u200b\u200c\u200d\u200e\u200f"

    # Keep BOM only at position 0
    cleaned = content.lstrip("\ufeff") if content.startswith("\ufeff") else content
    for char in invisible:
        cleaned = cleaned.replace(char, "")

    removed = len(content) - len(cleaned)
    if removed > 0 and not dry_run:
        path.write_text(cleaned, encoding="utf-8")

    return removed


def ensure_trailing_newline(path: Path, dry_run: bool = False) -> bool:
    """Ensure file ends with newline."""
    content = path.read_text(encoding="utf-8")
    if content and not content.endswith("\n"):
        if not dry_run:
            path.write_text(content + "\n", encoding="utf-8")
        return True
    return False


def fix_file(path: Path, dry_run: bool = False) -> dict:
    """Run all auto-fixes on a file."""
    result = {"path": str(path), "fixes": []}

    # Fix encoding first
    enc = fix_encoding(path, dry_run)
    if enc and enc["status"] == "fixed":
        result["fixes"].append(f"Encoding: fixed {enc['bytes_fixed']} bytes")

    # Fix anchors
    anchor_fixes = fix_anchors_in_file(path, dry_run)
    for fix in anchor_fixes:
        result["fixes"].append(
            f"Anchor line {fix['line']}: {fix['old']} → {fix['new']}"
        )

    # Remove invisible Unicode
    removed = remove_invisible_unicode(path, dry_run)
    if removed > 0:
        result["fixes"].append(f"Removed {removed} invisible Unicode characters")

    # Trailing newline
    if ensure_trailing_newline(path, dry_run):
        result["fixes"].append("Added trailing newline")

    return result


def main():
    parser = argparse.ArgumentParser(description="Auto-fix translated files")
    parser.add_argument("paths", nargs="+", help="Files or directories to fix")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show fixes without applying"
    )

    args = parser.parse_args()

    total_fixes = 0
    for target in args.paths:
        p = Path(target)
        if p.is_file():
            files = [p]
        elif p.is_dir():
            files = sorted(p.rglob("*.md"))
        else:
            print(f"Skipping {target}: not found", file=sys.stderr)
            continue

        for f in files:
            result = fix_file(f, args.dry_run)
            if result["fixes"]:
                prefix = "[DRY RUN] " if args.dry_run else ""
                print(f"{prefix}{result['path']}:")
                for fix in result["fixes"]:
                    print(f"  ✅ {fix}")
                total_fixes += len(result["fixes"])

    if total_fixes == 0:
        print("No fixes needed.")
    else:
        action = "would apply" if args.dry_run else "applied"
        print(f"\n{total_fixes} fix(es) {action}.")


if __name__ == "__main__":
    main()
