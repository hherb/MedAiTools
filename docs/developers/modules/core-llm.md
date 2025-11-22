# Core LLM Module

**File:** `medai/LLM.py`

The LLM module provides a unified interface for interacting with multiple Large Language Model providers.

## Overview

This module abstracts away the differences between LLM providers, allowing you to switch between local (Ollama) and cloud (OpenAI, Anthropic, Groq) models with minimal code changes.

## Supported Providers

| Provider | Local/Cloud | Models |
|----------|-------------|--------|
| Ollama | Local | llama3.2, mistral, codellama, etc. |
| OpenAI | Cloud | gpt-4o, gpt-4-turbo, gpt-3.5-turbo |
| Anthropic | Cloud | claude-3-opus, claude-3-sonnet |
| Groq | Cloud | llama-3.1-70b, mixtral-8x7b |
| LiteLLM | Both | Universal adapter for 100+ providers |

## Main Classes

### LLM Class

The primary interface for LLM interactions.

#### Constructor

```python
from medai.LLM import LLM

llm = LLM(
    provider: str = "ollama",      # Provider name
    model: str = "llama3.2",       # Model name
    api_base: str | None = None,   # API endpoint (optional)
    temperature: float = 0.7,      # Sampling temperature
    max_tokens: int = 4096,        # Max response tokens
    api_key: str | None = None     # API key (optional)
)
```

#### Methods

##### generate()

Synchronous text generation:

```python
from medai.LLM import LLM

llm = LLM(provider="ollama", model="llama3.2")

# Simple generation
response = llm.generate("What is hypertension?")
print(response)

# With parameters
response = llm.generate(
    prompt="Explain diabetes in simple terms",
    temperature=0.5,
    max_tokens=500
)

# Get full response object
response = llm.generate(
    prompt="What is diabetes?",
    quickanswer=False  # Returns dict with metadata
)
print(response['content'])
print(response['usage'])
```

##### generate_streaming()

Async streaming generation:

```python
import asyncio
from medai.LLM import LLM

async def stream_response():
    llm = LLM(provider="ollama", model="llama3.2")

    async for chunk in llm.generate_streaming("Explain heart disease"):
        print(chunk, end="", flush=True)

asyncio.run(stream_response())
```

##### completion_call()

Low-level async completion:

```python
async def get_completion():
    llm = LLM(provider="openai", model="gpt-4o")

    async for chunk in llm.completion_call(
        prompt="Write a haiku about medicine",
        temperature=0.9
    ):
        yield chunk
```

### Model Class

Base class for model configurations.

```python
from medai.LLM import Model

model = Model(
    provider="openai",
    model_name="gpt-4o",
    api_key="sk-...",
    api_base=None,  # Uses default
    temperature=0.7,
    max_tokens=4096
)

# Generate using the model
response = model.generate("Hello!")
```

### OllamaModel Class

Specialized class for Ollama models.

```python
from medai.LLM import OllamaModel

model = OllamaModel(
    model_name="llama3.2",
    api_base="http://localhost:11434",
    temperature=0.7
)

# Check if model is available
if model.is_available():
    response = model.generate("Hello!")
else:
    print("Model not loaded in Ollama")
```

## Factory Functions

Convenient functions for creating common model configurations:

```python
from medai.LLM import (
    get_local_default_model,
    get_openai_multimodal_model,
    get_groq_model,
    get_anthropic_model
)

# Local Ollama model
local = get_local_default_model()

# OpenAI GPT-4
gpt4 = get_openai_multimodal_model()

# Fast Groq inference
groq = get_groq_model()

# Anthropic Claude
claude = get_anthropic_model()
```

## Utility Functions

### answer_this()

Quick one-off LLM call without instantiating a class:

```python
from medai.LLM import answer_this

response = answer_this(
    prompt="What is the capital of France?",
    modelname="llama3.2",
    api_base="http://localhost:11434",
    provider="ollama"
)
print(response)
```

### get_available_models()

List models available from a provider:

```python
from medai.LLM import get_available_models

# List Ollama models
ollama_models = get_available_models("ollama")
for model in ollama_models:
    print(model['name'])

# List OpenAI models
openai_models = get_available_models("openai")
```

## Provider-Specific Configuration

### Ollama (Local)

```python
llm = LLM(
    provider="ollama",
    model="llama3.2",
    api_base="http://localhost:11434"  # Default
)

# List available models
import ollama
models = ollama.list()
```

### OpenAI

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

llm = LLM(
    provider="openai",
    model="gpt-4o",
    temperature=0.7
)
```

### Anthropic

```python
import os
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."

