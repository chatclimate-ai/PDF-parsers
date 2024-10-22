import logging
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin, urlparse
from typing import List, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']


class WebsiteScraper:
    def __init__(self, timeout: int = 10, max_retries: int = 3, use_selenium: bool = True):
        self.timeout = timeout
        self.max_retries = max_retries
        self.use_selenium = use_selenium
        if self.use_selenium:
            # Initialize Selenium WebDriver (Chrome in this case)
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Run in headless mode (no browser UI)
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def scrape(self, url: str) -> Dict:
        """
        Scrape the website including JavaScript-rendered content and return HTML, images and their URLs.
        :param url: The URL of the website to scrape
        :return: A dictionary containing 'html_content', 'image_urls', and 'image_data'
        """
        html_content = ""
        images_data = []

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Scraping website: {url} (Attempt {attempt + 1})")

                # Use Selenium for JavaScript-rendered content
                if self.use_selenium:
                    self.driver.get(url)
                    page_source = self.driver.page_source
                else:
                    response = requests.get(url, timeout=self.timeout)
                    response.raise_for_status()
                    page_source = response.text

                # Parse the HTML content
                soup = BeautifulSoup(page_source, 'html.parser')
                html_content = str(soup)

                # Extract and download images
                images_data = self.download_images(soup, url)

                # Exit the loop once successful
                break

            except (requests.Timeout, requests.RequestException) as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to scrape {url} after {self.max_retries} attempts")
                else:
                    continue  # Retry on failure

        return {
            "html_content": {
                    "url": url,
                    "content": html_content,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, 
            "images": images_data
            }

    def download_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Downloads images from the webpage and returns a list of dictionaries containing image URLs and image data.
        :param soup: The BeautifulSoup object of the webpage
        :param base_url: The base URL of the webpage
        :return: A list of dictionaries, each containing 'url' and 'content' for an image
        """
        images_data = []

        for img_tag in soup.find_all('img'):
            img_src = img_tag.get('src')
            full_img_url = urljoin(base_url, img_src)
            img_ext = os.path.splitext(urlparse(full_img_url).path)[1].lower()

            # Only process valid image URLs
            if img_ext in VALID_IMAGE_EXTENSIONS:
                try:
                    # Download the image
                    response = requests.get(full_img_url, timeout=self.timeout)
                    response.raise_for_status()

                    # Store the image data and URL
                    images_data.append({
                        "url": full_img_url,
                        "content": response.content,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    logger.info(f"Downloaded image from {full_img_url}")

                except requests.RequestException as e:
                    logger.warning(f"Failed to download image from {full_img_url}: {e}")

        return images_data



if __name__ == '__main__':
    url = "https://www.google.com"

    # Initialize the WebsiteScraper
    scraper = WebsiteScraper(timeout=10, max_retries=3, use_selenium=True)

    # Scrape the website
    data = scraper.scrape(url)

    # save the html content
    with open("html_content.html", "w") as f:
        f.write(data['html_content']['content'])

    # Save the images and their URLs
    for i, image_data in enumerate(data['images']):
        image_url = image_data['url']
        image_content = image_data['content']
        image_ext = os.path.splitext(urlparse(image_url).path)[1]
        with open(f"image_{i}{image_ext}", "wb") as f:
            f.write(image_content)
        print(f"Saved image_{i}{image_ext} from {image_url}")
