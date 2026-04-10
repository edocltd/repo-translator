<!-- i18n-source: README.md -->
<!-- i18n-date: 2026-04-10 -->

# repo-translator

🌐 [English](../../README.md) | [Українська](../uk/README.md) | [Español](../es/README.md) | [Français](../fr/README.md) | [Deutsch](../de/README.md) | [Português](../pt-br/README.md) | [中文](README.md) | [日本語](../ja/README.md)

**将 GitHub 仓库文档翻译为任何语言的通用工具。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![GitHub Stars](https://img.shields.io/github/stars/edocltd/repo-translator?style=flat&color=gold)](https://github.com/edocltd/repo-translator/stargazers)

不是 API 封装器——而是用于结构化、验证和同步的**框架**。使用任何方法翻译：Claude Code、Claude.ai、ChatGPT、Ollama 或手动翻译。工具确保结果正确。

> **基于真实经验构建**：每个功能都源于翻译 [claude-howto](https://github.com/luongnv89/claude-howto)（22K+ ⭐）为乌克兰语时遇到的真实问题。详见 [FAILURE-ANALYSIS.md](../../docs/failure-analysis.md) 中 48 个问题的完整分析。

---

## 目录

- [问题](#问题)
- [工作原理](#工作原理)
- [快速开始](#快速开始)
- [翻译方法](#翻译方法)
- [脚本参考](#脚本参考)
- [输出结构](#输出结构)
- [验证检查](#验证检查)
- [任何语言](#任何语言)
- [配置](#配置)
- [要求](#要求)
- [贡献](#贡献)
- [许可证](#许可证)

---

## 问题

你想翻译一个仓库的文档。你面临：

- **没有结构** — 翻译哪些文件？跳过哪些？结果放在哪里？
- **没有验证** — AI 是否静默删除了一半内容？破坏了锚点链接？损坏了编码？
- **没有一致性** — "hook" 在一个文件中翻译为 "钩子"，在另一个文件中翻译为 "hook"
- **没有同步** — 原文上周更新了。哪些翻译已过时？

现有工具（co-op-translator、gpt-translate）处理翻译，但完全跳过验证。

## 工作原理

```
SCAN  →  TRANSLATE  →  VALIDATE  →  FIX  →  SYNC
  ↓         ↓            ↓          ↓        ↓
"哪些      "任何       "是否      "自动    "什么
 文件?"    方法"      正确?"    修复"  过时?"
```

1. **扫描** — 分析仓库，分类文件（翻译/复制/跳过），自动检测现有翻译，估算工作量
2. **翻译** — 使用任何方法。工具生成包含术语表和规则的提示词
3. **验证** — 检查结构（行数、代码块、Mermaid）、锚点、编码、术语表
4. **修复** — 自动修复损坏的锚点、编码问题、不可见 Unicode
5. **同步** — 当原文变更时追踪过时的翻译

每个步骤都是独立脚本。可以一起使用或单独使用。

## 快速开始

```bash
git clone https://github.com/edocltd/repo-translator.git
```

```bash
# Scan any repo to see what needs translating
python repo-translator/scripts/scan.py --root /path/to/any-repo --lang zh

# Generate a translation prompt (copy-paste into Claude.ai / ChatGPT)
python repo-translator/scripts/prompt_generator.py /path/to/any-repo/README.md --lang zh

# After translating — validate the result
python repo-translator/scripts/validate.py --root /path/to/any-repo --lang zh

# Auto-fix broken anchors and encoding
python repo-translator/scripts/fix_anchors.py /path/to/any-repo/translations/zh/

# Check what's outdated after original changes
python repo-translator/scripts/sync_check.py --root /path/to/any-repo --lang zh
```

## 翻译方法

工具不关心你如何翻译。它确保结果正确。

| 方法 | 成本 | 设置 | 最适合 |
|------|------|------|--------|
| **Claude Code** | 免费 | 已安装 | 订阅者的最快工作流 |
| **复制粘贴** (Claude.ai / ChatGPT) | $0–20/月 | 任何 AI 聊天 | 有订阅的任何人 |
| **手动** | 免费 | 无 | 人工翻译，小型仓库 |
| **Ollama** | 免费 | 安装 Ollama | 隐私敏感，离线工作 |
| **API** (Anthropic / OpenAI) | 按用量付费 | API 密钥 | 自动化，大型仓库 |

## 脚本参考

### `scan.py` — 扫描与分类

```bash
python scripts/scan.py --root /path/to/repo --lang zh
```

自动检测现有翻译并排除。将文件分类为：`translate` / `copy` / `skip`。估算令牌数和 API 成本。

### `validate.py` — 验证翻译

```bash
python scripts/validate.py --root /path/to/repo --lang zh
```

使用 12 项验证检查，将翻译文件与原文进行比对。

### `fix_anchors.py` — 自动修复

```bash
python scripts/fix_anchors.py translations/zh/
```

修复：损坏的锚点链接、混合编码、不可见 Unicode 字符、缺失的尾部换行符。

### `prompt_generator.py` — 生成翻译提示词

```bash
python scripts/prompt_generator.py README.md --lang zh
```

创建包含规则和术语表的即用提示词，适用于任何 AI 聊天。

### `sync_check.py` — 追踪过时翻译

```bash
python scripts/sync_check.py --root /path/to/repo --lang zh
```

## 输出结构

```
any-repo/
├── README.md                    ← original
├── docs/
│   └── guide.md
├── src/
│   └── app.py                   ← not touched
└── translations/                ← created by repo-translator
    └── zh/
        ├── README.md            ← translated
        └── docs/
            └── guide.md         ← translated
```

只翻译 `.md` 文件。代码、图片和配置保留在原始位置。

## 要求

- Python 3.10+
- 核心脚本无外部依赖
- 可选：`pyyaml` 用于配置/术语表文件
- 可选：`git` 用于同步检查功能

## 贡献

欢迎贡献。提交 PR 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT 许可证 — 详见 [LICENSE](../../LICENSE)。

---

由 [@edocltd](https://github.com/edocltd) 构建
