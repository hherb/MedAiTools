# Research Assistant

Let AI conduct comprehensive research on any medical topic.

## Overview

The Research Assistant:
- Searches the web for relevant information
- Reads and analyzes multiple sources
- Synthesizes findings into a comprehensive report
- Provides citations and source links

## Getting Started

### Starting the Interface

```bash
cd MedAiTools
source venv/bin/activate

python -c "
import panel as pn
from ResearcherUI import ResearcherUI
ui = ResearcherUI()
pn.serve(ui.view(), port=5006, show=True)
"
```

Open your browser to `http://localhost:5006`

## Using the Research Assistant

### Basic Research

1. **Enter your question:**
   ```
   What are the current treatment guidelines for Type 2 Diabetes?
   ```

2. **Click Research** (or press Enter)

3. **Wait for processing:**
   - The AI searches multiple sources
   - Reads and analyzes content
   - Generates a report
   - This typically takes 1-3 minutes

4. **Review the report:**
   - Organized by topic
   - Includes key findings
   - Citations provided
   - Source links included

### Selecting AI Provider

Choose your preferred AI provider:
- **Ollama (Local):** Free, private, slower
- **OpenAI:** Fast, accurate, costs money
- **Anthropic:** High quality, costs money
- **Groq:** Fast free tier

Select from the provider dropdown before starting research.

### Research Settings

Adjust settings for your needs:
- **Model:** Choose specific model (GPT-4, Claude, etc.)
- **Report Length:** Brief, standard, or comprehensive
- **Source Count:** How many sources to use

## Types of Research Queries

### Treatment Questions
```
What are the first-line treatments for essential hypertension?
```
```
What is the current evidence for GLP-1 agonists in obesity management?
```

### Guideline Questions
```
What are the 2024 ACC/AHA guidelines for heart failure management?
```
```
Current CDC recommendations for childhood vaccination schedules
```

### Comparative Questions
```
Compare the efficacy of different SGLT2 inhibitors for diabetes
```
```
SSRIs vs SNRIs for treatment of major depression - which has better evidence?
```

### Epidemiology Questions
```
What is the current global prevalence of Type 2 Diabetes?
```
```
Risk factors for cardiovascular disease in women
```

### Mechanism Questions
```
How do checkpoint inhibitors work in cancer immunotherapy?
```
```
Explain the pathophysiology of Alzheimer's disease
```

## Understanding Research Reports

### Report Structure

A typical report includes:

1. **Executive Summary**
   - Key findings at a glance
   - Main conclusions

2. **Background**
   - Context and definitions
   - Why this topic matters

3. **Current Evidence**
   - What studies show
   - Key statistics and data

4. **Analysis**
   - Interpretation of evidence
   - Comparison of viewpoints

5. **Conclusions**
   - Summary of findings
   - Practical implications

6. **Sources**
   - Full citations
   - Links to original sources

### Reading Citations

Citations appear as:
```
Treatment X showed 30% improvement in outcomes [1].

Sources:
[1] Smith et al. (2024). Study Title. Journal Name. URL
```

## Tips for Better Research

### Crafting Good Questions

**Be specific:**
- Instead of: "Tell me about diabetes"
- Try: "What is the evidence for intensive vs standard glucose control in Type 2 Diabetes?"

**Include context:**
- Instead of: "Best treatment for infection"
- Try: "First-line antibiotic treatment for community-acquired pneumonia in adults"

**Specify time frame if relevant:**
- "Recent advances in CAR-T therapy (2022-2024)"
- "Current guidelines for stroke prevention"

**Specify population if relevant:**
- "Treatment of hypertension in pregnancy"
- "Pediatric asthma management guidelines"

### Getting More Comprehensive Results

For deeper research:
```
Provide a comprehensive review of the evidence for [topic], including:
- Current guidelines
- Recent clinical trials
- Controversies and debates
- Gaps in knowledge
- Future directions
```

### Getting Practical Information

For clinical applications:
```
What are the practical steps for [procedure/treatment]?
Include dosing, monitoring, and common complications.
```

## Limitations

### What Works Well
- Established medical topics
- Questions with clear answers
- Topics with recent publications

### What May Be Limited
- Very recent developments (knowledge cutoff)
- Highly specialized niches
- Questions requiring local/institutional knowledge
- Proprietary or paywalled information

### Verify Important Findings
- Research reports are AI-generated
- Always verify critical information
- Check original sources for clinical decisions
- Consult current guidelines and experts

## Integration with Other Features

### Combine with PDF Q&A
1. Research a topic broadly
2. Identify key papers mentioned
3. Download and upload to PDF Q&A
4. Ask detailed questions about specific papers

### Build on Previous Research
1. Start with broad research question
2. Identify subtopics of interest
3. Research each subtopic separately
4. Combine findings

### Systematic Reviews
1. Define your research question
2. Use Publication Browser to find papers
3. Use Research Assistant for background
4. Use PDF Q&A and Critique for analysis

## Example Session

**You:** What are the current treatment options for treatment-resistant depression?

**AI:** *[Generates comprehensive report]*

---

## Treatment Options for Treatment-Resistant Depression

### Executive Summary
Treatment-resistant depression (TRD) affects approximately 30% of patients with major depressive disorder. Current options include medication augmentation, switching strategies, and newer interventions like ketamine/esketamine and neuromodulation.

### Definition
TRD is typically defined as failure to respond adequately to at least two different antidepressants given at adequate doses for adequate duration...

### Current Treatment Approaches

**1. Medication Strategies**
- Augmentation with atypical antipsychotics (aripiprazole, quetiapine)
- Lithium augmentation
- Thyroid hormone augmentation
- Switching antidepressant classes

**2. Ketamine and Esketamine**
- FDA-approved esketamine (Spravato) for TRD
- Rapid onset of action (hours to days)
- Response rates of 50-70% in trials...

**3. Neuromodulation**
- ECT remains gold standard for severe TRD
- TMS approved for TRD
- VNS for chronic, refractory cases...

### Sources
[1] McIntyre RS, et al. (2023). Treatment-resistant depression...
[2] FDA. Esketamine prescribing information...
[3] APA Practice Guidelines...

---

## Python Usage

For programmatic research:

```python
import asyncio
from Researcher import research

async def main():
    report = await research(
        "Current evidence for intermittent fasting in Type 2 Diabetes"
    )
    print(report)

    # Save to file
    with open("research_report.md", "w") as f:
        f.write(report)

asyncio.run(main())
```

## Related Features

- [PDF Q&A](pdf-qa.md) - Analyze specific papers
- [Publication Browser](publications.md) - Find relevant papers
- [Study Critique](critique.md) - Assess paper quality
