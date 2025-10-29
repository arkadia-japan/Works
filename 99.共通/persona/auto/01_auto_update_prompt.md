# Claude Code: 人格スタイル自動アップデート用プロンプト

以下をClaude Codeに貼り、`delta_corpus.json` をアップロードして実行してください。新規/更新スニペットから "その人らしさ" を抽出し、`persona/analysis.json` と各ガイド（credo/voice/do_dont/boundaries/style_prompts）をマージ更新します。

---

```
あなたは人物スタイルの編集者/アーキビストです。目的は、差分スニペット（delta_corpus.json）を既存の analysis.json と各ガイド文書に統合し、“その人らしさ”の知識ベースを継続更新することです。誇大・断定・操作的手法は避け、根拠（引用/出典）と信頼度を付与します。

[入力]
- delta_corpus.json: {items:[{path,hash,snippets[]}...]}
- 既存: analysis.json / credo.md / voice_guide.md / do_dont.md / boundaries.md / style_prompts.md（この会話に貼付 or 要点のみ）

[出力]
- 1) updated_analysis.json（全体統合版。各主張に evidence[{quote,path,confidence}]≥2件）
- 2) updated_credo.md / updated_voice_guide.md / updated_do_dont.md / updated_boundaries.md / updated_style_prompts.md
- 3) changes.md（何をどこに、なぜ追加/修正したか。重複統合/矛盾解消のメモ）

[手順]
1) スニペットの内容を以下の観点で抽出:
- 価値観/信念/世界観/原則（If–Then）/判断ヒューリスティック
- 言い回し/比喩/語彙/レトリック/禁則
- 境界線/倫理カード/対象・対象外
- KPI/メトリクス/1st fold/チェックリスト/決定木 等

2) 既存 analysis.json にマージ
- 重複統合、表現の正規化、信頼度のスコアリング（0.6=仮、0.8=強い、0.9=中核）
- 矛盾は “tensions” に追加し、解釈または優先度を付与

3) ガイドの反映
- credo/voice/do_dont/boundaries/style_prompts に、抽出内容を要点で追加
- 文量過多は避け、モバイル可読（見出し≤28/CTA≤12）を維持

4) コンプラ
- 結果保証や操作的指南は除去/言い換え。条件/出典/レンジを併記

[品質チェック]
- evidence_alignment / operationality / coherence / safety / clarity を各10点で自己採点し、改善3か所を反映してから納品
```

---

実行手順（例）
1) `python persona/auto/sync_persona.py` で差分抽出
2) `delta_corpus.json` をアップロードし、本プロンプトで更新版を生成
3) 出力ファイルを `persona/` 直下に上書き

