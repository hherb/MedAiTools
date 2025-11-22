# Frequently Asked Questions

Common questions about MedAiTools.

## General Questions

### What is MedAiTools?

MedAiTools is an AI-powered workbench for medical researchers. It helps you:
- Ask questions about PDF documents
- Search and analyze research papers
- Generate quality assessments of studies
- Create synthetic patient data
- Conduct automated literature reviews

### Is MedAiTools free?

Yes, MedAiTools is open source and free to use. However:
- Some AI providers (OpenAI, Anthropic) require paid API keys
- You can use free options like Ollama (local) or Groq (free tier)

### Does MedAiTools require internet?

- **With Ollama:** No internet needed after setup
- **With cloud AI:** Yes, internet required for API calls
- **Publication browser:** Requires internet to fetch papers

### Is my data private?

Yes, by default:
- All data stays on your computer
- No data is sent anywhere unless you use cloud AI providers
- Cloud AI providers only see the text you send them, not your files

## Installation Questions

### What are the system requirements?

- **Minimum:** 8GB RAM, Python 3.8+
- **Recommended:** 16GB RAM, SSD storage
- **For local AI:** 16GB+ RAM or GPU with 8GB+ VRAM

### Do I need a GPU?

No, but a GPU speeds up local AI models. Without GPU:
- Local models run on CPU (slower but works)
- Cloud models work the same (processed remotely)

### Which AI provider should I use?

| Provider | Cost | Speed | Privacy | Best For |
|----------|------|-------|---------|----------|
| Ollama | Free | Medium | Excellent | Privacy-focused use |
| Groq | Free tier | Fast | Good | Quick results |
| OpenAI | Paid | Fast | Good | Best quality |
| Anthropic | Paid | Fast | Good | Long documents |

### Can I use multiple AI providers?

Yes! You can switch providers anytime:
- Use Ollama for development
- Use OpenAI for important research
- Configure different providers for different features

## Usage Questions

### What file formats are supported?

**PDF Q&A:**
- PDF files (text-based, not scanned images)

**Publications:**
- Papers from MedRxiv, bioRxiv
- Downloaded PDFs

### How large can PDFs be?

- Most PDFs under 100 pages work well
- Very large PDFs may take longer to process
- Consider splitting extremely large documents

### Can I use non-English documents?

- Most features work best with English
- PDF Q&A may work with other languages depending on AI model
- Results vary by language and model

### How accurate are the AI responses?

AI responses are generally accurate but:
- Always verify important information
- Check original sources for clinical decisions
- AI can occasionally misinterpret or hallucinate
- Use as a research aid, not a replacement for expert review

### Can I use this for clinical decisions?

**No.** MedAiTools is a research tool, not a clinical decision support system. For patient care:
- Consult current guidelines
- Use validated clinical tools
- Rely on professional judgment
- Verify all AI-generated information

## Feature-Specific Questions

### PDF Q&A

**Q: Why can't I extract text from my PDF?**
A: The PDF may be scanned images. Use OCR software first or try a different PDF with actual text.

**Q: Why are answers sometimes wrong?**
A: AI can misinterpret context. Try:
- Being more specific in your question
- Asking about specific sections
- Verifying answers against the document

**Q: Can I query multiple documents at once?**
A: Yes, upload multiple documents and ask questions across all of them.

### Publication Browser

**Q: Why don't I see recent papers?**
A: MedRxiv has a processing delay. Papers may take a few days to appear after submission.

**Q: Can I access papers from other sources?**
A: Currently supports MedRxiv/bioRxiv. Other sources may be added in future.

**Q: Why can't I download some PDFs?**
A: Some papers may have restricted access or the PDF URL may have changed.

### Research Assistant

**Q: How current is the information?**
A: The AI searches current web sources, but has a knowledge cutoff for its training data.

**Q: Why does research take so long?**
A: The AI is searching, reading, and synthesizing multiple sources. Use a faster model or reduce search depth for quicker results.

**Q: Can I trust the citations?**
A: Citations link to real sources, but always verify the information at the source.

### Synthetic Data

**Q: Is the synthetic data truly private?**
A: Yes, all data is randomly generated and doesn't correspond to real people.

**Q: Can I use this data for ML training?**
A: Yes, synthetic data is commonly used for ML development. However, validate models on real data before deployment.

**Q: Can I customize the generated data?**
A: Yes, you can specify demographics, conditions, and other parameters.

## Technical Questions

### Why use PostgreSQL instead of simpler databases?

PostgreSQL with pgvector provides:
- Efficient vector similarity search for RAG
- Scalability for large document collections
- Reliable storage for publications

### Can I use a different database?

Yes, TinyDB (JSON) is available for simpler use cases. SQLite support is limited.

### How does RAG work?

RAG (Retrieval-Augmented Generation):
1. Your document is split into chunks
2. Each chunk is converted to a vector (embedding)
3. Vectors are stored in the database
4. When you ask a question, similar chunks are retrieved
5. The AI generates an answer using those chunks as context

### Can I run this on a server?

Yes, you can:
- Deploy on any Linux server
- Use Docker for containerization
- Set up for multi-user access (requires additional configuration)

## Troubleshooting Questions

### The application is slow

- Use a faster AI model
- Process smaller documents
- Check system resources (RAM, CPU)
- Use SSD storage

### I'm getting errors

See the [Troubleshooting Guide](troubleshooting.md) for common solutions.

### My question isn't answered here

- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the feature-specific documentation
- Report issues on GitHub

## Future Development

### Will you add feature X?

MedAiTools is actively developed. Feature requests are welcome on GitHub.

### Can I contribute?

Yes! See the [Developer Documentation](../developers/README.md) and [Contributing Guide](../developers/contributing.md).

### How can I stay updated?

- Watch the GitHub repository
- Check for updates periodically
- Follow release notes
