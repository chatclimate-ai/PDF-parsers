from .parsers.docling_parser import DoclingPDFParser
from .parsers.llama_parser import LlamaPDFParser
from .parsers.pymupdf_parser import PyMuPDFParser
from typing import Literal, List, Union
from .parsers.schema import ParserOutput

import html2markdown
import html2text
import markdownify



class PDFParser:
    def __init__(
            self, 
            parser: Literal["docling", "llama", "pymupdf"] = "docling"
            ):
        
        if parser == "docling":
            self.parser = DoclingPDFParser()
        elif parser == "llama":
            self.parser = LlamaPDFParser()
        elif parser == "pymupdf":
            self.parser = PyMuPDFParser()
        else:
            raise ValueError("Invalid parser specified. Please use 'docling' or 'llama'.")
        
        
    def run(
            self, 
            pdf_path: Union[str, List[str]],
            modalities : List[str] = ["text", "tables", "images"],
            **kwargs
            ) -> List[ParserOutput]:
        """
        Run the PDF parser on the given PDF file.
        """
        
        outputs = self.parser.parse_and_export(pdf_path, modalities, **kwargs)

        return outputs


class HTMLParser:
    def __init__(
            self,
            parser: Literal["markdownify", "html2markdown", "html2text"] = "markdownify"
            ):
        
        self.parser = parser

    def run(
            self,
            html_content: str,
            **kwargs
            ) -> str:
        """
        Run the HTML parser on the given HTML content.
        """
        markdown_content = ""

        if self.parser == "markdownify":
            markdown_content = markdownify.markdownify(html_content, **kwargs)
        elif self.parser == "html2markdown":
            markdown_content = html2markdown.convert(html_content)
        elif self.parser == "html2text":
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            h.ignore_emphasis = True
            h.ignore_tables = True
            markdown_content = h.handle(html_content)
            # markdown_content = html2text.html2text(html_content, **kwargs)
        else:
            raise ValueError("Invalid parser specified. Please use 'markdownify', 'html2markdown' or 'html2text'.")
        
        return markdown_content


