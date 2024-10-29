import asyncio
import os
from pyppeteer import launch
from pyppeteer.page import Page
from .crawlers.pdf_crawler import WebsiteToPDF
from .crawlers.html_crawler import WebsiteToHTML

class WebsiteCrawler:
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

            for i in range(5):  # Adjust the range for how many times to scroll
                await page.evaluate('window.scrollBy(0, window.innerHeight);')
                await asyncio.sleep(2)  # Wait for images to load


            return page

        except Exception as e:
            raise Exception(f"An error occurred: {e}")


    async def process(self, url: str, output_dir: str, **kwargs):
        """
        The main function that crawls the website and calls the appropriate rendering method.
        """
        os.makedirs(output_dir, exist_ok=True)

        page = await self.crawl_website(url)
        
        convert_to_pdf = kwargs.get("convert_to_pdf", False)
        convert_to_html = kwargs.get("convert_to_html", False)


        if convert_to_pdf:
            output_path = kwargs.get("output_pdf_path", os.path.join(output_dir, "output.pdf"))
            use_screenshot_method = kwargs.get("use_screenshot_method", False)

            pdf_crawler = WebsiteToPDF()
            await pdf_crawler.process_website(page, output_path, use_screenshot_method)


        if convert_to_html:
            html_crawler = WebsiteToHTML()
            await html_crawler.scrape(page, output_dir=output_dir)

        # Close the browser once rendering is done
        await page.browser.close()


    def run(self, url: str, output_dir: str,  **kwargs):
        """
        A wrapper method to run the asynchronous scrape function synchronously.
        """
        asyncio.get_event_loop().run_until_complete(self.process(url, output_dir, **kwargs))








if __name__ == '__main__':
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    scraper = WebsiteCrawler(chrome_path)
    scraper.run(
        url = 'https://www.adobe.com/about-adobe.html',
        output_dir = 'adobe',
        convert_to_pdf = True,
        convert_to_html = True,
        use_screenshot_method = True
    )
