from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Dict, Optional
import pandas as pd
from PIL import Image

class ParserOutput(BaseModel):
    file_name: Optional[str] = Field(None, description="The name of the file.")
    text: str = Field(..., description="The parsed text from the document.")
    tables: List[Dict] = Field(..., description="The parsed tables from the document.")
    images: List[Dict] = Field(..., description="The parsed images from the document.")


    @field_validator('file_name')
    def validate_file_name(cls, file_name):
        if file_name is not None and not isinstance(file_name, str):
            raise ValueError("The 'file_name' key must be a string.")
        return file_name

    @field_validator('text')
    def validate_text(cls, text):
        if not isinstance(text, str):
            raise ValueError("The 'text' key must be a string.")
        return text

    @field_validator('tables')
    def validate_tables(cls, tables):
        if not tables:
            return tables
        for table in tables:
            if not isinstance(table, dict):
                raise ValueError("Each table must be a dictionary.")
            if "table_md" not in table or not isinstance(table["table_md"], str):
                raise ValueError("Each table must have a 'table_md' key of type str.")
            
            if "table_df" in table and not isinstance(table["table_df"], pd.DataFrame):
                raise ValueError("Each table that has a 'table_df' key must be a pandas DataFrame.")
            
            if "table_img" in table and not isinstance(table["table_img"], Image.Image):
                raise ValueError("Each table that has a 'table_img' key must be a PIL Image.")
            
            if "caption" in table and not isinstance(table["caption"], str):
                raise ValueError("Each table that has a 'caption' key must be a string.")
            
        return tables

    @field_validator('images')
    def validate_images(cls, images):
        if not images:
            return images
        
        for image in images:
            if not isinstance(image, dict):
                raise ValueError("Each image must be a dictionary.")
            if "image" not in image or not isinstance(image["image"], Image.Image):
                raise ValueError("Each image must have an 'image' key of type PIL Image.")
            if "caption" in image and not isinstance(image["caption"], str):
                raise ValueError("Each image that has a 'caption' key must be a string.")
        return images

    @model_validator(mode='after')
    def check_model_initialization(cls, values):
        if 'text' not in values:
            raise ValueError("The 'text' field is missing.")
        if 'tables' not in values or not isinstance(values['tables'], list):
            raise ValueError("The 'tables' field must be a list.")
        if 'images' not in values or not isinstance(values['images'], list):
            raise ValueError("The 'images' field must be a list.")
        return values
