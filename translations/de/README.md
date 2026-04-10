<!-- i18n-source: README.md -->
<!-- i18n-date: 2026-04-10 -->

# repo-translator

🌐 [English](../../README.md) | [Українська](../uk/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Deutsch](README.md) | [Português](../pt-br/README.md) | [中文](../zh/README.md) | [日本語](../ja/README.md)

**Universelles Werkzeug zur Übersetzung von GitHub-Repository-Dokumentation in jede Sprache.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GitHub Stars](https://img.shields.io/github/stars/edocltd/repo-translator?style=flat&color=gold)](https://github.com/edocltd/repo-translator/stargazers)

Kein API-Wrapper — ein **Framework** für Struktur, Validierung und Synchronisation. Übersetzen Sie mit jeder Methode: Claude Code, Claude.ai, ChatGPT, Ollama oder manuell. Das Tool stellt sicher, dass das Ergebnis korrekt ist.

> **Aus echter Erfahrung gebaut**: Jede Funktion existiert wegen eines echten Problems bei der Übersetzung von [claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐) ins Ukrainische. Siehe [FAILURE-ANALYSIS.md](../../FAILURE-ANALYSIS.md) für die vollständige Analyse von 48 Problemen.

---

## Inhaltsverzeichnis

- [Das Problem](#das-problem)
- [Wie es funktioniert](#wie-es-funktioniert)
- [Schnellstart](#schnellstart)
- [Übersetzungsmethoden](#übersetzungsmethoden)
- [Skript-Referenz](#skript-referenz)
- [Ausgabestruktur](#ausgabestruktur)
- [Validierungsprüfungen](#validierungsprüfungen)
- [Jede Sprache](#jede-sprache)
- [Konfiguration](#konfiguration)
- [Voraussetzungen](#voraussetzungen)
- [Mitwirken](#mitwirken)
- [Lizenz](#lizenz)

---

## Das Problem

Sie möchten die Dokumentation eines Repositories übersetzen. Sie stehen vor:

- **Keine Struktur** — Welche Dateien übersetzen? Welche überspringen? Wohin mit den Ergebnissen?
- **Keine Validierung** — Hat die KI stillschweigend die Hälfte des Inhalts gelöscht? Ankerlinks gebrochen? Kodierung beschädigt?
- **Keine Konsistenz** — "hook" in einer Datei als "Haken" und in einer anderen als "Hook" übersetzt
- **Keine Synchronisation** — Original letzte Woche aktualisiert. Welche Übersetzungen sind veraltet?

Bestehende Tools (co-op-translator, gpt-translate) behandeln die Übersetzung, überspringen aber die Validierung vollständig.

## Wie es funktioniert

```
SCAN  →  TRANSLATE  →  VALIDATE  →  FIX  →  SYNC
  ↓         ↓            ↓          ↓        ↓
"What     "Any        "Is it     "Auto-   "What's
 files?"   method"    correct?"   fix"    outdated?"
```

1. **Scannen** — Repository analysieren, Dateien klassifizieren (übersetzen / kopieren / überspringen), bestehende Übersetzungen erkennen, Aufwand schätzen
2. **Übersetzen** — Jede Methode verwenden. Das Tool generiert Prompts mit Glossar und Regeln
3. **Validieren** — Struktur prüfen (Zeilen, Codeblöcke, Mermaid), Anker, Kodierung, Glossar
4. **Korrigieren** — Gebrochene Anker, Kodierungsprobleme, unsichtbares Unicode automatisch beheben
5. **Synchronisieren** — Veraltete Übersetzungen verfolgen, wenn sich Originale ändern

Jeder Schritt ist ein unabhängiges Skript. Verwenden Sie sie zusammen oder einzeln.

## Schnellstart

```bash
git clone https://github.com/edocltd/repo-translator.git
```

```bash
# Scan any repo to see what needs translating
python repo-translator/scripts/scan.py --root /path/to/any-repo --lang de

# Generate a translation prompt (copy-paste into Claude.ai / ChatGPT)
python repo-translator/scripts/prompt_generator.py /path/to/any-repo/README.md --lang de

# After translating — validate the result
python repo-translator/scripts/validate.py --root /path/to/any-repo --lang de

# Auto-fix broken anchors and encoding
python repo-translator/scripts/fix_anchors.py /path/to/any-repo/translations/de/

# Check what's outdated after original changes
python repo-translator/scripts/sync_check.py --root /path/to/any-repo --lang de
```

## Übersetzungsmethoden

Dem Tool ist es egal, WIE Sie übersetzen. Es stellt sicher, dass das Ergebnis korrekt ist.

| Methode | Kosten | Einrichtung | Ideal für |
|---------|--------|-------------|-----------|
| **Claude Code** | 0 $ extra | Bereits installiert | Schnellster Workflow für Abonnenten |
| **Kopieren-Einfügen** (Claude.ai / ChatGPT) | 0–20 $/Monat | Beliebiger KI-Chat | Jeder mit Abonnement |
| **Manuell** | 0 $ | Keine | Menschliche Übersetzer, kleine Repos |
| **Ollama** | 0 $ | Ollama installieren | Datenschutz, Offline-Arbeit |
| **API** (Anthropic / OpenAI) | Nutzungsbasiert | API-Schlüssel | Automatisierung, große Repos |

## Skript-Referenz

### `scan.py` — Scannen und Klassifizieren

```bash
python scripts/scan.py --root /path/to/repo --lang de
```

Erkennt automatisch bestehende Übersetzungen und schließt sie aus. Klassifiziert Dateien: `translate` / `copy` / `skip`. Schätzt Token-Anzahl und API-Kosten.

### `validate.py` — Übersetzungen validieren

```bash
python scripts/validate.py --root /path/to/repo --lang de
```

Prüft übersetzte Dateien gegen Originale mit 12 Validierungsprüfungen.

### `fix_anchors.py` — Automatische Korrektur

```bash
python scripts/fix_anchors.py translations/de/
```

Behebt: gebrochene Ankerlinks, gemischte Kodierung, unsichtbare Unicode-Zeichen, fehlende Zeilenenden.

### `prompt_generator.py` — Übersetzungs-Prompts generieren

```bash
python scripts/prompt_generator.py README.md --lang de
```

Erstellt fertige Prompts mit Regeln und Glossar für jeden KI-Chat.

### `sync_check.py` — Veraltete Übersetzungen verfolgen

```bash
python scripts/sync_check.py --root /path/to/repo --lang de
```

## Ausgabestruktur

```
any-repo/
├── README.md                    ← original
├── docs/
│   └── guide.md
├── src/
│   └── app.py                   ← not touched
└── translations/                ← created by repo-translator
    └── de/
        ├── README.md            ← translated
        └── docs/
            └── guide.md         ← translated
```

Nur `.md`-Dateien werden übersetzt. Code, Bilder und Konfigurationen bleiben am Originalstandort.

## Voraussetzungen

- Python 3.10+
- Keine externen Abhängigkeiten für Kernscripte
- Optional: `pyyaml` für Konfig-/Glossardateien
- Optional: `git` für Sync-Check-Funktionalität

## Mitwirken

Beiträge willkommen. Bitte [CONTRIBUTING.md](../../CONTRIBUTING.md) lesen vor PRs.

## Lizenz

MIT-Lizenz — siehe [LICENSE](../../LICENSE) für Details.

---

Gebaut von [@edocltd](https://github.com/edocltd)
