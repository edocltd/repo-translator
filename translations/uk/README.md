<!-- i18n-source: README.md -->
<!-- i18n-date: 2026-04-10 -->

# repo-translator

🌐 [English](../../README.md) | [Українська](README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Deutsch](../de/README.md) | [Português](../pt-br/README.md) | [中文](../zh/README.md) | [日本語](../ja/README.md)

**Універсальний інструмент для перекладу документації GitHub-репозиторіїв на будь-яку мову.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GitHub Stars](https://img.shields.io/github/stars/edocltd/repo-translator?style=flat&color=gold)](https://github.com/edocltd/repo-translator/stargazers)

Не обгортка для API — **фреймворк** для структури, валідації та синхронізації. Перекладайте будь-яким способом: Claude Code, Claude.ai, ChatGPT, Ollama або вручну. Інструмент гарантує правильність результату.

> **Створено на реальному досвіді**: Кожна функція існує через реальну проблему, виявлену при перекладі [claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐) українською. Див. [FAILURE-ANALYSIS.md](../../FAILURE-ANALYSIS.md) для повного аналізу 48 проблем.

---

## Зміст

- [Проблема](#проблема)
- [Як це працює](#як-це-працює)
- [Швидкий старт](#швидкий-старт)
- [Методи перекладу](#методи-перекладу)
- [Довідник скриптів](#довідник-скриптів)
- [Структура виводу](#структура-виводу)
- [Перевірки валідації](#перевірки-валідації)
- [Будь-яка мова](#будь-яка-мова)
- [Конфігурація](#конфігурація)
- [Вимоги](#вимоги)
- [Внесок](#внесок)
- [Ліцензія](#ліцензія)

---

## Проблема

Ви хочете перекласти документацію репозиторію. Ви стикаєтесь з:

- **Немає структури** — Які файли перекладати? Які пропустити? Куди класти результати?
- **Немає валідації** — Чи AI мовчки видалив половину контенту? Зламав якорні посилання? Пошкодив кодування?
- **Немає консистентності** — "hook" перекладено як "хук" в одному файлі і "гачок" в іншому
- **Немає синхронізації** — Оригінал оновлено минулого тижня. Які переклади застаріли?

Існуючі інструменти (co-op-translator, gpt-translate) виконують переклад, але повністю ігнорують валідацію.

## Як це працює

```
SCAN  →  TRANSLATE  →  VALIDATE  →  FIX  →  SYNC
  ↓         ↓            ↓          ↓        ↓
"What     "Any        "Is it     "Auto-   "What's
 files?"   method"    correct?"   fix"    outdated?"
```

1. **Сканування** — Аналіз репо, класифікація файлів (перекласти / скопіювати / пропустити), автовиявлення існуючих перекладів, оцінка обсягу
2. **Переклад** — Будь-яким способом. Інструмент генерує промпти з глосарієм та правилами
3. **Валідація** — Перевірка структури (рядки, код-блоки, Mermaid), якорів, кодування, глосарію
4. **Виправлення** — Автовиправлення зламаних якорів, проблем кодування, невидимих Unicode
5. **Синхронізація** — Відстеження застарілих перекладів при зміні оригіналів

Кожен крок — незалежний скрипт. Використовуйте разом або окремо.

## Швидкий старт

```bash
git clone https://github.com/edocltd/repo-translator.git
```

```bash
# Scan any repo to see what needs translating
python repo-translator/scripts/scan.py --root /path/to/any-repo --lang uk

# Generate a translation prompt (copy-paste into Claude.ai / ChatGPT)
python repo-translator/scripts/prompt_generator.py /path/to/any-repo/README.md --lang uk

# After translating — validate the result
python repo-translator/scripts/validate.py --root /path/to/any-repo --lang uk

# Auto-fix broken anchors and encoding
python repo-translator/scripts/fix_anchors.py /path/to/any-repo/translations/uk/

# Check what's outdated after original changes
python repo-translator/scripts/sync_check.py --root /path/to/any-repo --lang uk
```

## Методи перекладу

Інструменту байдуже ЯК ви перекладаєте. Він гарантує правильність результату.

| Метод | Вартість | Налаштування | Найкраще для |
|-------|----------|-------------|-------------|
| **Claude Code** | $0 додатково | Вже встановлений | Найшвидший процес для підписників |
| **Copy-paste** (Claude.ai / ChatGPT) | $0–20/міс | Будь-який AI-чат | Будь-хто з підпискою |
| **Вручну** | $0 | Нічого | Людські перекладачі, малі репо |
| **Ollama** | $0 | Встановити Ollama | Конфіденційність, офлайн-робота |
| **API** (Anthropic / OpenAI) | За використання | API-ключ | Автоматизація, великі репо |

## Довідник скриптів

### `scan.py` — Сканування та класифікація

Аналізує репозиторій та визначає що робити з кожним файлом.

```bash
python scripts/scan.py --root /path/to/repo --lang uk
python scripts/scan.py --root /path/to/repo --lang de --json
python scripts/scan.py --root /path/to/repo --lang fr --output plan.json
```

Ключові функції:
- Автоматично виявляє існуючі переклади (`uk/`, `vi/`, `translations/`, `i18n/` тощо) та виключає їх
- Класифікує файли: `translate` (проза .md) / `copy` (CHANGELOG, код-важкі .md) / `skip` (LICENSE, бінарні)
- Оцінює кількість токенів та вартість API

### `validate.py` — Валідація перекладів

Перевіряє перекладені файли порівняно з оригіналами за 12 перевірками.

```bash
python scripts/validate.py --root /path/to/repo --lang uk
python scripts/validate.py --root /path/to/repo --lang uk --file README.md
```

### `fix_anchors.py` — Автовиправлення

Автоматично виправляє типові проблеми перекладу.

```bash
python scripts/fix_anchors.py translations/uk/
python scripts/fix_anchors.py --dry-run translations/uk/
```

Виправляє: зламані якорні посилання, змішане кодування (CP1251/UTF-8), невидимі Unicode-символи, відсутні завершальні переноси рядків.

### `prompt_generator.py` — Генерація промптів

Створює готові промпти з правилами та глосарієм для будь-якого AI-чату.

```bash
python scripts/prompt_generator.py README.md --lang uk
python scripts/prompt_generator.py large-file.md --lang uk --chunk --max-tokens 4000
python scripts/prompt_generator.py README.md --lang uk --glossary examples/glossary-uk.yaml
```

### `sync_check.py` — Відстеження застарілих перекладів

Виявляє які переклади застаріли після зміни оригіналів.

```bash
python scripts/sync_check.py --root /path/to/repo --lang uk
```

Використовує метадані `i18n-source-sha` у перекладених файлах для порівняння з поточним git SHA.

## Структура виводу

```
any-repo/
├── README.md                    ← original
├── docs/
│   └── guide.md
├── src/
│   └── app.py                   ← not touched
└── translations/                ← created by repo-translator
    └── uk/
        ├── README.md            ← translated
        └── docs/
            └── guide.md         ← translated
```

Перекладаються тільки `.md` файли. Код, зображення та конфіги залишаються у вихідному розташуванні. Посилання переписуються на оригінали за потреби.

## Перевірки валідації

| Перевірка | Тип | Автовиправлення |
|-----------|-----|-----------------|
| Кодування UTF-8 | Критична | ✅ |
| Кількість рядків ≥85% оригіналу | Помилка | ❌ Переперекласти |
| Кількість код-блоків = оригіналу | Помилка | ❌ Переперекласти |
| Кількість Mermaid-діаграм = оригіналу | Помилка | ❌ Переперекласти |
| Незакриті код-блоки | Помилка | ❌ Переперекласти |
| Вміст код-блоків збережено | Попередження | ❌ Вручну |
| Кількість заголовків збігається | Попередження | ❌ Вручну |
| Кількість рядків таблиць збігається | Попередження | ❌ Вручну |
| Якорні посилання резолвляться | Помилка | ✅ |
| URL збережено | Попередження | ❌ Вручну |
| Невидимі Unicode-символи | Попередження | ✅ |
| Завершальний перенос рядка | Попередження | ✅ |

## Будь-яка мова

Використовує коди ISO 639-1. 35+ мов вбудовано, будь-який код приймається:

```bash
python scripts/scan.py --lang uk      # Ukrainian
python scripts/scan.py --lang ja      # Japanese
python scripts/scan.py --lang ar      # Arabic
python scripts/scan.py --lang pt-br   # Brazilian Portuguese
python scripts/scan.py --lang de      # German
```

## Конфігурація

Працює без конфігурації. Для налаштування створіть `.repo-translator.yaml` у цільовому репо:

```yaml
source_lang: en
translations_dir: translations

include:
  - "**/*.md"
  - "**/*.mdx"

exclude:
  - "CHANGELOG.md"
  - "node_modules/**"
```

Див. [.repo-translator.yaml.example](../../.repo-translator.yaml.example) для всіх опцій.

## Вимоги

- Python 3.10+
- Без зовнішніх залежностей для основних скриптів
- Опціонально: `pyyaml` для файлів конфігу/глосарію (fallback на базовий парсинг)
- Опціонально: `git` для функції sync-check

## Внесок

Внески вітаються. Прочитайте [CONTRIBUTING.md](../../CONTRIBUTING.md) перед створенням PR.

## Ліцензія

Ліцензія MIT — див. [LICENSE](../../LICENSE) для деталей.

---

Створено [@edocltd](https://github.com/edocltd)
