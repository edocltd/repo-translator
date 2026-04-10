<!-- i18n-source: docs/failure-analysis.md -->
<!-- i18n-date: 2026-04-10 -->

# Fehleranalyse: 48 reale Probleme bei der Repository-Übersetzung

Jedes hier dokumentierte Problem wurde bei der tatsächlichen Übersetzungsarbeit an [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐) festgestellt. Jeder Eintrag enthält: Szenario, Risikostufe und implementierte Abwehr.

---

## Kategorie 1: Scannen & Repo-Analyse

### P1.1: Riesiges Repository
**Szenario**: Benutzer startet das Tool auf einem Monorepo mit 50.000+ Dateien.
**Abwehr**: Dateilimit (Standard: 500), Tiefenlimit (10 Ebenen), Warnung mit Vorschlag zur Eingrenzung.

### P1.2: Repository ohne Git
**Szenario**: Verzeichnis ohne `.git/`.
**Abwehr**: Tool funktioniert ohne Git. Sync-Check deaktiviert mit Warnung. Verwendet Datei-Hash statt Commit-SHA.

### P1.3: Bestehende Übersetzungsstruktur
**Szenario**: Repo hat bereits `uk/`, `translations/`, `i18n/`-Verzeichnisse.
**Abwehr**: Automatische Erkennung bestehender Übersetzungen und Ausschluss vom Scannen. Bericht über Gefundenes.

### P1.4: Symlinks und zirkuläre Referenzen
**Abwehr**: Symlinks nicht folgen. Besuchte Pfade über `set(realpath)` verfolgen.

### P1.5: Binärdateien mit .md-Erweiterung
**Abwehr**: Erste 8KB auf Null-Bytes prüfen. Bei >1% Nullen → als Binärdatei klassifizieren, überspringen.

### P1.6: Leere .md-Dateien
**Abwehr**: Dateien <10 Bytes überspringen. Dateien mit nur Frontmatter (keine Prosa) überspringen.

### P1.7: Gleicher Dateiname in verschiedenen Verzeichnissen
**Abwehr**: Immer vollständige Verzeichnisstruktur beibehalten. Niemals flach machen.

---

## Kategorie 2: Übersetzungsqualität (KI-Ausgabe)

### P2.1: KI kürzt Datei ⚠️ KRITISCH
**Realer Fall**: Original 1945 Zeilen, KI lieferte 540 (58% verloren).
**Abwehr**: Zeilenzahl nach Übersetzung prüfen. Ablehnen wenn <85% des Originals.

### P2.2: KI übersetzt Codeblöcke ⚠️ KRITISCH
**Realer Fall**: `mkdir -p .claude/commands` wurde zu `створити_каталог .claude/commands`.
**Abwehr**: Codeblöcke als Platzhalter VOR dem Senden an KI extrahieren. DANACH wiederherstellen. Code passiert nie die KI.

### P2.3: KI übersetzt Mermaid-Labels
**Abwehr**: Mermaid-Blöcke wie Codeblöcke behandeln (Platzhalter-Extraktion).

### P2.4: KI ändert Markdown-Formatierung
**Abwehr**: Überschriftenzahl, Tabellenzeilen, Bold/Italic-Marker mit Original validieren.

### P2.5: KI halluziniert URLs
**Abwehr**: URLs aus Original und Übersetzung extrahieren. Hinzugefügte/entfernte URLs melden.

### P2.6: KI entfernt HTML-Tags
**Abwehr**: HTML als Platzhalter extrahieren (wie Codeblöcke).

### P2.7: KI fügt Übersetzernotizen hinzu
**Abwehr**: Prompt-Regel: "KEINE Notizen hinzufügen." Validierung: Nach "note:", "translator"-Mustern suchen.

