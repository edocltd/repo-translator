<!-- i18n-source: CONTRIBUTING.md -->
<!-- i18n-date: 2026-04-10 -->

# repo-translator への貢献

ご関心をお寄せいただきありがとうございます。このガイドでは、変更を行うためのプロセスと基準について説明します。

## 貢献の種類

- **バグ修正** — スキャン、検証、アンカーの問題を修正
- **新しい検証チェック** — 実際の翻訳問題を検出するチェックを追加
- **言語サポート** — 用語集の追加、新しい言語でのテスト
- **ドキュメント** — 説明の改善、例の追加
- **翻訳** — ツール自体を使用してプロジェクトドキュメントを翻訳

## 始め方

```bash
git clone https://github.com/edocltd/repo-translator.git
cd repo-translator
git checkout -b your-branch-name
```

コアスクリプトに外部依存関係は不要です。

## コード基準

- Python 3.10+、モダンな型アノテーション使用
- 関数にdocstring必須
- デッドコードや未使用インポートなし
- ハードコードされたパスなし — `Path`オブジェクトを使用
- プレースホルダー関数やコメントアウトされたコードなし

## コミットメッセージ

conventional commitsに従う：`type(scope): description`

タイプ：`feat`、`fix`、`docs`、`refactor`、`test`、`chore`

## ライセンス

貢献することにより、あなたの貢献がMITの下でライセンスされることに同意します。
