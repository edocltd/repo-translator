# Contributing to repo-translator

Thank you for your interest in contributing. This guide covers the process and standards for making changes.

## Types of Contributions

- **Bug fixes** — Fix issues with scanning, validation, or anchor fixing
- **New validation checks** — Add checks that catch real translation problems
- **Language support** — Add glossaries, test on new languages, fix language-specific issues
- **Documentation** — Improve explanations, add examples, fix errors
- **Translations** — Translate project documentation using the tool itself

## Getting Started

```bash
git clone https://github.com/edocltd/repo-translator.git
cd repo-translator
git checkout -b your-branch-name
```

No external dependencies required for core scripts. Optional: `pip install pyyaml` for glossary support.

## Project Structure

```
scripts/          # Core scripts (scan, validate, fix, prompt, sync)
examples/         # Example glossaries and configs
templates/        # Reserved for prompt templates
translations/     # Translations of this project's docs
```

## Code Standards

### Python

- Python 3.10+ (use `list[str]` not `List[str]`, `str | None` not `Optional[str]`)
- Functions have docstrings explaining purpose
- No unused imports or dead code
- No hardcoded paths — use `Path` objects
- Handle errors explicitly (`try/except` with specific exceptions)
- Print user-facing output to stdout, errors to stderr

### File Naming

- Scripts: `snake_case.py`
- Docs: `UPPER-CASE.md` for root files, `kebab-case.md` for nested
- Glossaries: `glossary-{lang}.yaml`

### No Empty Code

- No placeholder functions that do nothing
- No commented-out code blocks
- No `pass` statements except in abstract methods
- No TODO comments without a linked issue

## Commit Messages

Follow conventional commits:

```
type(scope): description
```

| Type | Use For |
|------|---------|
| `feat` | New feature or script |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `refactor` | Code restructuring |
| `test` | Adding tests |
| `chore` | Build, CI, dependencies |

Scope should match the script name: `feat(scan)`, `fix(validate)`, `docs(readme)`.

## Pull Request Process

1. Create a branch with descriptive name (`fix/anchor-apostrophe`, `feat/glossary-check`)
2. Make focused changes (one feature or fix per PR)
3. Test on at least one real repository
4. Update CLAUDE.md if behavior changes
5. Submit PR with clear description of what and why

## Adding a Validation Check

1. Add the check function in `validate.py`
2. Add it to the `validate_file()` pipeline
3. Document severity (error vs warning) and auto-fix availability
4. Update the validation table in README.md and CLAUDE.md
5. Test on a real translated file

## Adding a Language Glossary

1. Create `examples/glossary-{lang}.yaml`
2. Follow the structure of `glossary-uk.yaml`
3. Include 20+ common technical terms
4. Include a `do_not_translate` list
5. Test with `prompt_generator.py`

## Reporting Issues

Include:
- Python version and OS
- Command you ran (exact)
- Expected behavior
- Actual behavior (paste full output)
- Repository you tested on (if public)

## License

By contributing, you agree that your contributions will be licensed under MIT.
