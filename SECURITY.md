# Security Policy

## Scope

repo-translator processes markdown files and generates translation prompts. It does not execute arbitrary code, make network requests, or handle authentication credentials.

## Reporting a Vulnerability

If you discover a security issue, please report it responsibly:

1. **DO NOT** open a public issue
2. Use [GitHub Private Vulnerability Reporting](https://github.com/edocltd/repo-translator/security/advisories)
3. Or email the maintainer directly

We will acknowledge receipt within 48 hours and provide a timeline for a fix.

## Security Considerations

- **No API keys in glossaries** — Glossary files should contain only terminology, never credentials
- **No code execution** — Scripts read and write files but never execute content from translated files
- **No network access** — Core scripts work entirely offline (sync_check uses local git only)
- **File access** — Scripts only access files within the specified `--root` directory

## Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | ✅ |
