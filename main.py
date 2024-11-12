import json
from parseval.core import PDFParsingPipeline


input_files = "data/test/input_files.json"
with open(input_files, "r") as f:
    input_files = json.load(f)

output_dir = "data/test/output"


if __name__ == "__main__":
    pipeline = PDFParsingPipeline()
    ground_truth = pipeline.get_ground_truth(input_files, output_dir)
    predictions = pipeline.get_parsed_text(input_files, output_dir)

    pipeline.evaluate_parser(ground_truth, predictions)


