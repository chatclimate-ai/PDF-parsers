import google.generativeai as genai
from typing import Generator, List, Union, Dict
import fitz
from PIL import Image
import io
from .schema import ParserOutput
import pandas as pd
import os

class GeminiPDFParser:
    def __init__(self, api_key: str):
        self.initialized = False
        self.api_key = api_key

    def __initialize_gemini(self, **kwargs) -> None:
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro-vision')
            self.initialized = True
        except Exception as e:
            raise ValueError(f"Error initializing Gemini: {e}")

    def parse_and_export(
            self,
            paths: Union[str, List[str]],
            modalities: List[str] = ["text", "tables", "images"],
            **kwargs
            ) -> List[ParserOutput]:
        
        if not self.initialized:
            self.__initialize_gemini(**kwargs)

        if isinstance(paths, str):
            paths = [paths]

        outputs = []
        for path in paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File {path} not found")
            if not path.endswith('.pdf'):
                raise ValueError(f"File {path} must be PDF")

            doc = fitz.open(path)
            text = ""
            tables = []
            images = []

            for page in doc:
                if "text" in modalities or "tables" in modalities:
                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    response = self.model.generate_content([
                        "Extract following from this page (respond in JSON format):",
                        "1. All text content",
                        "2. Any tables (in markdown format)",
                        img
                    ])
                    
                    try:
                        result = response.text
                        # Parse JSON response and extract text/tables
                        # Add extracted content to text and tables lists
                        text += result.get("text", "") + "\n"
                        table_data = result.get("tables", [])
                        for table in table_data:
                            tables.append({
                                "table_md": table,
                                "table_df": pd.read_csv(io.StringIO(table))
                            })
                    except Exception as e:
                        print(f"Error processing page {page.number}: {e}")

                if "images" in modalities:
                    for img in page.get_images():
                        xref = img[0]
                        image = fitz.Pixmap(doc, xref)
                        pil_img = Image.frombytes("RGB", [image.width, image.height], image.samples)
                        images.append({"image": pil_img})

            outputs.append(ParserOutput(text=text, tables=tables, images=images))

        return outputs