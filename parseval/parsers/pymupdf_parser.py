import fitz  # PyMuPDF
import pandas as pd
from PIL import Image
from typing import Union, List, Generator, Dict, Tuple
from io import BytesIO
from .schema import ParserOutput
from fitz import Page

class PyMuPDFParser:
    """
    Parse a PDF file using PyMuPDF
    """

    def __init__(self):
        self.data = []
        self.embed_images = True

    def parse_document(self, paths : Union[str, List[str]]) -> Generator[Dict, None, None]:
        """
        Parse the given document and return the parsed result as a generator.
        """
        for path in paths:
            doc = fitz.open(path)
            texts = []
            images = []
            tables = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                txt = page.get_text("text")
                tb = self._extract_tables(page)
                img = self._extract_images(page) if self.embed_images else []
                
                texts.append(txt)
                # tables.append(tb)
                images.extend(img)
            
            texts = "\n".join(texts)
            yield {
                "text": texts,
                "tables": tables,
                "images": images
            }

    def parse_and_export(self, paths : Union[str, List[str]]) -> List[ParserOutput]:
        """
        Parse the given document and export the parsed results.
        """
        if isinstance(paths, str):
            paths = [paths]
        
        for parsed_result in self.parse_document(paths):
            output = ParserOutput(
                text = parsed_result["text"],
                tables = parsed_result["tables"],
                images = parsed_result["images"]
            )
            self.data.append(output)

        return self.data

    def _extract_images(self, page: Page) -> List[Dict]:
        """
        Extract images from a page and return as a list of dictionaries with image and caption data.
        """
        images = []
        for img in page.get_images(full=True):
            xref = img[0]  # xref is the first element in the tuple returned by get_images
            base_image = page.parent.extract_image(xref)  # Extract the image with the xref
            img_data = BytesIO(base_image["image"])
            image = Image.open(img_data).convert('RGB')
            images.append({"image": image})
        return images

    def _extract_tables(self, page: Page) -> List[Dict]:
        """
        Placeholder for table extraction. PyMuPDF does not have built-in table extraction.
        """
        # Assuming any custom table extraction logic here.
        # It can use text layout or coordinate-based heuristics, or integrate other table extraction libraries
        tables = []  # Populate this with actual table extraction if needed
        return tables
