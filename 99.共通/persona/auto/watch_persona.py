#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
watch_persona.py

目的:
- edits.md の更新や、コンテンツ差分（delta_corpus.json）を検知して、
  Claude Code に貼り付けるだけで反映できる “バンドルMarkdown” を自動生成します。

使い方:
- 一度だけ生成:  python 99.共通/persona/auto/watch_persona.py --oneshot --edits --delta
- 常時監視:      python 99.共通/persona/auto/watch_persona.py --interval 30

出力:
- 99.共通/persona/auto/out/<timestamp>_edits_bundle.md
- 99.共通/persona/auto/out/<timestamp>_delta_bundle.md
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTO = ROOT/"auto"
OUT = AUTO/"out"

GUIDES_DIR = ROOT
EDITS = AUTO/"edits.md"
PROMPT_EDITS = AUTO/"02_edits_to_guides_prompt.md"
PROMPT_DELTA = AUTO/"01_auto_update_prompt.md"
DELTA_JSON = AUTO/"delta_corpus.json"

GUIDE_FILES = [
    (GUIDES_DIR/"analysis.json", "analysis.json"),
    (GUIDES_DIR/"credo.md", "credo.md"),
    (GUIDES_DIR/"voice_guide.md", "voice_guide.md"),
    (GUIDES_DIR/"do_dont.md", "do_dont.md"),
    (GUIDES_DIR/"boundaries.md", "boundaries.md"),
    (GUIDES_DIR/"style_prompts.md", "style_prompts.md"),
]

def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding='utf-8')
    except Exception:
        return ""

def now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def bundle_edits():
    prompt = read_text(PROMPT_EDITS)
    edits = read_text(EDITS)
    if not prompt or not edits:
        return None
    out = []
    out.append(prompt.strip())
    out.append("\n---\n")
    out.append("```markdown\n# edits.md\n\n" + edits.strip() + "\n```\n")
    for p, name in GUIDE_FILES:
        body = read_text(p)
        if not body:
            continue
        fence = "json" if name.endswith('.json') else "markdown"
        out.append(f"```{fence}\n# {name}\n\n{body.strip()}\n```\n")
    bundle = "".join(out)
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT/f"{now_tag()}_edits_bundle.md"
    out_path.write_text(bundle, encoding='utf-8')
    return out_path

def bundle_delta():
    prompt = read_text(PROMPT_DELTA)
    delta = read_text(DELTA_JSON)
    if not prompt or not delta:
        return None
    # 簡易チェック: items が 0 の場合は生成しない
    try:
        dj = json.loads(delta)
        if not dj.get('items'):
            return None
        if len(dj.get('items', [])) == 0:
            return None
    except Exception:
        pass
    out = []
    out.append(prompt.strip())
    out.append("\n---\n")
    out.append("```json\n" + delta.strip() + "\n```\n")
    OUT.mkdir(parents=True, exist_ok=True)
    out_path = OUT/f"{now_tag()}_delta_bundle.md"
    out_path.write_text("".join(out), encoding='utf-8')
    return out_path

def mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except Exception:
        return 0.0

def run_sync_delta():
    # 依存関係なく実行するため、同一プロセスで import せずにサブプロセス実行
    import subprocess, sys
    cmd = [sys.executable, str(AUTO/"sync_persona.py")]
    try:
        subprocess.run(cmd, check=False)
    except Exception:
        pass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=0, help="監視頻度(秒)。0なら監視せず1回実行")
    ap.add_argument("--oneshot", action='store_true', help="一度だけバンドル生成")
    ap.add_argument("--edits", action='store_true', help="editsバンドルを生成")
    ap.add_argument("--delta", action='store_true', help="deltaバンドルを生成（syncも実行）")
    args = ap.parse_args()

    if args.oneshot:
        paths = []
        if args.delta:
            run_sync_delta()
            p = bundle_delta()
            if p:
                paths.append(p)
        if args.edits:
            p = bundle_edits()
            if p:
                paths.append(p)
        if paths:
            print("generated:")
            for p in paths:
                print(" -", p)
        else:
            print("no bundle generated")
        return

    # watch mode
    last_edits_mtime = mtime(EDITS)
    last_delta_count = None
    while True:
        # edits 監視
        cur_m = mtime(EDITS)
        if cur_m and cur_m != last_edits_mtime:
            p = bundle_edits()
            if p:
                print("edits bundle:", p)
            last_edits_mtime = cur_m
        # delta 監視（sync実行→差分があればバンドル）
        run_sync_delta()
        try:
            dj = json.loads(read_text(DELTA_JSON) or '{}')
            cur_cnt = len(dj.get('items', []))
        except Exception:
            cur_cnt = 0
        if cur_cnt and cur_cnt != last_delta_count:
            p = bundle_delta()
            if p:
                print("delta bundle:", p)
            last_delta_count = cur_cnt

        time.sleep(max(args.interval, 30) if args.interval else 30)

if __name__ == "__main__":
    main()

