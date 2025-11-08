#!/usr/bin/env python3
"""
DocxファイルをMarkdownに変換するスクリプト
"""

import os
import sys
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

def convert_paragraph_to_markdown(para):
    """段落をMarkdownに変換"""
    text = para.text.strip()
    if not text:
        return ""

    # 見出しレベルを判定
    if para.style.name.startswith('Heading'):
        level = para.style.name.replace('Heading ', '')
        if level.isdigit():
            return f"{'#' * int(level)} {text}\n"

    # リスト項目
    if para.style.name.startswith('List'):
        return f"- {text}\n"

    # 太字やイタリックの処理
    md_text = ""
    for run in para.runs:
        run_text = run.text
        if run.bold and run.italic:
            run_text = f"***{run_text}***"
        elif run.bold:
            run_text = f"**{run_text}**"
        elif run.italic:
            run_text = f"*{run_text}*"
        md_text += run_text

    return md_text + "\n"

def convert_table_to_markdown(table):
    """テーブルをMarkdownに変換"""
    md_table = []

    # ヘッダー行
    if len(table.rows) > 0:
        headers = []
        for cell in table.rows[0].cells:
            headers.append(cell.text.strip())
        md_table.append("| " + " | ".join(headers) + " |")
        md_table.append("| " + " | ".join(["---"] * len(headers)) + " |")

        # データ行
        for row in table.rows[1:]:
            cells = []
            for cell in row.cells:
                cells.append(cell.text.strip())
            md_table.append("| " + " | ".join(cells) + " |")

    return "\n".join(md_table) + "\n\n"

def convert_docx_to_markdown(docx_path, md_path):
    """DocxファイルをMarkdownに変換"""
    try:
        doc = Document(docx_path)
        markdown_content = []

        print(f"変換中: {docx_path} -> {md_path}")

        # ドキュメントの各要素を処理
        for element in doc.element.body:
            if isinstance(element, CT_P):
                # 段落
                para = Paragraph(element, doc)
                md_para = convert_paragraph_to_markdown(para)
                if md_para:
                    markdown_content.append(md_para)
            elif isinstance(element, CT_Tbl):
                # テーブル
                table = Table(element, doc)
                md_table = convert_table_to_markdown(table)
                markdown_content.append(md_table)

        # Markdownファイルに保存
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(markdown_content))

        print(f"✓ 変換完了: {md_path}")
        return True

    except Exception as e:
        print(f"✗ エラー: {docx_path} - {str(e)}")
        return False

def main():
    # 変換するディレクトリ
    source_dir = "恋愛コンサル スタッフ研修"

    if not os.path.exists(source_dir):
        print(f"エラー: ディレクトリが見つかりません: {source_dir}")
        sys.exit(1)

    # ディレクトリ内のすべてのDocxファイルを検索
    docx_files = [f for f in os.listdir(source_dir) if f.endswith('.docx')]

    if not docx_files:
        print(f"エラー: Docxファイルが見つかりません: {source_dir}")
        sys.exit(1)

    print(f"\n{len(docx_files)}個のDocxファイルを変換します\n")

    success_count = 0
    for docx_file in docx_files:
        docx_path = os.path.join(source_dir, docx_file)
        md_file = docx_file.replace('.docx', '.md')
        md_path = os.path.join(source_dir, md_file)

        if convert_docx_to_markdown(docx_path, md_path):
            success_count += 1

    print(f"\n変換完了: {success_count}/{len(docx_files)} ファイル")

if __name__ == "__main__":
    main()
