#!/usr/bin/env python3
"""Scan repository and generate translation plan."""

import argparse
import json
import re
import sys
from pathlib import Path

# ISO 639-1 language codes (subset, extensible)
LANGUAGES = {
    "uk": "Українська",
    "de": "Deutsch",
    "fr": "Français",
    "es": "Español",
    "pt": "Português",
    "pt-br": "Português (Brasil)",
    "it": "Italiano",
    "nl": "Nederlands",
    "pl": "Polski",
    "cs": "Čeština",
    "ru": "Русский",
    "ja": "日本語",
    "ko": "한국어",
    "zh": "中文 (简体)",
    "zh-tw": "中文 (繁體)",
    "ar": "العربية",
    "hi": "हिन्दी",
    "tr": "Türkçe",
    "vi": "Tiếng Việt",
    "th": "ไทย",
    "sv": "Svenska",
    "da": "Dansk",
    "fi": "Suomi",
    "no": "Norsk",
    "ro": "Română",
    "hu": "Magyar",
    "bg": "Български",
    "hr": "Hrvatski",
    "sk": "Slovenčina",
    "sl": "Slovenščina",
    "et": "Eesti",
    "lt": "Lietuvių",
    "lv": "Latviešu",
    "id": "Bahasa Indonesia",
    "ms": "Bahasa Melayu",
    "bn": "বাংলা",
}

# Default patterns
DEFAULT_INCLUDE = ["**/*.md", "**/*.mdx"]
DEFAULT_EXCLUDE = [
    ".git/**",
    "node_modules/**",
    ".venv/**",
    "__pycache__/**",
    "translations/**",
    "*.min.js",
    "coverage/**",
    ".github/workflows/**",
]

# Files that are typically not translated
SKIP_FILENAMES = {
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    "package-lock.json",
    "yarn.lock",
    "poetry.lock",
    "Pipfile.lock",
    "coverage.xml",
}

# Files typically copied without translation
COPY_FILENAMES = {
    "CHANGELOG.md",
    "RELEASE_NOTES.md",
}


def is_text_file(path: Path, sample_size: int = 8192) -> bool:
    """Check if file is text (not binary) by looking for null bytes."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(sample_size)
        null_ratio = chunk.count(b"\x00") / max(len(chunk), 1)
        return null_ratio < 0.01
    except (OSError, PermissionError):
        return False


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English."""
    return len(text) // 4


