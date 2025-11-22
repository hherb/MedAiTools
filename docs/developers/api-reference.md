# API Reference

This document provides detailed API documentation for the core MedAiTools modules.

## Table of Contents

- [Configuration (medai.Settings)](#configuration)
- [LLM Interface (medai.LLM)](#llm-interface)
- [RAG System](#rag-system)
- [PDF Processing](#pdf-processing)
- [Persistent Storage](#persistent-storage)
- [Publication Scraping](#publication-scraping)
- [Study Analysis](#study-analysis)
- [Synthetic Data Generation](#synthetic-data-generation)
- [Event System](#event-system)

---

## Configuration

### medai.Settings

Singleton class for application configuration.

```python
from medai.Settings import Settings

settings = Settings()
```

#### Attributes

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `llm_provider` | str | LLM provider name | "ollama" |
| `llm_model` | str | Model name | "llama3.2" |
| `embedding_provider` | str | Embedding provider | "ollama" |
| `embedding_model` | str | Embedding model | "bge-m3" |
| `db_host` | str | PostgreSQL host | "localhost" |
| `db_port` | int | PostgreSQL port | 5432 |
| `db_name` | str | Database name | "medaitools" |
| `library_path` | str | Document storage path | "~/medai/library" |

#### Methods

```python
# Access settings as attributes
provider = settings.llm_provider

# Load settings from file
settings.load_settings()

# Save settings
settings.save_settings({"llm_provider": "openai"})
```

### SharedMemory

Global shared state singleton.

```python
from medai.Settings import SharedMemory

memory = SharedMemory()
memory.current_document = "path/to/doc.pdf"
```

### Logger

Centralized logging singleton.

```python
from medai.Settings import Logger

logger = Logger()
logger.info("Processing document")
logger.error("Failed to connect", exc_info=True)
```

---

## LLM Interface

### medai.LLM.LLM

Unified interface for multiple LLM providers.

```python
from medai.LLM import LLM
```

#### Constructor

```python
LLM(
    provider: str = "ollama",
    model: str = "llama3.2",
    api_base: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4096
)
```

#### Methods

##### generate

```python
def generate(
    prompt: str,
    quickanswer: bool = True,
    **kwargs
) -> str | dict
```

Generate a response from the LLM.

**Parameters:**
- `prompt`: The input prompt
- `quickanswer`: If True, return string; if False, return full response dict

**Returns:** Generated text or response dictionary

**Example:**
```python
llm = LLM(provider="ollama", model="llama3.2")
response = llm.generate("What is hypertension?")
print(response)
```

##### generate_streaming

```python
async def generate_streaming(
    prompt: str,
    **kwargs
) -> AsyncGenerator[str, None]
```

Generate a streaming response.

**Example:**
```python
async for chunk in llm.generate_streaming("Explain diabetes"):
    print(chunk, end="", flush=True)
```

##### completion_call

```python
async def completion_call(
    prompt: str,
    **kwargs
) -> AsyncGenerator[str, None]
```

Async completion with streaming.

### Model Classes

```python
from medai.LLM import Model, OllamaModel

# Generic model
model = Model(
    provider="openai",
    model_name="gpt-4o",
    api_key="sk-..."
)

# Ollama-specific model
ollama = OllamaModel(
    model_name="llama3.2",
    api_base="http://localhost:11434"
)
```

### Factory Functions

```python
from medai.LLM import (
    get_local_default_model,
    get_openai_multimodal_model,
    get_groq_model
)

# Get default local Ollama model
local_model = get_local_default_model()

# Get OpenAI GPT-4
openai_model = get_openai_multimodal_model()

# Get Groq model
groq_model = get_groq_model()
```

### Utility Functions

```python
from medai.LLM import answer_this

# Quick one-off LLM call
response = answer_this(
    prompt="What is the capital of France?",
    modelname="llama3.2",
    api_base="http://localhost:11434"
)
```

---

## RAG System

### RAG

Retrieval-Augmented Generation for document Q&A.

```python
from RAG import RAG
```

#### Constructor

```python
RAG(
    storage: PersistentStorage | None = None,
    llm: LLM | None = None
)
```

#### Methods

##### ingest

```python
def ingest(
    pdfpath: str,
    force: bool = False
) -> None
```

Ingest a PDF document into the RAG system.

**Parameters:**
- `pdfpath`: Path to PDF file
- `force`: Re-ingest even if already indexed

**Example:**
```python
rag = RAG()
rag.ingest("research_paper.pdf")
```

##### query

```python
def query(
    question: str,
    pdfpath: str | None = None,
    top_k: int = 5
) -> Response
```

Query the RAG system.

**Parameters:**
- `question`: Natural language question
- `pdfpath`: Optional filter to specific document
- `top_k`: Number of context chunks to retrieve

**Returns:** Response object with answer and sources

**Example:**
```python
response = rag.query(
    question="What are the main findings?",
    pdfpath="research_paper.pdf"
)
print(response.response)
print(response.source_nodes)
```

##### has_been_ingested

```python
def has_been_ingested(pdfpath: str) -> bool
```

Check if a document has been indexed.

##### set_llm

```python
def set_llm(
    provider: str,
    model: str,
    temperature: float = 0.7
) -> None
```

Change the LLM used for generation.

---

## PDF Processing

### PDFParser

Multi-method PDF to markdown conversion.

```python
from PDFParser import pdf2md, PDFParser
```

#### Functions

##### pdf2md

```python
def pdf2md(
    pdf_path: str,
    method: str = "pymupdf",
    timeout: int = 60
) -> str
```

Convert PDF to markdown text.

**Parameters:**
- `pdf_path`: Path to PDF file
- `method`: Parsing method ("pymupdf", "llamaparse", "llmsherpa")
- `timeout`: Timeout in seconds

**Returns:** Markdown text content

**Example:**
```python
markdown = pdf2md("document.pdf", method="pymupdf")
print(markdown[:1000])
```

### PDFExtractor

Simple text extraction.

```python
from PDFExtractor import extract_text

text = extract_text("document.pdf")
```

### PDFFinder

Find PDF files in directories.

```python
from PDFFinder import find_pdfs

pdfs = find_pdfs("/path/to/directory")
for pdf in pdfs:
    print(pdf)
```

---

## Persistent Storage

### PersistentStorage

PostgreSQL database abstraction with RAG support.

```python
from PersistentStorage import PersistentStorage
```

#### Constructor

```python
PersistentStorage(
    host: str = "localhost",
    port: int = 5432,
    dbname: str = "medaitools",
    user: str = "medai",
    password: str = "password"
)
```

#### Methods

##### ingest_pdf

```python
def ingest_pdf(
    pdf_path: str,
    metadata: dict | None = None,
    batch_size: int = 50
) -> bool
```

Ingest a PDF and create embeddings.

**Example:**
```python
storage = PersistentStorage()
storage.ingest_pdf(
    "research.pdf",
    metadata={"author": "Smith", "year": 2024}
)
```

##### get_query_engine

```python
def get_query_engine(
    pdf_path: str | None = None,
    top_k: int = 5
) -> QueryEngine
```

Get a LlamaIndex query engine for semantic search.

##### has_been_ingested

```python
def has_been_ingested(pdf_path: str) -> bool
```

Check if document exists in storage.

##### upsert

```python
def upsert(
    table: str,
    data: dict,
    conflict_column: str
) -> bool
```

Insert or update a record.

### PublicationStorage

Specialized storage for publications.

```python
from PersistentStorage import PublicationStorage

pub_storage = PublicationStorage()
pub_storage.store_publication({
    "doi": "10.1101/2024.01.01.12345",
    "title": "Study Title",
    "abstract": "...",
    "authors": "Smith J, Doe A"
})
```

---

## Publication Scraping

### MedrXivScraper

Fetch publications from MedRxiv.

```python
from PGMedrXivScraper import MedrXivScraper
```

#### Constructor

```python
MedrXivScraper(
    storage: PersistentStorage | None = None
)
```

#### Methods

##### fetch_from_medrXiv

```python
def fetch_from_medrXiv(
    from_date: str,
    to_date: str,
    fetch_pdfs: bool = False,
    category: str | None = None
) -> list[dict]
```

Fetch publications from date range.

**Parameters:**
- `from_date`: Start date (YYYY-MM-DD)
- `to_date`: End date (YYYY-MM-DD)
- `fetch_pdfs`: Also download PDF files
- `category`: Filter by category

**Returns:** List of publication dictionaries

**Example:**
```python
scraper = MedrXivScraper()
pubs = scraper.fetch_from_medrXiv(
    from_date="2024-01-01",
    to_date="2024-01-31",
    category="infectious diseases"
)
```

##### fetch_pdf_from_medrXiv

```python
def fetch_pdf_from_medrXiv(
    publication: dict,
    upsert: bool = False
) -> str
```

Download PDF for a publication.

**Returns:** Local path to downloaded PDF

##### count

```python
def count() -> int
```

Get total publications in storage.

---

## Study Analysis

### StudyCritique

Research paper quality assessment.

```python
from StudyCritique import StudyCritique
```

#### Constructor

```python
StudyCritique(
    llm: LLM | None = None
)
```

#### Methods

##### summary

```python
def summary(
    document: str,
    max_sentences: int = 15
) -> str
```

Generate a summary of the document.

##### critique

```python
def critique(document: str) -> str
```

Generate a quality critique.

**Returns:** Detailed critique with identified weaknesses

**Example:**
```python
critique = StudyCritique()
with open("study.md") as f:
    document = f.read()

summary = critique.summary(document)
analysis = critique.critique(document)
print(analysis)
```

##### rerank

```python
def rerank(
    summaries: list[str],
    query: str,
    top_k: int = 5
) -> list[str]
```

Rerank summaries by relevance to query.

### MetaAnalysisAppraiser

Quality assessment for meta-analyses.

```python
from MetaAnalysisAppraiser import MetaAnalysisAppraiser

appraiser = MetaAnalysisAppraiser()
score = appraiser.appraise(document_text)
```

### KeywordExtractor

Extract keywords from text.

```python
from KeywordExtractor import KeywordExtractor, YakeKeywordExtractor

extractor = KeywordExtractor(method="yake")
keywords = extractor.extract(text, top_n=10)
```

### SemanticSummarizer

Graph-based semantic summarization.

```python
from SemanticSummarizer import SemanticSummarizer

summarizer = SemanticSummarizer()
summary = summarizer.summarize(long_text, ratio=0.3)
```

---

## Synthetic Data Generation

### synthetic_demographics

Generate Australian population data.

```python
from synthetic_demographics import (
    create_synthetic_person,
    get_random_address,
    get_random_postcode
)
```

#### create_synthetic_person

```python
def create_synthetic_person(
    age: int | None = None,
    gender: str | None = None,
    state: str | None = None
) -> dict
```

Generate a synthetic person with demographics.

**Returns:** Dictionary with name, address, DOB, Medicare number, etc.

**Example:**
```python
person = create_synthetic_person(age=45, gender="F")
print(person["given_name"], person["family_name"])
print(person["address"])
print(person["medicare_number"])
```

### synthetic_health_record_generator

Generate clinical notes.

```python
from synthetic_health_record_generator import (
    generate_health_record,
    generate_synthetic_note
)
```

#### generate_health_record

```python
def generate_health_record(
    person: dict,
    encounter_type: str = "consultation",
    diagnosis: str | None = None,
    **kwargs
) -> str
```

Generate a clinical note for a patient encounter.

**Example:**
```python
person = create_synthetic_person()
note = generate_health_record(
    person,
    encounter_type="consultation",
    diagnosis="Type 2 Diabetes"
)
print(note)
```

### MedicalData

Medical reference data.

```python
from MedicalData import (
    random_diagnosis,
    random_facility,
    random_speciality
)

diagnosis = random_diagnosis()
facility = random_facility(type=1)  # 1=hospital
specialty = random_speciality()
```

### RandomData

Random data utilities.

```python
from RandomData import (
    get_random_genderstring,
    get_random_date,
    randomize_date_format
)

gender = get_random_genderstring()
date = get_random_date(min_year=1950, max_year=2000)
formatted = randomize_date_format(date)
```

---

## Event System

### EventDispatcher

Publish/subscribe event system.

```python
from EventDispatcher import EventDispatcher
```

#### Singleton Access

```python
dispatcher = EventDispatcher()
```

#### Methods

##### register_listener

```python
def register_listener(
    event: str,
    callback: Callable
) -> None
```

Register a callback for an event.

##### dispatch_event

```python
def dispatch_event(
    event: str,
    data: Any = None
) -> None
```

Dispatch an event to all listeners.

**Example:**
```python
def on_document_ingested(data):
    print(f"Document ingested: {data['path']}")

dispatcher = EventDispatcher()
dispatcher.register_listener("document_ingested", on_document_ingested)

# Later, when a document is ingested:
dispatcher.dispatch_event("document_ingested", {"path": "/path/to/doc.pdf"})
```

##### unregister_listener

```python
def unregister_listener(
    event: str,
    callback: Callable
) -> None
```

Remove a listener.

---

## Error Handling

Most functions raise standard Python exceptions:

- `FileNotFoundError`: File doesn't exist
- `ValueError`: Invalid parameter
- `ConnectionError`: Database/API connection failed
- `TimeoutError`: Operation timed out

**Example:**
```python
from RAG import RAG

rag = RAG()

try:
    rag.ingest("nonexistent.pdf")
except FileNotFoundError:
    print("PDF file not found")
except ConnectionError:
    print("Database connection failed")
```

---

## Type Definitions

Common types used throughout the API:

```python
from typing import TypedDict, Optional

class Publication(TypedDict):
    doi: str
    title: str
    authors: str
    abstract: str
    category: Optional[str]
    published_date: str
    pdf_url: Optional[str]
    pdf_path: Optional[str]

class SyntheticPerson(TypedDict):
    given_name: str
    family_name: str
    date_of_birth: str
    gender: str
    address: str
    postcode: str
    state: str
    medicare_number: str
    phone: str
    email: str
```
