from docling.document_converter import DocumentConverter




# class DoclingParser:
#     """
#     Parse a PDF file using the Docling Parser
#     """

#     def __init__(self, path):
#         pass



source = "https://www.adobe.com/about-adobe.html"
converter = DocumentConverter()
result = converter.convert(source)

with open("output.md", "w") as f:
    f.write(result)
