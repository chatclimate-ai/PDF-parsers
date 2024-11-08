from parseval.crawl import WebsiteCrawler
import html2markdown
import html2text
import markdownify
from parseval.parse import PDFParser


CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
output_dir = 'data/finance'

# scraper = WebsiteCrawler(CHROME_PATH)


# # Scanned PDF
# scraper.run(
#         url = 'https://www.adobe.com/about-adobe.html',
#         output_dir = output_dir,
#         convert_to_pdf = True,
#         convert_to_html = True,
#         use_screenshot_method = False,
#         output_pdf_name = 'adobe_crawled.pdf',

#     )

pdf_file_path = "data/finance/2006-04-17_10-K_d10k.pdf" 
# "data/adobe/adobe_crawled.pdf"
# "data/adobe/adobe.pdf"
# scraper.pdf_output_path
# "data/finance/2006-04-17_10-K_d10k.pdf" 
# "data/arxiv/2404.12720v1.pdf" 
# html_filename = scraper.html_filename
# html_content = scraper.get_html_content()
# html_metadata = scraper.meta_data

print(f"PDF file path: {pdf_file_path}")
# Parse the PDF file to markdown with docling
# parser = PDFParser()
# output = parser.run(pdf_file_path, embed_images=False)[0]


html_filename = pdf_file_path.split('/')[-1].replace('.pdf', '.html')
# # save the text content to a file
# with open(f"{output_dir}/{html_filename.split('.')[0]}_docling.md", "w") as f:
#     f.write(output.text)


# Parse the PDF file to markdown with llama parse
parser = PDFParser(parser='pymupdf')
output = parser.run(pdf_file_path)[0]

# save the text content to a file
with open(f"{output_dir}/{html_filename.split('.')[0]}_pymupdf.md", "w") as f:
    f.write(output.text)

# exit()
# read the html content
# with open(f"{output_dir}/{html_filename}", "r") as f:
#     html_content = f.read()


# # Convert the HTML content to markdown
# markdown_content = html2markdown.convert(html_content)
# with open(f"{output_dir}/{html_filename.split('.')[0]}_html2md.md", "w") as f:
#     f.write(markdown_content)


# markdown_content = markdownify.markdownify(html_content, bullets="-")
# with open(f"{output_dir}/{html_filename.split('.')[0]}_markdownify.md", "w") as f:
#     f.write(markdown_content)


# markdown_content = html2text.html2text(html_content)
# with open(f"{output_dir}/{html_filename.split('.')[0]}_html2txt.md", "w") as f:
#     f.write(markdown_content)




