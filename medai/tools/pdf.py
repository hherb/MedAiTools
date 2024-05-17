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