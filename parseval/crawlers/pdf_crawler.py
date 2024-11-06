from pyppeteer.page import Page
from PIL import Image
from io import BytesIO


class WebsiteToPDF:
    """
    A class to render a website as a PDF using Pyppeteer."""
    def __init__(self):
        pass

    async def render_with_screenshots(self, page: Page, output_pdf_path: str) -> None:
        """
        Launch the browser, navigate to the URL, handle pop-ups, and save the page as a screenshot.
        """
        try:
            # Get full page dimensions and set the viewport to capture the entire page
            dimensions = await page.evaluate('''() => {
                return {
                    width: document.documentElement.scrollWidth,
                    height: document.documentElement.scrollHeight
                };
            }''')
            await page.setViewport({'width': dimensions['width'], 'height': dimensions['height']})

            # Capture the full-page screenshot
            screenshot_byte = await page.screenshot({'fullPage': True})
            image = Image.open(BytesIO(screenshot_byte)).convert('RGB')
            image.save(output_pdf_path, 'PDF', resolution=100.0, save_all=True)

        except Exception as e:
            raise Exception(f"An error occurred: {e}")

   

    async def render_with_css(self, page: Page, output_pdf_path: str) -> None:
        """
        Launch the browser, navigate to the URL, handle pop-ups, and save the page as a PDF.
        """
        try:
            # Save the page as a PDF
            await page.pdf({
                'path': output_pdf_path,
                'printBackground': True,
                'landscape': True,
                'preferCSSPageSize': True
            })

        except Exception as e:
            raise Exception(f"An error occurred: {e}")
        


    async def process_website(self, page: Page, output_pdf_path: str, use_screenshot_method=False):
        """
        The main function that crawls the website and calls the appropriate rendering method.
        """
        if use_screenshot_method:
            await self.render_with_screenshots(page, output_pdf_path)
        else:
            await self.render_with_css(page, output_pdf_path)
        

        return output_pdf_path
