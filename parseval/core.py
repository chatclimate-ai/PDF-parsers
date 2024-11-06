from parseval.crawl import WebsiteCrawler
import html2markdown
import html2text
import markdownify
import os
from parseval.parse import PDFParser


CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
output_dir = 'adobe_as_img'

scraper = WebsiteCrawler(CHROME_PATH)




scraper.run(
        url = 'https://www.adobe.com/about-adobe.html',
        output_dir = output_dir,
        convert_to_pdf = True,
        convert_to_html = True,
        use_screenshot_method = True,
        output_pdf_name = 'adobe.pdf',

    )

pdf_file_path = scraper.pdf_output_path
html_filename = scraper.html_filename
# Parse the PDF file
parser = PDFParser()
text_md, tables, images = parser.run(pdf_file_path)

# save the text content to a file
with open(f"{output_dir}/{html_filename.split('.')[0]}_parsed.md", "w") as f:
    f.write(text_md)


html_file_path = os.path.join(output_dir, html_filename)
html_content = scraper.get_html_content()
html_metadata = scraper.meta_data



markdown_content = html2markdown.convert(html_content)
with open(f"{output_dir}/{html_filename.split('.')[0]}_html2md.md", "w") as f:
    f.write(markdown_content)


markdown_content = markdownify.markdownify(html_content)
with open(f"{output_dir}/{html_filename.split('.')[0]}_markdownify.md", "w") as f:
    f.write(markdown_content)


markdown_content = html2text.html2text(html_content)
with open(f"{output_dir}/{html_filename.split('.')[0]}_html2txt.md", "w") as f:
    f.write(markdown_content)






output_dir = 'adobe_as_css'

scraper = WebsiteCrawler(CHROME_PATH)

scraper.run(
        url = 'https://www.adobe.com/about-adobe.html',
        output_dir = output_dir,
        convert_to_pdf = True,
        convert_to_html = True,
        use_screenshot_method = False,
        output_pdf_name = 'adobe.pdf',

    )

pdf_file_path = scraper.pdf_output_path
html_filename = scraper.html_filename

parser = PDFParser()
text_md, tables, images = parser.run(pdf_file_path)

# save the text content to a file
with open(f"{output_dir}/{html_filename.split('.')[0]}_parsed.md", "w") as f:
    f.write(text_md)


html_file_path = os.path.join(output_dir, html_filename)
html_content = scraper.get_html_content()
html_metadata = scraper.meta_data



markdown_content = html2markdown.convert(html_content)
with open(f"{output_dir}/{html_filename.split('.')[0]}_html2md.md", "w") as f:
    f.write(markdown_content)


markdown_content = markdownify.markdownify(html_content)
with open(f"{output_dir}/{html_filename.split('.')[0]}_markdownify.md", "w") as f:
    f.write(markdown_content)


markdown_content = html2text.html2text(html_content)
with open(f"{output_dir}/{html_filename.split('.')[0]}_html2txt.md", "w") as f:
    f.write(markdown_content)




output_dir = 'adobe_no_embed'

scraper = WebsiteCrawler(CHROME_PATH)

scraper.run(
        url = 'https://www.adobe.com/about-adobe.html',
        output_dir = output_dir,
        convert_to_pdf = True,
        convert_to_html = True,
        use_screenshot_method = False,
        output_pdf_name = 'adobe.pdf',

    )

pdf_file_path = scraper.pdf_output_path
html_filename = scraper.html_filename

parser = PDFParser()
text_md, tables, images = parser.run(pdf_file_path, embed_images=False)

# save the text content to a file
with open(f"{output_dir}/{html_filename.split('.')[0]}_parsed.md", "w") as f:
    f.write(text_md)


html_file_path = os.path.join(output_dir, html_filename)
html_content = scraper.get_html_content()
html_metadata = scraper.meta_data



markdown_content = html2markdown.convert(html_content)
with open(f"{output_dir}/{html_filename.split('.')[0]}_html2md.md", "w") as f:
    f.write(markdown_content)


markdown_content = markdownify.markdownify(html_content)
with open(f"{output_dir}/{html_filename.split('.')[0]}_markdownify.md", "w") as f:
    f.write(markdown_content)


markdown_content = html2text.html2text(html_content)
with open(f"{output_dir}/{html_filename.split('.')[0]}_html2txt.md", "w") as f:
    f.write(markdown_content)
