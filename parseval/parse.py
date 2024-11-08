from .parsers.docling_parser import DoclingPDFParser
from .parsers.llama_parser import LlamaPDFParser
from typing import Literal, List, Union
from .parsers.schema import ParserOutput

class PDFParser:
    def __init__(self, parser: Literal["docling", "llama"] = "docling"):
        
        if parser == "docling":
            self.parser = DoclingPDFParser()
        elif parser == "llama":
            self.parser = LlamaPDFParser()
        else:
            raise ValueError("Invalid parser specified. Please use 'docling' or 'llama'.")
        
        
    def run(self, pdf_path: Union[str, List[str]], **kwargs) -> List[ParserOutput]:
        """
        Run the PDF parser on the given PDF file.
        """
        
        outputs = self.parser.parse_and_export(pdf_path, **kwargs)

        return outputs

