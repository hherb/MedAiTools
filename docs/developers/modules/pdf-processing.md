# PDF Processing Modules

This document covers the PDF processing capabilities in MedAiTools.

## Overview

MedAiTools provides multiple methods for extracting text from PDF documents:

| Module | Purpose | Best For |
|--------|---------|----------|
| PDFParser | Multi-method PDF to markdown | General use |
| PDFExtractor | Simple text extraction | Quick extraction |
| PDFFinder | Find PDFs in directories | File discovery |

---

## PDFParser

**File:** `PDFParser.py`

Multi-method PDF to markdown conversion with fallback strategies.

### Supported Methods

1. **PyMuPDF4LLM** (default) - Fast, local, good for most PDFs
2. **LlamaParse** - Cloud-based, accurate, handles complex layouts
3. **LLMSherpa** - Layout-aware, good for academic papers

### Main Function

#### pdf2md()

```python
from PDFParser import pdf2md

markdown = pdf2md(
    pdf_path: str,          # Path to PDF file
    method: str = "pymupdf", # Parsing method
    timeout: int = 60       # Timeout in seconds
) -> str
```

**Example:**
```python
# Default method (PyMuPDF4LLM)
markdown = pdf2md("/path/to/document.pdf")

# Use LlamaParse for complex layouts
markdown = pdf2md("/path/to/document.pdf", method="llamaparse")

# Use LLMSherpa for academic papers
markdown = pdf2md("/path/to/document.pdf", method="llmsherpa")
```

### PDFParser Class

For more control over parsing:

```python
from PDFParser import PDFParser

parser = PDFParser()

# Parse with automatic method selection
markdown = parser.parse("/path/to/document.pdf")

# Parse with specific method
markdown = parser.parse("/path/to/document.pdf", method="pymupdf")

# Parse with fallback chain
markdown = parser.parse_with_fallback(
    "/path/to/document.pdf",
    methods=["pymupdf", "llamaparse", "llmsherpa"]
)
```

### Method Details

#### PyMuPDF4LLM

Fast local parsing using PyMuPDF:

```python
from PDFParser import pdf2md

# PyMuPDF is the default
markdown = pdf2md("document.pdf", method="pymupdf")
```

**Pros:**
- Fast (processes locally)
- No API keys required
- Works offline

**Cons:**
- May struggle with complex layouts
- Limited table extraction

#### LlamaParse

Cloud-based parsing with LlamaIndex:

```python
import os
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-..."

markdown = pdf2md("document.pdf", method="llamaparse")
```

**Pros:**
- Excellent accuracy
- Handles complex layouts
- Good table extraction

**Cons:**
- Requires API key
- Network dependent
- Usage limits

#### LLMSherpa

Layout-aware parsing:

```python
markdown = pdf2md("document.pdf", method="llmsherpa")
```

**Pros:**
- Preserves document structure
- Good for academic papers
- Identifies sections/headings

**Cons:**
- Requires LLMSherpa server
- Slower than PyMuPDF

### Timeout Handling

```python
from PDFParser import pdf2md, run_with_timeout

# With timeout
try:
    markdown = pdf2md("large_document.pdf", timeout=120)
except TimeoutError:
    print("PDF parsing timed out")

# Custom timeout handling
result = run_with_timeout(
    func=pdf2md,
    args=("document.pdf",),
    timeout=60
)
```

### Error Handling

```python
from PDFParser import pdf2md

try:
    markdown = pdf2md("document.pdf")
except FileNotFoundError:
    print("PDF file not found")
except ValueError as e:
    print(f"Invalid PDF: {e}")
except TimeoutError:
    print("Parsing timed out")
except Exception as e:
    print(f"Parsing failed: {e}")
```

---

## PDFExtractor

**File:** `PDFExtractor.py`

Simple text extraction without markdown formatting.

### Main Function

#### extract_text()

```python
from PDFExtractor import extract_text

text = extract_text(
    pdf_path: str,     # Path to PDF file
    pages: list | None = None  # Specific pages (optional)
) -> str
```

**Example:**
```python
# Extract all text
text = extract_text("/path/to/document.pdf")

# Extract specific pages
text = extract_text("/path/to/document.pdf", pages=[0, 1, 2])
```

### Page-by-Page Extraction

```python
from PDFExtractor import extract_pages

pages = extract_pages("/path/to/document.pdf")
for i, page_text in enumerate(pages):
    print(f"Page {i+1}:\n{page_text}\n")
```

### Metadata Extraction

```python
from PDFExtractor import get_metadata

metadata = get_metadata("/path/to/document.pdf")
print(f"Title: {metadata.get('title')}")
print(f"Author: {metadata.get('author')}")
print(f"Pages: {metadata.get('page_count')}")
```

---

## PDFFinder

**File:** `PDFFinder.py`

Find PDF files in directories.

### Main Function

#### find_pdfs()

```python
from PDFFinder import find_pdfs

pdfs = find_pdfs(
    directory: str,         # Directory to search
    recursive: bool = True  # Search subdirectories
) -> list[str]
```

