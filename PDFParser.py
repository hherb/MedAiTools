# Copyright (C) 2024  Dr Horst Herb
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""This module converts PDF files to markdown text using the LlamaParse API

The LlamaParse API is a cloud-based service that converts PDF files to markdown text.
You can ge your LLAM_CLOUD_API_KEY from the https://cloud.llamaindex.ai/. 
The API is free for limited use. For larger volumes, you need to pay a fee.

The PDFParser class is a wrapper around the LlamaParse API that provides a simple interface 
to convert PDF files to markdown text. The wrapper allows to later change the underlying 
conversion service without having to change further source code depnding on this module 
"""

from llama_parse import LlamaParse
from weasyprint import HTML
import markdown
from medai.tools.apikeys import load_api_keys  


def convert_md_to_pdf(markdown_text: str, output_pdf_filename: str):
    # Convert markdown to HTML
    html = markdown.markdown(markdown_text)
    # Convert to PDF
    HTML(string=html).write_pdf(output_pdf_filename)
    

class PDFParser():
    """A simple wrapper around the LlamaParse API to convert PDF files to markdown text"""

    def __init__(self):
        load_api_keys(['LLAMA_CLOUD_API_KEY',]) #get the LLAMA_CLOUD_API_KEY from the environment
        self.parser = LlamaParse(
            #api_key="llx-...",  # can also be set in your env as LLAMA_CLOUD_API_KEY
            result_type="markdown",  # "markdown" and "text" are available
            num_workers=4,  # if multiple files passed, split in `num_workers` API calls
            verbose=True,
            language="en",  # Optionally you can define a language, default=en
        )

    async def aparse(self, file_path: str) -> str:
        """Parse a PDF file to markdown text asynchronously"""
        parsed = await self.parser.aload_data(file_path)
        return parsed[0].text
    
    def parse(self, file_path: str) -> str:
        """Parse a PDF file to markdown text"""
        parsed = self.parser.load_data(file_path)
        return parsed[0].text

if __name__ == "__main__":
    import sys
    import asyncio

    if len(sys.argv) != 2:
        print("Usage: python PDFParser.py <pdf_file>")
        sys.exit(1)
    # Create an event loop
    loop = asyncio.get_event_loop()
    pdf_file = sys.argv[1]
    parser = PDFParser()
    markdown_text = loop.run_until_complete(parser.aparse(pdf_file))
    print(markdown_text)