def has_translatable_prose(path: Path, min_prose_ratio: float = 0.1) -> bool:
    """Check if .md file has enough prose to translate (vs pure code/config)."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return False

    # Remove code blocks
    no_code = re.sub(r"```[^\n]*\n.*?```", "", content, flags=re.DOTALL)
    no_code = re.sub(r"~~~~[^\n]*\n.*?~~~~", "", no_code, flags=re.DOTALL)

    # Remove frontmatter
    no_code = re.sub(r"^---\n.*?---\n", "", no_code, flags=re.DOTALL)

    # Remove HTML tags
    no_code = re.sub(r"<[^>]+>", "", no_code)

    # Remove URLs
    no_code = re.sub(r"https?://\S+", "", no_code)

    # What remains is prose + markdown formatting
    prose_chars = len(no_code.strip())
    total_chars = max(len(content), 1)

    return (prose_chars / total_chars) >= min_prose_ratio


def matches_pattern(path: Path, patterns: list[str], root: Path) -> bool:
    """Check if path matches any glob pattern."""
    rel = path.relative_to(root)
    for pattern in patterns:
        if rel.match(pattern):
            return True
        # Also check just the filename for simple patterns
        if not "/" in pattern and not "\\" in pattern:
            if path.name == pattern or path.match(pattern):
                return True
    return False


def scan_repo(
    root: Path,
    lang: str,
    translations_dir: str = "translations",
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    max_files: int = 500,
    skip_filenames: set[str] | None = None,
    copy_filenames: set[str] | None = None,
) -> dict:
    """Scan repository and classify files for translation."""

    if include is None:
        include = DEFAULT_INCLUDE
    if exclude is None:
        exclude = DEFAULT_EXCLUDE
    if skip_filenames is None:
        skip_filenames = SKIP_FILENAMES
    if copy_filenames is None:
        copy_filenames = COPY_FILENAMES

    root = root.resolve()

    # Add translations dir to exclude
    exclude_with_translations = list(exclude) + [f"{translations_dir}/**"]

    files = []
    skipped_reasons = {}
    visited = set()

    for pattern in include:
        for path in root.glob(pattern):
            # Resolve to handle symlinks, track visited to avoid cycles
            real = path.resolve()
            if real in visited:
                continue
            visited.add(real)

            if not path.is_file():
                continue

            # Check exclude patterns
            try:
                rel = path.relative_to(root)
            except ValueError:
                continue

            if any(rel.match(p) for p in exclude_with_translations):
                skipped_reasons[str(rel)] = "excluded by pattern"
                continue

            # Check skip filenames
            if path.name in skip_filenames:
                skipped_reasons[str(rel)] = "skip filename"
                continue

            # Check if text file
            if not is_text_file(path):
                skipped_reasons[str(rel)] = "binary file"
                continue

            # Classify action
            if path.name in copy_filenames:
                action = "copy"
                reason = "copy filename (technical log)"
            elif not has_translatable_prose(path):
                action = "copy"
                reason = "no translatable prose (mostly code/config)"
            else:
                action = "translate"
                reason = None

            try:
                size = path.stat().st_size
                content = path.read_text(encoding="utf-8", errors="replace")
                tokens = estimate_tokens(content)
                line_count = content.count("\n") + 1
                code_blocks = len(re.findall(r"^```", content, re.MULTILINE)) // 2
                mermaid_blocks = len(
                    re.findall(r"^```mermaid", content, re.MULTILINE)
                )
            except (OSError, PermissionError):
                continue

            files.append(
                {
                    "path": str(rel).replace("\\", "/"),
                    "action": action,
                    "reason": reason,
                    "size_bytes": size,
                    "lines": line_count,
                    "estimated_tokens": tokens,
                    "code_blocks": code_blocks,
                    "mermaid_blocks": mermaid_blocks,
                }
            )

    # Sort: translate first, then copy; within each — by path
    files.sort(key=lambda f: (0 if f["action"] == "translate" else 1, f["path"]))

    # Check limits
    translate_count = sum(1 for f in files if f["action"] == "translate")
    if translate_count > max_files:
        print(
            f"⚠️  Found {translate_count} files to translate (limit: {max_files}).",
            file=sys.stderr,
        )
        print(
            f"   Use --max-files {translate_count} to override, "
            f"or narrow scope in .repo-translator.yaml",
            file=sys.stderr,
        )

    # Stats
    to_translate = [f for f in files if f["action"] == "translate"]
    to_copy = [f for f in files if f["action"] == "copy"]
    total_tokens = sum(f["estimated_tokens"] for f in to_translate)

    lang_name = LANGUAGES.get(lang, lang)

    plan = {
        "source_repo": str(root),
        "target_lang": lang,
        "target_lang_name": lang_name,
        "translations_dir": f"{translations_dir}/{lang}",
        "files": files,
        "skipped": skipped_reasons,
        "stats": {
            "total_files_found": len(files) + len(skipped_reasons),
            "to_translate": len(to_translate),
            "to_copy": len(to_copy),
            "skipped": len(skipped_reasons),
            "total_lines": sum(f["lines"] for f in to_translate),
            "total_code_blocks": sum(f["code_blocks"] for f in to_translate),
            "total_mermaid": sum(f["mermaid_blocks"] for f in to_translate),
            "estimated_tokens": total_tokens,
            "estimated_cost_usd": round(total_tokens * 0.000015, 2),
        },
    }

    return plan


def print_plan(plan: dict) -> None:
    """Print human-readable plan summary."""
    stats = plan["stats"]
    lang = plan["target_lang"]
    lang_name = plan["target_lang_name"]

    print(f"\n{'='*60}")
    print(f"  repo-translator — Translation Plan")
    print(f"{'='*60}")
    print(f"  Language:     {lang_name} ({lang})")
    print(f"  Target dir:   {plan['translations_dir']}/")
    print(f"  Source:        {plan['source_repo']}")
    print(f"{'='*60}\n")

    print(f"  📊 Summary:")
    print(f"     To translate: {stats['to_translate']} files")
    print(f"     To copy:      {stats['to_copy']} files")
    print(f"     Skipped:      {stats['skipped']} files")
    print(f"     Total lines:  {stats['total_lines']}")
    print(f"     Code blocks:  {stats['total_code_blocks']}")
    print(f"     Mermaid:      {stats['total_mermaid']}")
    print(f"     Est. tokens:  {stats['estimated_tokens']:,}")
    print(f"     Est. cost:    ${stats['estimated_cost_usd']:.2f} (API)")
    print()

    # List files to translate
    translate_files = [f for f in plan["files"] if f["action"] == "translate"]
    if translate_files:
        print(f"  📝 Files to translate ({len(translate_files)}):")
        for f in translate_files:
            size_kb = f["size_bytes"] / 1024
            print(f"     {f['path']:<50} {size_kb:>6.1f} KB")

    # List files to copy
    copy_files = [f for f in plan["files"] if f["action"] == "copy"]
    if copy_files:
        print(f"\n  📋 Files to copy ({len(copy_files)}):")
        for f in copy_files:
            reason = f.get("reason", "")
            print(f"     {f['path']:<50} ({reason})")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Scan repository and generate translation plan"
    )
    parser.add_argument(
        "--root", "-r", default=".", help="Repository root (default: current dir)"
    )
    parser.add_argument("--lang", "-l", required=True, help="Target language code")
    parser.add_argument(
        "--translations-dir",
        "-d",
        default="translations",
        help="Translations directory name (default: translations)",
    )
    parser.add_argument(
        "--max-files", type=int, default=500, help="Max files limit (default: 500)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Output JSON file (default: print to stdout)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON instead of summary"
    )

    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Load config if exists
    config_path = root / ".repo-translator.yaml"
    include = None
    exclude = None
    if config_path.exists():
        try:
            import yaml

            with open(config_path) as f:
                config = yaml.safe_load(f)
            include = config.get("include")
            exclude = config.get("exclude")
        except ImportError:
            pass  # yaml not available, use defaults

    plan = scan_repo(
        root=root,
        lang=args.lang,
        translations_dir=args.translations_dir,
        include=include,
        exclude=exclude,
        max_files=args.max_files,
    )

    if args.json or args.output:
        output = json.dumps(plan, indent=2, ensure_ascii=False)
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"Plan saved to {args.output}")
        else:
            print(output)
    else:
        print_plan(plan)


if __name__ == "__main__":
    main()
