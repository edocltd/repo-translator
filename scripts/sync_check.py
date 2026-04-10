#!/usr/bin/env python3
"""Check if translations are outdated vs originals."""

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path


def get_git_sha(file_path: Path, repo_root: Path) -> str | None:
    """Get last commit SHA for a file."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%h", "-1", "--", str(file_path)],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        sha = result.stdout.strip()
        return sha if sha else None
    except (FileNotFoundError, subprocess.SubprocessError):
        return None


def get_file_hash(path: Path) -> str:
    """Get MD5 hash of file content."""
    content = path.read_bytes()
    return hashlib.md5(content).hexdigest()[:8]


def get_git_diff_stats(
    file_path: Path, old_sha: str, new_sha: str, repo_root: Path
) -> dict | None:
    """Get diff stats between two commits for a file."""
    try:
        result = subprocess.run(
            [
                "git",
                "diff",
                "--stat",
                old_sha,
                new_sha,
                "--",
                str(file_path),
            ],
            capture_output=True,
            text=True,
            cwd=repo_root,
        )
        return {"diff": result.stdout.strip()}
    except (FileNotFoundError, subprocess.SubprocessError):
        return None


def extract_i18n_metadata(path: Path) -> dict:
    """Extract i18n metadata from translated file header."""
    meta = {}
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return meta

    for line in content.split("\n")[:10]:
        m = re.match(r"<!--\s*i18n-source:\s*(.+?)\s*-->", line)
        if m:
            meta["source"] = m.group(1).strip()

        m = re.match(r"<!--\s*i18n-source-sha:\s*(.+?)\s*-->", line)
        if m:
            meta["sha"] = m.group(1).strip()

        m = re.match(r"<!--\s*i18n-date:\s*(.+?)\s*-->", line)
        if m:
            meta["date"] = m.group(1).strip()

    return meta


def is_git_repo(path: Path) -> bool:
    """Check if path is inside a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            cwd=path,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def sync_check(
    repo_root: Path,
    translations_dir: Path,
    lang: str,
) -> dict:
    """Check all translations for sync status."""

    lang_dir = translations_dir / lang
    if not lang_dir.exists():
        return {"error": f"Translation directory not found: {lang_dir}"}

    use_git = is_git_repo(repo_root)
    results = {"files": [], "summary": {"total": 0, "current": 0, "outdated": 0, "missing_meta": 0, "new_files": 0}}

    # Find all translated .md files
    for trans_path in sorted(lang_dir.rglob("*.md")):
        rel = trans_path.relative_to(lang_dir)
        orig_path = repo_root / rel

        if not orig_path.exists():
            # Translation-specific file (TRANSLATION_NOTES, etc.)
            results["summary"]["new_files"] += 1
            continue

        results["summary"]["total"] += 1
        meta = extract_i18n_metadata(trans_path)

        if not meta.get("sha") and not meta.get("date"):
            results["summary"]["missing_meta"] += 1
            results["files"].append(
                {
                    "path": str(rel).replace("\\", "/"),
                    "status": "missing_meta",
                    "message": "No i18n metadata found",
                }
            )
            continue

        # Compare
        if use_git and meta.get("sha"):
            current_sha = get_git_sha(orig_path, repo_root)
            if current_sha and meta["sha"] != current_sha:
                diff = get_git_diff_stats(
                    orig_path, meta["sha"], current_sha, repo_root
                )
                results["summary"]["outdated"] += 1
                results["files"].append(
                    {
                        "path": str(rel).replace("\\", "/"),
                        "status": "outdated",
                        "translated_sha": meta["sha"],
                        "current_sha": current_sha,
                        "translated_date": meta.get("date", "unknown"),
                        "diff": diff.get("diff", "") if diff else "",
                    }
                )
            else:
                results["summary"]["current"] += 1
        else:
            # Fallback: compare file hashes
            orig_hash = get_file_hash(orig_path)
            results["files"].append(
                {
                    "path": str(rel).replace("\\", "/"),
                    "status": "unknown",
                    "message": "Cannot determine sync status (no git or no SHA in metadata)",
                    "original_hash": orig_hash,
                }
            )

    # Known language codes and translation dir names to skip
    skip_dirs = {
        ".git", "node_modules", ".venv", "__pycache__",
        "translations", "i18n", "l10n", "lang", "locales",
        translations_dir.name,
    }
    # Also detect language code directories (uk/, vi/, zh/, etc.)
    try:
        from scan import LANGUAGES
        for item in repo_root.iterdir():
            if item.is_dir() and item.name.lower() in LANGUAGES:
                skip_dirs.add(item.name)
    except ImportError:
        # Fallback: skip 2-3 char dirs that contain .md files
        for item in repo_root.iterdir():
            if item.is_dir() and len(item.name) <= 3 and item.name.isalpha():
                md_count = sum(1 for _ in item.rglob("*.md"))
                if md_count > 3:  # Likely a language dir
                    skip_dirs.add(item.name)

    # Find untranslated files
    for orig_path in sorted(repo_root.rglob("*.md")):
        rel = orig_path.relative_to(repo_root)
        parts = rel.parts
        if any(p in skip_dirs for p in parts):
            continue

        trans_path = lang_dir / rel
        if not trans_path.exists():
            results["files"].append(
                {
                    "path": str(rel).replace("\\", "/"),
                    "status": "not_translated",
                }
            )

    return results


def print_results(results: dict) -> None:
    """Print sync check results."""
    if "error" in results:
        print(f"Error: {results['error']}", file=sys.stderr)
        return

    s = results["summary"]

    print(f"\n{'='*60}")
    print(f"  repo-translator — Sync Check")
    print(f"{'='*60}\n")
    print(f"  Total translated: {s['total']}")
    print(f"  ✅ Current:        {s['current']}")

    if s["outdated"] > 0:
        print(f"  ⚠️  Outdated:       {s['outdated']}")
    if s["missing_meta"] > 0:
        print(f"  ❓ No metadata:    {s['missing_meta']}")

    # Show outdated files
    outdated = [f for f in results["files"] if f["status"] == "outdated"]
    if outdated:
        print(f"\n  Outdated files:")
        for f in outdated:
            print(f"\n    📄 {f['path']}")
            print(
                f"       Translated from: {f['translated_sha']} ({f.get('translated_date', '?')})"
            )
            print(f"       Current:         {f['current_sha']}")
            if f.get("diff"):
                print(f"       Changes:         {f['diff']}")

    # Show untranslated files
    not_translated = [f for f in results["files"] if f["status"] == "not_translated"]
    if not_translated:
        print(f"\n  Not yet translated ({len(not_translated)}):")
        for f in not_translated[:20]:
            print(f"    ❌ {f['path']}")
        if len(not_translated) > 20:
            print(f"    ... and {len(not_translated) - 20} more")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Check if translations are up to date"
    )
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

    args = parser.parse_args()

    root = Path(args.root).resolve()
    trans_dir = root / args.translations_dir

    results = sync_check(root, trans_dir, args.lang)

    if args.json:
        import json
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_results(results)


if __name__ == "__main__":
    main()
