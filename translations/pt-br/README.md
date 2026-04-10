<!-- i18n-source: README.md -->
<!-- i18n-date: 2026-04-10 -->

# repo-translator

🌐 [English](../../README.md) | [Українська](../uk/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Deutsch](../de/README.md) | [Português](README.md) | [中文](../zh/README.md) | [日本語](../ja/README.md)

**Ferramenta universal para traduzir documentação de repositórios GitHub para qualquer idioma.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GitHub Stars](https://img.shields.io/github/stars/edocltd/repo-translator?style=flat&color=gold)](https://github.com/edocltd/repo-translator/stargazers)

Não é um wrapper de API — é um **framework** para estrutura, validação e sincronização. Traduza usando qualquer método: Claude Code, Claude.ai, ChatGPT, Ollama ou manualmente. A ferramenta garante que o resultado esteja correto.

> **Construído a partir de experiência real**: Cada funcionalidade existe por causa de um problema real encontrado ao traduzir [claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐) para ucraniano. Veja [FAILURE-ANALYSIS.md](../../docs/failure-analysis.md) para a análise completa de 48 problemas.

---

## Índice

- [O Problema](#o-problema)
- [Como Funciona](#como-funciona)
- [Início Rápido](#início-rápido)
- [Métodos de Tradução](#métodos-de-tradução)
- [Referência dos Scripts](#referência-dos-scripts)
- [Estrutura de Saída](#estrutura-de-saída)
- [Verificações de Validação](#verificações-de-validação)
- [Qualquer Idioma](#qualquer-idioma)
- [Configuração](#configuração)
- [Requisitos](#requisitos)
- [Contribuir](#contribuir)
- [Licença](#licença)

---

## O Problema

Você quer traduzir a documentação de um repositório. Você enfrenta:

- **Sem estrutura** — Quais arquivos traduzir? Quais pular? Onde colocar os resultados?
- **Sem validação** — A IA deletou silenciosamente metade do conteúdo? Quebrou links de âncora? Corrompeu a codificação?
- **Sem consistência** — "hook" traduzido como "gancho" em um arquivo e "hook" em outro
- **Sem sincronização** — Original atualizado semana passada. Quais traduções estão desatualizadas?

Ferramentas existentes (co-op-translator, gpt-translate) lidam com a tradução, mas ignoram a validação completamente.

## Como Funciona

```
SCAN  →  TRANSLATE  →  VALIDATE  →  FIX  →  SYNC
  ↓         ↓            ↓          ↓        ↓
"What     "Any        "Is it     "Auto-   "What's
 files?"   method"    correct?"   fix"    outdated?"
```

1. **Escanear** — Analisar o repo, classificar arquivos (traduzir / copiar / pular), detectar traduções existentes, estimar esforço
2. **Traduzir** — Use qualquer método. A ferramenta gera prompts com glossário e regras
3. **Validar** — Verificar estrutura (linhas, blocos de código, Mermaid), âncoras, codificação, glossário
4. **Corrigir** — Corrigir automaticamente âncoras quebradas, problemas de codificação, Unicode invisível
5. **Sincronizar** — Rastrear traduções desatualizadas quando os originais mudam

Cada etapa é um script independente. Use-os juntos ou separadamente.

## Início Rápido

```bash
git clone https://github.com/edocltd/repo-translator.git
```

```bash
# Scan any repo to see what needs translating
python repo-translator/scripts/scan.py --root /path/to/any-repo --lang pt-br

# Generate a translation prompt (copy-paste into Claude.ai / ChatGPT)
python repo-translator/scripts/prompt_generator.py /path/to/any-repo/README.md --lang pt-br

# After translating — validate the result
python repo-translator/scripts/validate.py --root /path/to/any-repo --lang pt-br

# Auto-fix broken anchors and encoding
python repo-translator/scripts/fix_anchors.py /path/to/any-repo/translations/pt-br/

# Check what's outdated after original changes
python repo-translator/scripts/sync_check.py --root /path/to/any-repo --lang pt-br
```

## Métodos de Tradução

A ferramenta não se importa COMO você traduz. Ela garante que o resultado esteja correto.

| Método | Custo | Configuração | Ideal Para |
|--------|-------|--------------|------------|
| **Claude Code** | $0 extra | Já instalado | Fluxo mais rápido para assinantes |
| **Copiar-colar** (Claude.ai / ChatGPT) | $0–20/mês | Qualquer chat IA | Qualquer pessoa com assinatura |
| **Manual** | $0 | Nenhuma | Tradutores humanos, repos pequenos |
| **Ollama** | $0 | Instalar Ollama | Privacidade, trabalho offline |
| **API** (Anthropic / OpenAI) | Pago por uso | Chave API | Automação, repos grandes |

## Referência dos Scripts

### `scan.py` — Escanear e Classificar

```bash
python scripts/scan.py --root /path/to/repo --lang pt-br
```

Detecta automaticamente traduções existentes e as exclui. Classifica arquivos: `translate` / `copy` / `skip`. Estima contagem de tokens e custo de API.

### `validate.py` — Validar Traduções

```bash
python scripts/validate.py --root /path/to/repo --lang pt-br
```

Verifica arquivos traduzidos contra originais com 12 verificações de validação.

### `fix_anchors.py` — Correção Automática

```bash
python scripts/fix_anchors.py translations/pt-br/
```

Corrige: links de âncora quebrados, codificação mista, caracteres Unicode invisíveis, quebras de linha ausentes.

### `prompt_generator.py` — Gerar Prompts de Tradução

```bash
python scripts/prompt_generator.py README.md --lang pt-br
```

Cria prompts prontos para colar com regras e glossário para qualquer chat IA.

### `sync_check.py` — Rastrear Traduções Desatualizadas

```bash
python scripts/sync_check.py --root /path/to/repo --lang pt-br
```

## Estrutura de Saída

```
any-repo/
├── README.md                    ← original
├── docs/
│   └── guide.md
├── src/
│   └── app.py                   ← not touched
└── translations/                ← created by repo-translator
    └── pt-br/
        ├── README.md            ← translated
        └── docs/
            └── guide.md         ← translated
```

Apenas arquivos `.md` são traduzidos. Código, imagens e configurações permanecem no local original.

## Requisitos

- Python 3.10+
- Sem dependências externas para scripts principais
- Opcional: `pyyaml` para arquivos de config/glossário
- Opcional: `git` para funcionalidade de sync-check

## Contribuir

Contribuições são bem-vindas. Leia [CONTRIBUTING.md](CONTRIBUTING.md) antes de enviar PRs.

## Licença

Licença MIT — veja [LICENSE](../../LICENSE) para detalhes.

---

Construído por [@edocltd](https://github.com/edocltd)
