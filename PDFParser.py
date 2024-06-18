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
import pathlib
from tqdm import tqdm
import asyncio
import aiofiles
from aiofiles.os import listdir
from concurrent.futures import ThreadPoolExecutor
import logging
import pymupdf4llm  # pip install -U pymupdf4llm
from llama_parse import LlamaParse
from llmsherpa.readers import LayoutPDFReader #Requires a nlm-ingestor server running, eg via docker. See https://github.com/nlmatics/nlm-ingestor
from weasyprint import HTML #needed to covert html into markdown
import markdown
from medai.tools.apikeys import load_api_keys  

import concurrent.futures


LLMSHERPA_API_URL = "http://localhost:5010/api/parseDocument?renderFormat=all" #&useNewIndentParser=true" "&applyOcr=yes"

PARSEMETHODS=("llamaparse", "llmsherpa", "pymupdf4llm")

# Configure logging
#logging.basicConfig(level=logging.info, format='%(asctime)s - %(levelname)s - %(message)s')

#this is a hack  - pymupdf4llm has a bug that causes it to hang on parsing some pdfs
#until this is fixed, we'll enforce a timeout on that function so that the app continues working
def run_with_timeout(func, timeout, *args, **kwargs):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return "Function timed out"
        

def pdf2md(pdf_filename: str, output_md_filename: str = None, method : str ="pymupdf4llm", remove_all_line_numbers=True):
    """Convert a PDF file to markdown text
        :param pdf_filename: The name of the PDF file to convert
        :param output_md_filename: The name of the markdown file to write the output to
            if no filename is stated, the function will only return the markdown text
        :param method: The method to use for conversion, one of "pymupdf4llm", "llamaparse", "llmsherpa"
        :param remove_all_line_numbers: If True, remove all line numbers from the text
        :return: The markdown text
    """
    markdown_text=None
    if method not in PARSEMETHODS:
        raise ValueError(f"Unknown method: {method}")
    if method == "pymupdf4llm":
        try:
            logging.warning(f"Calling pymupdf4llm with  {pdf_filename} to markdown")
            try:
                markdown_text = run_with_timeout(pymupdf4llm.to_markdown, 60, pdf_filename) #give it 60 seconds to coplete, else abort
            except Exception as e:
                logging.error(f"Error converting {pdf_filename} to markdown: {e}, moving pdf to 'failed' folder")
                #move file to error folder
                shutil.move(pdf_filename, os.path.join(os.path.dirname(pdf_filename), "failed", os.path.basename(pdf_filename))) 
            #markdown_text = pymupdf4llm.to_markdown(pdf_filename)
            logging.warning(f"Finished converting {pdf_filename} to markdown")
        except Exception as e:
            logging.error(f"Error converting {pdf_filename} to markdown: {e}")
            return None
    elif method == "llamaparse":
        parser = PDFParser()
        markdown_text = parser.parse(pdf_filename)
    elif method == "llmsherpa":
        convert_pdf_to_md(pdf_filename, output_md_filename)
    else:
        raise ValueError(f"Unknown method: {method}")
    logging.info(f"Converted {pdf_filename} to markdown")
    if remove_all_line_numbers:
        logging.info("Removing all line numbers")
        markdown_text = remove_line_numbers(markdown_text)
    if output_md_filename is not None:
        logging.info(f"Writing markdown to file: {output_md_filename}")
        #with open(output_md_filename, "w", encoding='utf-8', errors='replace') as f:
            #f.write(markdown_text)
        pathlib.Path(output_md_filename).write_bytes(markdown_text.encode())
    #wait(1)
    return markdown_text

def pdf2llama(pdf_path: str, output_md_filename: str = None):
    """Convert a PDF file to markdown text using the LlamaParse API
    :param pdf_path: The path of the PDF file to convert
    :return: Llamaindex nodes list for ingestion into the LlamaIndex
    """
    md_read=pymupdf4llm.LlamaMarkdownReader()
    nodes = md_read.load_data(pdf_path)
    for node in nodes:
        node.text=remove_line_numbers(node.text)
        node.metadata['filename']=os.path.basename(node.metadata['file_path'])
    return(nodes)

async def async_to_markdown(pdf_filename: str) -> str:
    loop = asyncio.get_running_loop()
    logging.info(f"converting pdf: {pdf_filename}")
    return await loop.run_in_executor(None, pymupdf4llm.to_markdown, pdf_filename)

async def a_pdf2md(pdf_filename: str, output_md_filename: str = None, method: str = "pymupdf4llm", remove_all_line_numbers=True):
    """Convert a PDF file to markdown text asynchronously.
    """
    if method not in PARSEMETHODS:
        raise ValueError(f"Unknown method: {method}")
    if method == "pymupdf4llm":
        markdown_text = await async_to_markdown(pdf_filename)
        logging.info(f"Finished converting: {pdf_filename}")
    elif method == "llamaparse":
        parser = LlamaParse()  # Assuming LlamaParse is initialized this way
        markdown_text = parser.parse(pdf_filename)
    elif method == "llmsherpa":
        # Assuming convert_pdf_to_md is an existing synchronous function
        # This part of the code might need to be adapted if convert_pdf_to_md can be made asynchronous
        markdown_text = convert_pdf_to_md(pdf_filename, output_md_filename)
    else:
        raise ValueError(f"Unknown method: {method}")
    if remove_all_line_numbers:
        remove_line_numbers(markdown_text)
    if output_md_filename is not None:
        async with aiofiles.open(output_md_filename, "w") as f:
            await f.write(markdown_text)

    return markdown_text

