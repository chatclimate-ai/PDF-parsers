import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Tuple
from datetime import datetime
from pyppeteer.page import Page

VALID_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg']


class WebsiteToHTML:
    def __init__(self):
        pass

    async def scrape(self, page: Page, output_dir: str):
        """
        Scrape the website including JavaScript-rendered content and return HTML and images.
        """
        os.makedirs(output_dir, exist_ok=True)

        try:
            page_source = await page.content()
            page_url = page.url

            soup = BeautifulSoup(page_source, 'html.parser')

            html_content = str(soup)
            html_filename = self.get_file_name_from_url(page_url)

            # Save the HTML content to a file
            with open(os.path.join(output_dir, f"{html_filename}.html"), 'w') as html_file:
                html_file.write(html_content)


            images, image_data = await self.download_images(soup, page_url)
            
            for i, image in enumerate(images):
                with open(os.path.join(output_dir, image_data[i]['filename']), 'wb') as img_file:
                    img_file.write(image)
            

            meta_data = {
                "url": page_url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "html_filename": f"{html_filename}.html",
                "images": image_data
            }

            with open(os.path.join(output_dir, 'metadata.json'), 'w') as metadata_file:
                metadata_file.write(json.dumps(meta_data, indent=4))

            
        
        except Exception as e:
            raise Exception(f"An error occurred: {e}")

        

    async def download_images(self, soup: BeautifulSoup, url: str) -> Tuple[List[bytes], List[Dict]]:
        """
        Downloads images from the webpage and returns a list of dictionaries containing image URLs, image data, and alt text.
        """
        images = []
        image_data = []
        unique_urls = set()
       
        for tag in soup.find_all(['img', 'picture']):
            img_url = None

            if tag.name == 'img':
                img_url = tag.get('src') or tag.get('data-src')
                img_tag = tag
            
            elif tag.name == 'picture':
                img_tag = tag.find('img')
                if img_tag:
                    img_url = img_tag.get('src') or img_tag.get('data-src')
                
                if not img_url:
                    source_tag = tag.find('source')
                    if source_tag:
                        img_url = source_tag.get('srcset') or source_tag.get('data-srcset')
                
            if img_url is None:
                continue

            full_img_url = urljoin(url, img_url)
            if full_img_url in unique_urls:
                continue

            unique_urls.add(full_img_url)

            try:
                head_response = requests.head(full_img_url, timeout=10)
                head_response.raise_for_status()

                content_type = head_response.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    continue  # Skip if it's not an image

            except Exception as e:
                continue
            
            try:
                response = requests.get(full_img_url, timeout= 10)
                response.raise_for_status()
                

                image_content = response.content
                caption=self.extract_caption(img_tag)
                filename=self.get_file_name_from_url(full_img_url)

                # if no extension in the filename, add one
                if '.' not in filename:
                    file_extension = ''
                    if 'jpeg' in content_type:
                        file_extension = 'jpg'
                    elif 'png' in content_type:
                        file_extension = 'png'
                    elif 'gif' in content_type:
                        file_extension = 'gif'
                    elif 'bmp' in content_type:
                        file_extension = 'bmp'
                    elif 'tiff' in content_type:
                        file_extension = 'tiff'
                    elif 'svg' in content_type:
                        file_extension = 'svg'
                    filename = f"{filename}.{file_extension}"
            
                images.append(image_content)
                image_data.append({
                    "url": full_img_url,
                    "caption": caption,
                    "filename": filename,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            except Exception as e:
                raise Exception(f"An error occurred: {e}")

        return images, image_data


    @staticmethod
    def extract_caption(tag: BeautifulSoup) -> str:
        """
        Extract caption for a media file by finding the closest preceding heading or figcaption.
        :param tag: The BeautifulSoup tag of the media file
        :return: The extracted caption or "No caption available"
        """
        heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'figcaption']
        previous_tag = tag.find_previous(heading_tags)
        if previous_tag:
            return previous_tag.get_text(strip=True)
        return "No caption available"

    @staticmethod
    def get_file_name_from_url(url: str) -> str:
        """
        Extract the file name from the URL.
        :param url: The URL of the file
        :return: The file name extracted from the URL
        """
        return os.path.basename(urlparse(url).path)
