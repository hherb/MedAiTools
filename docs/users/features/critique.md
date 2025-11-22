# Study Critique

Get AI-powered quality assessments of research papers.

## Overview

The Study Critique feature:
- Summarizes research papers
- Identifies methodological strengths and weaknesses
- Assesses bias risk
- Provides quality ratings
- Extracts key information

## Getting Started

### Starting the Interface

```bash
cd MedAiTools
source venv/bin/activate

python -c "
import panel as pn
from StudyCritiqueUI import StudyCritiquePanel
panel = StudyCritiquePanel()
pn.serve(panel.view(), port=5009, show=True)
"
```

Open your browser to `http://localhost:5009`

## Using Study Critique

### Uploading a Paper

1. Click **Upload PDF**
2. Select a research paper
3. Wait for processing
4. Document appears in the panel

### Generating a Summary

1. With document loaded, click **Generate Summary**
2. Wait for AI processing
3. Review the concise summary

The summary includes:
- Study objective
- Methods overview
- Key findings
- Main conclusions

### Getting a Quality Critique

1. Click **Critique**
2. Wait for detailed analysis
3. Review the assessment

The critique evaluates:
- Study design appropriateness
- Sample size and selection
- Methodology rigor
- Statistical analysis
- Bias and confounding
- Limitations
- Overall quality rating

### Extracting Keywords

1. Click **Extract Keywords**
2. Review key terms
3. Use for searching related papers

## Understanding the Critique

### Quality Dimensions

**Study Design**
- Is the design appropriate for the research question?
- RCT, cohort, case-control, cross-sectional, etc.
- Control group presence and appropriateness

**Sampling**
- Sample size adequacy
- Selection bias concerns
- Representativeness of population
- Power calculations reported?

**Methodology**
- Intervention clearly described?
- Outcomes well-defined?
- Measurement methods valid?
- Blinding implemented?

**Statistical Analysis**
- Appropriate methods used?
- Multiple comparisons addressed?
- Missing data handled?
- Effect sizes reported?

**Bias Assessment**
- Selection bias
- Information/measurement bias
- Confounding
- Publication bias (for reviews)

**Reporting Quality**
- CONSORT/STROBE compliance
- Results clearly presented
- Limitations discussed
- Conflicts of interest disclosed

### Quality Ratings

Papers receive overall ratings:
- **Good:** Strong methodology, minimal bias risk
- **Fair:** Some limitations but generally sound
- **Poor:** Significant methodological concerns

## Types of Studies Supported

### Clinical Trials
- RCTs
- Quasi-experimental studies
- Before-after studies

### Observational Studies
- Cohort studies
- Case-control studies
- Cross-sectional surveys

### Reviews
- Systematic reviews
- Meta-analyses
- Narrative reviews

### Other
- Case reports/series
- Qualitative studies
- Diagnostic accuracy studies

## Example Critique

**Paper:** "Effect of Drug X on Blood Pressure in Hypertensive Patients"

### Summary
This randomized controlled trial evaluated Drug X versus placebo in 200 patients with essential hypertension over 12 weeks. The treatment group showed significant systolic BP reduction of 15 mmHg compared to 5 mmHg in placebo (p<0.001).

### Quality Assessment

**Study Design: Good**
- Appropriate RCT design for evaluating treatment efficacy
- Parallel group design with adequate follow-up

**Sample: Fair**
- Sample size of 200 is adequate for primary outcome
- Single-center study limits generalizability
- Strict inclusion criteria may not represent real-world population

**Methods: Good**
- Double-blinding maintained
- Outcomes measured using validated methods
- Randomization process clearly described

**Statistics: Good**
- Intention-to-treat analysis performed
- Appropriate methods (t-test, ANCOVA)
- Missing data handled with multiple imputation

**Bias Risk: Low-Moderate**
- Selection: Low (adequate randomization)
- Performance: Low (double-blinded)
- Attrition: Moderate (15% dropout, but ITT used)

**Limitations Identified:**
1. Single-center reduces generalizability
2. 12-week follow-up may miss long-term effects
3. Strict exclusion criteria limit external validity
4. Industry-funded (potential conflict of interest)

**Overall Quality: Good**
This is a well-conducted RCT with minor limitations. Results are likely reliable for the studied population.

## Tips for Using Critiques

### Critical Reading
Use critiques to:
- Identify which findings to trust
- Understand study limitations
- Compare study quality across papers
- Inform evidence synthesis

### For Systematic Reviews
- Screen papers for quality
- Assess risk of bias
- Determine inclusion/exclusion
- Weight evidence appropriately

### For Clinical Decision-Making
- Consider quality when applying evidence
- Higher quality = more confidence
- Understand what limitations mean for your patients

## Limitations

### What Works Well
- Standard research paper formats
- Well-structured academic papers
- Clear methods sections

### What May Be Limited
- Non-English papers
- Unusual study designs
- Papers with minimal methods detail
- Very specialized methodologies

### Important Notes
- AI critique is a screening tool
- Not a substitute for expert review
- Use alongside human judgment
- Verify critical assessments

## Integration with Other Features

### After Finding Papers
1. Find papers in Publication Browser
2. Download PDFs
3. Run critiques on promising papers
4. Focus on high-quality studies

### With PDF Q&A
1. Run critique for overview
2. Use PDF Q&A for specific questions
3. Combine insights

### Building Evidence Tables
1. Critique multiple papers
2. Compare quality ratings
3. Extract key data points
4. Build systematic comparison

## Python Usage

For programmatic critiques:

```python
from StudyCritique import StudyCritique
from PDFParser import pdf2md

# Initialize
critique = StudyCritique()

# Load document
document = pdf2md("study.pdf")

# Generate summary
summary = critique.summary(document, max_sentences=10)
print("Summary:")
print(summary)

# Generate critique
analysis = critique.critique(document)
print("\nCritique:")
print(analysis)
```

### Batch Processing

```python
from pathlib import Path
from StudyCritique import StudyCritique
from PDFParser import pdf2md

critique = StudyCritique()

# Process multiple papers
papers_dir = Path("papers/")
results = []

for pdf in papers_dir.glob("*.pdf"):
    document = pdf2md(str(pdf))
    result = {
        "file": pdf.name,
        "summary": critique.summary(document),
        "critique": critique.critique(document)
    }
    results.append(result)
    print(f"Processed: {pdf.name}")

# Save results
import json
with open("critique_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

## Related Features

- [PDF Q&A](pdf-qa.md) - Ask detailed questions
- [Publication Browser](publications.md) - Find papers
- [Research Assistant](research.md) - Background research
