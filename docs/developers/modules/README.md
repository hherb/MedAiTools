# Module Documentation

This directory contains detailed documentation for each module in MedAiTools.

## Module Categories

### Core Library (`medai/`)
- [Settings](core-settings.md) - Configuration management
- [LLM](core-llm.md) - LLM abstraction layer

### Data Storage
- [PersistentStorage](storage.md) - PostgreSQL and RAG storage
- [DBBackend](storage.md#dbbackend) - TinyDB wrapper

### Document Processing
- [PDFParser](pdf-processing.md) - PDF to markdown conversion
- [PDFExtractor](pdf-processing.md#pdfextractor) - Text extraction
- [PDFFinder](pdf-processing.md#pdffinder) - PDF discovery

### Research & Analysis
- [RAG](research.md) - Retrieval Augmented Generation
- [Researcher](research.md#researcher) - GPT-Researcher integration
- [StudyCritique](analysis.md) - Paper quality assessment
- [MetaAnalysisAppraiser](analysis.md#metaanalysisappraiser) - Meta-analysis evaluation
- [KeywordExtractor](analysis.md#keywordextractor) - Keyword extraction
- [SemanticSummarizer](analysis.md#semanticsummarizer) - Text summarization

### Publication Scraping
- [PGMedrXivScraper](publication-scraping.md) - MedRxiv integration

### Synthetic Data
- [synthetic_demographics](synthetic-data.md) - Population generation
- [synthetic_health_record_generator](synthetic-data.md#health-records) - Clinical notes
- [MedicalData](synthetic-data.md#medicaldata) - Reference data

### UI Components
- [ResearcherUI](ui-components.md) - Main research interface
- [RAG_UI](ui-components.md#rag_ui) - PDF Q&A interface
- [MedrXivPanel](ui-components.md#medrxivpanel) - Publication browser
- [StudyCritiqueUI](ui-components.md#studycritiqueui) - Analysis interface

### Utilities
- [EventDispatcher](utilities.md) - Event system
