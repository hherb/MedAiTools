# Research Modules

This document covers the research and RAG (Retrieval-Augmented Generation) capabilities in MedAiTools.

## Overview

| Module | Purpose |
|--------|---------|
| RAG | Document Q&A with semantic search |
| Researcher | Automated web research |

---

## RAG

**File:** `RAG.py`

Retrieval-Augmented Generation for document question-answering.

### How It Works

1. **Ingestion**: PDF is parsed, chunked, and embedded
2. **Storage**: Embeddings stored in pgvector
3. **Query**: Question is embedded and similar chunks retrieved
4. **Generation**: LLM generates answer using retrieved context

```
┌──────────┐     ┌─────────┐     ┌───────────┐     ┌──────────┐
│   PDF    │────▶│ Chunker │────▶│ Embedder  │────▶│ pgvector │
└──────────┘     └─────────┘     └───────────┘     └──────────┘

┌──────────┐     ┌───────────┐     ┌──────────┐     ┌──────────┐
│ Question │────▶│ Embedder  │────▶│ pgvector │────▶│   LLM    │
└──────────┘     └───────────┘     │ (search) │     │(generate)│
                                   └──────────┘     └──────────┘
```

### Constructor

```python
from RAG import RAG

rag = RAG(
    storage: PersistentStorage | None = None,  # Custom storage
    llm: LLM | None = None                     # Custom LLM
)
```

### Methods

#### ingest()

Ingest a PDF document:

```python
rag.ingest(
    pdfpath: str,      # Path to PDF file
    force: bool = False # Re-ingest even if exists
) -> None
```

**Example:**
```python
rag = RAG()

# Initial ingestion
rag.ingest("/path/to/research_paper.pdf")

# Force re-ingestion
rag.ingest("/path/to/research_paper.pdf", force=True)
```

#### query()

Query the document(s):

```python
response = rag.query(
    question: str,           # Natural language question
    pdfpath: str | None = None,  # Filter to specific doc
    top_k: int = 5           # Context chunks to retrieve
) -> Response
```

**Example:**
```python
# Query all documents
response = rag.query("What are common treatments for diabetes?")
print(response.response)

# Query specific document
response = rag.query(
    question="What are the main findings?",
    pdfpath="/path/to/specific_study.pdf"
)

# Show sources
for node in response.source_nodes:
    print(f"Source: {node.metadata.get('filename')}")
    print(f"Text: {node.text[:200]}...")
```

#### has_been_ingested()

Check if document is indexed:

```python
if not rag.has_been_ingested("/path/to/document.pdf"):
    rag.ingest("/path/to/document.pdf")
```

#### set_llm()

Change the LLM:

```python
# Switch to a different model
rag.set_llm(
    provider="openai",
    model="gpt-4o",
    temperature=0.3
)
```

### Response Object

```python
response = rag.query("What is the methodology?")

# Main response text
print(response.response)

# Source nodes with relevance scores
for node in response.source_nodes:
    print(f"Score: {node.score}")
    print(f"Text: {node.text}")
    print(f"Metadata: {node.metadata}")
```

### Configuration

```python
rag = RAG()

# Configure chunking
rag.chunk_size = 512
rag.chunk_overlap = 50

# Configure retrieval
rag.top_k = 5
rag.similarity_threshold = 0.7

# Configure generation
rag.temperature = 0.3
rag.max_tokens = 1024
```

### Custom Prompts

```python
CUSTOM_QA_PROMPT = """
You are a medical research assistant. Answer the question based ONLY on the provided context.
If the answer is not in the context, say "I cannot find this information in the document."

Context:
{context}

Question: {question}

Answer:
"""

rag.set_qa_prompt(CUSTOM_QA_PROMPT)
```

### Multi-Document Queries

```python
# Ingest multiple documents
pdfs = ["/path/to/study1.pdf", "/path/to/study2.pdf", "/path/to/study3.pdf"]
for pdf in pdfs:
    rag.ingest(pdf)

# Query across all documents
response = rag.query(
    "Compare the methodologies used in these studies",
    top_k=10  # Get more context for comparison
)
```

---

## Researcher

**File:** `Researcher.py`

Automated web research using GPT-Researcher.

### How It Works

1. **Query Analysis**: Breaks research question into sub-queries
2. **Web Search**: Searches multiple sources (Tavily, Google, etc.)
3. **Content Extraction**: Scrapes and processes relevant pages
4. **Synthesis**: Generates comprehensive research report

### Main Function

#### research()

```python
from Researcher import research

report = await research(
    query: str,              # Research question
    report_type: str = "research_report",  # Type of report
    sources: list[str] | None = None       # Specific sources
) -> str
```

