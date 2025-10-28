docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True  # OCR機能を有効化
pipeline_options.do_table_structure = True  # 表構造認識を有効化

converter = DocumentConverter(
    format_options={
        "pdf": pipeline_options,
    }
)

result = converter.convert("complex_document.pdf")
markdown_content = result.document.export_to_markdown()
