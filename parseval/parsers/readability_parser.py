"""Parser using python-readability library: https://github.com/buriy/python-readability"""

from typing import List
import re
from readability import Document
import bleach




class ReadabilityParser:
    """HTML parser which uses the python-readability library."""

    def __init__(self) -> None:
        pass

    def parse_html(self, html_content: str, **kwargs) -> str:
        """Parse HTML using readability

        :param html: HTML string to parse
        :param url: URL of  web page

        :return ParsedHTML: parsed HTML
        """
        url = kwargs.get("url", None)
       
        readability_doc = Document(html_content, url=url)
        title = readability_doc.title()
        text = readability_doc.summary(html_partial=True)
        text_html_stripped = bleach.clean(text, tags=[], strip=True)
        # text_by_line = [
        #     line.strip() for line in text_html_stripped.split("\n") if line.strip()
        # ]
        # text_by_line = self._combine_bullet_lines_with_next(text_by_line)
        # main_text = "\n".join(text_by_line)

        main_text = text_html_stripped

        return f"# {title}\n\n{main_text}"

    @staticmethod
    def _combine_bullet_lines_with_next(lines: List[str]) -> List[str]:
        """
        Iterate through all lines of text.

        If a line is a bullet or numbered list heading (e.g. (1), 1., i.),
        then combine it with the next line.
        """

        list_header_regex = [
            r"([\divxIVX]+\.)+",  # dotted number or roman numeral
            r"(\([\divxIVX]+\))+",  # parenthesized number or roman numeral
            r"[*•\-\–\+]",  # bullets
            r"([a-zA-Z]+\.)+",  # dotted abc
            r"(\([a-zA-Z]+\))+",  # parenthesized abc
        ]

        idx = 0

        while idx < len(lines) - 1:
            if any(re.match(regex, lines[idx].strip()) for regex in list_header_regex):
                lines[idx] = lines[idx].strip() + " " + lines[idx + 1].strip()
                lines[idx + 1] = ""
                idx += 1

            idx += 1

        # strip empty lines
        return [line for line in lines if line]




if __name__ == "__main__":
    html_path = "data/test/v4/2404.12720v1/2404.12720v1.html"
    with open(html_path, "r") as f:
        html_content = f.read()

    parser = ReadabilityParser()
    text = parser.parse_html(html_content)
    with open("2404.12720v1.txt", "w") as f:
        f.write(text)
