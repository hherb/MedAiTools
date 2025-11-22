# UI Components

This document covers the web-based user interface components in MedAiTools.

## Overview

MedAiTools uses [Panel](https://panel.holoviz.org/) for its web UI. All UI components are modular and can be used independently or combined.

| Module | Purpose |
|--------|---------|
| ResearcherUI | Main research assistant interface |
| RAG_UI | PDF Q&A chat interface |
| MedrXivPanel | Publication browser |
| StudyCritiqueUI | Paper analysis interface |
| DailyNews | News aggregation panel |

---

## ResearcherUI

**File:** `ResearcherUI.py`

Main research assistant web interface.

### Features

- Research query input
- LLM provider selection
- API key management
- Research report display
- Source citations

### Usage

```python
from ResearcherUI import ResearcherUI
import panel as pn

# Create and serve
ui = ResearcherUI()
pn.serve(ui.view(), port=5006, show=True)
```

### Components

```python
from ResearcherUI import (
    ResearcherUI,
    APIKeySettings,
    LLMSettings
)

# Main UI
ui = ResearcherUI()

# API Key configuration widget
api_settings = APIKeySettings()

# LLM selection widget
llm_settings = LLMSettings()
```

### Customization

```python
class CustomResearcherUI(ResearcherUI):
    """Custom research UI with additional features."""

    def __init__(self):
        super().__init__()
        # Add custom widgets
        self.custom_filter = pn.widgets.Select(
            name="Filter",
            options=["All", "Clinical", "Basic Science"]
        )

    def view(self):
        base_view = super().view()
        return pn.Column(
            self.custom_filter,
            base_view
        )
```

### Configuration

The UI reads settings from `researcher_settings.json`:

```json
{
    "default_llm_provider": "openai",
    "default_model": "gpt-4o",
    "max_results": 10,
    "report_format": "markdown"
}
```

---

## RAG_UI

**File:** `RAG_UI.py`

PDF document Q&A chat interface.

### Features

- PDF upload
- Chat-based Q&A
- Source highlighting
- Conversation history
- Document switching

### Usage

```python
from RAG_UI import PDFPanel
import panel as pn

# Create and serve
panel = PDFPanel()
pn.serve(panel.view(), port=5007, show=True)
```

### PDFPanel Class

```python
from RAG_UI import PDFPanel

panel = PDFPanel()

# Programmatic PDF loading
panel.load_pdf("/path/to/document.pdf")

# Submit a question
response = panel.submit_question("What are the main findings?")
```

### Chat Interface

```python
# Access chat history
history = panel.chat_history

# Clear conversation
panel.clear_chat()

# Export conversation
export = panel.export_chat()
```

### Customization

```python
class CustomPDFPanel(PDFPanel):
    """Custom PDF panel with additional features."""

    def __init__(self):
        super().__init__()
        # Add summary button
        self.summary_btn = pn.widgets.Button(name="Generate Summary")
        self.summary_btn.on_click(self._generate_summary)

    def _generate_summary(self, event):
        if self.current_pdf:
            summary = self.rag.query("Summarize this document")
            self.display_message(summary.response)
```

---

## MedrXivPanel

**File:** `MedrXivPanel.py`

Publication browser and fetcher.

### Features

- Date range selection
- Category filtering
- Publication search
- PDF download
- Metadata display

### Usage

```python
from MedrXivPanel import MedrXivPanel
import panel as pn

panel = MedrXivPanel()
pn.serve(panel.view(), port=5008, show=True)
```

### Components

```python
from MedrXivPanel import MedrXivPanel

panel = MedrXivPanel()

# Access widgets
panel.date_from  # Date picker
panel.date_to    # Date picker
panel.category   # Category selector
panel.search_box # Search input

# Trigger fetch
panel.fetch_publications()

# Get selected publication
pub = panel.selected_publication
```

### Publication Display

```python
# Get current publications list
publications = panel.publications

# Filter displayed publications
panel.filter_by_category("Cardiology")
panel.search("diabetes")

# Download PDF for selected
panel.download_pdf(pub)
```

### Event Handling

```python
# Register callback for selection
def on_select(pub):
    print(f"Selected: {pub['title']}")

panel.on_publication_selected = on_select
```

---

## StudyCritiqueUI

**File:** `StudyCritiqueUI.py`

Research paper analysis interface.

### Features

- PDF upload
- Summary generation
- Quality critique
- Keyword extraction
- Export results

### Usage

```python
from StudyCritiqueUI import StudyCritiquePanel
import panel as pn

panel = StudyCritiquePanel()
pn.serve(panel.view(), port=5009, show=True)
```

### Components

```python
from StudyCritiqueUI import StudyCritiquePanel

panel = StudyCritiquePanel()

# Load document
panel.load_document("/path/to/paper.pdf")

# Generate analyses
panel.generate_summary()
panel.generate_critique()
panel.extract_keywords()

# Access results
print(panel.summary)
print(panel.critique)
print(panel.keywords)
```

---

## DailyNews

**File:** `DailyNews.py`

News aggregation panel.

### Features

- Medical news aggregation
- Category filtering
- Source selection
- Refresh functionality

### Usage

```python
from DailyNews import NewsPanel
import panel as pn

panel = NewsPanel()
pn.serve(panel.view(), port=5010, show=True)
```

---

## Creating Custom UI Components

### Basic Panel Structure

```python
import panel as pn
from medai.Settings import Settings

class CustomPanel:
    """Base structure for custom panels."""

    def __init__(self):
        self.settings = Settings()
        self._setup_widgets()
        self._setup_callbacks()

    def _setup_widgets(self):
        """Initialize widgets."""
        self.title = pn.pane.Markdown("# My Custom Panel")
        self.input = pn.widgets.TextInput(name="Input")
        self.submit = pn.widgets.Button(name="Submit")
        self.output = pn.pane.Markdown("")

    def _setup_callbacks(self):
        """Setup event handlers."""
        self.submit.on_click(self._on_submit)

    def _on_submit(self, event):
        """Handle submit button click."""
        self.output.object = f"You entered: {self.input.value}"

    def view(self):
        """Return the panel layout."""
        return pn.Column(
            self.title,
            self.input,
            self.submit,
            self.output
        )
```

### Adding LLM Integration

```python
import panel as pn
from medai.LLM import LLM

class LLMPanel:
    """Panel with LLM integration."""

    def __init__(self):
        self.llm = LLM(provider="ollama", model="llama3.2")
        self._setup_widgets()

    def _setup_widgets(self):
        self.prompt = pn.widgets.TextAreaInput(
            name="Prompt",
            height=100
        )
        self.submit = pn.widgets.Button(name="Generate")
        self.submit.on_click(self._generate)
        self.output = pn.pane.Markdown("")
        self.loading = pn.indicators.LoadingSpinner(value=False)

    def _generate(self, event):
        self.loading.value = True
        try:
            response = self.llm.generate(self.prompt.value)
            self.output.object = response
        finally:
            self.loading.value = False

    def view(self):
        return pn.Column(
            self.prompt,
            pn.Row(self.submit, self.loading),
            self.output
        )
```

### Chat Interface Pattern

```python
import panel as pn

class ChatPanel:
    """Chat interface pattern."""

    def __init__(self):
        self.messages = []
        self._setup_widgets()

    def _setup_widgets(self):
        self.chat_display = pn.Column(sizing_mode='stretch_width')
        self.input = pn.widgets.TextInput(
            placeholder="Type your message...",
            sizing_mode='stretch_width'
        )
        self.send = pn.widgets.Button(name="Send")
        self.send.on_click(self._send_message)

        # Also send on Enter
        self.input.param.watch(self._on_enter, 'value_input')

    def _on_enter(self, event):
        if event.new == '\n':
            self._send_message(None)

    def _send_message(self, event):
        if self.input.value.strip():
            self._add_message("user", self.input.value)
            response = self._get_response(self.input.value)
            self._add_message("assistant", response)
            self.input.value = ""

    def _add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

        style = "background-color: #e3f2fd;" if role == "user" else "background-color: #f5f5f5;"
        msg = pn.pane.Markdown(
            f"**{role.title()}:** {content}",
            style={style}
        )
        self.chat_display.append(msg)

    def _get_response(self, message):
        # Override in subclass
        return "Response placeholder"

    def view(self):
        return pn.Column(
            self.chat_display,
            pn.Row(self.input, self.send)
        )
```

### File Upload Pattern

```python
import panel as pn

class FileUploadPanel:
    """File upload pattern."""

    def __init__(self, accepted_types=['.pdf']):
        self.accepted_types = accepted_types
        self._setup_widgets()

    def _setup_widgets(self):
        self.file_input = pn.widgets.FileInput(
            accept=','.join(self.accepted_types)
        )
        self.file_input.param.watch(self._on_upload, 'value')
        self.status = pn.pane.Markdown("")

    def _on_upload(self, event):
        if self.file_input.value:
            filename = self.file_input.filename
            content = self.file_input.value

            # Save file
            path = f"/tmp/{filename}"
            with open(path, 'wb') as f:
                f.write(content)

            self.status.object = f"Uploaded: {filename}"
            self._process_file(path)

    def _process_file(self, path):
        # Override in subclass
        pass

    def view(self):
        return pn.Column(
            self.file_input,
            self.status
        )
```

---

## Styling

### CSS Customization

```python
# Load custom CSS
pn.config.raw_css.append("""
.custom-panel {
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
}

.custom-button {
    background-color: #1976d2;
    color: white;
}
""")

# Apply to widget
button = pn.widgets.Button(
    name="Submit",
    css_classes=['custom-button']
)
```

### Using styles.css

The project includes `styles.css` for consistent styling:

```python
import panel as pn

# Load project styles
pn.config.css_files.append("styles.css")
```

---

## Serving Multiple Panels

```python
import panel as pn
from ResearcherUI import ResearcherUI
from RAG_UI import PDFPanel
from MedrXivPanel import MedrXivPanel

# Create panels
researcher = ResearcherUI()
rag = PDFPanel()
medrxiv = MedrXivPanel()

# Create tabbed interface
tabs = pn.Tabs(
    ("Research", researcher.view()),
    ("PDF Q&A", rag.view()),
    ("Publications", medrxiv.view())
)

# Serve
pn.serve(tabs, port=5006, show=True)
```

---

## Deployment

### Production Serving

```python
import panel as pn
from ResearcherUI import ResearcherUI

ui = ResearcherUI()

pn.serve(
    ui.view(),
    port=5006,
    address='0.0.0.0',  # Allow external connections
    show=False,
    websocket_origin='*',
    num_procs=4  # Multiple workers
)
```

### With Gunicorn

```bash
# Serve with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:create_app
```

```python
# app.py
import panel as pn
from ResearcherUI import ResearcherUI

def create_app():
    ui = ResearcherUI()
    return pn.serve(ui.view(), show=False)
```

---

## Related Modules

- [RAG](research.md) - Backend for RAG_UI
- [Researcher](research.md#researcher) - Backend for ResearcherUI
- [PGMedrXivScraper](publication-scraping.md) - Backend for MedrXivPanel
- [StudyCritique](analysis.md) - Backend for StudyCritiqueUI
