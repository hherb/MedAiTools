# Analysis Modules

This document covers the text analysis and critique capabilities in MedAiTools.

## Overview

| Module | Purpose |
|--------|---------|
| StudyCritique | Research paper quality assessment |
| MetaAnalysisAppraiser | Meta-analysis evaluation |
| KeywordExtractor | Keyword extraction |
| SemanticSummarizer | Graph-based summarization |
| Summarizer | Simple LLM summarization |

---

## StudyCritique

**File:** `StudyCritique.py`

AI-powered research paper quality assessment.

### Purpose

Analyzes research papers to:
- Generate concise summaries
- Identify methodological weaknesses
- Evaluate study design
- Assess bias risk

### Constructor

```python
from StudyCritique import StudyCritique

critique = StudyCritique(
    llm: LLM | None = None  # Custom LLM (optional)
)
```

### Methods

#### summary()

Generate a summary of the document:

```python
summary = critique.summary(
    document: str,        # Document text (markdown/plain)
    max_sentences: int = 15  # Maximum sentences
) -> str
```

**Example:**
```python
from StudyCritique import StudyCritique
from PDFParser import pdf2md

critique = StudyCritique()

# Parse PDF to text
document = pdf2md("/path/to/study.pdf")

# Generate summary
summary = critique.summary(document, max_sentences=10)
print(summary)
```

#### critique()

Generate a quality critique:

```python
analysis = critique.critique(
    document: str  # Document text
) -> str
```

**Example:**
```python
analysis = critique.critique(document)
print(analysis)
```

**Output includes:**
- Study design assessment
- Sample size evaluation
- Methodology critique
- Statistical analysis review
- Bias identification
- Limitations
- Overall quality score

#### rerank()

Rerank summaries by relevance to a query:

```python
ranked = critique.rerank(
    summaries: list[str],  # List of summaries
    query: str,            # Search query
    top_k: int = 5         # Number to return
) -> list[str]
```

**Example:**
```python
# Multiple document summaries
summaries = [
    critique.summary(doc1),
    critique.summary(doc2),
    critique.summary(doc3)
]

# Rank by relevance
ranked = critique.rerank(
    summaries,
    query="diabetes treatment outcomes",
    top_k=2
)
```

### Assessment Criteria

The critique uses these criteria (based on NIH/NHLBI guidelines):

1. **Study Design**
   - Appropriate for research question?
   - Control group present?
   - Randomization used?

2. **Sample**
   - Size adequate?
   - Selection bias addressed?
   - Demographics described?

3. **Methods**
   - Interventions clearly described?
   - Outcomes pre-specified?
   - Blinding implemented?

4. **Analysis**
   - Statistical methods appropriate?
   - Missing data handled?
   - Confounders addressed?

5. **Reporting**
   - Results clearly presented?
   - Limitations discussed?
   - Conflicts disclosed?

---

## MetaAnalysisAppraiser

**File:** `MetaAnalysisAppraiser.py`

Specialized assessment for meta-analyses and systematic reviews.

### Purpose

Evaluates meta-analyses using NHLBI quality assessment criteria.

### Constructor

```python
from MetaAnalysisAppraiser import MetaAnalysisAppraiser

appraiser = MetaAnalysisAppraiser(
    llm: LLM | None = None
)
```

### Methods

#### appraise()

```python
assessment = appraiser.appraise(
    document: str  # Meta-analysis text
) -> dict
```

**Returns:**
```python
{
    "overall_quality": "good",  # good, fair, poor
    "criteria": {
        "research_question": {"met": True, "notes": "..."},
        "literature_search": {"met": True, "notes": "..."},
        "inclusion_criteria": {"met": False, "notes": "..."},
        # ... more criteria
    },
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "recommendations": ["...", "..."]
}
```

### Criteria Assessed

1. Clear research question/PICO
2. Comprehensive literature search
3. Pre-specified inclusion/exclusion criteria
4. Dual reviewer screening
5. Quality assessment of included studies
6. Heterogeneity assessment
7. Publication bias evaluation
8. Appropriate meta-analytic methods

---

## KeywordExtractor

**File:** `KeywordExtractor.py`

Multi-method keyword extraction.

### Supported Methods

- **YAKE** - Unsupervised keyword extraction
- **RAKE** - Rapid Automatic Keyword Extraction
- **Custom** - LLM-based extraction

### Constructor

```python
from KeywordExtractor import KeywordExtractor

extractor = KeywordExtractor(
    method: str = "yake"  # "yake", "rake", or "llm"
)
```

### Methods

#### extract()

```python
keywords = extractor.extract(
    text: str,      # Input text
    top_n: int = 10 # Number of keywords
) -> list[str]
```

**Example:**
```python
extractor = KeywordExtractor(method="yake")

text = """
Diabetes mellitus is a metabolic disease characterized by
hyperglycemia resulting from defects in insulin secretion,
insulin action, or both.
"""

keywords = extractor.extract(text, top_n=5)
print(keywords)
# ['diabetes mellitus', 'metabolic disease', 'hyperglycemia',
#  'insulin secretion', 'insulin action']
```

### YakeKeywordExtractor

```python
from KeywordExtractor import YakeKeywordExtractor

extractor = YakeKeywordExtractor(
    language: str = "en",
    max_ngram_size: int = 3,
    deduplication_threshold: float = 0.9
)

keywords = extractor.extract(text, top_n=10)
```

### RakeKeywordExtractor

