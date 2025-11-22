# Developer Quick Start Guide

This guide will help you set up a development environment for MedAiTools and start contributing.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** (3.10+ recommended)
- **PostgreSQL 14+** with pgvector extension
- **Git** for version control
- **Ollama** (optional, for local LLM execution)

## Step 1: Clone the Repository

```bash
git clone https://github.com/hherb/MedAiTools.git
cd MedAiTools
```

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
.\venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# For development, also install dev dependencies
pip install pytest pytest-cov black flake8 mypy
```

## Step 4: Database Setup

### Install PostgreSQL with pgvector

```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE EXTENSION vector;"

# macOS (Homebrew)
brew install postgresql pgvector
createdb medaitools
psql medaitools -c "CREATE EXTENSION vector;"
```

### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE medaitools;
CREATE USER medai WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE medaitools TO medai;

# Connect to the database and enable pgvector
\c medaitools
CREATE EXTENSION IF NOT EXISTS vector;
```

## Step 5: Configuration

### Create Local Configuration

Create `config_local.json` for your local settings (this file is git-ignored):

```json
{
    "db_host": "localhost",
    "db_port": 5432,
    "db_name": "medaitools",
    "db_user": "medai",
    "db_password": "your_password",

    "llm_provider": "ollama",
    "llm_model": "llama3.2",
    "ollama_base_url": "http://localhost:11434",

    "embedding_provider": "ollama",
    "embedding_model": "bge-m3",

    "library_path": "~/medai/library"
}
```

### Set Up API Keys (Optional)

For cloud LLM providers, create a `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Groq
GROQ_API_KEY=gsk_...

# Tavily (for web search)
TAVILY_API_KEY=tvly-...

# LlamaParse (for PDF parsing)
LLAMA_CLOUD_API_KEY=llx-...
```

## Step 6: Install Local LLM (Ollama)

For local LLM execution (recommended for development):

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull llama3.2
ollama pull bge-m3  # For embeddings
```

## Step 7: Verify Installation

### Test Database Connection

```python
from PersistentStorage import PersistentStorage

storage = PersistentStorage()
print(f"Connected: {storage.is_connected()}")
```

### Test LLM

```python
from medai.LLM import LLM

llm = LLM(provider="ollama", model="llama3.2")
response = llm.generate("Say hello!")
print(response)
```

### Test PDF Processing

```python
from PDFParser import pdf2md

markdown = pdf2md("pdf_sample.pdf")
print(markdown[:500])
```

## Step 8: Run the Application

### Start the Web UI

```python
# Run the main research UI
python -c "
import panel as pn
from ResearcherUI import ResearcherUI

ui = ResearcherUI()
pn.serve(ui.view(), port=5006)
"
```

Then open `http://localhost:5006` in your browser.

### Run Individual Components

```python
# PDF Q&A Interface
from RAG_UI import PDFPanel
import panel as pn

panel = PDFPanel()
pn.serve(panel.view(), port=5007)
```

## Project Structure for Developers

