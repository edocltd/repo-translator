<!-- i18n-source: README.md -->
<!-- i18n-date: 2026-04-10 -->

# repo-translator

🌐 [English](../../README.md) | [Українська](../uk/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Deutsch](../de/README.md) | [Português](../pt-br/README.md) | [中文](../zh/README.md) | [日本語](README.md)

**GitHubリポジトリのドキュメントをあらゆる言語に翻訳するためのユニバーサルツール。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GitHub Stars](https://img.shields.io/github/stars/edocltd/repo-translator?style=flat&color=gold)](https://github.com/edocltd/repo-translator/stargazers)

APIラッパーではなく、構造化、検証、同期のための**フレームワーク**です。Claude Code、Claude.ai、ChatGPT、Ollama、または手動で翻訳できます。ツールは結果の正確性を保証します。

> **実体験から構築**: すべての機能は、[claude-howto](https://github.com/luongnv89/claude-howto)（22K+ ⭐）をウクライナ語に翻訳する際に遭遇した実際の問題から生まれました。48の問題の完全な分析は [FAILURE-ANALYSIS.md](../../FAILURE-ANALYSIS.md) をご覧ください。

---

## 目次

- [問題](#問題)
- [仕組み](#仕組み)
- [クイックスタート](#クイックスタート)
- [翻訳方法](#翻訳方法)
- [スクリプトリファレンス](#スクリプトリファレンス)
- [出力構造](#出力構造)
- [検証チェック](#検証チェック)
- [あらゆる言語](#あらゆる言語)
- [設定](#設定)
- [要件](#要件)
- [貢献](#貢献)
- [ライセンス](#ライセンス)

---

## 問題

リポジトリのドキュメントを翻訳したい。以下の問題に直面します：

- **構造がない** — どのファイルを翻訳する？どれをスキップする？結果はどこに置く？
- **検証がない** — AIが無言でコンテンツの半分を削除した？アンカーリンクが壊れた？エンコーディングが破損した？
- **一貫性がない** — "hook"があるファイルでは「フック」、別のファイルでは「hook」と翻訳されている
- **同期がない** — オリジナルが先週更新された。どの翻訳が古くなっている？

既存のツール（co-op-translator、gpt-translate）は翻訳を処理しますが、検証を完全にスキップします。

## 仕組み

```
SCAN  →  TRANSLATE  →  VALIDATE  →  FIX  →  SYNC
  ↓         ↓            ↓          ↓        ↓
"What     "Any        "Is it     "Auto-   "What's
 files?"   method"    correct?"   fix"    outdated?"
```

1. **スキャン** — リポジトリを分析し、ファイルを分類（翻訳/コピー/スキップ）、既存の翻訳を自動検出、作業量を見積もり
2. **翻訳** — 任意の方法を使用。ツールが用語集とルール付きのプロンプトを生成
3. **検証** — 構造（行数、コードブロック、Mermaid）、アンカー、エンコーディング、用語集を確認
4. **修正** — 壊れたアンカー、エンコーディング問題、不可視Unicodeを自動修正
5. **同期** — オリジナルが変更された時に古い翻訳を追跡

各ステップは独立したスクリプトです。一緒にまたは個別に使用できます。

## クイックスタート

```bash
git clone https://github.com/edocltd/repo-translator.git
```

```bash
# Scan any repo to see what needs translating
python repo-translator/scripts/scan.py --root /path/to/any-repo --lang ja

# Generate a translation prompt (copy-paste into Claude.ai / ChatGPT)
python repo-translator/scripts/prompt_generator.py /path/to/any-repo/README.md --lang ja

# After translating — validate the result
python repo-translator/scripts/validate.py --root /path/to/any-repo --lang ja

# Auto-fix broken anchors and encoding
python repo-translator/scripts/fix_anchors.py /path/to/any-repo/translations/ja/

# Check what's outdated after original changes
python repo-translator/scripts/sync_check.py --root /path/to/any-repo --lang ja
```

## 翻訳方法

ツールは翻訳方法を問いません。結果の正確性を保証します。

| 方法 | コスト | セットアップ | 最適な用途 |
|------|--------|------------|-----------|
| **Claude Code** | 追加$0 | インストール済み | サブスクライバー向け最速ワークフロー |
| **コピー＆ペースト** (Claude.ai / ChatGPT) | $0–20/月 | 任意のAIチャット | サブスクリプション保有者 |
| **手動** | $0 | なし | 人間の翻訳者、小規模リポジトリ |
| **Ollama** | $0 | Ollamaインストール | プライバシー重視、オフライン作業 |
| **API** (Anthropic / OpenAI) | 従量課金 | APIキー | 自動化、大規模リポジトリ |

## スクリプトリファレンス

### `scan.py` — スキャンと分類

```bash
python scripts/scan.py --root /path/to/repo --lang ja
```

既存の翻訳を自動検出して除外。ファイルを分類：`translate` / `copy` / `skip`。トークン数とAPIコストを見積もり。

### `validate.py` — 翻訳の検証

```bash
python scripts/validate.py --root /path/to/repo --lang ja
```

12の検証チェックでオリジナルと翻訳ファイルを照合。

### `fix_anchors.py` — 自動修正

```bash
python scripts/fix_anchors.py translations/ja/
```

修正対象：壊れたアンカーリンク、混合エンコーディング、不可視Unicode文字、末尾改行の欠落。

### `prompt_generator.py` — 翻訳プロンプト生成

```bash
python scripts/prompt_generator.py README.md --lang ja
```

ルールと用語集付きのすぐ使えるプロンプトを作成。

### `sync_check.py` — 古い翻訳の追跡

```bash
python scripts/sync_check.py --root /path/to/repo --lang ja
```

## 出力構造

```
any-repo/
├── README.md                    ← original
├── docs/
│   └── guide.md
├── src/
│   └── app.py                   ← not touched
└── translations/                ← created by repo-translator
    └── ja/
        ├── README.md            ← translated
        └── docs/
            └── guide.md         ← translated
```

`.md`ファイルのみが翻訳されます。コード、画像、設定ファイルは元の場所に残ります。

## 要件

- Python 3.10+
- コアスクリプトに外部依存関係なし
- オプション：設定/用語集ファイル用の`pyyaml`
- オプション：sync-check機能用の`git`

## 貢献

貢献を歓迎します。PRの前に [CONTRIBUTING.md](../../CONTRIBUTING.md) をお読みください。

## ライセンス

MITライセンス — 詳細は [LICENSE](../../LICENSE) をご覧ください。

---

[@edocltd](https://github.com/edocltd) による構築
