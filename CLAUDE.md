# CLAUDE.md — repo-translator

> Це єдине джерело правди про проєкт. Перед будь-якою зміною — прочитай цей файл повністю.

## Що це

Універсальний інструмент для перекладу markdown-документації будь-якого GitHub-репозиторію на будь-яку мову. Не API-обгортка — фреймворк для структури, валідації та синхронізації. Сам переклад може бути виконаний будь-яким способом (Claude Code, copy-paste, Ollama, вручну, API).

## Поточна структура проєкту

```
repo-translator/
├── scripts/
│   ├── scan.py              # Сканування репо, класифікація файлів, генерація плану
│   ├── validate.py          # Валідація перекладів (10 перевірок)
│   ├── fix_anchors.py       # Автовиправлення якорів, кодування, invisible Unicode
│   ├── prompt_generator.py  # Генерація промптів для copy-paste workflow
│   └── sync_check.py        # Перевірка синхронізації з оригіналом
├── examples/
│   └── glossary-uk.yaml     # Приклад глосарію для української мови
├── templates/
│   └── .gitkeep             # Зарезервовано для майбутніх шаблонів промптів
├── .repo-translator.yaml.example  # Приклад конфігурації
├── .gitignore
├── README.md                # Документація для користувачів
├── CLAUDE.md                # ЦЕЙ ФАЙЛ — документація для розробки
├── FAILURE-ANALYSIS.md      # Аналіз 48 проблем з реального досвіду
├── REPO-TRANSLATOR-SPEC.md  # Повна специфікація (початкова версія)
└── LICENSE                  # MIT
```

## Архітектура: 5-етапний конвеєр

```
SCAN → TRANSLATE → VALIDATE → FIX → SYNC
```

Кожен етап — окремий скрипт, незалежний від інших. Людина може запускати їх окремо.

### Потік даних

```
Репозиторій (будь-який)
    │
    ▼
[scan.py] ──→ Виводить план: які файли перекладати, які пропустити
    │
    ▼
[Людина/AI перекладає] ──→ Файли у translations/{lang}/
    │
    ▼
[validate.py] ──→ Перевіряє: рядки, код-блоки, якорі, кодування
    │
    ├── Помилки? ──→ [fix_anchors.py] ──→ Автовиправлення
    │
    └── Все ОК? ──→ git commit
    │
    ▼
[sync_check.py] ──→ "Файл X застарів" (коли оригінал оновився)
```

---

## Скрипти: детальний опис

### 1. scan.py — Сканування репозиторію

**Призначення**: Проаналізувати репозиторій і визначити що з кожним файлом робити.

**Ключова поведінка**:
- Сканує ТІЛЬКИ `.md` та `.mdx` файли (налаштовується через `include`)
- **Автоматично детектує** існуючі переклади:
  - Папки з кодами мов ISO 639-1 (`uk/`, `vi/`, `zh/`, `de/` тощо)
  - Контейнерні папки (`translations/`, `i18n/`, `l10n/`, `lang/`, `locales/`)
  - Перевіряє наявність .md файлів всередині (щоб не виключити папку `no/` яка не є перекладом)
- **Автоматично виключає** знайдені перекладацькі папки зі сканування
- Класифікує файли: `translate` / `copy` / `skip`
- Оцінює кількість токенів та вартість API

**CLI**:
```
python scripts/scan.py --root /path/to/repo --lang uk
python scripts/scan.py --root /path/to/repo --lang uk --json
python scripts/scan.py --root /path/to/repo --lang uk --output plan.json
python scripts/scan.py --root /path/to/repo --lang uk --translations-dir translations
python scripts/scan.py --root /path/to/repo --lang uk --max-files 1000
```

