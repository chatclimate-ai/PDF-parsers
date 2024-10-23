import asyncio
from pyppeteer import launch
from pyppeteer.page import Page
from PIL import Image
from io import BytesIO


class WebsiteToPDF:
    def __init__(self, browser_path: str = None):
        """
        Initialize the scraper with an optional path to a Chromium or Chrome browser binary.
        :param browser_path: Path to Chromium or Chrome browser (optional).
        """
        self.browser_path = browser_path

    async def handle_popups(self, page : Page):
        """
        Handle common pop-ups like cookie consent, language selection, etc.
        """
        await page.evaluate('''() => {
            const popups = document.querySelectorAll('.modal, .cookie-consent, .cookie-banner, .popup');
            popups.forEach(popup => popup.remove());
        }''')

    async def crawl_website(self, url: str) -> Page:
        """
        Launch the browser, navigate to the URL, handle pop-ups, and save the page as a PDF.
        """
        try:
            browser = await launch(
                headless=False,
                executablePath=self.browser_path,
                args=['--disable-http2']
            )
            
            # Open a new tab
            page: Page = await browser.newPage()

            # Go to the URL
            await page.goto(url, {'waitUntil': 'load', 'timeout': 120000})

            # Handle pop-ups (cookie consent, language modals, etc.)
            await self.handle_popups(page)

            # # Close the browser
            # await browser.close()

            return page

        except Exception as e:
            raise Exception(f"An error occurred: {e}")

    async def render_with_screenshots(self, page: Page, output_pdf: str) -> None:
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
            image.save(output_pdf, 'PDF', resolution=100.0, save_all=True)

        except Exception as e:
            raise Exception(f"An error occurred: {e}")

   

    async def render_with_css(self, page: Page, output_pdf: str) -> None:
        """
        Launch the browser, navigate to the URL, handle pop-ups, and save the page as a PDF.
        """
        try:
            # Save the page as a PDF
            await page.pdf({
                'path': output_pdf,
                'printBackground': True,
                'landscape': True,
                'preferCSSPageSize': True
            })

        except Exception as e:
            raise Exception(f"An error occurred: {e}")
        


    async def process_website(self, url: str, output_pdf_path: str, use_screenshot_method=False):
        """
        The main function that crawls the website and calls the appropriate rendering method.
        """
        page = await self.crawl_website(url)
        if use_screenshot_method:
            await self.render_with_screenshots(page, output_pdf_path)
        else:
            await self.render_with_css(page, output_pdf_path)
        
        # Close the browser once rendering is done
        await page.browser.close()


    def download_website_as_pdf(self, url: str, output_pdf_path: str, use_screenshot_method=False):
        """
        A wrapper method to run the asynchronous scrape function synchronously.
        """
        asyncio.get_event_loop().run_until_complete(self.process_website(url, output_pdf_path, use_screenshot_method))



if __name__ == '__main__':
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    scraper = WebsiteToPDF(chrome_path)
    scraper.download_website_as_pdf('https://www.adobe.com/about-adobe.html', 'output.pdf', use_screenshot_method=True)