### P2.8: Große Datei überschreitet Kontext ⚠️ KRITISCH
**Realer Fall**: 87KB / 3136 Zeilen Datei.
**Abwehr**: Aufteilen nach `##`-Überschriften. Wenn Abschnitt immer noch zu groß → nach `###` aufteilen. Jeder Chunk erhält gleiches Glossar und Regeln.

### P2.9: KI gibt abgeschnittene Antwort zurück
**Abwehr**: Prüfen ob letzte Zeile vollständiger Satz ist. Prüfen ob Code-Fence-Anzahl gerade ist (alle Blöcke geschlossen).

---

## Kategorie 3: Links & Anker

### P3.1: Kaputte Anker nach Übersetzung ⚠️ KRITISCH
**Realer Fall**: `[See below](#slash-commands)` aber Überschrift ist jetzt `## Слеш-команди` → Anker ist `#слеш-команди`.
**Abwehr**: Nach Übersetzung alle Überschriften sammeln → Anker generieren → mit Links vergleichen → Abweichungen automatisch korrigieren.

### P3.2: Apostroph-Varianten in Ankern ⚠️ KRITISCH
**Realer Fall**: Überschrift verwendet `'` (U+0027) das im Anker entfernt wird, aber Link verwendet `ʼ` (U+02BC) das beibehalten wird → Abweichung.
**Abwehr**: Alle Apostroph-Varianten beim Ankervergleich normalisieren.

### P3.3: Doppelte Überschriften
**Realer Fall**: Zwei `## Prompt-хуки`-Überschriften. GitHub fügt `-1`-Suffix zur zweiten hinzu. Validator behandelte dies nicht.
**Abwehr**: Überschriftenzähler verfolgen. `-1`, `-2`-Suffixe für Duplikate generieren.

### P3.4: Relative Links zu nicht übersetzten Dateien
**Szenario**: `translations/uk/docs/guide.md` verlinkt auf `../src/deploy.sh` das an diesem Pfad nicht existiert.
**Abwehr**: Relative Links umschreiben: wenn Ziel übersetzt → lokalen Link beibehalten. Wenn nicht → auf Original umschreiben.

### P3.5: Absolute Pfade
**Abwehr**: Erkennen und warnen. Nicht automatisch umschreiben (framework-spezifisches Verhalten).

### P3.6: Dateiübergreifende Ankerlinks
**Szenario**: `[See](other.md#section)` wo `other.md` übersetzt ist → `#section` könnte zu `#секція` werden.
**Abwehr**: Zuerst Zieldatei auflösen, dann Anker in der korrekten Version prüfen.

---

## Kategorie 4: Kodierung & Dateiformat

### P4.1: Datei nicht UTF-8 ⚠️ KRITISCH
**Realer Fall**: KI lieferte teilweise CP1251 in UTF-8-Datei. 240 ungültige Bytes.
**Abwehr**: UTF-8 nach jedem Schreiben verifizieren. Auto-Reparatur: schlechte Byte-Bereiche erkennen, CP1251 → UTF-8 Neukodierung versuchen.

### P4.2: BOM (Byte Order Mark)
**Abwehr**: BOM beim Lesen ignorieren. Niemals BOM schreiben.

### P4.3: CRLF vs LF
**Abwehr**: Zeilenenden des Originals übernehmen. Standard: LF.

### P4.4: Fehlender abschließender Zeilenumbruch
**Abwehr**: Immer `\n` am Dateiende hinzufügen.

### P4.5: Unsichtbare Unicode-Zeichen
**Abwehr**: U+200B (Zero-Width Space), U+200C, U+200D, U+200E, U+200F nach Übersetzung entfernen.

---

## Kategorie 5: Sprachspezifische Probleme

### P5.1: RTL-Sprachen (Arabisch, Hebräisch)
**Abwehr**: Warnung bei Initialisierung. Eingeschränkte Markdown-Unterstützung für RTL.

### P5.2: CJK-Sprachen (Chinesisch, Japanisch, Koreanisch)
**Abwehr**: Zeilenzahl-Toleranz anpassen (CJK-Text ist kürzer). Codeblock-Anzahl als primäre Strukturprüfung verwenden.

