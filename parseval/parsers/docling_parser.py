from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions
from docling.datamodel.document import ConversionResult
from docling.datamodel.base_models import InputFormat, Table, ConversionStatus, Page
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling_core.types.doc import PictureItem, TableItem, TextItem, DoclingDocument
import pandas as pd
import json
import os
from PIL import Image
import numpy as np
from typing import Union, List, Generator


class DoclingPDFParser:
    """
    Parse a PDF file using the Docling Parser
    """

    def __init__(self):

        # pipeline_options = PdfPipelineOptions()
        # pipeline_options.do_ocr=False
        # pipeline_options.do_table_structure=True
        # pipeline_options.table_structure_options.do_cell_matching = False


        self.metadata = {
            "tables": [],
            "images": [],
            "texts": []
        }

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



    def parse_and_export(self, paths: Union[str, List[str]], **kwargs):
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
            pipeline_options.generate_table_images = kwargs.get("generate_table_images", False)
            
            # Set backend
            backend = kwargs.get("backend", DoclingParseDocumentBackend())

            # Initialize the Docling Parser
            self.__initialize_docling(pipeline_options, backend)


        # Parse the document using the Docling Parser. This will return a generator of ConversionResult objects
        for result in self.parse_document(paths, **kwargs):
            if result.status == ConversionStatus.SUCCESS:
                self.__export_result(result.document, result.pages)
            
            else:
                raise ValueError(f"Failed to parse the document: {result.errors}")

        

    def __export_result(self, document: DoclingDocument, pages: List[Page]):
        """
        Export the parsed results to the output directory.
        """
        # Export the tables


        # self.output_dir = os.path.splitext(self.path)[0]  # Use the PDF filename to create an output folder
        # if not os.path.exists(self.output_dir):
        #     os.makedirs(self.output_dir)
        



   