llm = LLM(
    provider="anthropic",
    model="claude-3-sonnet-20240229",
    max_tokens=4096
)
```

### Groq

```python
import os
os.environ["GROQ_API_KEY"] = "gsk_..."

llm = LLM(
    provider="groq",
    model="llama-3.1-70b-versatile",
    temperature=0.5
)
```

### LiteLLM (Universal)

```python
# LiteLLM supports 100+ providers with unified interface
llm = LLM(
    provider="litellm",
    model="gpt-4",  # or any supported model
    api_key="..."
)
```

## Structured Output

For JSON/structured responses:

```python
from medai.LLM import LLM
from pydantic import BaseModel

class DiagnosisResult(BaseModel):
    condition: str
    confidence: float
    recommendations: list[str]

llm = LLM(provider="openai", model="gpt-4o")

response = llm.generate(
    prompt="Diagnose based on symptoms: fever, cough, fatigue",
    response_format=DiagnosisResult
)
# Returns structured DiagnosisResult object
```

## Error Handling

```python
from medai.LLM import LLM, LLMError, RateLimitError, AuthenticationError

llm = LLM(provider="openai", model="gpt-4o")

try:
    response = llm.generate("Hello")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded, retrying...")
except LLMError as e:
    print(f"LLM error: {e}")
```

## Prompt Templates

Common patterns for medical AI prompts:

```python
from medai.LLM import LLM

llm = LLM(provider="ollama", model="llama3.2")

# Medical summarization
SUMMARY_PROMPT = """
Summarize the following medical document in {max_sentences} sentences.
Focus on key findings, methodology, and conclusions.

Document:
{document}

Summary:
"""

response = llm.generate(
    SUMMARY_PROMPT.format(
        max_sentences=5,
        document=document_text
    )
)

# Clinical note generation
CLINICAL_NOTE_PROMPT = """
Generate a clinical consultation note for the following encounter:

Patient: {patient_name}, {age}yo {gender}
Chief Complaint: {chief_complaint}
History: {history}

Write a professional SOAP note:
"""

note = llm.generate(
    CLINICAL_NOTE_PROMPT.format(
        patient_name="John Smith",
        age=45,
        gender="male",
        chief_complaint="chest pain",
        history="Previous MI 2019"
    )
)
```

## Performance Tips

### 1. Reuse LLM Instances

```python
# Good - create once, use many times
llm = LLM(provider="ollama", model="llama3.2")
for question in questions:
    response = llm.generate(question)

# Bad - creates new connection each time
for question in questions:
    llm = LLM(provider="ollama", model="llama3.2")
    response = llm.generate(question)
```

### 2. Use Streaming for Long Responses

```python
# Better UX for long responses
async for chunk in llm.generate_streaming(long_prompt):
    display(chunk)
```

### 3. Batch Requests When Possible

```python
# If provider supports batching
responses = llm.generate_batch([
    "Question 1",
    "Question 2",
    "Question 3"
])
```

### 4. Cache Frequent Requests

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_generate(prompt: str) -> str:
    return llm.generate(prompt)
```

## Integration with Other Modules

### With RAG

```python
from RAG import RAG
from medai.LLM import LLM

# Custom LLM for RAG
llm = LLM(provider="openai", model="gpt-4o")
rag = RAG(llm=llm)
```

### With StudyCritique

```python
from StudyCritique import StudyCritique
from medai.LLM import LLM

llm = LLM(provider="anthropic", model="claude-3-opus")
critique = StudyCritique(llm=llm)
```

### With Synthetic Data

```python
from synthetic_health_record_generator import generate_health_record
from medai.LLM import get_local_default_model

model = get_local_default_model()
record = generate_health_record(person, llm=model)
```

## Troubleshooting

### Ollama Not Responding

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
systemctl restart ollama

# Pull model if missing
ollama pull llama3.2
```

### API Key Issues

```python
import os

# Verify key is set
assert os.getenv("OPENAI_API_KEY"), "API key not set"

# Test connection
llm = LLM(provider="openai", model="gpt-4o")
try:
    llm.generate("test")
except AuthenticationError:
    print("Invalid API key")
```

### Out of Memory

```python
# Use smaller model
llm = LLM(provider="ollama", model="llama3.2:7b")

# Reduce context
llm = LLM(provider="ollama", model="llama3.2", max_tokens=1024)
```

## Related Modules

- [Settings](core-settings.md) - Configuration for LLM providers
- [RAG](research.md) - Uses LLM for question answering
- [StudyCritique](analysis.md) - Uses LLM for paper analysis
