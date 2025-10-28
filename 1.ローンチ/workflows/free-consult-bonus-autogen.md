version: "1.0"
name: "free-consult-bonus-autogen"
description: "無料個別相談の参加特典を自動生成し、評価・改善・自動格納まで実行するワークフロー"

# ==========
# パラメータ
# ==========
inputs:
  base_date:
    type: string
    default: "{{now:YYYY-MM-DD}}"
  human_review_enabled:
    type: boolean
    default: true     # falseにすると完全自動
  score_threshold:
    type: number
    default: 4.5
  max_revision_rounds:
    type: integer
    default: 3
  # 参照フォルダ
  concept_dir:
    type: string
    default: "/mnt/c/Users/yoona/1.Works/1.ローンチ/コンセプト"
  scripts_dir:
    type: string
    default: "/mnt/c/Users/yoona/1.Works/1.ローンチ/ローンチ台本"
  lp_dir:
    type: string
    default: "/mnt/c/Users/yoona/1.Works/1.ローンチ/ランディングページ"
  stepmail_dir:
    type: string
    default: "/mnt/c/Users/yoona/1.Works/1.ローンチ/ステップメール"
  youtube_dir:
    type: string
    default: "/mnt/c/Users/yoona/1.Works/3.YouTube/resources/My"

  # 出力フォルダ
  out_pdf_dir:
    type: string
    default: "/mnt/c/Users/yoona/1.Works/1.ローンチ/特典/PDF/"
  out_video_dir:
    type: string
    default: "/mnt/c/Users/yoona/1.Works/1.ローンチ/特典/動画/"
  out_gpts_dir:
    type: string
    default: "/mnt/c/Users/yoona/1.Works/1.ローンチ/特典/GPTs/"
  out_outline_dir:
    type: string
    default: "/mnt/c/Users/yoona/1.Works/1.ローンチ/特典/構成/"
  out_temp_dir:
    type: string
    default: "/mnt/c/Users/yoona/1.Works/1.ローンチ/特典/temp/"

