# Quick Start Guide

Get started with MedAiTools in 5 minutes!

## Prerequisites

Make sure you have:
- MedAiTools installed ([Installation Guide](installation.md))
- Virtual environment activated
- Either Ollama running locally OR API keys configured

## Starting the Application

### Option 1: Web Interface (Recommended)

Start the main research interface:

```bash
cd MedAiTools
source venv/bin/activate  # Linux/macOS
# or .\venv\Scripts\activate on Windows

python -c "
import panel as pn
from ResearcherUI import ResearcherUI
ui = ResearcherUI()
pn.serve(ui.view(), port=5006, show=True)
"
```

Your browser will open to `http://localhost:5006`

### Option 2: PDF Q&A Interface

For document-focused work:

```bash
python -c "
import panel as pn
from RAG_UI import PDFPanel
panel = PDFPanel()
pn.serve(panel.view(), port=5007, show=True)
"
```

## Your First Tasks

### Task 1: Ask Questions About a PDF

1. Open the PDF Q&A interface (port 5007)
2. Click "Upload PDF" and select a research paper
3. Wait for processing (you'll see "Document indexed")
4. Type a question like "What are the main findings?"
5. Press Enter and get your answer!

**Example questions:**
- "What methodology was used?"
- "What were the sample sizes?"
- "Summarize the conclusions"
- "What limitations are mentioned?"

### Task 2: Search MedRxiv Publications

1. Start the publication browser:
   ```bash
   python -c "
   import panel as pn
   from MedrXivPanel import MedrXivPanel
   panel = MedrXivPanel()
   pn.serve(panel.view(), port=5008, show=True)
   "
   ```

2. Set date range (last 7 days is a good start)
3. Select a category (e.g., "Infectious Diseases")
4. Click "Fetch Publications"
5. Browse titles and abstracts
6. Click "Download PDF" for papers of interest

### Task 3: Research a Topic

1. Open the Research interface (port 5006)
2. Enter a research question:
   ```
   What are the current treatment guidelines for Type 2 Diabetes?
   ```
3. Click "Research"
4. Wait for the AI to:
   - Search the web
   - Read relevant sources
   - Generate a comprehensive report

The report includes citations and source links.

### Task 4: Analyze a Paper's Quality

1. Start the critique interface:
   ```bash
   python -c "
   import panel as pn
   from StudyCritiqueUI import StudyCritiquePanel
   panel = StudyCritiquePanel()
   pn.serve(panel.view(), port=5009, show=True)
   "
   ```

2. Upload a research paper
3. Click "Generate Summary" for a concise summary
4. Click "Critique" for quality assessment
5. Review the analysis:
   - Study design evaluation
   - Methodology assessment
   - Bias identification
   - Limitations

## Basic Python Usage

You can also use MedAiTools from Python:

### PDF Question & Answer

```python
from RAG import RAG

# Initialize
rag = RAG()

# Upload and index a document
rag.ingest("my_paper.pdf")

# Ask questions
answer = rag.query("What are the main findings?")
print(answer.response)
```

### Quick Research

```python
import asyncio
from Researcher import research

async def main():
    report = await research("Latest diabetes treatment advances")
    print(report)

asyncio.run(main())
```

### Generate Synthetic Data

```python
from synthetic_demographics import create_synthetic_person

# Create a synthetic patient
patient = create_synthetic_person(age=55, gender='M')

print(f"Name: {patient['full_name']}")
print(f"DOB: {patient['date_of_birth']}")
print(f"Address: {patient['full_address']}")
print(f"Medicare: {patient['medicare_number']}")
```

## Interface Navigation

### Research Interface (port 5006)
- **Query Box:** Enter your research question
- **Provider Selection:** Choose AI provider (Ollama, OpenAI, etc.)
- **Research Button:** Start the research process
- **Results Area:** View the generated report
- **Sources:** See citations and links

### PDF Q&A (port 5007)
- **Upload Button:** Select a PDF file
- **Document Selector:** Switch between uploaded documents
- **Chat Input:** Type your questions
- **Chat History:** View conversation
- **Clear Button:** Start fresh conversation

### Publication Browser (port 5008)
- **Date Range:** Select time period
- **Category:** Filter by research category
- **Search Box:** Search within results
- **Results List:** Click to view details
- **Download:** Get PDF for local analysis

## Tips for Best Results

### Better PDF Q&A
- Upload clear, text-based PDFs (not scanned images)
- Ask specific questions
- Reference sections: "In the methods section, what sample size was used?"
- Follow up with clarifying questions

### Better Research
- Be specific: "Type 2 diabetes treatment in elderly patients" vs just "diabetes"
- Include time context: "Recent advances in..." or "Current guidelines for..."
- Specify region if relevant: "FDA-approved treatments for..."

### Better Critiques
- Upload the complete paper
- Use well-structured PDF files
- Review the critique alongside the original paper

## Common Workflows

### Literature Review Workflow
1. Search MedRxiv for recent papers on your topic
2. Download relevant PDFs
3. Ingest them into the RAG system
4. Ask comparative questions across documents
5. Use critique tool to assess quality

### Paper Writing Support
1. Ingest reference papers
2. Ask questions to extract key information
3. Use research tool for background information
4. Generate summaries for literature review section

### Quick Paper Screening
1. Upload a paper
2. Ask: "What is this paper about in one sentence?"
3. Ask: "What are the key findings?"
4. Decide if worth reading in full

## Next Steps

Now that you're up and running:

- Learn more about [PDF Q&A](features/pdf-qa.md)
- Explore the [Publication Browser](features/publications.md)
- Try the [Research Assistant](features/research.md)
- Generate [Synthetic Data](features/synthetic-data.md)

## Getting Help

- Check [Troubleshooting](troubleshooting.md) for common issues
- See [FAQ](faq.md) for frequently asked questions
- Report issues on GitHub
