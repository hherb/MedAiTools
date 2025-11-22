# Troubleshooting Guide

Solutions to common problems with MedAiTools.

## Installation Issues

### "Python not found"

**Windows:**
1. Reinstall Python from python.org
2. Check "Add Python to PATH" during installation
3. Restart your terminal

**Mac/Linux:**
```bash
# Check Python version
python3 --version

# If not found, install:
# Mac
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11
```

### "pip not found"

```bash
# Try python -m pip
python -m pip install -r requirements.txt

# Or install pip
python -m ensurepip --upgrade
```

### "Permission denied" during installation

**Linux/Mac:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or fix permissions
sudo chown -R $USER:$USER ~/.local
```

**Windows:**
Run terminal as Administrator

### Out of memory during installation

Install packages in groups:
```bash
pip install pandas numpy
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

## Database Issues

### "Cannot connect to PostgreSQL"

1. **Check PostgreSQL is running:**
   ```bash
   # Linux
   sudo systemctl status postgresql

   # Mac
   brew services list | grep postgresql
   ```

2. **Start if not running:**
   ```bash
   # Linux
   sudo systemctl start postgresql

   # Mac
   brew services start postgresql
   ```

3. **Check your credentials** in `config_local.json`

4. **Test connection:**
   ```bash
   psql -h localhost -U medai -d medaitools
   ```

### "pgvector extension not found"

```bash
# Install pgvector
# Ubuntu
sudo apt install postgresql-14-pgvector

# Mac
brew install pgvector

# Then enable in database
psql -d medaitools -c "CREATE EXTENSION vector;"
```

### "Database does not exist"

```bash
# Create the database
sudo -u postgres createdb medaitools

# Or via psql
sudo -u postgres psql
CREATE DATABASE medaitools;
```

## AI/LLM Issues

### "Ollama not responding"

1. **Check if running:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Start Ollama:**
   ```bash
   # Linux
   systemctl start ollama

   # Mac/Windows
   # Start Ollama application
   ```

3. **Check model is downloaded:**
   ```bash
   ollama list
   # Should show llama3.2 or your model
   ```

4. **Download model if missing:**
   ```bash
   ollama pull llama3.2
   ```

### "OpenAI API error: Invalid API key"

1. Check your key in `.env` file:
   ```
   OPENAI_API_KEY=sk-...
   ```

2. Verify key is valid at platform.openai.com

3. Check for typos or extra spaces

### "Rate limit exceeded"

- Wait a few minutes and try again
- Switch to a different provider temporarily
- Use local Ollama for development

### "Model not found"

```bash
# For Ollama
ollama pull llama3.2

# For OpenAI, verify model name
# Use: gpt-4o, gpt-3.5-turbo, etc.
```

### Slow responses

- **Local models:** Use smaller model (llama3.2:7b)
- **Cloud models:** Check internet connection
- **PDF Q&A:** Reduce number of context chunks

## PDF Processing Issues

### "PDF upload fails"

1. **Check file isn't corrupted:**
   - Try opening in a PDF viewer
   - Try a different PDF

2. **Check file size:**
   - Very large PDFs may timeout
   - Try splitting into parts

3. **Check file permissions:**
   - Ensure you have read access

### "Cannot extract text from PDF"

This usually means the PDF is scanned images:
- Use OCR software first (Adobe Acrobat, etc.)
- Or try a different PDF with actual text

### "PDF processing timeout"

For large PDFs:
```python
# Use longer timeout
from PDFParser import pdf2md
markdown = pdf2md("large.pdf", timeout=300)  # 5 minutes
```

### "Encoding errors in PDF"

Some PDFs have encoding issues:
- Try `method="llamaparse"` in PDF parser
- Or convert PDF to text manually first

## Web Interface Issues

### "Cannot access localhost:5006"

1. **Check the server is running:**
   - Look for error messages in terminal

2. **Try a different port:**
   ```python
   pn.serve(ui.view(), port=5007)
   ```

3. **Check firewall settings**

4. **Try 127.0.0.1 instead of localhost**

### "Page not loading / blank screen"

1. Check browser console for errors (F12)
2. Clear browser cache
3. Try a different browser
4. Check terminal for Python errors

### "WebSocket connection failed"

Add websocket origin:
```python
pn.serve(ui.view(), websocket_origin='*')
```

## Search and Research Issues

### "No results from MedRxiv"

1. **Check internet connection**
2. **Verify date range is valid**
3. **Try broader search criteria**
4. **MedRxiv API may be temporarily down**

### "Research taking too long"

- Use faster model (gpt-3.5-turbo)
- Reduce number of search results
- Check internet connection

### "Tavily API error"

1. Verify API key in `.env`:
   ```
   TAVILY_API_KEY=tvly-...
   ```
2. Check key is valid at tavily.com
3. Check usage limits

## Memory Issues

### "Out of memory" during processing

1. **Use smaller models:**
   ```python
   llm = LLM(provider="ollama", model="llama3.2:7b")
   ```

2. **Process smaller batches:**
   ```python
   storage.ingest_pdf(pdf_path, batch_size=10)
   ```

3. **Close other applications**

4. **Increase swap space (Linux):**
   ```bash
   sudo fallocate -l 8G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

### "CUDA out of memory" (GPU)

1. **Use CPU instead:**
   ```bash
   export CUDA_VISIBLE_DEVICES=""
   ```

2. **Use smaller model**

3. **Reduce batch size**

## Common Error Messages

### "ImportError: No module named..."

```bash
pip install module_name

# Or reinstall all
pip install -r requirements.txt
```

### "FileNotFoundError: config.json"

Make sure you're running from the MedAiTools directory:
```bash
cd /path/to/MedAiTools
```

### "JSONDecodeError in config"

Check your JSON syntax in config files:
- No trailing commas
- Proper quotes
- Valid JSON format

### "SSL certificate error"

```bash
# Update certificates
pip install --upgrade certifi
```

## Getting More Help

### Collect Debug Information

When reporting issues, include:
```bash
# Python version
python --version

# Installed packages
pip freeze > packages.txt

# System info
uname -a  # Linux/Mac
systeminfo  # Windows
```

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Logs

Look for errors in:
- Terminal output
- `~/.medai/logs/` (if configured)
- PostgreSQL logs

### Report Issues

Include:
1. What you were trying to do
2. Exact error message
3. Steps to reproduce
4. System information
5. Configuration (without secrets)
