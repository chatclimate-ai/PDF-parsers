import json
from parseval.core import PDFParsingPipeline
import toml


VERSION = "v5"


with open(f"data/test/{VERSION}/input_files.json", "r") as f:
    input_files = json.load(f)
output_dir = f"data/test/{VERSION}"

CONFIG = toml.load("config.toml")

if __name__ == "__main__":
    pipeline = PDFParsingPipeline(
        pdf_parser= CONFIG["tool"]["pdf_parser"]["name"],
        html_parser= CONFIG["tool"]["html_parser"]["name"],
        eval_method= CONFIG["tool"]["evaluation"]["name"]

    )
    pipeline.run(
        input_files = input_files,
        output_dir = output_dir,
        pdf_parsing_options = CONFIG["pdf_parser"][CONFIG["tool"]["pdf_parser"]["name"]],
        html_parsing_options = CONFIG["html_parser"][CONFIG["tool"]["html_parser"]["name"]],
        crawler_options = CONFIG["crawler"]["options"] if CONFIG["tool"]["crawler"]["use"] else {},
        evaluation_options = CONFIG["evaluation"]["options"]
        )
