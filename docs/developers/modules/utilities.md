# Utility Modules

This document covers utility modules in MedAiTools.

## EventDispatcher

**File:** `EventDispatcher.py`

A publish/subscribe event system using the Singleton pattern.

### Purpose

Enables loose coupling between components by allowing them to communicate through events without direct references.

### Usage

```python
from EventDispatcher import EventDispatcher

# Get singleton instance
dispatcher = EventDispatcher()

# Register a listener
def on_document_ingested(data):
    print(f"Document ingested: {data['path']}")
    print(f"Chunks created: {data['chunk_count']}")

dispatcher.register_listener("document_ingested", on_document_ingested)

# Dispatch an event (from another module)
dispatcher.dispatch_event("document_ingested", {
    "path": "/path/to/document.pdf",
    "chunk_count": 42
})

# Unregister when done
dispatcher.unregister_listener("document_ingested", on_document_ingested)
```

### Methods

#### register_listener()

```python
dispatcher.register_listener(
    event: str,           # Event name
    callback: Callable    # Function to call
) -> None
```

#### dispatch_event()

```python
dispatcher.dispatch_event(
    event: str,           # Event name
    data: Any = None      # Event data
) -> None
```

#### unregister_listener()

```python
dispatcher.unregister_listener(
    event: str,           # Event name
    callback: Callable    # Function to remove
) -> None
```

### Common Events

| Event | Data | Description |
|-------|------|-------------|
| `document_ingested` | `{path, chunk_count}` | PDF ingested into RAG |
| `publication_fetched` | `{doi, title}` | New publication downloaded |
| `research_complete` | `{query, report}` | Research finished |
| `llm_response` | `{prompt, response}` | LLM generated response |
| `error` | `{module, message}` | Error occurred |

### Event-Driven Architecture Example

```python
from EventDispatcher import EventDispatcher
from PersistentStorage import PersistentStorage
from KeywordExtractor import KeywordExtractor

dispatcher = EventDispatcher()
storage = PersistentStorage()
extractor = KeywordExtractor()

# When a document is ingested, extract keywords
def extract_keywords_on_ingest(data):
    path = data['path']
    content = storage.get_document_content(path)
    keywords = extractor.extract(content, top_n=10)
    storage.update_document(path, {"keywords": keywords})
    print(f"Keywords extracted for {path}")

dispatcher.register_listener("document_ingested", extract_keywords_on_ingest)
```

---

## medai/tools/apikeys.py

**File:** `medai/tools/apikeys.py`

API key management utilities.

### Functions

#### load_api_keys()

```python
from medai.tools.apikeys import load_api_keys

# Load from .env file and environment
keys = load_api_keys()

print(keys.get("OPENAI_API_KEY"))
print(keys.get("ANTHROPIC_API_KEY"))
```

#### get_api_key()

```python
from medai.tools.apikeys import get_api_key

# Get specific key with fallback
openai_key = get_api_key("OPENAI_API_KEY", default=None)

if openai_key:
    # Use OpenAI
    pass
else:
    # Fallback to local LLM
    pass
```

#### set_api_key()

```python
from medai.tools.apikeys import set_api_key

# Set key for current session
set_api_key("TAVILY_API_KEY", "tvly-...")
```

### API Key Sources

Keys are loaded from (in priority order):
1. Environment variables
2. `.env` file in project root
3. `~/.medai/credentials`
4. Config files

### Supported API Keys

| Key | Service |
|-----|---------|
| `OPENAI_API_KEY` | OpenAI API |
| `ANTHROPIC_API_KEY` | Anthropic Claude |
| `GROQ_API_KEY` | Groq API |
| `TAVILY_API_KEY` | Tavily Search |
| `SERPER_API_KEY` | Serper Search |
| `LLAMA_CLOUD_API_KEY` | LlamaParse |
| `HUGGINGFACE_TOKEN` | HuggingFace |

---

## Discussion

**File:** `Discussion.py`

Conversation/discussion handling utilities.

### Purpose

Manages conversation threads and discussion context.

### Usage

```python
from Discussion import Discussion

# Create a discussion
discussion = Discussion(topic="Diabetes Treatment")

# Add messages
discussion.add_message(role="user", content="What are the main treatments?")
discussion.add_message(role="assistant", content="The main treatments include...")

# Get full context
context = discussion.get_context()

# Export
export = discussion.export()
```

---

## annotation_categorizer

**File:** `annotation_categorizer.py`

Text annotation categorization utilities.

### Functions

```python
from annotation_categorizer import (
    read_terms,
    categorize_annotations,
    categorize_text
)

# Load categorization terms
terms = read_terms("categories.txt")

# Categorize annotations
annotations = ["diabetes", "insulin", "blood pressure"]
categories = categorize_annotations(annotations, terms)

# Categorize full text
text = "Patient presents with diabetes and hypertension..."
categories = categorize_text(text, terms)
```

---

## MyWebSearcher

**File:** `MyWebSearcher.py`

Web search wrapper for multiple providers.

### Usage

```python
from MyWebSearcher import WebSearcher

searcher = WebSearcher(provider="tavily")

# Search
results = searcher.search(
    query="diabetes treatment guidelines 2024",
    num_results=10
)

for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Snippet: {result['snippet']}")
```

### Providers

- `tavily` - Tavily API (recommended)
- `serper` - Serper Google Search
- `google` - Google Custom Search
- `bing` - Bing Search

---

## PubMedFetcher

**File:** `PubMedFetcher.py`

PubMed data retrieval utilities.

### Usage

```python
from PubMedFetcher import PubMedFetcher

fetcher = PubMedFetcher()

# Search PubMed
results = fetcher.search("diabetes AND treatment", max_results=100)

# Get article details
article = fetcher.get_article("12345678")  # PMID

# Fetch full text if available
full_text = fetcher.get_full_text("12345678")
```

---

## gptr.py

**File:** `gptr.py`

GPT-Researcher command-line interface entry point.

### Usage

```bash
# Run research from command line
python gptr.py "What are the latest diabetes treatments?"

# With options
python gptr.py "Research query" --provider openai --model gpt-4o --output report.md
```

### Programmatic Usage

```python
from gptr import run_research

report = run_research(
    query="Diabetes treatment guidelines",
    provider="openai",
    model="gpt-4o"
)

print(report)
```

---

## Best Practices

### Using EventDispatcher

1. **Register early, unregister when done**
```python
# In __init__
dispatcher.register_listener("event", self._handler)

# In cleanup/destructor
dispatcher.unregister_listener("event", self._handler)
```

2. **Use meaningful event names**
```python
# Good
"document_ingested"
"publication_fetched"

# Bad
"event1"
"done"
```

3. **Keep handlers fast**
```python
# Good - queue heavy work
def handler(data):
    queue.put(data)

# Bad - blocks event dispatch
def handler(data):
    time.sleep(60)  # Blocking
```

### API Key Security

1. **Never commit keys**
```python
# Use .env file (git-ignored)
# Or environment variables
```

2. **Validate keys before use**
```python
key = get_api_key("OPENAI_API_KEY")
if not key:
    raise ValueError("OpenAI API key not configured")
```

3. **Use appropriate scopes**
```python
# Different keys for different environments
if os.getenv("ENV") == "production":
    key = get_api_key("PROD_API_KEY")
else:
    key = get_api_key("DEV_API_KEY")
```

---

## Related Modules

- [Settings](core-settings.md) - Configuration management
- [LLM](core-llm.md) - LLM integration
- [Research](research.md) - Uses web searcher
