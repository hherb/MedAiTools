# Publication Browser

Browse, search, and download research papers from MedRxiv and other sources.

## Overview

The Publication Browser helps you:
- Find the latest preprints in your field
- Filter by date, category, and keywords
- Download papers for local analysis
- Track publications you've reviewed

## Getting Started

### Starting the Interface

```bash
cd MedAiTools
source venv/bin/activate

python -c "
import panel as pn
from MedrXivPanel import MedrXivPanel
panel = MedrXivPanel()
pn.serve(panel.view(), port=5008, show=True)
"
```

Open your browser to `http://localhost:5008`

## Using the Browser

### Setting Date Range

1. Find the **From Date** and **To Date** pickers
2. Select your desired date range
3. Tip: Start with the last 7 days to avoid long load times

### Selecting Categories

Choose from medical categories:
- Cardiovascular Medicine
- Infectious Diseases
- Oncology
- Neurology
- Epidemiology
- Public Health
- And many more...

Leave blank to search all categories.

### Fetching Publications

1. Set your date range and category
2. Click **Fetch Publications**
3. Wait for results (may take a moment for large date ranges)
4. Publications appear in the list below

### Browsing Results

Each publication shows:
- **Title** - Click to expand details
- **Authors** - Research team
- **Date** - Publication date
- **Category** - Research area

Click on a publication to see:
- Full abstract
- DOI link
- Download options

### Searching Within Results

Use the search box to filter displayed results:
- Search by keyword: "diabetes"
- Search by author: "Smith"
- Search in title/abstract

### Downloading Papers

1. Select a publication
2. Click **Download PDF**
3. The PDF is saved to your library folder
4. You can then use it with PDF Q&A

## Categories Available

### Common Medical Categories
- Addiction Medicine
- Allergy and Immunology
- Cardiovascular Medicine
- Dermatology
- Emergency Medicine
- Endocrinology
- Gastroenterology
- Geriatric Medicine
- Hematology
- Infectious Diseases
- Nephrology
- Neurology
- Oncology
- Ophthalmology
- Pediatrics
- Psychiatry
- Respiratory Medicine
- Rheumatology

### Research Types
- Epidemiology
- Health Economics
- Health Informatics
- Health Policy
- Medical Education
- Public and Global Health

## Tips for Effective Searching

### Finding Relevant Papers

**Use specific categories:**
Instead of browsing everything, select a specific category that matches your interest.

**Start with recent papers:**
Set a short date range (1 week) first, then expand if needed.

**Use keyword search:**
After fetching, use the search box to filter by specific terms.

### Managing Large Result Sets

**Narrow your search:**
- Use specific date ranges
- Select one category at a time
- Apply keyword filters

**Batch processing:**
For systematic reviews, fetch papers in chunks by date range.

## Integration with Other Features

### Send to PDF Q&A
After downloading a paper:
1. Open the PDF Q&A interface
2. Upload the downloaded PDF
3. Ask questions about the paper

### Analyze with Study Critique
1. Download a paper of interest
2. Open Study Critique interface
3. Upload for quality assessment

### Build a Research Library
Downloaded papers are saved to:
```
~/medai/library/medrxiv/[year]/[month]/
```

You can then:
- Ingest multiple papers into RAG
- Search across your library
- Build systematic reviews

## Workflow Example

### Systematic Literature Search

1. **Define criteria:**
   - Topic: "COVID-19 vaccines"
   - Date range: "2023-01-01" to "2023-12-31"
   - Category: "Infectious Diseases"

2. **Fetch publications:**
   - Set date range
   - Select category
   - Click Fetch

3. **Screen titles:**
   - Browse the results
   - Note relevant papers

4. **Download candidates:**
   - Download PDFs for relevant papers

5. **Full-text review:**
   - Use PDF Q&A to extract key data
   - Use Study Critique to assess quality

6. **Organize findings:**
   - Papers are saved with DOI-based filenames
   - Easy to track and reference

## Data Stored

For each publication, MedAiTools stores:
- DOI (unique identifier)
- Title and authors
- Abstract
- Category
- Publication date
- PDF URL
- Local PDF path (if downloaded)
- Keywords (if extracted)
- Summary (if generated)

## Troubleshooting

### "No publications found"
- Try a different date range
- Try a different or broader category
- Check your internet connection

### Downloads failing
- Check you have write permission to library folder
- Verify internet connection
- Some papers may not have free PDF access

### Slow loading
- Use smaller date ranges
- MedRxiv API can be slow during peak times
- Try during off-peak hours

## Python Usage

For programmatic access:

```python
from PGMedrXivScraper import MedrXivScraper

scraper = MedrXivScraper()

# Fetch publications
pubs = scraper.fetch_from_medrXiv(
    from_date="2024-01-01",
    to_date="2024-01-31",
    category="Cardiovascular Medicine"
)

print(f"Found {len(pubs)} publications")

for pub in pubs[:5]:
    print(f"- {pub['title']}")

# Download a PDF
pdf_path = scraper.fetch_pdf_from_medrXiv(pubs[0])
print(f"Downloaded to: {pdf_path}")
```

## Related Features

- [PDF Q&A](pdf-qa.md) - Analyze downloaded papers
- [Study Critique](critique.md) - Assess paper quality
- [Research Assistant](research.md) - Broader research
