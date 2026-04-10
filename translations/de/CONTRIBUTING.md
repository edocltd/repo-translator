<!-- i18n-source: CONTRIBUTING.md -->
<!-- i18n-date: 2026-04-10 -->

# Zu repo-translator beitragen

Vielen Dank für Ihr Interesse. Dieser Leitfaden beschreibt den Prozess und die Standards für Änderungen.

## Arten von Beiträgen

- **Fehlerbehebungen** — Probleme mit Scannen, Validierung oder Ankern beheben
- **Neue Validierungsprüfungen** — Prüfungen hinzufügen, die echte Übersetzungsprobleme erkennen
- **Sprachunterstützung** — Glossare hinzufügen, neue Sprachen testen
- **Dokumentation** — Erklärungen verbessern, Beispiele hinzufügen
- **Übersetzungen** — Projektdokumentation mit dem Tool selbst übersetzen

## Erste Schritte

```bash
git clone https://github.com/edocltd/repo-translator.git
cd repo-translator
git checkout -b your-branch-name
```

Keine externen Abhängigkeiten für Kernscripte erforderlich.

## Code-Standards

- Python 3.10+ mit modernen Typ-Annotationen
- Funktionen mit Docstrings
- Kein toter Code oder ungenutzte Imports
- Keine hartcodierten Pfade — `Path`-Objekte verwenden
- Keine Platzhalter-Funktionen oder auskommentierter Code

## Commit-Nachrichten

Conventional Commits befolgen: `type(scope): description`

Typen: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Lizenz

Mit Ihrem Beitrag stimmen Sie zu, dass Ihre Beiträge unter MIT lizenziert werden.
