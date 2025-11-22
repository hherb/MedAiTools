# Publication Scraping Module

**File:** `PGMedrXivScraper.py`

This module provides automated fetching of research publications from MedRxiv (and bioRxiv).

## Overview

The MedrXivScraper:
- Fetches publication metadata from MedRxiv API
- Downloads PDFs
- Stores data in PostgreSQL
- Parses and indexes documents for search

## MedrXivScraper Class

### Constructor

```python
from PGMedrXivScraper import MedrXivScraper

scraper = MedrXivScraper(
    storage: PersistentStorage | None = None  # Custom storage
)
```

### Methods

#### fetch_from_medrXiv()

Fetch publications from a date range:

```python
publications = scraper.fetch_from_medrXiv(
    from_date: str,           # Start date (YYYY-MM-DD)
    to_date: str,             # End date (YYYY-MM-DD)
    fetch_pdfs: bool = False, # Also download PDFs
    category: str | None = None  # Filter by category
) -> list[dict]
```

**Example:**
```python
# Fetch metadata only
publications = scraper.fetch_from_medrXiv(
    from_date="2024-01-01",
    to_date="2024-01-31"
)

print(f"Found {len(publications)} publications")
for pub in publications[:5]:
    print(f"- {pub['title']}")

# Fetch with PDFs
publications = scraper.fetch_from_medrXiv(
    from_date="2024-01-01",
    to_date="2024-01-07",
    fetch_pdfs=True
)
```

#### fetch_pdf_from_medrXiv()

Download PDF for a specific publication:

```python
pdf_path = scraper.fetch_pdf_from_medrXiv(
    publication: dict,     # Publication metadata
    upsert: bool = False   # Update storage
) -> str
```

**Example:**
```python
pub = publications[0]
pdf_path = scraper.fetch_pdf_from_medrXiv(pub, upsert=True)
print(f"PDF saved to: {pdf_path}")
```

#### count()

Get total publications in storage:

```python
total = scraper.count()
print(f"Total publications: {total}")
```

#### search()

Search publications:

```python
results = scraper.search(
    query: str,
    field: str = "title",  # "title", "abstract", "authors"
    limit: int = 100
) -> list[dict]
```

**Example:**
```python
results = scraper.search("diabetes", field="title")
```

#### get_by_doi()

Get publication by DOI:

```python
pub = scraper.get_by_doi("10.1101/2024.01.01.12345")
```

#### get_categories()

List available categories:

```python
categories = scraper.get_categories()
for cat in categories:
    print(cat)
```

### Publication Data Structure

```python
{
    "doi": "10.1101/2024.01.01.12345",
    "title": "Study on Novel Treatment Approaches",
    "authors": "Smith J; Doe A; Johnson B",
    "abstract": "Background: This study investigates...",
    "category": "Clinical Trial",
    "published_date": "2024-01-15",
    "version": "1",
    "pdf_url": "https://www.medrxiv.org/content/...",
    "pdf_path": "/home/user/medai/library/...",
    "jatsxml_url": "https://...",
    "author_corresponding": "Smith J",
    "author_corresponding_institution": "University of...",
    "license": "CC-BY-NC-ND 4.0"
}
```

## Available Categories

Common MedRxiv categories:

- Addiction Medicine
- Allergy and Immunology
- Anesthesia
- Cardiovascular Medicine
- Dermatology
- Emergency Medicine
- Endocrinology
- Epidemiology
- Gastroenterology
- Genetic and Genomic Medicine
- Geriatric Medicine
- Health Economics
- Health Informatics
- Health Policy
- Hematology
- HIV/AIDS
- Infectious Diseases
- Intensive Care and Critical Care Medicine
- Medical Education
- Medical Ethics
- Nephrology
- Neurology
- Nursing
- Nutrition
- Obstetrics and Gynecology
- Occupational and Environmental Health
- Oncology
- Ophthalmology
- Orthopedics
- Otolaryngology
- Pain Medicine
- Palliative Medicine
- Pathology
- Pediatrics
- Pharmacology and Therapeutics
- Primary Care Research
- Psychiatry and Clinical Psychology
- Public and Global Health
- Radiology and Imaging
- Rehabilitation Medicine and Physical Therapy
- Respiratory Medicine
- Rheumatology
- Sexual and Reproductive Health
- Sports Medicine
- Surgery
- Toxicology
- Transplantation
- Urology

## Configuration

### Storage Path

Publications are stored in the library path:

```python
from medai.Settings import Settings

settings = Settings()
print(settings.library_path)  # ~/medai/library
```

