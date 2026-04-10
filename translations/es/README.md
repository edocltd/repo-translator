<!-- i18n-source: README.md -->
<!-- i18n-date: 2026-04-10 -->

# repo-translator

🌐 [English](../../README.md) | [Українська](../uk/README.md) | [Español](README.md) | [Français](../fr/README.md) | [Deutsch](../de/README.md) | [Português](../pt-br/README.md) | [中文](../zh/README.md) | [日本語](../ja/README.md)

**Herramienta universal para traducir la documentación de repositorios GitHub a cualquier idioma.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GitHub Stars](https://img.shields.io/github/stars/edocltd/repo-translator?style=flat&color=gold)](https://github.com/edocltd/repo-translator/stargazers)

No es un wrapper de API — es un **framework** para estructura, validación y sincronización. Traduce usando cualquier método: Claude Code, Claude.ai, ChatGPT, Ollama o manualmente. La herramienta garantiza que el resultado sea correcto.

> **Construido desde experiencia real**: Cada función existe por un problema real encontrado al traducir [claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐) al ucraniano. Ver [FAILURE-ANALYSIS.md](../../docs/failure-analysis.md) para el análisis completo de 48 problemas.

---

## Índice

- [El Problema](#el-problema)
- [Cómo Funciona](#cómo-funciona)
- [Inicio Rápido](#inicio-rápido)
- [Métodos de Traducción](#métodos-de-traducción)
- [Referencia de Scripts](#referencia-de-scripts)
- [Estructura de Salida](#estructura-de-salida)
- [Verificaciones de Validación](#verificaciones-de-validación)
- [Cualquier Idioma](#cualquier-idioma)
- [Configuración](#configuración)
- [Requisitos](#requisitos)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

---

## El Problema

Quieres traducir la documentación de un repositorio. Te enfrentas a:

- **Sin estructura** — ¿Qué archivos traducir? ¿Cuáles omitir? ¿Dónde poner los resultados?
- **Sin validación** — ¿La IA eliminó silenciosamente la mitad del contenido? ¿Rompió enlaces ancla? ¿Corrompió la codificación?
- **Sin consistencia** — "hook" traducido como "gancho" en un archivo y "hook" en otro
- **Sin sincronización** — El original se actualizó la semana pasada. ¿Qué traducciones están desactualizadas?

Las herramientas existentes (co-op-translator, gpt-translate) manejan la traducción pero omiten la validación por completo.

## Cómo Funciona

```
SCAN  →  TRANSLATE  →  VALIDATE  →  FIX  →  SYNC
  ↓         ↓            ↓          ↓        ↓
"¿Qué     "Cualquier  "¿Es       "Auto-   "¿Qué está
 archivos?" método"   correcto?" fix"    desactualizado?"
```

1. **Escaneo** — Analiza el repo, clasifica archivos (traducir / copiar / omitir), detecta traducciones existentes, estima el esfuerzo
2. **Traducción** — Usa cualquier método. La herramienta genera prompts con glosario y reglas
3. **Validación** — Verifica estructura (líneas, bloques de código, Mermaid), anclas, codificación, glosario
4. **Corrección** — Corrige automáticamente anclas rotas, problemas de codificación, Unicode invisible
5. **Sincronización** — Rastrea traducciones desactualizadas cuando los originales cambian

Cada paso es un script independiente. Úsalos juntos o por separado.

## Inicio Rápido

```bash
git clone https://github.com/edocltd/repo-translator.git
```

```bash
# Scan any repo to see what needs translating
python repo-translator/scripts/scan.py --root /path/to/any-repo --lang es

# Generate a translation prompt (copy-paste into Claude.ai / ChatGPT)
python repo-translator/scripts/prompt_generator.py /path/to/any-repo/README.md --lang es

# After translating — validate the result
python repo-translator/scripts/validate.py --root /path/to/any-repo --lang es

# Auto-fix broken anchors and encoding
python repo-translator/scripts/fix_anchors.py /path/to/any-repo/translations/es/

# Check what's outdated after original changes
python repo-translator/scripts/sync_check.py --root /path/to/any-repo --lang es
```

## Métodos de Traducción

A la herramienta no le importa CÓMO traduces. Garantiza que el resultado sea correcto.

| Método | Costo | Configuración | Ideal Para |
|--------|-------|---------------|------------|
| **Claude Code** | $0 extra | Ya instalado | Flujo más rápido para suscriptores |
| **Copiar-pegar** (Claude.ai / ChatGPT) | $0–20/mes | Cualquier chat IA | Cualquiera con suscripción |
| **Manual** | $0 | Ninguna | Traductores humanos, repos pequeños |
| **Ollama** | $0 | Instalar Ollama | Privacidad, trabajo offline |
| **API** (Anthropic / OpenAI) | Pago por uso | Clave API | Automatización, repos grandes |

## Referencia de Scripts

### `scan.py` — Escanear y Clasificar

Analiza un repositorio y determina qué hacer con cada archivo.

```bash
python scripts/scan.py --root /path/to/repo --lang es
python scripts/scan.py --root /path/to/repo --lang de --json
python scripts/scan.py --root /path/to/repo --lang fr --output plan.json
```

Características clave:
- Detecta automáticamente traducciones existentes (`uk/`, `vi/`, `translations/`, `i18n/`, etc.) y las excluye
- Clasifica archivos: `translate` (prosa .md) / `copy` (CHANGELOG, .md con mucho código) / `skip` (LICENSE, binarios)
- Estima cantidad de tokens y costo de API

### `validate.py` — Validar Traducciones

Verifica archivos traducidos contra originales con 12 verificaciones.

```bash
python scripts/validate.py --root /path/to/repo --lang es
python scripts/validate.py --root /path/to/repo --lang es --file README.md
```

### `fix_anchors.py` — Corrección Automática

Corrige automáticamente problemas comunes de traducción.

```bash
python scripts/fix_anchors.py translations/es/
python scripts/fix_anchors.py --dry-run translations/es/
```

Corrige: enlaces ancla rotos, codificación mixta (CP1251/UTF-8), caracteres Unicode invisibles, saltos de línea faltantes.

### `prompt_generator.py` — Generar Prompts de Traducción

Crea prompts listos para pegar con reglas y glosario para cualquier chat IA.

```bash
python scripts/prompt_generator.py README.md --lang es
python scripts/prompt_generator.py large-file.md --lang es --chunk --max-tokens 4000
python scripts/prompt_generator.py README.md --lang es --glossary examples/glossary-es.yaml
```

### `sync_check.py` — Rastrear Traducciones Desactualizadas

Detecta qué traducciones están desactualizadas después de cambios en el original.

```bash
python scripts/sync_check.py --root /path/to/repo --lang es
```

Usa metadatos `i18n-source-sha` en archivos traducidos para comparar con el SHA actual de git.

## Estructura de Salida

```
any-repo/
├── README.md                    ← original
├── docs/
│   └── guide.md
├── src/
│   └── app.py                   ← not touched
└── translations/                ← created by repo-translator
    └── es/
        ├── README.md            ← translated
        └── docs/
            └── guide.md         ← translated
```

Solo se traducen archivos `.md`. Código, imágenes y configuraciones permanecen en su ubicación original. Los enlaces se reescriben para apuntar a los originales cuando es necesario.

## Verificaciones de Validación

| Verificación | Tipo | Auto-corrección |
|-------------|------|-----------------|
| Codificación UTF-8 | Crítica | ✅ |
| Conteo de líneas ≥85% del original | Error | ❌ Re-traducir |
| Conteo de bloques de código = original | Error | ❌ Re-traducir |
| Conteo de diagramas Mermaid = original | Error | ❌ Re-traducir |
| Bloques de código sin cerrar | Error | ❌ Re-traducir |
| Contenido de bloques de código preservado | Advertencia | ❌ Manual |
| Conteo de encabezados coincide | Advertencia | ❌ Manual |
| Conteo de filas de tabla coincide | Advertencia | ❌ Manual |
| Enlaces ancla resuelven | Error | ✅ |
| URLs preservadas | Advertencia | ❌ Manual |
| Caracteres Unicode invisibles | Advertencia | ✅ |
| Salto de línea final | Advertencia | ✅ |

## Cualquier Idioma

Usa códigos ISO 639-1. 35+ idiomas incluidos, cualquier código aceptado:

```bash
python scripts/scan.py --lang uk      # Ukrainian
python scripts/scan.py --lang ja      # Japanese
python scripts/scan.py --lang ar      # Arabic
python scripts/scan.py --lang pt-br   # Brazilian Portuguese
python scripts/scan.py --lang de      # German
```

## Configuración

Funciona sin configuración. Para personalizar, crea `.repo-translator.yaml` en el repo destino:

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

Ver [.repo-translator.yaml.example](../../.repo-translator.yaml.example) para todas las opciones.

## Requisitos

- Python 3.10+
- Sin dependencias externas para scripts principales
- Opcional: `pyyaml` para archivos de config/glosario (fallback a parsing básico)
- Opcional: `git` para la funcionalidad de sync-check

## Contribuir

Las contribuciones son bienvenidas. Lee [CONTRIBUTING.md](CONTRIBUTING.md) antes de enviar PRs.

## Licencia

Licencia MIT — ver [LICENSE](../../LICENSE) para detalles.

---

Construido por [@edocltd](https://github.com/edocltd)
