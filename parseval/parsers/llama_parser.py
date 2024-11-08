from llama_parse import LlamaParse
from llama_index.core.schema import Document, TextNode, ImageNode
import os
from typing import Generator, List, Union, Dict
import pandas as pd
from .schema import ParserOutput
import io
from PIL import Image



class LlamaPDFParser:
    def __init__(self):
        self.data: List[ParserOutput] = []
        self.initialized = False


    def __initialize_llama(self, **kwargs) -> None:
        """
        Initialize the LlamaParse converter with the given options.
        """
        try:
            self.converter = LlamaParse(
                api_key= os.environ.get("llama_parse_key"),
                show_progress = False,
                # split_by_page = False,
                # invalidate_cache=True,
                # do_not_cache=True,
                **kwargs
            )

            self.initialized = True
        
        except Exception as e:
            print(f"An error occurred: {e}")
            self.initialized = False
            exit(0)
    

    def parse_document(self, paths: Union[str, List[str]]) -> Generator[Dict, None, None]: # Document, None, None]:
        """
        Parse the given document and return the parsed result.
        """
        if not self.initialized:
            raise ValueError ("The Docling Parser has not been initialized.")
        
        if isinstance(paths, str):
            paths = [paths]

        
        for path in paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"The file {path} does not exist.")
            
            if not path.endswith(".pdf"):
                raise ValueError(f"The file {path} must be a PDF file.")
        
        document: List[Dict] = self.converter.get_json_result(paths)
        yield from document


    def parse_and_export(self, paths: Union[str, List[str]], **kwargs) -> List[ParserOutput]:
        if not self.initialized:
            language = kwargs.get("language", "en")
            result_type = kwargs.get("result_type", "markdown")
            continuous_mode = kwargs.get("continuous_mode", True)
            take_screenshot = kwargs.get("take_screenshot", False)
            disable_ocr = kwargs.get("disable_ocr", False)
            is_formatting_instruction = kwargs.get("is_formatting_instruction", False)

            self.__initialize_llama(
                language= language, 
                result_type= result_type,
                continuous_mode= continuous_mode,
                take_screenshot= take_screenshot,
                disable_ocr= disable_ocr,
                is_formatting_instruction= is_formatting_instruction
            )

        

        for result in self.parse_document(paths):
            output = self.__export_result(result)
            file_name = result["file_path"].split("/")[-1].split(".")[0]

            self.data.append(
                    ParserOutput(
                        file_name=file_name,
                        text=output.text,
                        tables=output.tables,
                        images=output.images
                    )
                )
        
        return self.data



    def __export_result(self, parsing_result: dict) -> ParserOutput:
        """
        Export the parsed result to the ParserOutput schema.
        """
        text = []
        tables = []

        pages: List[Dict] = parsing_result["pages"]

        for page in pages:
            page_text = page["text"]
            text.append(page_text)

            # for item in page["items"]:
            #     if item["type"] == "table":
            #         table_md = item["md"]
            #         table_df = pd.read_csv(io.StringIO(item["csv"]), sep=",")

            #         tables.append({
            #         "table_md": table_md,
            #         "table_df": table_df
            #         })  
            
        text = "\n".join(text)
        
        images = []
        # image_dicts = self.converter.get_images([parsing_result], download_path="llama2_images")

        # for img in image_dicts:
        #     image_path = img["path"]
        #     image = Image.open(image_path).convert("RGB")
        #     images.append({
        #             "image": image,
        #         })
            
        return ParserOutput(text=text, tables=tables, images=images)




if __name__ == "__main__":
    path = ["data/websites/adobe.pdf"] #, "data/multi-lingual/Scanned rockwool.pdf"]

    parser = LlamaPDFParser()
    parser.parse_and_export(path)
