# PDF Question & Answer

The PDF Q&A feature allows you to have natural language conversations with your research documents.

## Overview

Upload any PDF document and ask questions in plain English. The AI will:
- Search through your document
- Find relevant sections
- Generate accurate answers
- Show you the source passages

## Getting Started

### Starting the Interface

```bash
cd MedAiTools
source venv/bin/activate

python -c "
import panel as pn
from RAG_UI import PDFPanel
panel = PDFPanel()
pn.serve(panel.view(), port=5007, show=True)
"
```

Open your browser to `http://localhost:5007`

### Uploading a Document

1. Click the **Upload PDF** button
2. Select a PDF file from your computer
3. Wait for processing (usually 30-60 seconds)
4. You'll see "Document indexed successfully"

### Asking Questions

Simply type your question in the chat box and press Enter:

```
What is the main hypothesis of this study?
```

The AI will respond with an answer based on the document content.

## Types of Questions You Can Ask

### Summary Questions
- "What is this paper about?"
- "Summarize the abstract"
- "What are the main conclusions?"

### Specific Information
- "What was the sample size?"
- "What statistical methods were used?"
- "What were the inclusion criteria?"

### Methods Questions
- "How was the study conducted?"
- "What was the study design?"
- "How were participants recruited?"

### Results Questions
- "What were the main findings?"
- "What was the p-value for the primary outcome?"
- "Were there any significant differences between groups?"

### Comparative Questions
- "How do the results compare to previous studies?"
- "What are the limitations mentioned by the authors?"
- "What future research do the authors suggest?"

## Working with Multiple Documents

### Switching Documents

If you've uploaded multiple PDFs:
1. Use the document selector dropdown
2. Choose the document you want to query
3. Questions will now reference that document

### Cross-Document Queries

To compare across documents:
1. Upload all relevant documents
2. Ask: "Compare the methodologies used in all uploaded documents"
3. Or be specific: "What sample sizes were used across all studies?"

## Tips for Better Results

### Be Specific
Instead of: "Tell me about the results"
Try: "What were the primary outcomes in the treatment group compared to control?"

### Reference Sections
- "In the discussion section, what limitations are mentioned?"
- "According to Table 2, what was the mortality rate?"
- "From the abstract, what is the main finding?"

### Ask Follow-up Questions
- First: "What was the main intervention?"
- Then: "How was this intervention administered?"
- Then: "What were the side effects?"

### Use Clear Language
- Avoid jargon when possible
- Break complex questions into parts
- Be direct about what you want to know

## Understanding Responses

### Source Citations
Answers include references to where the information was found:
```
The study used a randomized controlled design (p.3, Methods section).
```

### Confidence Levels
If the AI isn't sure, it will indicate this:
```
Based on the available text, it appears that... However, this is not explicitly stated.
```

### "I don't know" Responses
If information isn't in the document:
```
I couldn't find specific information about dosage in this document.
```

## Limitations

### What Works Well
- Text-based PDF documents
- Well-structured academic papers
- Clear, readable text

### What Doesn't Work Well
- Scanned images without OCR
- Heavily formatted tables
- PDFs with mostly images/figures
- Encrypted or password-protected PDFs

### Troubleshooting Poor Results

**If answers seem wrong:**
- Check that the PDF was properly uploaded
- Try rephrasing your question
- Ask about specific sections

**If the system says it can't find information:**
- Verify the information is actually in the document
- Use different keywords
- Be more specific about where to look

## Example Session

**Upload:** "diabetes_treatment_study.pdf"

**You:** What type of study is this?

**AI:** This is a randomized controlled trial (RCT) investigating the efficacy of a new oral medication for Type 2 Diabetes. The study was conducted over 24 weeks with 500 participants.

**You:** What was the primary endpoint?

**AI:** The primary endpoint was change in HbA1c from baseline to week 24. Secondary endpoints included fasting plasma glucose, body weight, and adverse events.

**You:** What were the results for the primary endpoint?

**AI:** The treatment group showed a mean HbA1c reduction of 1.2% compared to 0.5% in the placebo group (p < 0.001). This difference was statistically significant and clinically meaningful.

**You:** Were there any safety concerns?

**AI:** The study reported that the medication was generally well-tolerated. The most common adverse events were mild gastrointestinal symptoms (nausea in 8% of treatment group vs 3% in placebo). No serious adverse events were attributed to the study medication.

## Python Usage

For programmatic use:

```python
from RAG import RAG

# Initialize
rag = RAG()

# Upload document
rag.ingest("my_document.pdf")

# Ask questions
response = rag.query("What are the main findings?")
print(response.response)

# See sources
for source in response.source_nodes:
    print(f"Source: {source.text[:200]}...")
```

## Related Features

- [Research Assistant](research.md) - For web-based research
- [Study Critique](critique.md) - For quality assessment
- [Publication Browser](publications.md) - Find papers to analyze
