# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a class tool converting MarkDown towards HTML.
"""

import re
import os
import markdown

from logger.loggerobject import DWHLoggerObject

class Markdown(DWHLoggerObject):
    CSS = """
        body {
          font-family: system-ui, sans-serif;
          max-width: 90%;
          margin: auto;
        }

        h1 { color: #003366; }
        table { border-collapse: collapse; width: 100% }
        th, td { border: 1px solid #ccc; padding: 6px; }
        """

    LEFT = ":---"
    CENTER = ":---:"
    RIGHT = "---:"

    class Bullet:
        def __enter__(self):
            self.start()
            return self

        def start(self):
            self.__markdown.paragraph()

        def item(self, text):
            indent = "  " * self.__level
            self.__markdown.paragraph(f"{indent}- {text}")

        def end(self):
            self.__markdown.paragraph()
        
        def __exit__(self, *args):
            self.end()

        def bullet(self):
            return Markdown.Bullet(self.__markdown, self.__level + 1)

        def __init__(self, markdown, level = 0):
            self.__markdown = markdown
            self.__level = level

    def open(self):
        self.info(f"Creating markdown documentation '{self.__filename}' ...")

        directory = os.path.dirname(os.path.join(self.__directory, self.__filename))
        try:
            os.makedirs(directory, exist_ok=True)
        except:
            self.exception(f"Unable to create directory '{directory}'")
            return

        self.__file = open(os.path.join(self.__directory, self.__filename), 'w', encoding='utf-8')

    def title(self, text):
        if self.__file is None:
            return
        self.__file.write(f"# {text.upper()}\n\n")

    def subtitle(self, text):
        if self.__file is None:
            return
        self.__file.write(f"## {text}\n\n")

    def part(self, text):
        if self.__file is None:
            return
        self.__file.write(f"### {text}\n\n")

    def paragraph(self, text = "\n"):
        if self.__file is None:
            return
        self.__file.write(f"{text}\n")

    def table(self, headers, rows):
        def get_cell(value):
            if value is None:
                return ""
            if isinstance(value, str):
                return value
            if isinstance(value, list) or isinstance(value, tuple):
                return "<br>".join(value)
            return str(value)

        if self.__file is None:
            return

        header_title = "| "
        header_align = "| "
        if isinstance(headers, list):
            for header in headers:
                header_title += get_cell(header) + " |"
                header_align += Markdown.LEFT + " |"
        elif isinstance(headers, dict):
            for header in headers.values():
                if "title" in header:
                    header_title += get_cell(header["title"])
                header_title += " |"
                if "align" in header:
                    header_align += header["align"]
                else:
                    header_align += Markdown.LEFT
                header_align += " |"
        else:
            return

        self.__file.write(f"{header_title}\n")
        self.__file.write(f"{header_align}\n")
        for row in rows:
            row_line = "| "
            if isinstance(row, dict):
                for key in headers.keys():
                    row_line += get_cell(row[key]) + " |"
            elif isinstance(row, list) or isinstance(row, tuple):
                for item in row:
                    row_line += get_cell(item) + " |"
            else:
                continue
            self.__file.write(f"{row_line}\n")
        self.__file.write("\n")

    def link(self, text, url = None):
        return f"[{text}]({url if url is not None else text})"

    def bullet(self):
        return Markdown.Bullet(self)

    def close(self):
        if self.__file is None:
            return None

        self.__file.close()
        self.__file = None

        # Convert to HTML

        filename = os.path.join(self.__directory, self.__filename)

        html = open(filename[:-3] + ".html", "w", encoding="utf-8")
        md = open(filename, "r", encoding="utf-8")
        md_body = re.sub(r'\\_', r'\\\\_',md.read())
        md_body = re.sub(r'\\\.', r'\\\\\.',md_body)
        html_body = re.sub(r'href="([^"]+)\.md"', r'href="\1.html"', markdown.markdown(md_body, extensions=["extra", "tables", "fenced_code"]))
        html_content = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <meta charset="utf-8">
                    <style>
                        {Markdown.CSS}
                    </style>
                </head>
                <body>
                    {html_body}
                </body>
            </html>
            """
        html.write(html_content)
        md.close()
        html.close()

        return self.__filename

    def __init__(self, directory, filename):
        super().__init__("MarkDown")
        self.__directory = directory
        self.__filename = filename
        self.__file = None
        self.open()
