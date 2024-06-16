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

import os
import re
from tqdm import tqdm
import asyncio
from aiofiles.os import listdir
from concurrent.futures import ThreadPoolExecutor

import pymupdf4llm  # pip install -U pymupdf4llm
from llama_parse import LlamaParse
from llmsherpa.readers import LayoutPDFReader #Requires a nlm-ingestor server running, eg via docker. See https://github.com/nlmatics/nlm-ingestor
from weasyprint import HTML #needed to covert html into markdown
import markdown
from medai.tools.apikeys import load_api_keys  

LLMSHERPA_API_URL = "http://localhost:5010/api/parseDocument?renderFormat=all" #&useNewIndentParser=true" "&applyOcr=yes"

PARSEMETHODS=("llamaparse", "llmsherpa", "pymupf4llm")

def pdf2md(pdf_filename: str, output_md_filename: str = None, method : PARSEMETHODS ="pymupdf4llm", remove_all_line_numbers=False):
    """Convert a PDF file to markdown text
        :param pdf_filename: The name of the PDF file to convert
        :param output_md_filename: The name of the markdown file to write the output to
            if no filename is stated, the function will only return the markdown text
        :param method: The method to use for conversion, one of "pymupdf4llm", "llamaparse", "llmsherpa"
        :param remove_all_line_numbers: If True, remove all line numbers from the text
        :return: The markdown text
    """
    if method == "pymupdf4llm":
        markdown_text = markdown_text = pymupdf4llm.to_markdown(pdf_filename)
    elif method == "llamaparse":
        parser = PDFParser()
        markdown_text = parser.parse(pdf_filename)
    elif method == "llmsherpa":
        convert_pdf_to_md(pdf_filename, output_md_filename)
    else:
        raise ValueError(f"Unknown method: {method}")
    if remove_all_line_numbers:
        markdown_text
    if output_md_filename is not None:
        with open(output_md_filename, "w") as f:
            f.write(markdown_text)
    return markdown_text

async def all_pdfs2md(pdf_directory: str, output_md_dir=None, maxnum=None, method="pymupdf4llm", force=False, remove_all_line_numbers=True):
    """Convert all PDF files in a directory to markdown files asynchronously."""
    i = 0
    files = await listdir(pdf_directory)
    for pdf_file in tqdm(files, desc="Converting PDFs to markdown", unit="file", total=len(files)):
        if not pdf_file.endswith(".pdf"):
            continue
        #print(f"Converting {pdf_file} to markdown")
        pdfpath = os.path.join(pdf_directory, pdf_file)
        if output_md_dir is not None:
            mdpath = os.path.join(output_md_dir, f"{os.path.basename(pdf_file)}.md")
        else:
            mdpath = f"{pdfpath}.md"
        if not force and os.path.exists(mdpath):
            #print(f"{mdpath} already exists, skipping")
            continue
        # Assuming pdf2md is a synchronous function, run it in a thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, pdf2md, pdfpath, mdpath, method, remove_all_line_numbers)
        i += 1
        if maxnum and i >= maxnum:
            break
    return i


def remove_line_numbers(text: str):
    """Remove line numbers from a text string and lines that are only line numbers
    :param text: The text to remove line numbers from
    :return: The text with line numbers and lines that are only line numbers removed
    """

    # Compile a regular expression to match line numbers at the start of a line.
    # This pattern matches one or more digits at the beginning of a line,
    # possibly followed by any non-alphanumeric characters (like a space, dot, or dash).
    line_number_pattern = re.compile(r'^\d+\s*[\.\-\)]?\s*')

    # Split the text into lines, apply the pattern to remove line numbers, and filter out empty lines.
    lines = text.split('\n')
    modified_lines = [line_number_pattern.sub('', line) for line in lines if line.strip()]

    # Join the modified lines back into a single text string.
    modified_text = '\n'.join(modified_lines)
    return modified_text


def convert_md_to_pdf(markdown_text: str, output_pdf_filename: str):
    # Convert markdown to HTML
    html = markdown.markdown(markdown_text)
    # Convert to PDF
    HTML(string=html).write_pdf(output_pdf_filename)

def convert_pdf_to_md(pdf_filename: str, output_md_filename: str, parser_api_url=LLMSHERPA_API_URL):
    # Convert PDF to HTML
    reader = LayoutPDFReader(parser_api_url=parser_api_url )
    doc = reader.read_pdf(pdf_filename)
    html=doc.to_html()
    # Convert HTML to markdown
    markdown_text = html #markdown.markdown(html)
    with open(output_md_filename, "w") as f:
        f.write(markdown_text)
    
class PDFParser():
    """A simple wrapper around the LlamaParse API to convert PDF files to markdown text"""

    def __init__(self, api_key=None, result_type="markdown", num_workers=4, verbose=True, language="en"):
        load_api_keys(['LLAMA_CLOUD_API_KEY',]) #get the LLAMA_CLOUD_API_KEY from the environment
        self.parser = LlamaParse(
            api_key=api_key,  # can also be set in your env as LLAMA_CLOUD_API_KEY
            result_type=result_type,  # "markdown" and "text" are available
            num_workers=num_workers,  # if multiple files passed, split in `num_workers` API calls
            verbose=verbose,
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


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python PDFParser.py <pdf_directory> - all pdfs in the directory will be converted to markdown")
        sys.exit(1)
    pdf_directory = os.path.abspath(sys.argv[1])
    print(f"Converting all PDF files in {pdf_directory} to markdown")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(all_pdfs2md(pdf_directory, output_md_dir="./library/markdown", remove_all_line_numbers=True))