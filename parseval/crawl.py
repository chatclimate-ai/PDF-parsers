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
        self.html_filepath: str = None
        self.html_content: str = None
        self.meta_data: dict = None
        self.pdf_output_path: str = None

        self.url_page = {}

    @staticmethod
    async def handle_popups(page : Page):
        """
        Handle common pop-ups like cookie consent, language selection, etc.
        """
        await page.evaluate('''() => {
            const popups = document.querySelectorAll('.modal, .cookie-consent, .cookie-banner, .popup');
            popups.forEach(popup => popup.remove());
        }''')

    @staticmethod
    async def auto_scroll(page: Page):
        # Step 1: Scroll down by one viewport height to capture the top portion with the nav bar
        await page.evaluate('window.scrollBy(0, window.innerHeight);')
        # Wait for content to load and the initial view to render
        await asyncio.sleep(3)

        # Step 2: Hide navigation bar after first scroll
        await page.addStyleTag({
            'content': '''
                nav, header, .navbar, .navigation { 
                    display: none !important; 
                }
            '''
        })

        # Use smaller scroll increments for the rest of the page
        viewport_height = await page.evaluate('window.innerHeight')
        scroll_increment = viewport_height / 2

        previous_height = await page.evaluate('document.body.scrollHeight')
        while True:
            # Scroll down by a smaller increment without the nav bar obstructing
            await page.evaluate(f'window.scrollBy(0, {scroll_increment});')
            # Wait for new content to load
            await asyncio.sleep(3)
            new_height = await page.evaluate('document.body.scrollHeight')
            # Break if we've reached the bottom of the page
            if new_height == previous_height:
                break
            previous_height = new_height

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

            # Adjust the viewport size to desired dimensions (e.g., 1920x1080)
            await page.setViewport({'width': 1280, 'height': 1080})
          
            # Go to the URL
            await page.goto(url, {'waitUntil': 'load', 'timeout': 120000})

            # Handle pop-ups (cookie consent, language modals, etc.)
            await self.handle_popups(page)

            await self.auto_scroll(page)

            return page

        except Exception as e:
            raise Exception(f"An error occurred: {e}")


    async def process(
            self, 
            url: str, 
            output_dir: str,
            convert_to_pdf: bool = False,
            convert_to_html: bool = False,
            **kwargs
            ):
        """
        The main function that crawls the website and calls the appropriate rendering method.
        """
        os.makedirs(output_dir, exist_ok=True)

        # if url in self.url_page:
        #     page = self.url_page[url]
        # else:
        #     page = await self.crawl_website(url)
        #     self.url_page[url] = page
        page = await self.crawl_website(url)

        if convert_to_pdf:
            pdf_output_name = kwargs.get(
                "output_pdf_name", 
                "output.pdf")
            
            self.pdf_output_path = os.path.join(output_dir, pdf_output_name)
            use_screenshot_method = kwargs.get("use_screenshot_method", False)

            pdf_crawler = WebsiteToPDF()
            await pdf_crawler.process_website(page, self.pdf_output_path, use_screenshot_method)


        if convert_to_html:
            html_crawler = WebsiteToHTML()
            self.html_filepath, self.html_content, self.meta_data = await html_crawler.scrape(page, output_dir=output_dir)

        # Close the browser once rendering is done
        await page.browser.close()

    # def kill_page(self, url: str):
    #     if url in self.url_page:
    #         page = self.url_page[url]
    #         page.browser.close()
    #         del self.url_page[url]

    def run(
            self, 
            url: str, 
            output_dir: str,
            convert_to_pdf: bool = False,
            convert_to_html: bool = False,
            **kwargs
            ):
        """
        A wrapper method to run the asynchronous scrape function synchronously.
        """
        asyncio.get_event_loop().run_until_complete(self.process(url, output_dir, convert_to_pdf, convert_to_html, **kwargs))

    def get_html_filepath(self):
        """
        Get the file path to the generated HTML file.
        """
        return self.html_filepath
    
    def get_html_content(self):
        """
        Get the HTML content of the page.
        """
        return self.html_content
    
    def get_meta_data(self):
        """
        Get the meta data of the page.
        """
        return self.meta_data
    
    def get_pdf_output_path(self):
        """
        Get the path to the generated PDF file.
        """
        return self.pdf_output_path
    
   





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
