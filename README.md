# MedAiTools - An AI-Assisted Workbench for Medical Researchers

**A collection of tools and Python libraries for medical practice and research, with an emphasis on local execution to protect privacy and avoid subscription dependencies.**

**Status:** Some tools are functional as proofs of concept. Feel free to experiment and contribute to their development.

## Librarian
**Natural Language Database Query and Knowledge Retrieval System**

- **Upload and Query:** Upload PDF files and query your data using natural language.
- **Document Interrogation:** Interrogate a single document, a list of documents, or all documents stored in the database.
- **Purpose:** To provide AI-driven answers grounded in attributable sources, with easy updates and extensibility.

  
  ![image](https://github.com/hherb/MedAiTools/assets/15961294/82ef7b87-4faf-4aef-9bad-21b28f6c4857)

---

## MedRxivScraper
**Automated System for Fetching and Summarizing Pre-Publications**

- **Background Fetching:** Automatically fetches new publications and their associated full papers from medRxiv and ingests them into the knowledge base.
- **High-Quality Summaries:** Provides abstractive summaries of texts of any length and re-ranks retrieved documents according to user preferences and domain relevance.
- **User-Configurable Interest:** Presents new papers of interest with titles and summaries based on user-configurable criteria in natural language.
- **Integration with Librarian:** A single click or keystroke opens the document for interrogation.
- **Purpose:** To establish an automated "news service" that presents the latest pre-publications along with AI-generated critiques.

----

## StudyCritique
**AI-Based Analysis of Publications**

- **Weakness Detection:** Analyzes publications to identify weaknesses in argumentation or methods.

---

## LiteratureReviewer
**Deep Web Scraping and Pre-Screening of Relevant Papers**

- **Knowledge Base Integration:** Uses existing knowledge bases to retrieve relevant papers, which are then pre-screened by AI according to user-definable criteria in natural language.
- **Configurable Agents:** We use a variety of libraries (eg gpt-researcher, phidata, ...) as well as hand crafted agentic researchers with fine granular tunability by the end user to ensure fitness for each purpose


  ![image](https://github.com/hherb/MedAiTools/assets/15961294/5c560b91-c005-4b00-9fd4-5ed278705228)


  ![image](https://github.com/hherb/MedAiTools/assets/15961294/07df10cc-f85f-413e-86ea-880fe698c970)

---

## Design Principles

- **Free from Restrictive Licensing:** Avoids proprietary tools and restrictive licenses.
- **Commercial API Use:** Integrates commercial APIs (e.g., Tavily for web searching) only when necessary and ensures open alternatives are available.
- **Local Execution:** Enables local execution without requiring network access where possible.
- **Efficient Storage:** Stores all data locally to avoid redundant downloads and generation.
- **Robust Infrastructure:** Utilizes PostgreSQL with pgvector extension and local file systems for all storage needs, without relying on external servers or services.

---

**Join us in developing these tools to enhance medical research while maintaining privacy and independence.**

---

  ![image](https://github.com/hherb/MedAiTools/assets/15961294/0dbb1388-5796-4c15-8de5-ed9cc0a12ea7)