```
MedAiTools/
├── medai/                      # Core library (import with `from medai import ...`)
│   ├── Settings.py             # Configuration singleton - START HERE
│   ├── LLM.py                  # LLM abstraction - UNDERSTAND THIS
│   └── tools/
│       ├── apikeys.py          # API key management
│       └── pdf.py              # PDF utilities
│
├── Core Modules (alphabetical):
│   ├── DBBackend.py            # TinyDB wrapper
│   ├── EventDispatcher.py      # Event pub/sub system
│   ├── KeywordExtractor.py     # Keyword extraction
│   ├── MedicalData.py          # Medical reference data
│   ├── MetaAnalysisAppraiser.py # Meta-analysis quality
│   ├── PDFExtractor.py         # PDF text extraction
│   ├── PDFFinder.py            # PDF file discovery
│   ├── PDFParser.py            # PDF to markdown
│   ├── PersistentStorage.py    # PostgreSQL/RAG storage
│   ├── PGMedrXivScraper.py     # MedRxiv scraper
│   ├── RAG.py                  # RAG implementation
│   ├── RandomData.py           # Random data utilities
│   ├── Researcher.py           # GPT-Researcher wrapper
│   ├── SemanticSummarizer.py   # Text summarization
│   ├── StudyCritique.py        # Paper critique
│   ├── Summarizer.py           # Simple summarization
│   ├── SyntheticHealthData.py  # Synthetic patient data
│   ├── synthetic_demographics.py # Demographics generation
│   └── synthetic_health_record_generator.py # Clinical notes
│
├── UI Modules:
│   ├── DailyNews.py            # News panel
│   ├── MedrXivPanel.py         # Publication browser
│   ├── RAG_UI.py               # PDF Q&A interface
│   ├── ResearcherUI.py         # Main research UI
│   └── StudyCritiqueUI.py      # Paper analysis UI
│
├── Configuration:
│   ├── config.json             # Main configuration
│   ├── config.yaml             # LLM/VectorDB config
│   ├── config_local.json       # Local overrides (git-ignored)
│   └── requirements.txt        # Python dependencies
│
└── Data:
    └── seed_data/              # Medical reference data
```

## Common Development Tasks

### Adding a New Feature

1. **Identify the layer**: UI, Application Logic, Service, or Storage
2. **Create module**: Follow existing naming conventions
3. **Add tests**: Create test file in same directory
4. **Update docs**: Add to module documentation

### Modifying LLM Behavior

Edit `medai/LLM.py` or create a wrapper:

```python
from medai.LLM import LLM

class CustomLLM(LLM):
    def generate(self, prompt: str) -> str:
        # Add custom preprocessing
        enhanced_prompt = f"You are a medical expert. {prompt}"
        return super().generate(enhanced_prompt)
```

### Adding a New Data Source

1. Create scraper module (see `PGMedrXivScraper.py` as example)
2. Add storage methods to `PersistentStorage.py`
3. Create UI panel if needed
4. Register events with `EventDispatcher`

### Working with the RAG System

```python
from RAG import RAG

# Initialize
rag = RAG()

# Ingest a document
rag.ingest("path/to/document.pdf")

# Query with context
response = rag.query(
    question="What are the main findings?",
    pdfpath="path/to/document.pdf",
    top_k=5
)
```

## Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_rag.py -v
```

### Write a Test

```python
# test_mymodule.py
import pytest
from mymodule import MyClass

def test_basic_functionality():
    obj = MyClass()
    result = obj.process("input")
    assert result == "expected_output"

@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    obj = MyClass()
    result = obj.process(sample_data)
    assert "key" in result
```

## Debugging Tips

### Enable Debug Logging

```python
from medai.Settings import Logger

logger = Logger()
logger.setLevel("DEBUG")
```

### Inspect LLM Calls

```python
from medai.LLM import LLM

llm = LLM(provider="ollama", model="llama3.2")

# Enable verbose mode
response = llm.generate(prompt, verbose=True)
```

### Check Database Queries

```python
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
```

## Code Style

Follow these conventions:

- **PEP 8** for Python style
- **Type hints** for function signatures
- **Docstrings** for public functions
- **Black** for code formatting

```bash
# Format code
black .

# Check style
flake8 .

# Type checking
mypy .
```

## Next Steps

1. Read the [Architecture Overview](architecture.md)
2. Explore [Module Documentation](modules/)
3. Check the [Contributing Guide](contributing.md)
4. Look at existing code for patterns and conventions

## Troubleshooting

### Common Issues

**PostgreSQL connection fails:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check pgvector extension
psql -d medaitools -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

**Ollama not responding:**
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
systemctl restart ollama
```

**Import errors:**
```bash
# Ensure you're in the project root
cd /path/to/MedAiTools

# Check PYTHONPATH includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Out of memory with embeddings:**
```python
# Use smaller batch sizes
storage.ingest_pdf(pdf_path, batch_size=10)
```
