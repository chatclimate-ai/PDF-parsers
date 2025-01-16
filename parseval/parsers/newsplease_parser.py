"""Parser using news-please library: https://github.com/fhamborg/news-please"""


from newsplease import NewsPlease



class NewsPleaseParser:
    """HTML parser which uses the news-please library."""

    def __init__(self) -> None:
        pass

    def parse_html(self, html_content: str, **kwargs) -> str:
        """
        """

        try:
            url = kwargs.get("url", None)
            fetch_images = kwargs.get("fetch_images", True)

            article = NewsPlease.from_html(
                html=html_content, 
                url=url, 
                fetch_images=fetch_images
            )
            
        except Exception as e:
            print(f"Failed to parse because {e}")
            return "No text found"

        return article.maintext