### P5.3: Spezielle Zeichenkonvertierung (Türkisch İ/ı)
**Abwehr**: Unicode-bewussten Vergleich verwenden (`str.casefold()`).

### P5.4: Glossar pro Sprache
**Abwehr**: Glossar wird pro Sprache generiert. Eingebaute Termdatenbank für 10-15 populäre Sprachen.

---

## Kategorie 6: Frontmatter & Metadaten

### P6.1: YAML-Frontmatter bricht bei Übersetzung
**Abwehr**: YAML separat parsen. Nur `description`-Feld übersetzen. Werte nach Übersetzung immer in Anführungszeichen setzen.

### P6.2: Doppeltes Frontmatter
**Abwehr**: Nur erster `---...---`-Block am Dateianfang ist Frontmatter.

### P6.3: Tilde-eingegrenzte Blöcke (`~~~~`)
**Abwehr**: Sowohl ` ``` ` als auch `~~~~` als Codeblock-Marker behandeln.

---

## Kategorie 7: Dateisystem

### P7.1: Keine Schreibrechte
**Abwehr**: Schreibzugriff vor Beginn prüfen.

### P7.2: Festplatte voll
**Abwehr**: Benötigten Speicher schätzen (2× Quell-.md-Größe). Freien Speicher prüfen.

### P7.3: Lange Pfade (Windows 260-Zeichen-Limit)
**Abwehr**: Warnung wenn resultierender Pfad >250 Zeichen.

### P7.4: Sonderzeichen in Dateinamen
**Abwehr**: Originalnamen beibehalten. `Path`-Objekte verwenden, nicht String-Verkettung.

### P7.5: Groß-/Kleinschreibung
**Abwehr**: Exakte Originaldateinamen verwenden. Bei reinen Groß-/Kleinschreibungsduplikaten warnen.

---

## Kategorie 8: Git & Versionskontrolle

### P8.1: Riesiger Diff
**Abwehr**: Empfehlung zur Aufteilung in Batch-PRs nach Priorität.

### P8.2: Merge-Konflikte
**Abwehr**: Jede Sprache ist ein separates Unterverzeichnis → keine Konflikte zwischen Sprachen.

### P8.3: Squash-Merge verliert SHA-Tracking
**Abwehr**: Fallback auf datumsbasierte Suche wenn SHA nicht im Verlauf gefunden.

---

## Kategorie 9: Konfiguration

### P9.1: Ungültiges YAML in Konfiguration
**Abwehr**: Beim Laden validieren. Fallback auf Standardwerte mit Warnung.

### P9.2: Unbekannter Sprachcode
**Abwehr**: Gegen ISO 639-1 validieren. Fuzzy-Match: "ukr" → "Meinten Sie uk?"

### P9.3: Glossar-Konflikte
**Abwehr**: Auf widersprüchliche Stammwort-Übersetzungen beim Laden prüfen. Warnen.

---

## Kategorie 10: Randfälle

### P10.1: Datei besteht nur aus Tabellen
**Abwehr**: Tabellen zeilenweise verarbeiten. `|`-Anzahl pro Zeile mit Original abgleichen.

### P10.2: Markdown mit Inline-HTML
**Abwehr**: HTML-Tags → Platzhalter. Text zwischen Tags übersetzen, nicht Attribute.

### P10.3: LaTeX-Formeln
**Abwehr**: `$...$` und `$$...$$` erkennen. Als Platzhalter extrahieren.

### P10.4: Emoji in Überschriften
**Abwehr**: Emoji beim Anker-Generieren entfernen (entspricht GitHub-Verhalten).

### P10.5: Datei ohne Überschriften
**Abwehr**: Nach Leerzeilen statt `##` aufteilen. Wenn <4000 Tokens → ganze Datei übersetzen.