Structure:
```
~/medai/library/
├── medrxiv/
│   ├── 2024/
│   │   ├── 01/
│   │   │   ├── 10.1101.2024.01.01.12345.pdf
│   │   │   └── ...
│   │   └── ...
│   └── ...
└── ...
```

### Database Table

```sql
CREATE TABLE publications (
    id SERIAL PRIMARY KEY,
    doi VARCHAR(100) UNIQUE,
    title TEXT NOT NULL,
    authors TEXT,
    abstract TEXT,
    category VARCHAR(100),
    published_date DATE,
    version VARCHAR(10),
    pdf_url TEXT,
    pdf_path TEXT,
    jatsxml_url TEXT,
    author_corresponding TEXT,
    author_corresponding_institution TEXT,
    license VARCHAR(50),
    processed BOOLEAN DEFAULT FALSE,
    keywords TEXT[],
    summary TEXT,
    fetched_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Usage Patterns

### Daily Fetch Job

```python
from datetime import datetime, timedelta
from PGMedrXivScraper import MedrXivScraper

def daily_fetch():
    """Fetch yesterday's publications."""
    scraper = MedrXivScraper()

    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    publications = scraper.fetch_from_medrXiv(
        from_date=yesterday,
        to_date=today,
        fetch_pdfs=True
    )

    print(f"Fetched {len(publications)} new publications")
    return publications
```

### Category-Specific Fetch

```python
def fetch_cardiology_papers(from_date: str, to_date: str):
    """Fetch cardiology papers only."""
    scraper = MedrXivScraper()

    return scraper.fetch_from_medrXiv(
        from_date=from_date,
        to_date=to_date,
        category="Cardiovascular Medicine",
        fetch_pdfs=True
    )
```

### Fetch and Analyze Pipeline

```python
from PGMedrXivScraper import MedrXivScraper
from PDFParser import pdf2md
from StudyCritique import StudyCritique
from KeywordExtractor import KeywordExtractor

async def fetch_and_analyze(from_date: str, to_date: str):
    """Fetch papers and perform analysis."""
    scraper = MedrXivScraper()
    critique = StudyCritique()
    extractor = KeywordExtractor()

    # Fetch publications
    publications = scraper.fetch_from_medrXiv(
        from_date=from_date,
        to_date=to_date,
        fetch_pdfs=True
    )

    for pub in publications:
        if pub.get("pdf_path"):
            # Parse PDF
            text = pdf2md(pub["pdf_path"])

            # Extract keywords
            keywords = extractor.extract(text, top_n=10)

            # Generate summary
            summary = critique.summary(text)

            # Update publication
            scraper.update(pub["doi"], {
                "keywords": keywords,
                "summary": summary,
                "processed": True
            })

            print(f"Analyzed: {pub['title']}")
```

### Search and Filter

```python
def search_publications(
    query: str,
    category: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int = 100
) -> list[dict]:
    """Search publications with filters."""
    scraper = MedrXivScraper()

    # Build SQL query
    conditions = ["abstract ILIKE %s"]
    params = [f"%{query}%"]

    if category:
        conditions.append("category = %s")
        params.append(category)

    if from_date:
        conditions.append("published_date >= %s")
        params.append(from_date)

    if to_date:
        conditions.append("published_date <= %s")
        params.append(to_date)

    sql = f"""
        SELECT * FROM publications
        WHERE {' AND '.join(conditions)}
        ORDER BY published_date DESC
        LIMIT {limit}
    """

    return scraper.storage.query(sql, tuple(params))
```

## Error Handling

```python
from PGMedrXivScraper import MedrXivScraper

scraper = MedrXivScraper()

try:
    publications = scraper.fetch_from_medrXiv(
        from_date="2024-01-01",
        to_date="2024-01-31"
    )
except ConnectionError:
    print("Failed to connect to MedRxiv API")
except TimeoutError:
    print("API request timed out")
except Exception as e:
    print(f"Fetch failed: {e}")
```

## Rate Limiting

The scraper includes built-in rate limiting:

```python
# Default: 100ms between requests
scraper.request_delay = 0.1

# For aggressive fetching (use carefully)
scraper.request_delay = 0.05

# For conservative fetching
scraper.request_delay = 0.5
```

## Integration with UI

```python
from MedrXivPanel import MedrXivPanel
import panel as pn

# Launch publication browser UI
panel = MedrXivPanel()
pn.serve(panel.view(), port=5009)
```

## Related Modules

- [PersistentStorage](storage.md) - Database storage
- [PDFParser](pdf-processing.md) - PDF processing
- [StudyCritique](analysis.md) - Paper analysis
- [MedrXivPanel](ui-components.md) - Web interface
