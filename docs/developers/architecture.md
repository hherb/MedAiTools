# MedAiTools Architecture Overview

This document describes the overall architecture of MedAiTools, including component interactions, data flows, and design patterns.

## System Architecture

MedAiTools follows a layered architecture pattern:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        UI LAYER (Web Panels)                         │
│   ResearcherUI  │  RAG_UI  │  StudyCritiqueUI  │  MedrXivPanel      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LOGIC LAYER                           │
│  Researcher  │  RAG  │  StudyCritique  │  MedrXivScraper            │
│  SemanticSummarizer  │  KeywordExtractor  │  SyntheticData          │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       SERVICE LAYER                                  │
│  LLM (medai.LLM)  │  PDFParser  │  EventDispatcher                  │
│  Configuration (medai.Settings)  │  Logging                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  STORAGE & DATABASE LAYER                            │
│  PersistentStorage (PostgreSQL + pgvector)  │  DBBackend (TinyDB)   │
│  File System Storage  │  DiskCache                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   EXTERNAL INTEGRATIONS                              │
│  LLM APIs (Ollama, OpenAI, Anthropic, Groq)                         │
│  Vector DBs (pgvector, Qdrant)  │  Web APIs (Tavily, MedRxiv)       │
└─────────────────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### UI Layer

The UI layer provides web-based interfaces built with [Panel](https://panel.holoviz.org/). Each UI module corresponds to a major feature:

- **ResearcherUI** (`ResearcherUI.py`) - Main research assistant interface
- **RAG_UI** (`RAG_UI.py`) - PDF document Q&A chat interface
- **StudyCritiqueUI** (`StudyCritiqueUI.py`) - Research paper analysis interface
- **MedrXivPanel** (`MedrXivPanel.py`) - Publication browser and fetcher

### Application Logic Layer

Contains the core business logic for each feature:

- **Researcher** - Orchestrates web research using GPT-Researcher
- **RAG** - Manages document ingestion and retrieval-augmented generation
- **StudyCritique** - Performs quality assessment of research papers
- **MedrXivScraper** - Fetches publications from MedRxiv API
- **SemanticSummarizer** - Graph-based text summarization
- **KeywordExtractor** - Multi-method keyword extraction (RAKE, YAKE)

### Service Layer

Provides shared services used across the application:

- **LLM** (`medai/LLM.py`) - Unified interface to multiple LLM providers
- **PDFParser** - Multi-method PDF to markdown conversion
- **EventDispatcher** - Publish/subscribe event system
- **Settings** (`medai/Settings.py`) - Centralized configuration management

### Storage Layer

Handles data persistence:

- **PersistentStorage** - PostgreSQL with pgvector for RAG indexing
- **DBBackend** - TinyDB for lightweight JSON storage
- **File System** - PDF and document storage

### External Integrations

Connections to external services:

- LLM providers (Ollama, OpenAI, Anthropic, Groq)
- Vector databases (Qdrant, pgvector)
- Research APIs (MedRxiv, PubMed, Tavily)

## Core Components

### Configuration System

The `Settings` singleton manages all application configuration:

```python
from medai.Settings import Settings

settings = Settings()

# Access configuration values as attributes
llm_provider = settings.llm_provider
embedding_model = settings.embedding_model

# Configuration sources (in priority order):
# 1. config_local.json (user overrides)
# 2. config.json (main config)
# 3. config.yaml (LLM/VectorDB specific)
# 4. Default values in Settings.py
```

### LLM Abstraction

The `LLM` class provides a unified interface to multiple LLM providers:

```python
from medai.LLM import LLM, Model

# Create an LLM instance
llm = LLM(provider="ollama", model="llama3.2")

# Generate a response
response = llm.generate("What is hypertension?")

# Streaming response
async for chunk in llm.generate_streaming("Explain diabetes"):
    print(chunk)
```

Supported providers:
- **Ollama** - Local LLM execution (default)
- **OpenAI** - GPT-3.5, GPT-4 models
- **Anthropic** - Claude models
- **Groq** - Fast inference
- **LiteLLM** - Universal adapter

### Event System

The `EventDispatcher` enables loose coupling between components:

```python
from EventDispatcher import EventDispatcher

dispatcher = EventDispatcher()

# Register a listener
def on_pdf_ingested(data):
    print(f"PDF ingested: {data['filename']}")

dispatcher.register_listener("pdf_ingested", on_pdf_ingested)

# Dispatch an event
dispatcher.dispatch_event("pdf_ingested", {"filename": "study.pdf"})
```

## Data Flows

### PDF Question-Answering Flow

```
┌──────────┐    ┌─────────┐    ┌───────────────────┐    ┌───────────┐
│  User    │───▶│ RAG_UI  │───▶│ PersistentStorage │───▶│ PDFParser │
│  Upload  │    │         │    │                   │    │           │
└──────────┘    └─────────┘    └───────────────────┘    └───────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │ Create Embeddings│
                               │ (BGE-M3/OpenAI)  │
                               └─────────────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │ Store in pgvector│
                               └─────────────────┘

┌──────────┐    ┌─────────┐    ┌───────────────────┐    ┌─────────┐
│  User    │───▶│ RAG_UI  │───▶│ Semantic Search   │───▶│   LLM   │
│  Query   │    │         │    │ (pgvector)        │    │         │
└──────────┘    └─────────┘    └───────────────────┘    └─────────┘
                                                              │
                                                              ▼
                                                       ┌───────────┐
                                                       │  Response │
                                                       └───────────┘
```

### Publication Scraping Flow

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│ MedrXivPanel│───▶│ MedrXivScraper   │───▶│ MedRxiv API │
│ (Date Range)│    │                  │    │             │
└─────────────┘    └──────────────────┘    └─────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ Store Metadata   │
                   │ (PostgreSQL)     │
                   └──────────────────┘
                            │
                            ▼
                   ┌──────────────────┐    ┌───────────┐
                   │ Fetch PDF        │───▶│ PDFParser │
                   │                  │    │           │
                   └──────────────────┘    └───────────┘
                                                  │
                                                  ▼
                                          ┌───────────────┐
                                          │ KeywordExtract│
                                          │ + Summarize   │
                                          └───────────────┘
```

### Synthetic Data Generation Flow

```
┌─────────────┐    ┌───────────────────────┐    ┌─────────────┐
│ Parameters  │───▶│ synthetic_demographics │───▶│ Person Data │
│             │    │                        │    │             │
└─────────────┘    └───────────────────────┘    └─────────────┘
                                                       │
                                                       ▼
                                            ┌───────────────────┐
                                            │ MedicalData       │
                                            │ (diagnosis, etc.) │
                                            └───────────────────┘
                                                       │
                                                       ▼
                                            ┌───────────────────┐
                                            │ HealthRecord      │
                                            │ Generator + LLM   │
                                            └───────────────────┘
                                                       │
                                                       ▼
                                            ┌───────────────────┐
                                            │ Clinical Note     │
                                            │ (Anonymized)      │
                                            └───────────────────┘
```

## Design Patterns

### Singleton Pattern

Used for components that should have exactly one instance:

- **Settings** - Application configuration
- **EventDispatcher** - Event bus
- **Logger** - Centralized logging
- **SharedMemory** - Inter-module communication

```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### Factory Pattern

Used for creating LLM model instances:

```python
def get_local_default_model():
    """Factory for local Ollama model"""
    return Model(
        provider="ollama",
        model_name="llama3.2",
        api_base="http://localhost:11434"
    )

def get_openai_multimodal_model():
    """Factory for OpenAI GPT-4 model"""
    return Model(
        provider="openai",
        model_name="gpt-4o"
    )
```

### Strategy Pattern

PDFParser uses multiple parsing strategies:

```python
class PDFParser:
    def pdf2md(self, pdf_path: str, method: str = "pymupdf"):
        if method == "pymupdf":
            return self._parse_with_pymupdf(pdf_path)
        elif method == "llamaparse":
            return self._parse_with_llamaparse(pdf_path)
        elif method == "llmsherpa":
            return self._parse_with_llmsherpa(pdf_path)
```

### Observer Pattern

EventDispatcher implements publish/subscribe:

```python
class EventDispatcher:
    def __init__(self):
        self._listeners = {}

    def register_listener(self, event: str, callback):
        self._listeners.setdefault(event, []).append(callback)

    def dispatch_event(self, event: str, data):
        for callback in self._listeners.get(event, []):
            callback(data)
```

### Adapter Pattern

LLM class adapts multiple providers to a common interface:

```python
class LLM:
    def generate(self, prompt: str) -> str:
        if self.provider == "ollama":
            return self._ollama_generate(prompt)
        elif self.provider == "openai":
            return self._openai_generate(prompt)
        elif self.provider == "anthropic":
            return self._anthropic_generate(prompt)
        # ... unified interface regardless of provider
```

## Database Schema

### PostgreSQL (PersistentStorage)

```sql
-- Documents table for RAG indexing
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filepath VARCHAR(500) UNIQUE,
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Embeddings with pgvector
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_text TEXT,
    embedding vector(1536),  -- Dimension depends on model
    chunk_index INTEGER
);

-- Publications from MedRxiv
CREATE TABLE publications (
    id SERIAL PRIMARY KEY,
    doi VARCHAR(100) UNIQUE,
    title TEXT,
    authors TEXT,
    abstract TEXT,
    category VARCHAR(100),
    published_date DATE,
    pdf_url TEXT,
    pdf_path TEXT,
    keywords TEXT[],
    summary TEXT,
    fetched_at TIMESTAMP DEFAULT NOW()
);
```

### TinyDB (DBBackend)

```python
# JSON-based local storage
{
    "medrxiv": [
        {
            "doi": "10.1101/2024.01.01.12345",
            "title": "Study Title",
            "abstract": "...",
            "fetched_at": "2024-01-15T10:30:00"
        }
    ],
    "research": [
        {
            "query": "diabetes treatment",
            "results": [...],
            "timestamp": "2024-01-15T10:30:00"
        }
    ]
}
```

## Extension Points

### Adding a New LLM Provider

1. Create adapter in `medai/LLM.py`:

```python
class NewProviderModel(Model):
    def generate(self, prompt: str) -> str:
        # Implement provider-specific logic
        pass
```

2. Register in factory function:

```python
def get_model(provider: str, model_name: str) -> Model:
    if provider == "new_provider":
        return NewProviderModel(model_name)
```

### Adding a New Data Source

1. Create scraper module:

```python
class NewSourceScraper:
    def fetch(self, query: str) -> list[dict]:
        # Implement fetching logic
        pass

    def store(self, data: list[dict]):
        # Store in PersistentStorage
        pass
```

2. Create UI panel if needed in a new `*Panel.py` file

### Adding a New Analysis Tool

1. Create analysis module:

```python
class NewAnalyzer:
    def __init__(self, llm: LLM):
        self.llm = llm

    def analyze(self, document: str) -> dict:
        # Implement analysis logic
        pass
```

2. Integrate with existing UI or create new panel

## Performance Considerations

### Embedding Generation

- Use batch processing for multiple documents
- Cache embeddings to avoid regeneration
- Consider using GPU acceleration for local embeddings

### Database Queries

- Use connection pooling (configured in PersistentStorage)
- Create appropriate indexes for frequently queried columns
- Use approximate nearest neighbor search for large vector collections

### LLM Calls

- Use streaming for long responses
- Implement request batching where possible
- Cache frequently requested responses

## Security Considerations

### Data Privacy

- All data is stored locally by default
- No data sent to external services unless explicitly configured
- API keys stored in environment variables or local config files

### Input Validation

- Sanitize file paths before processing
- Validate PDF files before ingestion
- Escape SQL parameters using parameterized queries

## Next Steps

- [Module Documentation](modules/) - Deep dive into each module
- [Quick Start Guide](quickstart.md) - Get started developing
- [Contributing Guide](contributing.md) - How to contribute
