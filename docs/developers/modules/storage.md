# Storage Modules

This document covers the data persistence layers in MedAiTools.

## Overview

MedAiTools uses two storage backends:

1. **PersistentStorage** - PostgreSQL with pgvector for production use and RAG
2. **DBBackend** - TinyDB for lightweight local JSON storage

## PersistentStorage

**File:** `PersistentStorage.py`

PostgreSQL-based storage with vector embedding support for RAG systems.

### Features

- Connection pooling with psycopg3
- pgvector extension for semantic search
- LlamaIndex integration for RAG queries
- Automatic PDF embedding generation
- Publication metadata storage

### Constructor

```python
from PersistentStorage import PersistentStorage

storage = PersistentStorage(
    host: str = "localhost",
    port: int = 5432,
    dbname: str = "medaitools",
    user: str = "medai",
    password: str = "password"
)
```

Or use Settings:

```python
from PersistentStorage import PersistentStorage
from medai.Settings import Settings

settings = Settings()
storage = PersistentStorage(
    host=settings.db_host,
    port=settings.db_port,
    dbname=settings.db_name,
    user=settings.db_user,
    password=settings.db_password
)
```

### Core Methods

#### ingest_pdf()

Ingest a PDF document and create embeddings:

```python
storage.ingest_pdf(
    pdf_path: str,              # Path to PDF file
    metadata: dict | None = None,  # Optional metadata
    batch_size: int = 50        # Embedding batch size
) -> bool
```

**Example:**
```python
success = storage.ingest_pdf(
    "/path/to/research_paper.pdf",
    metadata={
        "author": "Smith et al.",
        "year": 2024,
        "category": "cardiology"
    }
)
```

#### get_query_engine()

Get a LlamaIndex query engine for semantic search:

```python
engine = storage.get_query_engine(
    pdf_path: str | None = None,  # Filter to specific document
    top_k: int = 5                 # Number of results
) -> QueryEngine
```

**Example:**
```python
engine = storage.get_query_engine(
    pdf_path="/path/to/document.pdf",
    top_k=3
)

response = engine.query("What are the main findings?")
print(response.response)
for node in response.source_nodes:
    print(f"- {node.text[:100]}...")
```

#### has_been_ingested()

Check if a document is already indexed:

```python
if not storage.has_been_ingested("/path/to/document.pdf"):
    storage.ingest_pdf("/path/to/document.pdf")
```

#### upsert()

Insert or update a record:

```python
storage.upsert(
    table: str,           # Table name
    data: dict,           # Record data
    conflict_column: str  # Column for conflict detection
) -> bool
```

**Example:**
```python
storage.upsert(
    table="publications",
    data={
        "doi": "10.1101/2024.01.01.12345",
        "title": "New Study",
        "abstract": "...",
        "fetched_at": datetime.now()
    },
    conflict_column="doi"
)
```

#### query()

Execute raw SQL query:

```python
results = storage.query(
    sql: str,
    params: tuple | None = None
) -> list[dict]
```

**Example:**
```python
results = storage.query(
    "SELECT * FROM publications WHERE category = %s ORDER BY published_date DESC LIMIT 10",
    ("cardiology",)
)
```

#### execute()

Execute SQL without returning results:

```python
storage.execute(
    "UPDATE publications SET processed = TRUE WHERE doi = %s",
    ("10.1101/2024.01.01.12345",)
)
```

### PublicationStorage Class

Specialized storage for research publications:

```python
from PersistentStorage import PublicationStorage

pub_storage = PublicationStorage()
```

#### store_publication()

```python
pub_storage.store_publication({
    "doi": "10.1101/2024.01.01.12345",
    "title": "Study on Hypertension Treatment",
    "authors": "Smith J, Doe A, Johnson B",
    "abstract": "Background: ...",
    "category": "cardiology",
    "published_date": "2024-01-15",
    "pdf_url": "https://...",
    "keywords": ["hypertension", "treatment", "clinical trial"]
})
```

#### get_publications()

```python
pubs = pub_storage.get_publications(
    category="cardiology",
    from_date="2024-01-01",
    to_date="2024-12-31",
    limit=100
)
```

#### search_publications()

Semantic search in publications:

```python
results = pub_storage.search_publications(
    query="diabetes treatment outcomes",
    top_k=10
)
```

### Database Schema