```python
from KeywordExtractor import RakeKeywordExtractor

extractor = RakeKeywordExtractor()
keywords = extractor.extract(text, top_n=10)
```

### LLM-Based Extraction

```python
from KeywordExtractor import KeywordExtractor

extractor = KeywordExtractor(method="llm")
keywords = extractor.extract(
    text,
    top_n=10,
    context="medical research"  # Domain hint
)
```

---

## SemanticSummarizer

**File:** `SemanticSummarizer.py`

Graph-based semantic text summarization.

### How It Works

1. Split text into sentences
2. Create sentence embeddings
3. Build similarity graph
4. Apply TextRank algorithm
5. Extract top sentences

### Constructor

```python
from SemanticSummarizer import SemanticSummarizer

summarizer = SemanticSummarizer(
    embedding_model: str = "all-MiniLM-L6-v2"
)
```

### Methods

#### summarize()

```python
summary = summarizer.summarize(
    text: str,         # Input text
    ratio: float = 0.3 # Compression ratio (0-1)
) -> str
```

**Example:**
```python
summarizer = SemanticSummarizer()

long_text = """
[Long research paper text...]
"""

summary = summarizer.summarize(long_text, ratio=0.2)
print(summary)
```

#### segment_text()

Split text into semantic segments:

```python
segments = summarizer.segment_text(
    text: str,
    min_segment_length: int = 100
) -> list[str]
```

#### make_sentences()

Extract sentences from text:

```python
sentences = summarizer.make_sentences(text)
```

### Configuration

```python
summarizer = SemanticSummarizer()

# Adjust parameters
summarizer.damping = 0.85  # TextRank damping factor
summarizer.min_similarity = 0.3  # Minimum sentence similarity
summarizer.min_sentence_length = 10  # Minimum words per sentence
```

---

## Summarizer

**File:** `Summarizer.py`

Simple LLM-based summarization.

### Constructor

```python
from Summarizer import Summarizer

summarizer = Summarizer(
    llm: LLM | None = None
)
```

### Methods

#### summarize()

```python
summary = summarizer.summarize(
    text: str,
    max_words: int = 200,
    style: str = "concise"  # "concise", "detailed", "bullet"
) -> str
```

**Example:**
```python
summarizer = Summarizer()

# Concise summary
summary = summarizer.summarize(document, max_words=100)

# Detailed summary
summary = summarizer.summarize(document, max_words=500, style="detailed")

# Bullet points
summary = summarizer.summarize(document, style="bullet")
```

---

## Common Patterns

### Complete Paper Analysis Pipeline

```python
from PDFParser import pdf2md
from StudyCritique import StudyCritique
from KeywordExtractor import KeywordExtractor
from SemanticSummarizer import SemanticSummarizer

def analyze_paper(pdf_path: str) -> dict:
    """Complete analysis of a research paper."""

    # Parse PDF
    document = pdf2md(pdf_path)

    # Initialize analyzers
    critique = StudyCritique()
    keyword_extractor = KeywordExtractor(method="yake")
    summarizer = SemanticSummarizer()

    # Run analysis
    return {
        "summary": critique.summary(document, max_sentences=10),
        "keywords": keyword_extractor.extract(document, top_n=10),
        "critique": critique.critique(document),
        "semantic_summary": summarizer.summarize(document, ratio=0.2)
    }
```

### Batch Paper Analysis

```python
from concurrent.futures import ThreadPoolExecutor

def analyze_papers_batch(pdf_paths: list[str]) -> list[dict]:
    """Analyze multiple papers in parallel."""

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(analyze_paper, pdf_paths))

    return results
```

### Custom Quality Criteria

```python
from StudyCritique import StudyCritique

class CustomCritique(StudyCritique):
    """Custom critique with domain-specific criteria."""

    def critique(self, document: str) -> str:
        # Add custom prompt for specific domain
        custom_prompt = f"""
        Analyze this clinical trial with focus on:
        1. Patient safety monitoring
        2. Adverse event reporting
        3. Data integrity measures

        Document:
        {document}
        """
        return self.llm.generate(custom_prompt)
```

---

## Integration with UI

```python
from StudyCritiqueUI import StudyCritiquePanel
import panel as pn

# Launch the analysis UI
panel = StudyCritiquePanel()
pn.serve(panel.view(), port=5008)
```

---

## Error Handling

```python
from StudyCritique import StudyCritique

critique = StudyCritique()

try:
    result = critique.critique(document)
except ValueError as e:
    print(f"Invalid document: {e}")
except Exception as e:
    print(f"Analysis failed: {e}")
```

---

## Performance Tips

### For Large Documents

```python
# Use semantic summarizer first to reduce size
summarizer = SemanticSummarizer()
condensed = summarizer.summarize(long_document, ratio=0.3)

# Then run detailed critique
critique = StudyCritique()
analysis = critique.critique(condensed)
```

### Keyword Extraction Speed

```python
# YAKE is fastest for large texts
extractor = KeywordExtractor(method="yake")  # Fast

# RAKE is good for medium texts
extractor = KeywordExtractor(method="rake")  # Medium

# LLM is slowest but most accurate
extractor = KeywordExtractor(method="llm")  # Slow, accurate
```

---

## Related Modules

- [LLM](core-llm.md) - Used for AI-powered analysis
- [PDFParser](pdf-processing.md) - Document parsing
- [RAG](research.md) - Document retrieval
- [StudyCritiqueUI](ui-components.md) - Web interface