### P10.6: Doppelte i18n-Metadaten
**Abwehr**: Vorhandene Metadaten vor dem Hinzufügen prüfen. Aktualisieren, nicht duplizieren.

### P10.7: Übersetzungen übersetzen ⚠️ KRITISCH
**Abwehr**: `translations_dir` IMMER vom Scannen ausschließen. Verifizieren dass Quelle ≠ Zielverzeichnis.

### P10.8: Rekursives Einschließen/Ausschließen
**Abwehr**: `exclude: ["**/CHANGELOG.md"]` schließt in jedem Verzeichnis aus. `exclude: ["CHANGELOG.md"]` nur im Root.

---

## Zusammenfassung der Abwehrmechanismen

### Automatisch (keine Benutzeraktion):
| Abwehr | Wann | Aktion |
|--------|------|--------|
| UTF-8-Prüfung | Nach jedem Schreiben | Auto-Reparatur oder Ablehnung |
| Codeblock-Platzhalter | Während Übersetzung | Code passiert nie die KI |
| Zeilenzahl-Prüfung | Nach Übersetzung | Ablehnen wenn <85% |
| Anker-Korrektur | Nach Übersetzung | Kaputte Anker automatisch ersetzen |
| Link-Umschreibung | Bei Dateierstellung | Relative Pfade automatisch umschreiben |
| Abschließender Zeilenumbruch | Beim Schreiben | Automatisch hinzufügen |
| Unsichtbare Unicode-Entfernung | Nach Übersetzung | Automatisch entfernen |
| Metadaten-Deduplizierung | Beim Header-Hinzufügen | Aktualisieren statt duplizieren |

### Warnungen (erfordern Benutzeraufmerksamkeit):
| Abwehr | Wann | Meldung |
|--------|------|---------|
| Großes Repo | Beim Scannen | "12.847 Dateien, Eingrenzung empfohlen" |
| Bestehende Übersetzungen | Bei Initialisierung | "uk/ gefunden, importieren?" |
| Glossar-Abweichung | Bei Validierung | "hook übersetzt als гачок (1x)" |
| RTL-Sprache | Bei Initialisierung | "Erfordert besondere Aufmerksamkeit" |
| Absolute Pfade | Beim Scannen | "Können nicht automatisch umgeschrieben werden" |

### Blockierend (Prozess stoppen):
| Abwehr | Wann | Grund |
|--------|------|-------|
| Datei >15% gekürzt | Nach Übersetzung | KI hat Inhalt verloren |
| Codeblock-Anzahl stimmt nicht | Nach Übersetzung | Struktur kaputt |
| Quelle = Zielverzeichnis | Bei Initialisierung | Würde Übersetzungen übersetzen |
| Keine Schreibrechte | Bei Initialisierung | Kann nicht speichern |

---

## Implementierungspriorität

### MVP (implementiert):
1. ✅ UTF-8-Validierung (P4.1)
2. ✅ Zeilenzahl-Prüfung (P2.1)
3. ✅ Codeblock-Anzahl-Prüfung (P2.1)
4. ✅ Automatische Anker-Korrektur (P3.1, P3.2, P3.3)
5. ✅ Übersetzungsverzeichnis-Ausschluss (P10.7)
6. ✅ Automatische Erkennung bestehender Übersetzungen (P1.3)

### Nächste Schritte (geplant):
7. Codeblock-Platzhalter-Extraktion (P2.2)
8. HTML-Platzhalter-Extraktion (P2.6)
9. Glossar-Prüfung (P5.4)
10. Frontmatter-Behandlung (P6.1)
11. Große-Datei-Aufteilung (P2.8)
12. Relative Link-Umschreibung (P3.4)

### Zukunft:
13. RTL-Unterstützung (P5.1)
14. CJK-Koeffizienten (P5.2)
15. LaTeX-Platzhalter (P10.3)
16. Übersetzungsspeicher