async def async_list_pdf_files(directory):
    loop = asyncio.get_running_loop()
    # Run the synchronous function os.listdir in an executor to avoid blocking
    files = await loop.run_in_executor(None, os.listdir, directory)
    # Filter for PDF files
    pdf_files = [file for file in files if file.endswith('.pdf')]
    return pdf_files

async def a_all_pdfs2md(pdf_directory: str, output_md_dir=None, maxnum=None, method="pymupdf4llm", force=False, remove_all_line_numbers=True):
    """Convert all PDF files in a directory to markdown files asynchronously."""
    i = 0
    logging.info(f"Listing files in directory: {pdf_directory}")
    files = await async_list_pdf_files(pdf_directory)
    logging.info(f"Found {len(files)} files")
    for pdf_file in tqdm(files, desc="Converting PDFs to markdown", unit="file", total=len(files)):
        # if not pdf_file.endswith(".pdf"):
        #     continue
        #print(f"Converting {pdf_file} to markdown")
        pdfpath = os.path.join(pdf_directory, pdf_file)
        if output_md_dir is not None:
            mdpath = os.path.join(output_md_dir, f"{os.path.basename(pdf_file)}.md")
        else:
            mdpath = f"{pdfpath}.md"
        if not force and os.path.exists(mdpath):
            #print(f"{mdpath} already exists, skipping")
            continue
        await a_pdf2md(pdfpath, output_md_filename=mdpath, method=method, remove_all_line_numbers=remove_all_line_numbers)
        i += 1
        if maxnum and i >= maxnum:
            break
        wait(1)
    return i

def all_pdfs2md(pdf_directory: str, output_md_dir=None, maxnum=None, method="pymupdf4llm", force=False, remove_all_line_numbers=True):
    """Convert all PDF files in a directory to markdown files asynchronously."""
    i = 0
    logging.info(f"Listing files in directory: {pdf_directory}")
    """list all *.pdf files in the 'pdf_directory'"""
    allfiles = [file for file in os.listdir(pdf_directory) if file.endswith('.pdf')]
    donefiles = [file[:-3] for file in os.listdir(output_md_dir) if file.endswith('.md')]
    files = [file for file in allfiles if file[:-3] not in donefiles]
    logging.warning(f"Found {len(files)} files not converted yet")
    skipped=0
    for pdf_file in tqdm(files, desc="Converting PDFs to markdown", unit="file", total=len(files)):
        #if not pdf_file.endswith(".pdf"):
        #     continue
        
        pdfpath = os.path.join(pdf_directory, pdf_file)
        if output_md_dir is not None:
            mdpath = os.path.join(output_md_dir, f"{os.path.basename(pdf_file)}.md")
        else:
            mdpath = f"{pdfpath}.md"
        if not force and os.path.exists(mdpath):
            #print(f"{mdpath} already exists, skipping")
            skipped+=1
            continue
        logging.info(f"Converting {pdfpath} to markdown as {mdpath}, skipped {skipped} existing files")
        skipped=0
        pdf2md(pdfpath, output_md_filename=mdpath, method=method, remove_all_line_numbers=remove_all_line_numbers)
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
    logging.info(f"Removed {len(lines) - len(modified_lines)} line numbers")
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


async def a_main(pdf_directory: str):
    try:
        logging.info("Starting main function")
        result = await a_all_pdfs2md(pdf_directory, output_md_dir="./library/markdown", remove_all_line_numbers=True)
        logging.debug(f"Completed with result: {result}")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

def main(pdf_directory: str):
    try:
        logging.info("Starting main function")
        result = all_pdfs2md(pdf_directory, output_md_dir="./library/markdown", remove_all_line_numbers=True)
        logging.info(f"Completed with result: {result}")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

# Example usage
#async def main(pdf_directory: str):
#   loop = asyncio.get_running_loop() 
#    await all_pdfs2md(pdf_directory, output_md_dir="./library/markdown", remove_all_line_numbers=True)

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python PDFParser.py <pdf_directory> - all pdfs in the directory will be converted to markdown")
        sys.exit(1)
    pdf_directory = os.path.abspath(sys.argv[1])
    output_md_dir="./library/markdown"
    files = [file for file in os.listdir(pdf_directory) if file.endswith('.pdf')]
    print(f"Converting all PDF files in {len(files)} to markdown")
    # for file in tqdm(files, desc="Converting PDFs to markdown", unit="file", total=len(files)):
    #     mdfilepath = os.path.join(output_md_dir, f"{os.path.basename(file)}.md")
    #     filepath=os.path.join(pdf_directory, file)
    #     pdf2md(filepath, output_md_filename=mdfilepath, remove_all_line_numbers=True)

    #asyncio.run(main(pdf_directory))
    main(pdf_directory)