**Example:**
```python
# Find all PDFs in directory
pdfs = find_pdfs("/path/to/documents")
for pdf in pdfs:
    print(pdf)

# Non-recursive search
pdfs = find_pdfs("/path/to/documents", recursive=False)
```

### Filter by Pattern

```python
from PDFFinder import find_pdfs_matching

# Find PDFs matching pattern
pdfs = find_pdfs_matching(
    directory="/path/to/documents",
    pattern="*2024*.pdf"
)
```

### Integration Example

```python
from PDFFinder import find_pdfs
from PDFParser import pdf2md
from PersistentStorage import PersistentStorage

storage = PersistentStorage()

# Find and ingest all PDFs
pdfs = find_pdfs("/path/to/library")
for pdf_path in pdfs:
    if not storage.has_been_ingested(pdf_path):
        try:
            markdown = pdf2md(pdf_path)
            storage.ingest_pdf(pdf_path)
            print(f"Ingested: {pdf_path}")
        except Exception as e:
            print(f"Failed: {pdf_path}: {e}")
```

---

## medai/tools/pdf.py

**File:** `medai/tools/pdf.py`

Additional PDF utilities in the core library.

### Functions

```python
from medai.tools.pdf import (
    is_valid_pdf,
    get_page_count,
    extract_images,
    merge_pdfs
)

# Validate PDF
if is_valid_pdf("/path/to/file.pdf"):
    print("Valid PDF")

# Get page count
pages = get_page_count("/path/to/document.pdf")

# Extract images
images = extract_images("/path/to/document.pdf", output_dir="/tmp/images")

# Merge PDFs
merge_pdfs(
    input_files=["/path/to/doc1.pdf", "/path/to/doc2.pdf"],
    output_file="/path/to/merged.pdf"
)
```

---

## Best Practices

### 1. Choose the Right Method

```python
def smart_parse(pdf_path: str) -> str:
    """Choose parsing method based on document characteristics."""
    page_count = get_page_count(pdf_path)

    if page_count > 100:
        # Large documents: use PyMuPDF for speed
        return pdf2md(pdf_path, method="pymupdf", timeout=300)
    elif is_academic_paper(pdf_path):
        # Academic papers: use LLMSherpa for structure
        return pdf2md(pdf_path, method="llmsherpa")
    else:
        # Default: PyMuPDF with fallback
        try:
            return pdf2md(pdf_path, method="pymupdf")
        except:
            return pdf2md(pdf_path, method="llamaparse")
```

### 2. Handle Timeouts

```python
import functools
import signal

def parse_with_retry(pdf_path: str, max_retries: int = 3) -> str:
    """Parse PDF with retry logic."""
    for attempt in range(max_retries):
        try:
            return pdf2md(pdf_path, timeout=60 * (attempt + 1))
        except TimeoutError:
            if attempt == max_retries - 1:
                raise
            print(f"Timeout, retrying with longer timeout...")
```

### 3. Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor
from PDFParser import pdf2md

def process_pdfs_parallel(pdf_paths: list[str], max_workers: int = 4):
    """Process multiple PDFs in parallel."""
    results = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(pdf2md, path): path
            for path in pdf_paths
        }

        for future in concurrent.futures.as_completed(future_to_path):
            path = future_to_path[future]
            try:
                results[path] = future.result()
            except Exception as e:
                results[path] = f"Error: {e}"

    return results
```

### 4. Caching

```python
from functools import lru_cache
import hashlib

def get_file_hash(filepath: str) -> str:
    """Get MD5 hash of file."""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

@lru_cache(maxsize=100)
def cached_pdf2md(file_hash: str, filepath: str) -> str:
    """Cache PDF parsing results by file hash."""
    return pdf2md(filepath)

def parse_pdf_cached(filepath: str) -> str:
    """Parse PDF with caching."""
    file_hash = get_file_hash(filepath)
    return cached_pdf2md(file_hash, filepath)
```

---

## Troubleshooting

### PDF Won't Parse

```python
# Try different methods
methods = ["pymupdf", "llamaparse", "llmsherpa"]
for method in methods:
    try:
        markdown = pdf2md(pdf_path, method=method)
        print(f"Success with {method}")
        break
    except Exception as e:
        print(f"{method} failed: {e}")
```

### Corrupted PDF

```python
from medai.tools.pdf import is_valid_pdf

if not is_valid_pdf(pdf_path):
    print("PDF is corrupted or invalid")
```

### Memory Issues

```python
# Process large PDFs page by page
from PDFExtractor import extract_pages

for page_num, page_text in enumerate(extract_pages(large_pdf)):
    process_page(page_num, page_text)
    # Text is garbage collected after each iteration
```

## Related Modules

- [RAG](research.md) - Uses PDFParser for document ingestion
- [PersistentStorage](storage.md) - Stores parsed documents
- [PGMedrXivScraper](publication-scraping.md) - Parses downloaded papers
