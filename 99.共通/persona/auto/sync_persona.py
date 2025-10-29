#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
差分収集スクリプト:
- 監視ルート配下の .md/.txt/.json を走査
- 前回ハッシュと比較し、新規/更新ファイルを抽出
- 段落/見出しベースで 400–1200 文字のスニペットに分割
- persona/auto/delta_corpus.json に保存
- インデックスを persona/.persona_index.json に保存
"""

import json, re, hashlib, os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
AUTO_DIR = ROOT/"auto"
INDEX_PATH = ROOT/".persona_index.json"
CONFIG_PATH = AUTO_DIR/"00_config.json"
DELTA_PATH = AUTO_DIR/"delta_corpus.json"

def load_json(p, default):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

def norm_text(t: str) -> str:
    t = t.replace('\r\n','\n').replace('\r','\n')
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()

def hash_text(t: str) -> str:
    return hashlib.sha1(t.encode('utf-8', errors='ignore')).hexdigest()

def should_exclude(path: Path, excludes):
    from fnmatch import fnmatch
    s = str(path)
    return any(fnmatch(s, pat) for pat in excludes)

def iter_files(root: Path, includes, excludes):
    from fnmatch import fnmatch
    for inc in includes:
        for p in root.rglob("*"):
            if p.is_file() and fnmatch(str(p), inc) and not should_exclude(p, excludes):
                yield p

def split_snippets(text: str, min_chars: int, max_chars: int):
    # 優先: 見出し/段落で切る
    blocks = re.split(r"\n(?=#+\s)|\n\n+", text)
    snippets = []
    buf = ""
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if len(b) >= min_chars and len(b) <= max_chars:
            snippets.append(b)
        else:
            buf += ("\n\n" if buf else "") + b
            if len(buf) >= min_chars:
                snippets.append(buf[:max_chars])
                buf = ""
    if buf:
        snippets.append(buf[:max_chars])
    # 先頭重複を減らす
    uniq = []
    seen = set()
    for s in snippets:
        key = hash_text(s[:200])
        if key not in seen:
            seen.add(key)
            uniq.append(s)
    return uniq[:50]

def main():
    cfg = load_json(CONFIG_PATH, {})
    roots = [Path(r) for r in cfg.get("roots", [])]
    includes = cfg.get("include_patterns", ["**/*.md", "**/*.txt", "**/*.json"])
    excludes = cfg.get("exclude_patterns", [])
    sn = cfg.get("snippet", {"min_chars": 400, "max_chars": 1200})

    index = load_json(INDEX_PATH, {})
    changed = []

    for root in roots:
        if not root.exists():
            continue
        for f in iter_files(root, includes, excludes):
            try:
                raw = f.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                continue
            text = norm_text(raw)
            h = hash_text(text)
            rec = index.get(str(f))
            if rec and rec.get('hash') == h:
                continue
            snippets = split_snippets(text, sn.get('min_chars',400), sn.get('max_chars',1200))
            changed.append({
                "path": str(f),
                "hash": h,
                "snippets": snippets
            })
            index[str(f)] = {"hash": h, "ts": datetime.utcnow().isoformat()}

    out = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_changed_files": len(changed),
        "items": changed
    }
    save_json(DELTA_PATH, out)
    save_json(INDEX_PATH, index)
    print(f"changed files: {len(changed)} -> {DELTA_PATH}")

if __name__ == "__main__":
    main()

