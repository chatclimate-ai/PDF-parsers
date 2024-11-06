from .parsers.docling_parser import DoclingPDFParser



class PDFParser:
    def __init__(self):
        self.parser = DoclingPDFParser()
        
        
    def run(self, pdf_path: str, **kwargs):
        """
        Run the PDF parser on the given PDF file.
        """
        
        self.parser.parse_and_export(pdf_path, **kwargs)

        text_md = self.parser.data[0]["texts"]
        tables = self.parser.data[0]["tables"]
        images = self.parser.data[0]["images"]

        return text_md, tables, images

