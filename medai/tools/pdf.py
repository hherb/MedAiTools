# MetaAnalysisAppraiser.py
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

"""This module provides a single function to parse a PDF file and return the text.
It uses LlamaParse from Llama Cloud, but you can install https://github.com/nlmatics
llmsherpa instead if you want this to run locally"""

import os
import argparse
from llama_parse import LlamaParse  # pip install llama-parse
from dotenv import load_dotenv

import asyncio 
#import nest_asyncio
#nest_asyncio.apply()

# Load the .env file
load_dotenv()
api_key = os.getenv("LLAMA_CLOUD_API_KEY")

parser = LlamaParse(
    api_key=api_key,  # can also be set in your env as LLAMA_CLOUD_API_KEY
    result_type="markdown"  # "markdown" and "text" are available
)

# async
async def parse_pdf(pdf_file):
    result = await parser.aload_data(pdf_file)
    return result[0].text


if __name__ == "__main__":
     # Create the parser
    arg_parser = argparse.ArgumentParser(description='Process a PDF file.')
    arg_parser.add_argument('FileName', metavar='filename', type=str, help='the name of the PDF file to process')

    # Parse the arguments
    args = arg_parser.parse_args()

    # Process the PDF file
    documents = asyncio.run(parse_pdf(args.FileName))
    print(documents)