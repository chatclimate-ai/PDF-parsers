from parseval.crawl import WebsiteCrawler
from parseval.parse import PDFParser, HTMLParser
from parseval.schemas import GroundTruth, Predictions, Metadata
from parseval.evaluate import ParserMetrics
from typing import List, Dict
import json


CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

class PDFParsingPipeline:
    pdf_parser: PDFParser
    html_parser: HTMLParser
    crawler: WebsiteCrawler
    evaluator: ParserMetrics

    def __init__(
            self, 
            pdf_parser: str = 'pymupdf', 
            html_parser: str = 'html2text',
            eval_method: str = 'lcs'
            ):
        
        self.pdf_parser = PDFParser(parser=pdf_parser)
        self.html_parser = HTMLParser(parser=html_parser)
        self.crawler = WebsiteCrawler(CHROME_PATH)
        self.evaluator = ParserMetrics(method=eval_method)

    
    def get_html_contents(
            self, 
            input_files: List[Dict],
            output_dir: str
            ) -> GroundTruth:
        
        html_paths: List[str] = []
        html_contents: List[str] = []
        metadatas: List[Metadata] = []

        for file_data in input_files:
            file_path: str = file_data['file_path']
            
            # if it's not a pdf (url), crawl the website and save the html content and metadata
            if not file_path.endswith(".pdf"):
                self.crawler.run(
                    url = file_path,
                    output_dir = output_dir,
                    convert_to_html=True,
                )
                html_filepath = self.crawler.get_html_filepath()
                html_content = self.crawler.get_html_content()
                metadata: Metadata = self.crawler.get_meta_data()

           
            else:
                try:
                    html_filepath = file_path.replace('.pdf', '.html')
                    with open(html_filepath, "r") as f:
                        html_content = f.read()
                
                except FileNotFoundError:
                    raise FileNotFoundError(f"HTML file not found at {html_filepath}")
                
                try:
                    metadata_path = html_filepath.split('/')[:-1] + ['metadata.json']
                    metadata_path = '/'.join(metadata_path)
                    with open(metadata_path, "r") as f:
                        metadata: Metadata = json.load(f)
                
                except FileNotFoundError:
                    raise FileNotFoundError(f"Metadata file not found at {metadata_path}")
                    

            
            html_paths.append(html_filepath)
            html_contents.append(html_content)
            metadatas.append(metadata)

        return GroundTruth(html_paths=html_paths, html_contents=html_contents, metadatas=metadatas)


    def get_parsed_text(
            self, 
            input_files: List[Dict],
            output_dir: str,
            modalities: List[str] = ['text'],
            pdf_parsing_options: Dict = {},
            crawler_options: Dict = {}
            ) -> List[str]:
        
        pdf_paths = []
        for file_data in input_files:
            file_path: str = file_data['file_path']
            
            # if it's not a pdf (url), crawl the website and save the html content and metadata
            if not file_path.endswith(".pdf"):
                self.crawler.run(
                    url = file_path,
                    output_dir = output_dir,
                    convert_to_pdf=True,
                    **crawler_options
                )
                pdf_filepath = self.crawler.get_pdf_output_path()
                
            else:
                pdf_filepath = file_path
            

            pdf_paths.append(pdf_filepath)
        
        parsing_outputs: Predictions = self.pdf_parser.run(pdf_paths, modalities=modalities, **pdf_parsing_options)

        # TODO: Remove table md from the text before evaluation, evaluate only the text and the tables separately

        return parsing_outputs


    def get_ground_truth(
            self,
            input_files: List[Dict],
            output_dir: str,
            html_parsing_options: Dict = {},
            ) -> GroundTruth:
        
        # For now, we use only the text modality
        ground_truth= self.get_html_contents(input_files, output_dir)

        for i, html_content in enumerate(ground_truth.html_contents):
            output = self.html_parser.run(html_content, **html_parsing_options)
            ground_truth.html_contents[i] = output

        return ground_truth


    

    def evaluate(
            self,
            ground_truths: GroundTruth,
            parsing_outputs: Predictions,
            output_dir: str,
            evaluation_options: Dict = {}
            ) -> List[Dict]:
        

        # Evaluate the parser text output only for now
        self.evaluator.evaluate_text(ground_truths, parsing_outputs, **evaluation_options)
        self.evaluator.save_evaluation(output_dir)
        self.evaluator.save_aggregation(output_dir)


    
    def run(
            self,
            input_files: List[Dict],
            output_dir: str,
            pdf_parsing_options: Dict = {},
            html_parsing_options: Dict = {},
            crawler_options: Dict = {},
            evaluation_options: Dict = {}
            ) -> None:
        
        ground_truth = self.get_ground_truth(input_files, output_dir, html_parsing_options)
        parsing_outputs = self.get_parsed_text(input_files, output_dir, pdf_parsing_options, crawler_options)

        self.evaluate(ground_truth, parsing_outputs, output_dir, evaluation_options)

        return None




    
    