**Example:**
```python
import asyncio

async def run_research():
    report = await research(
        "What are the latest treatments for Type 2 Diabetes?"
    )
    print(report)

asyncio.run(run_research())
```

### Report Types

- `research_report` - Comprehensive research report (default)
- `resource_report` - List of resources and summaries
- `outline_report` - Structured outline
- `custom_report` - Custom format

```python
# Resource report
report = await research(
    "Diabetes medications",
    report_type="resource_report"
)

# Outline
report = await research(
    "Heart disease prevention",
    report_type="outline_report"
)
```

### Configuration

```python
from Researcher import Configuration

config = Configuration(
    llm_provider="openai",
    fast_llm_model="gpt-3.5-turbo-16k",
    smart_llm_model="gpt-4o",
    embedding_provider="openai",
    max_iterations=5,
    max_search_results=10,
    report_format="markdown"
)

report = await research("Query", config=config)
```

### Search Providers

Configure search in `config.json`:

```json
{
    "retriever": "tavily",  // or "google", "serper", "bing"
    "max_search_results_per_query": 5
}
```

### Source Filtering

```python
# Research from specific domains
report = await research(
    "COVID-19 vaccine efficacy",
    sources=[
        "pubmed.ncbi.nlm.nih.gov",
        "nejm.org",
        "thelancet.com"
    ]
)
```

### Streaming Results

```python
from Researcher import research_streaming

async for chunk in research_streaming("Research query"):
    print(chunk, end="", flush=True)
```

### Integration with UI

The `ResearcherUI` module provides a web interface:

```python
from ResearcherUI import ResearcherUI
import panel as pn

ui = ResearcherUI()
pn.serve(ui.view(), port=5006)
```

---

## Common Patterns

### RAG + Research Pipeline

```python
async def comprehensive_research(topic: str):
    """Combine RAG and web research."""

    # Step 1: Check local documents
    rag = RAG()
    local_response = rag.query(topic)

    # Step 2: If insufficient, do web research
    if "cannot find" in local_response.response.lower():
        web_report = await research(topic)
        return web_report

    return local_response.response
```

### Document-Grounded Research

```python
async def grounded_research(topic: str, reference_pdfs: list[str]):
    """Research grounded in specific documents."""

    rag = RAG()

    # Ingest reference documents
    for pdf in reference_pdfs:
        rag.ingest(pdf)

    # Get document context
    context = rag.query(topic, top_k=10)

    # Research with context
    enhanced_query = f"""
    Based on the following background from reference documents:

    {context.response}

    Research the following topic and provide additional insights:
    {topic}
    """

    return await research(enhanced_query)
```

### Caching Research Results

```python
from DBBackend import DBResearch
from datetime import datetime, timedelta

db = DBResearch()

async def cached_research(query: str, cache_hours: int = 24):
    """Research with caching."""

    # Check cache
    cached = db.search(
        (where("query") == query) &
        (where("timestamp") > (datetime.now() - timedelta(hours=cache_hours)).isoformat())
    )

    if cached:
        return cached[0]["result"]

    # Fresh research
    result = await research(query)

    # Cache result
    db.insert({
        "query": query,
        "result": result,
        "timestamp": datetime.now().isoformat()
    })

    return result
```

---

## Error Handling

### RAG Errors

```python
from RAG import RAG, RAGError, DocumentNotFoundError

rag = RAG()

try:
    rag.ingest("/nonexistent.pdf")
except FileNotFoundError:
    print("PDF file not found")

try:
    response = rag.query("Question", pdfpath="/path/to/unknown.pdf")
except DocumentNotFoundError:
    print("Document not in index")
```

### Research Errors

```python
from Researcher import research, ResearchError, RateLimitError

try:
    report = await research("Query")
except RateLimitError:
    print("API rate limit exceeded")
except ResearchError as e:
    print(f"Research failed: {e}")
```

---

## Performance Tips

### RAG Performance

```python
# Use appropriate chunk size
rag.chunk_size = 512  # Balance between context and precision

# Limit top_k for faster queries
response = rag.query(question, top_k=3)

# Use similarity threshold to filter weak matches
rag.similarity_threshold = 0.7
```

### Research Performance

```python
# Limit iterations for faster results
config = Configuration(max_iterations=3)

# Use faster model for initial search
config = Configuration(
    fast_llm_model="gpt-3.5-turbo",
    smart_llm_model="gpt-4"  # Only for synthesis
)
```

---

## Related Modules

- [PersistentStorage](storage.md) - RAG storage backend
- [PDFParser](pdf-processing.md) - PDF parsing for ingestion
- [LLM](core-llm.md) - LLM for generation
- [ResearcherUI](ui-components.md) - Web interface
