# Core Settings Module

**File:** `medai/Settings.py`

The Settings module provides centralized configuration management using the Singleton pattern.

## Overview

The Settings module contains four main components:

1. **Settings** - Application configuration singleton
2. **SharedMemory** - Inter-module shared state
3. **Logger** - Centralized logging
4. **Singleton** - Base class for singleton pattern

## Settings Class

### Purpose

Manages all application configuration from multiple sources:
- `config_local.json` - User-specific overrides (highest priority)
- `config.json` - Main configuration file
- `config.yaml` - LLM and vector database settings
- Default values in code (lowest priority)

### Usage

```python
from medai.Settings import Settings

# Get the singleton instance
settings = Settings()

# Access configuration as attributes
llm_provider = settings.llm_provider
db_host = settings.db_host

# All settings are accessible this way
print(settings.embedding_model)
print(settings.library_path)
```

### Default Configuration Values

| Setting | Default | Description |
|---------|---------|-------------|
| `llm_provider` | "ollama" | LLM provider (ollama, openai, anthropic, groq) |
| `llm_model` | "llama3.2" | Default LLM model name |
| `ollama_base_url` | "http://localhost:11434" | Ollama API endpoint |
| `embedding_provider` | "ollama" | Embedding provider |
| `embedding_model` | "bge-m3" | Embedding model name |
| `db_host` | "localhost" | PostgreSQL host |
| `db_port` | 5432 | PostgreSQL port |
| `db_name` | "medaitools" | Database name |
| `db_user` | "medai" | Database user |
| `library_path` | "~/medai/library" | Document storage path |
| `chunk_size` | 512 | Text chunk size for embeddings |
| `chunk_overlap` | 50 | Overlap between chunks |

### Methods

#### `load_settings() -> dict`

Load settings from all configuration sources.

```python
settings = Settings()
config = settings.load_settings()
```

#### `save_settings(new_settings: dict) -> None`

Save settings to `config_local.json`.

```python
settings.save_settings({
    "llm_provider": "openai",
    "llm_model": "gpt-4o"
})
```

#### `__getattr__(name: str) -> Any`

Dynamic attribute access for configuration values.

```python
# These are equivalent:
value = settings.llm_provider
value = settings._config.get("llm_provider")
```

### Configuration Files

#### config.json

Main configuration file:

```json
{
    "retriever": "tavily",
    "embedding_provider": "openai",
    "llm_provider": "openai",
    "fast_llm_model": "gpt-3.5-turbo-16k",
    "smart_llm_model": "gpt-4o",
    "fast_token_limit": 2000,
    "smart_token_limit": 4000,
    "browse_chunk_max_length": 8192,
    "summary_token_limit": 700,
    "temperature": 0.4,
    "user_agent": "Mozilla/5.0...",
    "max_search_results_per_query": 5,
    "memory_backend": "local",
    "total_words": 1000,
    "report_format": "markdown",
    "max_iterations": 4,
    "agent_role": null,
    "scraper": "bs",
    "max_subtopics": 3,
    "report_source": "web"
}
```

#### config.yaml

LLM and vector database configuration:

```yaml
llm:
  provider: ollama
  model: "llama3.2"
  base_url: 'http://localhost:11434'

vectordb:
  provider: qdrant
  collection_name: medai_index

embeddings:
  provider: ollama
  model: bge-m3
```

#### config_local.json

User-specific overrides (git-ignored):

```json
{
    "db_password": "my_secure_password",
    "openai_api_key": "sk-...",
    "llm_provider": "openai"
}
```

## SharedMemory Class

### Purpose

Provides a global shared state for inter-module communication.

### Usage

```python
from medai.Settings import SharedMemory

memory = SharedMemory()

# Store shared state
memory.current_document = "/path/to/document.pdf"
memory.active_session = "session_123"

# Access from another module
current_doc = memory.current_document
```

### Common Use Cases

- Sharing current document path across UI components
- Storing active session information
- Caching expensive computations
- Passing data between event handlers

## Logger Class

### Purpose

Centralized logging with consistent formatting.

### Usage

```python
from medai.Settings import Logger

logger = Logger()

# Different log levels
logger.debug("Detailed debugging info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical failure")

# With exception info
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
```

### Configuration

```python
# Set log level
logger.setLevel("DEBUG")  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Log to file
logger.add_file_handler("/var/log/medaitools.log")
```

## Singleton Base Class

### Purpose

Base class for implementing singleton pattern.

### Usage

```python
from medai.Settings import Singleton

class MyService(Singleton):
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        # Initialize only once
        self.connection = create_connection()

# Always returns the same instance
service1 = MyService()
service2 = MyService()
assert service1 is service2
```

### Implementation

```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

## Environment Variables

The Settings module also respects these environment variables:

| Variable | Description |
|----------|-------------|
| `MEDAI_CONFIG_PATH` | Path to config directory |
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GROQ_API_KEY` | Groq API key |
| `TAVILY_API_KEY` | Tavily search API key |
| `LLAMA_CLOUD_API_KEY` | LlamaParse API key |
| `DATABASE_URL` | Full PostgreSQL connection string |

## Best Practices

### 1. Use config_local.json for Secrets

Never commit secrets to `config.json`. Use `config_local.json`:

```json
{
    "db_password": "secret",
    "openai_api_key": "sk-..."
}
```

### 2. Access Settings Once

Cache settings reference for performance:

```python
# Good
settings = Settings()
provider = settings.llm_provider
model = settings.llm_model

# Avoid calling Settings() repeatedly in loops
```

### 3. Use SharedMemory for Temporary State

Don't abuse SharedMemory for configuration:

```python
# Good - temporary state
memory.current_selection = [1, 2, 3]

# Bad - use Settings instead
memory.llm_provider = "openai"  # Should be in Settings
```

## Related Modules

- [LLM](core-llm.md) - Uses Settings for provider configuration
- [PersistentStorage](storage.md) - Uses Settings for database connection