```sql
-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filepath VARCHAR(500) UNIQUE NOT NULL,
    filename VARCHAR(255),
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_documents_filepath ON documents(filepath);

-- Embeddings table with pgvector
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER,
    embedding vector(1536),  -- Dimension depends on model
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_embeddings_document ON embeddings(document_id);
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops);

-- Publications table
CREATE TABLE publications (
    id SERIAL PRIMARY KEY,
    doi VARCHAR(100) UNIQUE,
    title TEXT NOT NULL,
    authors TEXT,
    abstract TEXT,
    category VARCHAR(100),
    published_date DATE,
    pdf_url TEXT,
    pdf_path TEXT,
    keywords TEXT[],
    summary TEXT,
    processed BOOLEAN DEFAULT FALSE,
    fetched_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_publications_doi ON publications(doi);
CREATE INDEX idx_publications_category ON publications(category);
CREATE INDEX idx_publications_date ON publications(published_date);
```

### Connection Pooling

PersistentStorage uses connection pooling for efficiency:

```python
# Pool is managed automatically
storage = PersistentStorage()

# Multiple queries reuse connections
for i in range(100):
    storage.query("SELECT 1")  # Uses pooled connections

# Explicit connection management if needed
with storage.get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM publications")
        results = cur.fetchall()
```

---

## DBBackend

**File:** `DBBackend.py`

TinyDB-based local JSON storage for lightweight use cases.

### Features

- No database server required
- JSON file storage
- Simple query interface
- Good for development and small datasets

### Classes

#### DataBase

Base class for TinyDB operations:

```python
from DBBackend import DataBase

db = DataBase(
    db_path: str = "data.json",
    table_name: str = "default"
)
```

**Methods:**

```python
# Insert
db.insert({"key": "value", "timestamp": "2024-01-01"})

# Query
results = db.search(where("key") == "value")

# Get all
all_records = db.all()

# Update
db.update({"key": "new_value"}, where("key") == "value")

# Delete
db.remove(where("key") == "value")
```

#### DBMedrXiv

Specialized for MedRxiv publications:

```python
from DBBackend import DBMedrXiv

db = DBMedrXiv()

# Store publication
db.insert({
    "doi": "10.1101/2024.01.01.12345",
    "title": "Study Title",
    "abstract": "...",
    "fetched_at": "2024-01-15T10:30:00"
})

# Search by DOI
pub = db.get_by_doi("10.1101/2024.01.01.12345")

# Case-insensitive search
results = db.case_insensitive_search("title", "diabetes")

# Get by substring
results = db.get_by_substring("abstract", "clinical trial")
```

#### DBResearch

For storing research results:

```python
from DBBackend import DBResearch

db = DBResearch()

# Store research session
db.insert({
    "query": "diabetes treatment guidelines",
    "results": [...],
    "sources": [...],
    "timestamp": "2024-01-15T10:30:00"
})

# Get recent research
recent = db.get_recent(limit=10)
```

### Data Files

TinyDB stores data in JSON files:

```
data/
├── medrxiv.json      # Publication cache
├── research.json     # Research results
└── cache.json        # General cache
```

### Query Examples

```python
from DBBackend import DBMedrXiv
from tinydb import where

db = DBMedrXiv()

# Exact match
results = db.search(where("category") == "cardiology")

# Contains
results = db.search(where("title").search("diabetes"))

# Date range
results = db.search(
    (where("published_date") >= "2024-01-01") &
    (where("published_date") <= "2024-12-31")
)

# Multiple conditions
results = db.search(
    (where("category") == "cardiology") &
    (where("processed") == False)
)
```

---

## When to Use Which

| Use Case | Recommended Storage |
|----------|---------------------|
| Production RAG system | PersistentStorage |
| Semantic search | PersistentStorage (pgvector) |
| Large datasets (>10K records) | PersistentStorage |
| Development/testing | DBBackend |
| Simple caching | DBBackend |
| No database server | DBBackend |
| Publication storage | PersistentStorage |
| Quick prototyping | DBBackend |

## Migration Between Backends

```python
from DBBackend import DBMedrXiv
from PersistentStorage import PublicationStorage

# Export from TinyDB
tinydb = DBMedrXiv()
publications = tinydb.all()

# Import to PostgreSQL
pg_storage = PublicationStorage()
for pub in publications:
    pg_storage.store_publication(pub)
```

## Related Modules

- [RAG](research.md) - Uses PersistentStorage for document indexing
- [PGMedrXivScraper](publication-scraping.md) - Stores publications
- [Settings](core-settings.md) - Database configuration
