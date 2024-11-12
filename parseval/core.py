from parseval.crawl import WebsiteCrawler
from parseval.parse import PDFParser, HTMLParser
from parseval.parsers.schema import ParserOutput
from parseval.evaluate import EvaluateParser
from typing import List, Dict, Tuple
import json


CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

class PDFParsingPipeline:
    pdf_parser: PDFParser
    html_parser: HTMLParser
    crawler: WebsiteCrawler

    def __init__(
            self, 
            pdf_parser: str = 'pymupdf', 
            html_parser: str = 'html2text'
            ):
        
        self.pdf_parser = PDFParser(parser=pdf_parser)
        self.html_parser = HTMLParser(parser=html_parser)
        self.crawler = WebsiteCrawler(CHROME_PATH)

    
    def get_html_contents(
            self, 
            input_files: List[Dict],
            output_dir: str
            ) -> Tuple[List[str], List[str], List[Dict]]:
        
        html_paths: List[str] = []
        html_contents: List[str] = []
        metadatas: List[Dict] = []

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
                metadata = self.crawler.get_meta_data()

           
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
                        metadata = json.load(f)
                
                except FileNotFoundError:
                    raise FileNotFoundError(f"Metadata file not found at {metadata_path}")
                    

            
            html_paths.append(html_filepath)
            html_contents.append(html_content)
            metadatas.append(metadata)

        return html_paths, html_contents, metadatas


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
        
        parsing_outputs: List[ParserOutput] = self.pdf_parser.run(pdf_paths, modalities=modalities, **pdf_parsing_options)
        return [output.text for output in parsing_outputs]


    def get_ground_truth(
            self,
            input_files: List[Dict],
            output_dir: str,
            html_parsing_options: Dict = {},
            ) -> List[str]:
        
        # For now, we use only the text modality
        _, html_contents, _ = self.get_html_contents(input_files, output_dir)

        ground_truths: List[str] = []
        for html_content in html_contents:
            output = self.html_parser.run(html_content, **html_parsing_options)
            ground_truths.append(output)


        return ground_truths


    

    def evaluate_parser(
            self,
            ground_truths: List[str],
            parsing_outputs: List[str],
            evaluation_method: str = 'lcs',
            ) -> List[Dict]:
        
        pass