**Параметри**:
- `--root, -r` — корінь репо (default: `.`)
- `--lang, -l` — код мови ISO 639-1 (обов'язковий)
- `--translations-dir, -d` — папка для перекладів (default: `translations`)
- `--max-files` — ліміт файлів (default: 500)
- `--json` — вивід JSON замість таблиці
- `--output, -o` — зберегти план у файл

**Логіка класифікації файлів**:
1. Файл у `SKIP_FILENAMES` (LICENSE, .gitignore тощо) → skip
2. Бінарний файл → skip
3. Файл у `COPY_FILENAMES` (CHANGELOG.md) → copy
4. .md файл з < 10% прози (переважно код) → copy
5. Решта .md файлів → translate

**Логіка виключення патернів** (порядок):
1. `Path.match(pattern)` — стандартний glob
2. Fallback: `rel_str.startswith(prefix + "/")` — для `**` патернів на Windows

**ВІДОМИЙ БАҐЄ**: `--translations-dir .` раніше ламав сканування (exclude `./**` = все). Тепер виправлено через `build_exclude_patterns()` який автоматично детектує мовні папки.

---

### 2. validate.py — Валідація перекладів

**Призначення**: Перевірити якість перекладеного файлу порівняно з оригіналом.

**10 перевірок**:

| # | Перевірка | Severity | Автовиправлення |
|---|-----------|----------|-----------------|
| 1 | UTF-8 валідність | error | Ні (див. fix_anchors.py) |
| 2 | Кількість рядків ±15% | error (<85%) / warning (<95%) | Ні |
| 3 | Кількість ``` пар (код-блоки) | error | Ні |
| 4 | Непарні ``` (незакриті блоки) | error | Ні |
| 5 | Кількість Mermaid-блоків | error | Ні |
| 6 | Кількість заголовків | warning | Ні |
| 7 | Кількість рядків таблиць | warning | Ні |
| 8 | Вміст код-блоків = оригінал | warning | Ні |
| 9 | Якорні посилання резолвляться | error | Так (fix_anchors.py) |
| 10 | URL збережені | warning | Ні |
| 11 | Invisible Unicode символи | warning | Так (fix_anchors.py) |
| 12 | Trailing newline | warning | Так (fix_anchors.py) |

**CLI**:
```
python scripts/validate.py --root /path/to/repo --lang uk
python scripts/validate.py --root /path/to/repo --lang uk --translations-dir .
python scripts/validate.py --root /path/to/repo --lang uk --file README.md
python scripts/validate.py --root /path/to/repo --lang uk --json
```

**Логіка якорів** (heading_to_anchor):
- Видаляє emoji
- Видаляє пунктуацію КРІМ Unicode word chars, пробілів, дефісів
- Lowercase
- Пробіли → дефіси
- Strip trailing дефіси
- Підтримує дублюючі заголовки (додає -1, -2)

**ВАЖЛИВО**: Апострофи `'` (U+0027), `ʼ` (U+02BC), `'` (U+2019) обробляються по-різному. `'` видаляється (не word char), `ʼ` зберігається (word char). Це джерело багів — `find_best_anchor()` нормалізує апострофи при порівнянні.

---

### 3. fix_anchors.py — Автовиправлення

**Призначення**: Автоматично виправити проблеми знайдені validate.py.

**Що виправляє**:
1. Зламані якорні посилання → fuzzy match до правильного якоря
2. Змішане кодування (CP1251 блоки в UTF-8 файлі) → перекодування
3. Invisible Unicode символи → видалення
4. Відсутній newline в кінці файлу → додавання

**CLI**:
```
python scripts/fix_anchors.py translations/uk/
python scripts/fix_anchors.py translations/uk/README.md
python scripts/fix_anchors.py --dry-run translations/uk/
```

**Логіка виправлення якорів**:
1. Збирає всі заголовки → генерує валідні якорі (з підтримкою дублікатів)
2. Знаходить всі `[text](#anchor)` посилання ПОЗА код-блоками
3. Якщо якір не в множині валідних → шукає найближчий через `normalize_anchor()` (видаляє апострофи) та substring match
4. Замінює в зворотному порядку (щоб не зсунути позиції)

**Логіка виправлення кодування**:
1. Читає файл як байти
2. Проходить побайтово, перевіряє валідність UTF-8
3. Невалідні байти — пробує декодувати як CP1251 → перекодувати в UTF-8

---

### 4. prompt_generator.py — Генерація промптів

**Призначення**: Створити готовий промпт для copy-paste в Claude.ai / ChatGPT.

**CLI**:
```
python scripts/prompt_generator.py README.md --lang uk
python scripts/prompt_generator.py README.md --lang uk --glossary examples/glossary-uk.yaml
python scripts/prompt_generator.py big-file.md --lang uk --chunk --max-tokens 4000
python scripts/prompt_generator.py README.md --lang uk --output prompt.txt
```

**Промпт включає**:
- 11 правил перекладу (не чіпати код, Mermaid, URL тощо)
- Глосарій (якщо є)
- Список "не перекладати" (якщо є)
- Оригінальний текст файлу

**Чанкування**: Якщо файл > max_tokens — розбиває по `##` заголовках. Кожен чанк отримує ті ж правила та глосарій.

**Пошук глосарію** (пріоритет):
1. `--glossary` параметр
2. `{file_dir}/.glossary-{lang}.yaml`
3. `translations/{lang}/.glossary.yaml`
4. `.repo-translator-glossary-{lang}.yaml`

---

### 5. sync_check.py — Перевірка синхронізації

**Призначення**: Визначити які переклади застаріли після оновлення оригіналу.

**CLI**:
```
python scripts/sync_check.py --root /path/to/repo --lang uk
python scripts/sync_check.py --root /path/to/repo --lang uk --translations-dir .
python scripts/sync_check.py --root /path/to/repo --lang uk --json
```

**Логіка**:
1. Для кожного файлу в translations/{lang}/ — знайти відповідний оригінал
2. Прочитати `<!-- i18n-source-sha: ... -->` з метаданих перекладу
3. Отримати поточний SHA оригіналу через `git log`
4. Якщо SHA різні → файл застарів
5. Показати diff stats

**Fallback без git**: Якщо репо не git — пропускає sync (попередження).

**i18n метадані** (на початку перекладеного файлу):
```html
<!-- i18n-source: README.md -->
<!-- i18n-source-sha: a1b2c3d -->
<!-- i18n-date: 2026-04-10 -->
```

---

## Ключові рішення та правила

### Структура перекладів

**Стандарт**: `translations/{lang}/` — дзеркало структури оригіналу, тільки перекладені .md файли.

```
repo/
├── README.md              ← оригінал
├── docs/guide.md
└── translations/
    └── uk/
        ├── README.md      ← переклад
        └── docs/guide.md  ← переклад
```

**Чому `translations/`**: Зрозуміло кожному без пояснень (на відміну від `i18n/`).

**Не копіювати код/зображення**: Тільки .md файли. Посилання на не-.md ресурси переписуються на оригінал.

### Автодетекція існуючих перекладів

Сканер автоматично знаходить і виключає:
- Папки з кодами ISO 639-1 в корені (`uk/`, `vi/`, `zh/` тощо) — якщо містять .md файли
- Контейнерні папки (`translations/`, `i18n/`, `l10n/`, `lang/`, `locales/`)

### Мови

ISO 639-1 коди. 35 мов в `LANGUAGES` dict. Невідомий код → попередження, але працює.

### Переклад — правила для AI

1. Код-блоки (``` та ~~~~) — НЕ перекладати, НЕ модифікувати
2. Mermaid-діаграми — НЕ модифікувати
3. URL та шляхи файлів — НЕ змінювати
4. YAML frontmatter — перекладати тільки `description`, решту залишити
5. HTML-теги — перекладати текст між тегами, НЕ чіпати атрибути
6. Зберігати Markdown-форматування 1:1
7. Кількість рядків перекладу ±5% від оригіналу
8. НЕ додавати пояснень/коментарів від перекладача
9. НЕ скорочувати — перекладати ВСЕ

---

## Відомі проблеми (TODO)

### Баги

1. **Path.match() на Windows**: `Path.match("uk/**")` не завжди матчить глибоко вкладені файли на старих Python. Workaround: fallback через `str.startswith()`.

2. **Глосарій-перевірка**: `check_glossary()` в validate.py — заглушка (не реалізовано). Потрібен NLP-based matching.

### Не реалізовано (MVP scope)

- [ ] Автоматичний переклад через API (Anthropic/OpenAI/Ollama)
- [ ] Переписування відносних посилань при створенні перекладу
- [ ] GitHub Action для автоматичного sync-check
- [ ] init команда (wizard для першого налаштування)
- [ ] Підтримка RTL мов
- [ ] Коефіцієнти перевірки рядків залежно від мови (CJK коротші)
- [ ] Translation memory (не перекладати повторно)
- [ ] Batch-режим для великих PR

---

## Тестування

### Тест на claude-howto (реальний репо, 22K+ ⭐)

```powershell
cd D:\Github\claude-howto

# Сканування (auto-detect uk/, vi/, zh/)
python D:\Github\repo-translator\scripts\scan.py --root . --lang uk

# Валідація існуючого перекладу
python D:\Github\repo-translator\scripts\validate.py --root . --lang uk --translations-dir .

# Синхронізація
python D:\Github\repo-translator\scripts\sync_check.py --root . --lang uk --translations-dir .

# Промпт для перекладу
python D:\Github\repo-translator\scripts\prompt_generator.py README.md --lang uk
```

### Тест на будь-якому іншому репо

```powershell
git clone https://github.com/someone/any-repo.git
cd any-repo
python D:\Github\repo-translator\scripts\scan.py --root . --lang de
```

---

## Контекст створення

Проєкт створено на основі реального досвіду перекладу [luongnv89/claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐) українською мовою. PR #64. Кожна функція та перевірка — відповідь на реальну проблему:

- AI скоротив файли на 58% → перевірка кількості рядків
- AI переклав код-блоки → плейсхолдери (TODO)
- Якорі зламались після перекладу → auto-fix
- CP1251 кодування від Claude Code → encoding detection
- Непослідовна термінологія → глосарій

Детальний аналіз 48 проблем: `FAILURE-ANALYSIS.md`
Повна специфікація: `REPO-TRANSLATOR-SPEC.md`
