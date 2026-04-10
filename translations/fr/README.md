<!-- i18n-source: README.md -->
<!-- i18n-date: 2026-04-10 -->

# repo-translator

🌐 [English](../../README.md) | [Українська](../uk/README.md) | [Español](../es/README.md) | [Français](README.md) | [Deutsch](../de/README.md) | [Português](../pt-br/README.md) | [中文](../zh/README.md) | [日本語](../ja/README.md)

**Outil universel pour traduire la documentation des dépôts GitHub dans n'importe quelle langue.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GitHub Stars](https://img.shields.io/github/stars/edocltd/repo-translator?style=flat&color=gold)](https://github.com/edocltd/repo-translator/stargazers)

Pas un wrapper d'API — un **framework** pour la structure, la validation et la synchronisation. Traduisez avec n'importe quelle méthode : Claude Code, Claude.ai, ChatGPT, Ollama ou manuellement. L'outil garantit que le résultat est correct.

> **Construit à partir d'expérience réelle** : Chaque fonctionnalité existe à cause d'un problème réel rencontré lors de la traduction de [claude-howto](https://github.com/luongnv89/claude-howto) (22K+ ⭐) en ukrainien. Voir [FAILURE-ANALYSIS.md](../../docs/failure-analysis.md) pour l'analyse complète des 48 problèmes.

---

## Table des matières

- [Le Problème](#le-problème)
- [Comment ça fonctionne](#comment-ça-fonctionne)
- [Démarrage rapide](#démarrage-rapide)
- [Méthodes de traduction](#méthodes-de-traduction)
- [Référence des scripts](#référence-des-scripts)
- [Structure de sortie](#structure-de-sortie)
- [Vérifications de validation](#vérifications-de-validation)
- [N'importe quelle langue](#nimporte-quelle-langue)
- [Configuration](#configuration)
- [Prérequis](#prérequis)
- [Contribuer](#contribuer)
- [Licence](#licence)

---

## Le Problème

Vous voulez traduire la documentation d'un dépôt. Vous faites face à :

- **Pas de structure** — Quels fichiers traduire ? Lesquels ignorer ? Où mettre les résultats ?
- **Pas de validation** — L'IA a-t-elle silencieusement supprimé la moitié du contenu ? Cassé les liens d'ancrage ? Corrompu l'encodage ?
- **Pas de cohérence** — "hook" traduit par "crochet" dans un fichier et "hook" dans un autre
- **Pas de synchronisation** — L'original a été mis à jour la semaine dernière. Quelles traductions sont obsolètes ?

Les outils existants (co-op-translator, gpt-translate) gèrent la traduction mais ignorent complètement la validation.

## Comment ça fonctionne

```
SCAN  →  TRANSLATE  →  VALIDATE  →  FIX  →  SYNC
  ↓         ↓            ↓          ↓        ↓
"What     "Any        "Is it     "Auto-   "What's
 files?"   method"    correct?"   fix"    outdated?"
```

1. **Scan** — Analyser le dépôt, classifier les fichiers (traduire / copier / ignorer), détecter les traductions existantes, estimer l'effort
2. **Traduction** — Utilisez n'importe quelle méthode. L'outil génère des prompts avec glossaire et règles
3. **Validation** — Vérifier la structure (lignes, blocs de code, Mermaid), ancres, encodage, glossaire
4. **Correction** — Corriger automatiquement les ancres cassées, problèmes d'encodage, Unicode invisible
5. **Synchronisation** — Suivre les traductions obsolètes quand les originaux changent

Chaque étape est un script indépendant. Utilisez-les ensemble ou séparément.

## Démarrage rapide

```bash
git clone https://github.com/edocltd/repo-translator.git
```

```bash
# Scan any repo to see what needs translating
python repo-translator/scripts/scan.py --root /path/to/any-repo --lang fr

# Generate a translation prompt (copy-paste into Claude.ai / ChatGPT)
python repo-translator/scripts/prompt_generator.py /path/to/any-repo/README.md --lang fr

# After translating — validate the result
python repo-translator/scripts/validate.py --root /path/to/any-repo --lang fr

# Auto-fix broken anchors and encoding
python repo-translator/scripts/fix_anchors.py /path/to/any-repo/translations/fr/

# Check what's outdated after original changes
python repo-translator/scripts/sync_check.py --root /path/to/any-repo --lang fr
```

## Méthodes de traduction

L'outil ne se soucie pas de COMMENT vous traduisez. Il garantit que le résultat est correct.

| Méthode | Coût | Configuration | Idéal pour |
|---------|------|---------------|------------|
| **Claude Code** | 0 $ extra | Déjà installé | Flux le plus rapide pour les abonnés |
| **Copier-coller** (Claude.ai / ChatGPT) | 0–20 $/mois | N'importe quel chat IA | Toute personne avec un abonnement |
| **Manuel** | 0 $ | Aucune | Traducteurs humains, petits dépôts |
| **Ollama** | 0 $ | Installer Ollama | Confidentialité, travail hors ligne |
| **API** (Anthropic / OpenAI) | À l'utilisation | Clé API | Automatisation, grands dépôts |

## Référence des scripts

### `scan.py` — Scanner et classifier

Analyse un dépôt et détermine quoi faire avec chaque fichier.

```bash
python scripts/scan.py --root /path/to/repo --lang fr
python scripts/scan.py --root /path/to/repo --lang de --json
python scripts/scan.py --root /path/to/repo --lang es --output plan.json
```

Fonctionnalités clés :
- Détecte automatiquement les traductions existantes (`uk/`, `vi/`, `translations/`, `i18n/`, etc.) et les exclut
- Classifie les fichiers : `translate` (prose .md) / `copy` (CHANGELOG, .md à forte teneur en code) / `skip` (LICENSE, binaires)
- Estime le nombre de tokens et le coût API

### `validate.py` — Valider les traductions

Vérifie les fichiers traduits par rapport aux originaux avec 12 vérifications.

```bash
python scripts/validate.py --root /path/to/repo --lang fr
python scripts/validate.py --root /path/to/repo --lang fr --file README.md
```

### `fix_anchors.py` — Correction automatique

Corrige automatiquement les problèmes courants de traduction.

```bash
python scripts/fix_anchors.py translations/fr/
python scripts/fix_anchors.py --dry-run translations/fr/
```

Corrige : liens d'ancrage cassés, encodage mixte (CP1251/UTF-8), caractères Unicode invisibles, sauts de ligne manquants.

### `prompt_generator.py` — Générer des prompts

Crée des prompts prêts à coller avec règles et glossaire pour tout chat IA.

```bash
python scripts/prompt_generator.py README.md --lang fr
python scripts/prompt_generator.py large-file.md --lang fr --chunk --max-tokens 4000
```

### `sync_check.py` — Suivre les traductions obsolètes

Détecte quelles traductions sont obsolètes après des changements dans l'original.

```bash
python scripts/sync_check.py --root /path/to/repo --lang fr
```

## Structure de sortie

```
any-repo/
├── README.md                    ← original
├── docs/
│   └── guide.md
├── src/
│   └── app.py                   ← not touched
└── translations/                ← created by repo-translator
    └── fr/
        ├── README.md            ← translated
        └── docs/
            └── guide.md         ← translated
```

Seuls les fichiers `.md` sont traduits. Le code, les images et les configurations restent à leur emplacement d'origine.

## Prérequis

- Python 3.10+
- Aucune dépendance externe pour les scripts principaux
- Optionnel : `pyyaml` pour les fichiers de config/glossaire
- Optionnel : `git` pour la fonctionnalité sync-check

## Contribuer

Les contributions sont les bienvenues. Lisez [CONTRIBUTING.md](CONTRIBUTING.md) avant de soumettre des PRs.

## Licence

Licence MIT — voir [LICENSE](../../LICENSE) pour les détails.

---

Construit par [@edocltd](https://github.com/edocltd)
