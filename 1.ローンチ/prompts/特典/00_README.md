# ローンチ特典用 プロンプト集 README

このフォルダは、無料個別相談の参加特典（PDF/動画/GPTs）と申込LP・告知資産を、Claude Codeで半自動生成・改善するためのプロンプト集です。各ファイルをClaudeに貼り付け、変数を置換して実行してください。

- 想定ユースケース: 広告/SNS → メルマガ・LINE → ローンチ動画/特典配布 → 申込LP → Zoom無料個別 → 恋愛コンサル販売
- 表現方針: 誇大・断定の禁止、根拠/条件/出典の明示、倫理と相手の尊重を最優先

## 収録ファイル
- `01_bonus_generation_prompt.md` 特典（PDF/動画/GPTs）生成
- `02_multi_format_master_prompt.md` マルチ形式（PDF/動画/マインドマップ/GPTs）一括生成
- `03_auto_eval_improve_prompt.md` 自動評価→修正→再評価ループ
- `04_offer_lp_prompt.md` 申込LP（特典訴求強化）生成
- `05_email_line_assets_prompt.md` メール/LINE/LP/SNS 告知資産生成
- `06_gpts_spec_prompt.md` GPTs仕様（system/instructions/guardrails）生成

## 共通変数（必要に応じて置換）
- `{FOLDERS}`: 参照フォルダ配列（例: ["/mnt/c/Users/yoona/1.Works/..."]）
- `{OFFER_URL}`: 無料個別申込みURL
- `{DEADLINE}`: 締切（例: 2025-11-30 23:59）
- `{BRAND_TONE}`: 口調（例: 専門的・フレンドリー・実行優先）
- `{COMPLIANCE_NOTES}`: コンプラ/NG表現（断定NG/医療・金融不可 など）
- `{FORMAT_PREF?}`: 生成形式の指定（pdf|video|mindmap|gpts|auto）
- `{TARGETS}`: 評価対象ファイル（例: ["ebook.md"]) 
- `{MIN_SCORE}` `{MAX_ITERS}`: 自動改善の閾値/反復回数

## 使い方（推奨フロー）
1) `01_bonus_generation_prompt.md` で特典の初稿を生成（PDF/動画/GPTs）
2) `02_multi_format_master_prompt.md` でマルチ成果物を同時生成
3) `03_auto_eval_improve_prompt.md` で評価→修正→再評価を自動化
4) `04_offer_lp_prompt.md` で申込LP（特典訴求強化）を生成
5) `05_email_line_assets_prompt.md` で告知資産を作成
6) 必要に応じ `06_gpts_spec_prompt.md` でGPTsアシスタントを構築

## PDF/動画への整形
- PDF: `pandoc ebook.md -o bonus.pdf` など、環境に応じて変換
- スライド: Marp対応（`slides.marp.md` → PDF/画像）

---
- バージョン: v1.0
- 変更管理: `03_auto_eval_improve_prompt.md`で生成されるレポートに沿って更新