# ==========
# ワークフロー
# ==========
steps:
  # 1) ソース読み込み・要約
  - id: read_sources
    name: "ReadSourceFiles"
    type: python
    code: |
      import os, glob, json
      def read_dir(d):
          paths = []
          for ext in ["**/*.md","**/*.txt","**/*.docx","**/*.pdf","**/*.json","**/*.yaml","**/*.yml"]:
              paths += glob.glob(os.path.join(d, ext), recursive=True)
          contents = []
          for p in paths[:60]:  # 上限（重い場合は増減）
              try:
                  if p.lower().endswith((".md",".txt",".json",".yaml",".yml")):
                      with open(p, "r", encoding="utf-8", errors="ignore") as f:
                          contents.append({"path": p, "text": f.read()[:12000]})
                  else:
                      # docx/pdfは簡易プレースホルダ（別途OCR・変換導入可能）
                      contents.append({"path": p, "text": f"[BINARY or PDF DOC PLACEHOLDER] {os.path.basename(p)}"})
              except Exception as e:
                  contents.append({"path": p, "text": f"[ERROR reading] {e}"})
          return contents

      data = {
        "concept": read_dir(inputs["concept_dir"]),
        "scripts": read_dir(inputs["scripts_dir"]),
        "lp": read_dir(inputs["lp_dir"]),
        "stepmail": read_dir(inputs["stepmail_dir"]),
        "youtube": read_dir(inputs["youtube_dir"]),
      }
      outputs = {"corpus": data}

  # 2) ネタ提案（3〜5案）
  - id: propose_ideas
    name: "ProposeIdeas"
    type: llm
    config:
      model: "gpt-5.1"   # Claude code側で互換モデルに置換可
      temperature: 0.7
    prompt: |
      あなたはDRMに特化したトップコンテンツプロデューサーです。
      目的：無料個別相談の申込み率を最大化する特典のネタ提案を行う。

      # 資料サマリ（抜粋）
      以下は社内資料の要旨です。重複・表現違いは統合して要点化してください。
      - コンセプト・ペルソナ:
      {{read_sources.corpus.concept}}
      - ローンチ台本:
      {{read_sources.corpus.scripts}}
      - LP:
      {{read_sources.corpus.lp}}
      - ステップメール:
      {{read_sources.corpus.stepmail}}
      - YouTube:
      {{read_sources.corpus.youtube}}

      # 要求
      ・参加特典の“切り口（テーマ）”を3〜5案
      ・各案に以下を添える：
        - 狙う感情トリガー（例：悔しさ→希望）
        - ベネフィット一言要約
        - 期待される効果（数行）
        - 推奨コンテンツ形式（PDF/動画/GPTsのいずれか、理由付き）
        - 想定タイトル案（3本）

      出力はMarkdownの箇条書きで簡潔に。

  # 3) 人間承認（ON時のみ）
  - id: pick_idea
    name: "PickIdea"
    if: "{{inputs.human_review_enabled == true}}"
    type: human
    description: "上のネタ提案から採用する案番号を指示してください（例：#1）。タイトル微修正や狙いの指定も可。"

  # 4) 自動選択（全自動モード）
  - id: auto_pick_idea
    name: "AutoPickIdea"
    if: "{{inputs.human_review_enabled == false}}"
    type: llm
    config:
      model: "gpt-5.1"
      temperature: 0.2
    prompt: |
      上のネタ提案から、最も「差別化・信頼醸成・保存価値」が高く、LP→無料相談へのCVに寄与しそうな案を1つ選び、
      「選定理由（3点）」「最終タイトル候補（1本）」を出力してください。
      以降はこの案で進めます。

  # 5) 構成（アウトライン）
  - id: outline
    name: "MakeOutline"
    type: llm
    config:
      model: "gpt-5.1"
      temperature: 0.5
    prompt: |
      あなたはDRM編集長です。選定したネタで特典のアウトラインを作成。
      章ごとに「目的・キーポイント・読者の反応」を付与し、所要時間/分量の目安も記述してください。
      また、PDF/動画/GPTsのどれで制作するか最終決定し、その理由も一言添えてください。

      【入力】
      ネタ提案:
      {{propose_ideas.output_text}}

      選定:
      {% if inputs.human_review_enabled %}
      {{pick_idea.output_text}}
      {% else %}
      {{auto_pick_idea.output_text}}
      {% endif %}

      【出力形式（Markdown）】
      - 最終タイトル:
      - 形式:
      - 想定読了/視聴時間:
      - 章立て:
        - 第1章: タイトル / 目的 / キーポイント / 想定反応 / 目安分量
        - 第2章: ...
      - 付録（チェックリスト/診断/テンプレ）

  # 6) 詳細ライティング（本文 or スライド or GPT設計）
  - id: drafting
    name: "DraftContent"
    type: llm
    config:
      model: "gpt-5.1"
      temperature: 0.7
    prompt: |
      あなたはハイコンバージョンのコピーライターです。
      以下の条件で本文（PDFなら本文、動画ならスライド＋ナレーション、GPTsならQ&A仕様）を作成。

      # トーン
      - カジュアル×知的、読者の痛みと希望に寄り添う
      - 感情と論理のバランス
      - 比喩は要所に
      - 「共感→発見→変化→行動」へ導く

      # 目的
      - 「この内容はすごい、続きは相談で」を自然に喚起
      - 「この人に相談したい」と感じさせる信頼
      - 保存版の実用性（何度も見返したくなる）

      # 入力（アウトライン）
      {{outline.output_text}}

      # 出力（形式に応じて）
      - 形式: PDF → 見出し/本文/図解指示/チェックリスト
      - 形式: 動画 → Slide N: 見出し / 箇条書き / ナレーション（読み上げ文） / B-roll・図示案
      - 形式: GPTs → セクション（想定質問カテゴリ）/ 質問リスト / 回答テンプレ（根拠・参照）

  # 7) 自動評価
  - id: evaluate
    name: "EvaluateContent"
    type: llm
    config:
      model: "gpt-5.1"
      temperature: 0.1
    prompt: |
      以下のコンテンツを3軸で5段階評価し、改善点を箇条書きで列挙してください。
      軸：①差別化 ②信頼醸成 ③保存価値
      出力はJSONで：
      {"scores":{"差別化":X,"信頼":Y,"保存価値":Z},"average":A,"improvements":["...","..."]}

      コンテンツ:
      {{drafting.output_text}}

  # 8) 改善ループ（必要なら最大N回）
  - id: maybe_revise
    name: "ReviseLoop"
    type: llm
    if: "{{evaluate.output_json.average < inputs.score_threshold and loop.index < inputs.max_revision_rounds}}"
    loop:
      count: "{{inputs.max_revision_rounds}}"
    config:
      model: "gpt-5.1"
      temperature: 0.6
    prompt: |
      以下の改善点をすべて反映して、コンテンツをリライトしてください。
      改変の意図を簡単に注記した後、完全版を再出力してください。

      改善点:
      {{evaluate.output_json.improvements}}

      直前の版:
      {{drafting.output_text}}

  # 9) 最終版の決定
  - id: finalize
    name: "Finalize"
    type: python
    code: |
      # 改善ループ有無で最終本文を選択
      final_text = """{{drafting.output_text}}"""
      try:
          # ループが走っていれば maybe_revise が最後に上書き
          revised = """{{maybe_revise.output_text}}""".strip()
          if revised:
              final_text = revised
      except Exception:
          pass
      outputs = {"final_text": final_text}

  # 10) 形式判定＆ファイル自動格納
  - id: save_file
    name: "SaveFile"
    type: python
    code: |
      import os, re, pathlib, json, textwrap, datetime

      base_date = inputs["base_date"]
      text = """{{finalize.final_text}}"""

      # 形式を抽出
      m = re.search(r"形式\s*:\s*(PDF|動画|GPTs)", text)
      content_type = m.group(1) if m else "PDF"

      # タイトル抽出
      mt = re.search(r"最終タイトル\s*:\s*(.+)", text)
      theme = (mt.group(1).strip() if mt else "特典").replace("/", "／")

      # 出力先と拡張子
      if content_type == "PDF":
          out_dir = inputs["out_pdf_dir"]
          ext = ".md"   # まずはMarkdown保存（PDF化は別タスクでOK）
      elif content_type == "動画":
          out_dir = inputs["out_video_dir"]
          ext = "_slide.md"
      elif content_type == "GPTs":
          out_dir = inputs["out_gpts_dir"]
          ext = "_gpt.md"
      else:
          out_dir = inputs["out_temp_dir"]
          ext = ".txt"

      pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
      filename = f"特典_{base_date}_{theme}{ext}"
      path = os.path.join(out_dir, filename)

      with open(path, "w", encoding="utf-8") as f:
          f.write(text)

      outputs = {"saved_path": path, "content_type": content_type, "filename": filename}

  # 11) ログ出力
  - id: log_summary
    name: "LogSummary"
    type: llm
    config:
      model: "gpt-5.1"
      temperature: 0.2
    prompt: |
      下記の保存結果をユーザーに短く報告してください。
      - 保存先: {{save_file.saved_path}}
      - 種別: {{save_file.content_type}}
      - ファイル名: {{save_file.filename}}

      末尾に「次にやること」を3つ、箇条書きで提案してください。
