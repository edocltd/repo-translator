#!/usr/bin/env python3
"""Generate translation prompts for copy-paste into AI chat."""

import argparse
import re
import sys
from pathlib import Path


def load_glossary(path: Path) -> dict:
    """Load glossary from YAML file."""
    if not path.exists():
        return {}
    try:
        import yaml

        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Fallback: simple key: value parsing
        glossary = {"terms": {}, "do_not_translate": []}
        section = None
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line == "terms:":
                    section = "terms"
                elif line == "do_not_translate:":
                    section = "dnt"
                elif section == "terms" and ":" in line:
                    k, v = line.split(":", 1)
                    k = k.strip().strip('"').strip("'")
                    v = v.strip().strip('"').strip("'")
                    if k and v:
                        glossary["terms"][k] = v
                elif section == "dnt" and line.startswith("- "):
                    glossary["do_not_translate"].append(
                        line[2:].strip().strip('"').strip("'")
                    )
        return glossary


def extract_code_blocks(content: str) -> list[tuple[int, int, str]]:
    """Extract code blocks with their positions."""
    blocks = []
    for match in re.finditer(
        r"(```[^\n]*\n.*?```|~~~~[^\n]*\n.*?~~~~)", content, re.DOTALL
    ):
        blocks.append((match.start(), match.end(), match.group()))
    return blocks


def generate_prompt(
    file_path: Path,
    lang_code: str,
    lang_name: str,
    glossary: dict,
    chunk: str | None = None,
) -> str:
    """Generate a translation prompt for a file or chunk."""

    if chunk is None:
        content = file_path.read_text(encoding="utf-8")
    else:
        content = chunk

    # Build glossary section
    terms = glossary.get("terms", {})
    dnt = glossary.get("do_not_translate", [])

    glossary_text = ""
    if terms:
        glossary_text += "GLOSSARY (use these translations consistently):\n"
        for eng, trans in terms.items():
            glossary_text += f"  {eng} → {trans}\n"

    dnt_text = ""
    if dnt:
        dnt_text = "DO NOT TRANSLATE these terms:\n  " + ", ".join(dnt) + "\n"

    prompt = f"""Translate the following Markdown file from English to {lang_name}.

RULES:
1. Translate all prose text, headings, list descriptions, table headers and cell text.
2. DO NOT translate or modify anything inside code blocks (``` or ~~~~).
3. DO NOT translate or modify Mermaid diagrams.
4. DO NOT translate or modify URLs, file paths, CLI commands.
5. DO NOT translate or modify YAML/JSON values in frontmatter (except 'description' field).
6. DO NOT translate HTML tag attributes.
7. Preserve all Markdown formatting exactly (headings, bold, italic, lists, tables).
8. Preserve the exact number of lines (±5%).
9. Preserve all code blocks with identical content.
10. DO NOT add any translator notes, comments, or explanations.
11. DO NOT shorten or summarize — translate EVERYTHING.

{glossary_text}
{dnt_text}
--- FILE: {file_path.name} ---

{content}

--- END OF FILE ---"""

    return prompt


def chunk_by_headings(content: str, max_tokens: int = 4000) -> list[dict]:
    """Split content into chunks by ## headings."""
    lines = content.split("\n")
    chunks = []
    current_chunk = []
    current_heading = "header"

    for line in lines:
        if re.match(r"^## ", line) and current_chunk:
            chunk_text = "\n".join(current_chunk)
            tokens = len(chunk_text) // 4
            if tokens > 0:
                chunks.append(
                    {
                        "heading": current_heading,
                        "content": chunk_text,
                        "tokens": tokens,
                    }
                )
            current_chunk = [line]
            current_heading = line.strip("# ").strip()
        else:
            current_chunk.append(line)

    if current_chunk:
        chunk_text = "\n".join(current_chunk)
        chunks.append(
            {
                "heading": current_heading,
                "content": chunk_text,
                "tokens": len(chunk_text) // 4,
            }
        )

    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Generate translation prompt for copy-paste"
    )
    parser.add_argument("file", help="Markdown file to generate prompt for")
    parser.add_argument("--lang", "-l", required=True, help="Target language code")
    parser.add_argument(
        "--lang-name", default=None, help="Target language name (auto-detected)"
    )
    parser.add_argument(
        "--glossary", "-g", default=None, help="Path to glossary YAML file"
    )
    parser.add_argument(
        "--output", "-o", default=None, help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--chunk",
        action="store_true",
        help="Split large files into chunks and generate separate prompts",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4000,
        help="Max tokens per chunk (default: 4000)",
    )

    args = parser.parse_args()

    # Import language names from scan module
    try:
        from scan import LANGUAGES
    except ImportError:
        LANGUAGES = {"uk": "Українська", "de": "Deutsch", "fr": "Français"}

    lang_name = args.lang_name or LANGUAGES.get(args.lang, args.lang)

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: {file_path} not found", file=sys.stderr)
        sys.exit(1)

    # Load glossary
    glossary = {}
    if args.glossary:
        glossary = load_glossary(Path(args.glossary))
    else:
        # Try default locations
        for gp in [
            file_path.parent / f".glossary-{args.lang}.yaml",
            Path(f"translations/{args.lang}/.glossary.yaml"),
            Path(f".repo-translator-glossary-{args.lang}.yaml"),
        ]:
            if gp.exists():
                glossary = load_glossary(gp)
                break

    content = file_path.read_text(encoding="utf-8")
    estimated_tokens = len(content) // 4

    if args.chunk and estimated_tokens > args.max_tokens:
        chunks = chunk_by_headings(content, args.max_tokens)
        output_parts = []
        for i, chunk in enumerate(chunks):
            prompt = generate_prompt(
                file_path, args.lang, lang_name, glossary, chunk["content"]
            )
            output_parts.append(
                f"{'='*60}\n"
                f"CHUNK {i + 1}/{len(chunks)}: {chunk['heading']} "
                f"(~{chunk['tokens']} tokens)\n"
                f"{'='*60}\n\n{prompt}\n"
            )
        output = "\n".join(output_parts)
        print(
            f"Split into {len(chunks)} chunks "
            f"(file: ~{estimated_tokens} tokens, limit: {args.max_tokens})",
            file=sys.stderr,
        )
    else:
        output = generate_prompt(file_path, args.lang, lang_name, glossary)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Prompt saved to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
