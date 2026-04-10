<!-- i18n-source: CONTRIBUTING.md -->
<!-- i18n-date: 2026-04-10 -->

# 为 repo-translator 做贡献

感谢您的关注。本指南介绍了进行更改的流程和标准。

## 贡献类型

- **Bug 修复** — 修复扫描、验证或锚点问题
- **新验证检查** — 添加能检测真实翻译问题的检查
- **语言支持** — 添加术语表、测试新语言
- **文档** — 改进说明、添加示例
- **翻译** — 使用工具本身翻译项目文档

## 开始

```bash
git clone https://github.com/edocltd/repo-translator.git
cd repo-translator
git checkout -b your-branch-name
```

核心脚本无需外部依赖。

## 代码标准

- Python 3.10+，使用现代类型注解
- 函数需有 docstring
- 无死代码或未使用的导入
- 无硬编码路径 — 使用 `Path` 对象
- 无占位函数或注释代码

## 提交消息

遵循 conventional commits：`type(scope): description`

类型：`feat`、`fix`、`docs`、`refactor`、`test`、`chore`

## 许可证

通过贡献，您同意您的贡献在 MIT 下许可。
