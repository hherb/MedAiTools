# Installation Guide

This guide walks you through installing MedAiTools on your computer.

## System Requirements

### Minimum Requirements
- **OS:** Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher
- **RAM:** 8GB
- **Storage:** 10GB free space
- **Internet:** Required for initial setup

### Recommended Requirements
- **RAM:** 16GB or more
- **Storage:** 50GB free space (for local LLM models)
- **GPU:** NVIDIA GPU with 8GB+ VRAM (for fast local AI)

## Installation Steps

### Step 1: Install Python

If you don't have Python installed:

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important:** Check "Add Python to PATH"
4. Click "Install Now"

**macOS:**
```bash
# Using Homebrew
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### Step 2: Download MedAiTools

```bash
# Clone the repository
git clone https://github.com/hherb/MedAiTools.git

# Enter the directory
cd MedAiTools
```

Or download the ZIP file from GitHub and extract it.

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it (Linux/macOS)
source venv/bin/activate

# Activate it (Windows)
.\venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This may take several minutes as it downloads all required packages.

### Step 5: Database Setup

MedAiTools uses PostgreSQL for storing documents and embeddings.

**Option A: Install PostgreSQL (Recommended)**

*Ubuntu/Debian:*
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

*macOS:*
```bash
brew install postgresql
brew services start postgresql
```

*Windows:*
Download and run the installer from [postgresql.org](https://www.postgresql.org/download/windows/)

**Create the database:**
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE medaitools;
CREATE USER medai WITH PASSWORD 'medai123';
GRANT ALL PRIVILEGES ON DATABASE medaitools TO medai;

# Enable pgvector extension
\c medaitools
CREATE EXTENSION IF NOT EXISTS vector;

# Exit
\q
```

**Option B: Use SQLite (Simpler, Limited Features)**

Edit `config_local.json`:
```json
{
    "database_backend": "sqlite",
    "sqlite_path": "~/medai/medaitools.db"
}
```

### Step 6: AI Provider Setup

Choose one or more AI providers:

**Option A: Local AI with Ollama (Free, Private)**

1. Install Ollama:
   ```bash
   # Linux/macOS
   curl -fsSL https://ollama.com/install.sh | sh

   # Windows: Download from ollama.com
   ```

2. Download a model:
   ```bash
   ollama pull llama3.2
   ollama pull bge-m3  # For embeddings
   ```

3. Ollama runs automatically in the background.

**Option B: Cloud AI (Faster, Costs Money)**

Create a `.env` file in the MedAiTools folder:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Groq (Fast & Free Tier)
GROQ_API_KEY=gsk_your-key-here

# Tavily (Web Search)
TAVILY_API_KEY=tvly-your-key-here
```

### Step 7: Configuration

Create `config_local.json` with your settings:

```json
{
    "db_host": "localhost",
    "db_port": 5432,
    "db_name": "medaitools",
    "db_user": "medai",
    "db_password": "medai123",

    "llm_provider": "ollama",
    "llm_model": "llama3.2",

    "library_path": "~/medai/library"
}
```

### Step 8: Verify Installation

```bash
# Activate virtual environment if not already active
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Run a simple test
python -c "from medai.Settings import Settings; print('Installation successful!')"
```

## Quick Test

Start the web interface:

```python
python -c "
import panel as pn
from RAG_UI import PDFPanel

panel = PDFPanel()
pn.serve(panel.view(), port=5007, show=True)
"
```

Open your browser to `http://localhost:5007`

## Troubleshooting Installation

### "pip not found"
```bash
python -m pip install --upgrade pip
```

### PostgreSQL connection fails
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify credentials in `config_local.json`
3. Check firewall allows port 5432

### Ollama not responding
```bash
# Check if running
curl http://localhost:11434/api/tags

# Restart if needed
systemctl restart ollama  # or start Ollama application
```

### Out of memory during installation
```bash
# Install packages one at a time
pip install pandas numpy
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### Permission denied errors (Linux)
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/medai
```

## Updating MedAiTools

```bash
cd MedAiTools
git pull
pip install -r requirements.txt --upgrade
```

## Uninstalling

```bash
# Remove the directory
rm -rf MedAiTools

# Remove data (optional)
rm -rf ~/medai

# Remove database (optional)
sudo -u postgres psql -c "DROP DATABASE medaitools;"
```

## Next Steps

- Follow the [Quick Start Guide](quickstart.md)
- Learn about [PDF Question & Answer](features/pdf-qa.md)
- Explore the [Research Assistant](features/research.md)
