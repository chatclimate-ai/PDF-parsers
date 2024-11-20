import json
from parseval.core import PDFParsingPipeline


input_files = "data/test/v2/input_files.json"
with open(input_files, "r") as f:
    input_files = json.load(f)

output_dir = "data/test/v2"


if __name__ == "__main__":
    pipeline = PDFParsingPipeline(
        pdf_parser="pymupdf",
        html_parser="html2text",
        eval_method="lcs"

    )
    pipeline.run(
        input_files = input_files,
        output_dir = output_dir,
        pdf_parsing_options = {
            # "do_ocr":True,
            # "ocr_options":"easyocr",
            # "do_table_structure":True,
            # "do_cell_matching":False,
            # "tableformer_mode":"ACCURATE",
            # "images_scale":1.0,
            # "generate_page_images":False,
            # "generate_picture_images":False,
            # "generate_table_images":False,
            # "backend":"docling",
            # "embed_images":False
        },
        html_parsing_options = {
            "heading_style":"ATX"
        },
        # crawler_options = {
        #     "use_screenshot_method":True
        # },
        evaluation_options = {
            "step_size":5,
            "window_size":100,
            "threshold":0.8,
            "preprocess":True,
        }
        )


