# -*- coding: utf-8 -*-
# pylint: disable=bare-except

"""
This module describes a class tool converting MarkDown towards HTML.
"""

import re
import markdown

class Markdown:
    CSS = """
        body {
          font-family: system-ui, sans-serif;
          max-width: 1200px;
          margin: auto;
        }

        h1 { color: #003366; }
        table { border-collapse: collapse; width: 100% }
        th, td { border: 1px solid #ccc; padding: 6px; }
        """

    def Convert(filename):
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
