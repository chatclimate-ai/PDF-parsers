from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions
from docling.datamodel.document import ConversionResult
from docling.datamodel.base_models import InputFormat, ConversionStatus
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling_core.types.doc import PictureItem, TableItem, ImageRefMode, DoclingDocument
import pandas as pd
from PIL import Image
from typing import Union, List, Generator, Dict, Tuple
from .schema import ParserOutput


class DoclingPDFParser:
    """
    Parse a PDF file using the Docling Parser
    """

    def __init__(self):
        self.data = []
        self.initialized = False

    def __initialize_docling(self, pipeline_options: PdfPipelineOptions, backend: Union[DoclingParseDocumentBackend, PyPdfiumDocumentBackend]) -> None:
        """
        Initialize the DocumentConverter with the given pipeline options and backend.

        :param pipeline_options: PdfPipelineOptions
            The pipeline options to use for parsing the document
        :param backend: Union[DoclingParseDocumentBackend, PyPdfiumDocumentBackend]
            The backend to use for parsing the document
        """
        self.converter = DocumentConverter(
            allowed_formats= [InputFormat.PDF],
            format_options= {
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options= pipeline_options,
                    backend= backend
                )
            }
        )

        self.initialized = True


    def parse_document(self, paths: Union[str, List[str]], **kwargs) -> Generator[ConversionResult, None, None]:
        """
        Parse the given document and return the parsed result.
        """
        if not self.initialized:
            raise ValueError ("The Docling Parser has not been initialized.")
        
        if isinstance(paths, str):
            paths = [paths]

        
        # yield self.converter.convert_all(paths, **kwargs) iterator
        yield from self.converter.convert_all(paths, **kwargs)



    def parse_and_export(self, paths: Union[str, List[str]], **kwargs) -> List[ParserOutput]:
        """
        Parse the given document and export the parsed results to the output directory.
        """
        if not self.initialized:
            # Set pipeline options
            pipeline_options = PdfPipelineOptions()

            # Set ocr options
            pipeline_options.do_ocr = kwargs.get("do_ocr", True)
            pipeline_options.ocr_options = kwargs.get("ocr_options", EasyOcrOptions(use_gpu=False, lang=["en"]))

            # Set table structure options
            pipeline_options.do_table_structure = kwargs.get("do_table_structure", True)
            pipeline_options.table_structure_options.do_cell_matching = kwargs.get("do_cell_matching", False)
            pipeline_options.table_structure_options.mode = kwargs.get("mode", "ACCURATE")

            # Set image options
            pipeline_options.images_scale = kwargs.get("images_scale", 1.0)
            pipeline_options.generate_page_images = kwargs.get("generate_page_images", False)
            pipeline_options.generate_picture_images = kwargs.get("generate_picture_images", True)
            pipeline_options.generate_table_images = kwargs.get("generate_table_images", True)
            
            # Set backend
            backend = kwargs.get("backend", DoclingParseDocumentBackend)

            self.embed_images = kwargs.get("embed_images", True)

            # Initialize the Docling Parser
            self.__initialize_docling(pipeline_options, backend)

            # pop the kwargs
            kwargs.pop("do_ocr", None)
            kwargs.pop("ocr_options", None)
            kwargs.pop("do_table_structure", None)
            kwargs.pop("do_cell_matching", None)
            kwargs.pop("mode", None)
            kwargs.pop("images_scale", None)
            kwargs.pop("generate_page_images", None)
            kwargs.pop("generate_picture_images", None)
            kwargs.pop("generate_table_images", None)
            kwargs.pop("backend", None)
            kwargs.pop("embed_images", None)

            


        # Parse the document using the Docling Parser. This will return a generator of ConversionResult objects
        for result in self.parse_document(paths, **kwargs):
            if result.status == ConversionStatus.SUCCESS:
                output = self.__export_result(result.document)
                file_name = result.document.name

                self.data.append(
                    ParserOutput(
                        file_name=file_name,
                        text=output.text,
                        tables=output.tables,
                        images=output.images
                    )
                )
            
            else:
                raise ValueError(f"Failed to parse the document: {result.errors}")

        return self.data
        

    def __export_result(self, document: DoclingDocument) -> ParserOutput:
        """
        Export the parsed results to the output directory.
        """
        if self.embed_images:
            text = document.export_to_markdown(
                image_mode=ImageRefMode.EMBEDDED,
            )
        
        else:
            text = document.export_to_markdown(
                image_mode=ImageRefMode.PLACEHOLDER,
            )

        tables = []
        images = []
        for item, _ in document.iterate_items():
            if isinstance(item, TableItem):
                table_md: str = item.export_to_markdown()
                table_df: pd.DataFrame = item.export_to_dataframe()
                table_img: Image.Image = item.image.pil_image

                caption = item.caption_text(document)


                tables.append({
                    "table_md": table_md,
                    "table_df": table_df,
                    "table_img": table_img,
                    "caption": caption
                })

            if isinstance(item, PictureItem):
                image: Image.Image = item.image.pil_image
                caption = item.caption_text(document)

                images.append({
                    "image": image,
                    "caption": caption
                })



        return ParserOutput(text=text, tables=tables, images=images)



# if __name__ == "__main__":
#     import os
#     import json
#     file_path = "data/coca-cola-business-and-sustainability-report-2018.pdf"


#     parser = DoclingPDFParser()
#     parser.parse_and_export(file_path)

#     print("Successfully parsed the document.")

#     file_name = parser.data[0]["file_name"]

#     output_dir = "output/docling_output"
#     os.makedirs(output_dir, exist_ok=True)
    
    
#     text_dir = f"{output_dir}/text"
#     os.makedirs(text_dir, exist_ok=True)

#     md = parser.data[0]["texts"]
#     with open(f"{text_dir}/{file_name}.md", "w") as f:
#         f.write(md)


#     tables_md_dir = f"{output_dir}/md_tables"
#     os.makedirs(tables_md_dir, exist_ok=True)

#     tables_csv_dir = f"{output_dir}/csv_tables"
#     os.makedirs(tables_csv_dir, exist_ok=True)

#     tables_img_dir = f"{output_dir}/img_tables"
#     os.makedirs(tables_img_dir, exist_ok=True)

#     tables = parser.data[0]["tables"]

#     for i, table in enumerate(tables):
#         table_md = table["table_md"]
#         table_df: pd.DataFrame = table["table_df"]
#         table_img: Image.Image = table["table_img"]
#         caption = table["caption"]

#         table_md = f"### {caption}\n\n" + table_md


#         with open(f"{tables_md_dir}/{file_name}_t{i}.md", "w") as f:
#             f.write(table_md)

#         table_df.to_csv(f"{tables_csv_dir}/{file_name}_t{i}.csv", index=False)

#         table_img.save(f"{tables_img_dir}/{file_name}_t{i}.png")


#     images_dir = f"{output_dir}/images"
#     os.makedirs(images_dir, exist_ok=True)

#     images = parser.data[0]["images"]
#     captions = []
#     for i, image in enumerate(images):
#         img: Image.Image = image["image"]
#         caption = image["caption"]


#         img.save(f"{images_dir}/{file_name}_i{i}.png")
#         captions.append(caption)
    
#     with open(f"{images_dir}/{file_name}_captions.json", "w") as f:
#         json.dump(captions, f, indent=4, ensure_ascii=False, default=str)
    
    
#     print("Data has been successfully exported to the output directory.")


#     # save the data to a json file
#     # import json
#     # with open("data.json", "w") as f:
#     #     json.dump(parser.data, f, indent=4)
    

  
        
