# Auto Sync: 人格スタイルの自動更新

目的
- 新規/更新コンテンツ（メルマガ/ブログ/SNS/台本 等）から、"その人らしさ"（価値観・表現・原則）を継続的に収集し、`persona/analysis.json` と各ガイド（credo/voice/do_dont/boundaries/style_prompts）をアップデートできる仕組み。

構成
- `00_config.json` — 監視フォルダ/拡張子/除外設定
- `sync_persona.py` — 差分収集（新規/更新ファイル→スニペット化）
- `delta_corpus.json` — 直近実行で抽出された差分スニペット
- `01_auto_update_prompt.md` — Claude Code 用。差分を吸収し analysis/guides を自動更新
- `../.persona_index.json` — 処理済みファイルのハッシュ索引（自動生成）

使い方
- 1) `00_config.json` の `roots` に対象パスを設定
- 2) 実行: `python persona/auto/sync_persona.py`
- 3) `delta_corpus.json` を `01_auto_update_prompt.md` と共に Claude Code へ貼付→更新版の `analysis.json` と各 md を出力
- 4) 反映: 出力を `persona/` 直下に上書き

メモ
- スニペット抽出は 400–1200 文字の段落/見出し単位。重複は自動抑制
- ファイル拡張子: .md/.txt/.json（設定で変更可）
- 大量更新時はバッチで（数千行超はサンプル抽出/頻出パターン優先）

## ウォッチャーによる半自動反映
- 監視実行（編集/差分を検出して“貼り付け用バンドル”を自動生成）
  - 一度だけ: `python 99.共通/persona/auto/watch_persona.py --oneshot --edits --delta`
  - 常時監視: `python 99.共通/persona/auto/watch_persona.py --interval 30`
- 生成物
  - `99.共通/persona/auto/out/<timestamp>_edits_bundle.md`（edits反映用）
  - `99.共通/persona/auto/out/<timestamp>_delta_bundle.md`（差分反映用）
- 使い方
  - 生成されたバンドル.mdをClaude Codeにそのまま貼り付け→出力された更新版を `99.共通/persona/` に上書き
