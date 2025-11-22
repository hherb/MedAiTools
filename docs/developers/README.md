# MedAiTools Developer Documentation

Welcome to the MedAiTools developer documentation. This guide provides comprehensive information for developers who want to contribute to or extend the MedAiTools platform.

## Table of Contents

1. [Quick Start Guide](quickstart.md) - Get up and running quickly
2. [Architecture Overview](architecture.md) - Understand the system design
3. [Module Documentation](modules/) - Detailed documentation for each module
4. [Contributing Guide](contributing.md) - How to contribute to the project
5. [API Reference](api-reference.md) - Core API documentation

## What is MedAiTools?

MedAiTools is an AI-assisted workbench for medical researchers. It provides tools for:

- **PDF Interrogation** - Upload and query medical documents using natural language
- **Publication Scraping** - Automated fetching and analysis of research papers from MedRxiv
- **Literature Review** - Deep web research with AI-powered summarization
- **Synthetic Health Records** - Generate realistic synthetic patient data for research

## Design Philosophy

MedAiTools is built around these core principles:

1. **Local-First Execution** - Prioritizes running models locally to protect patient privacy
2. **Open Source Dependencies** - Uses free, open-source alternatives where possible
3. **Privacy Protection** - No data leaves your environment unless explicitly configured
4. **Modularity** - Each component can be used independently or as part of the integrated platform
5. **Extensibility** - Easy to add new LLM providers, data sources, and analysis tools

## Tech Stack Overview

| Layer | Technology |
|-------|-----------|
| Frontend UI | Panel (web-based) |
| Backend | Python 3.8+ |
| LLM Providers | Ollama (local), OpenAI, Anthropic, Groq |
| Vector Database | Qdrant, pgvector (PostgreSQL) |
| Primary Database | PostgreSQL 14+ with pgvector extension |
| Cache | TinyDB, DiskCache |
| PDF Processing | PyMuPDF4LLM, LlamaParse |
| NLP | NLTK, RAKE, YAKE |
| Agent Framework | LangChain, LlamaIndex, GPT-Researcher |

## Directory Structure

```
MedAiTools/
├── medai/                  # Core library
│   ├── Settings.py         # Configuration singleton
│   ├── LLM.py              # LLM abstraction layer
│   └── tools/              # Utility tools
├── docs/                   # Documentation
│   ├── developers/         # Developer docs (you are here)
│   └── users/              # User documentation
├── seed_data/              # Medical reference data
├── icons/                  # UI assets
├── *.py                    # Application modules
├── config.json             # Main configuration
├── config.yaml             # LLM/VectorDB config
└── requirements.txt        # Python dependencies
```

## Getting Started

To start developing, see the [Quick Start Guide](quickstart.md).

For understanding the system architecture, see [Architecture Overview](architecture.md).

## Support

- Report issues on GitHub
- See the [Contributing Guide](contributing.md) for contribution guidelines
