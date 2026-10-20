# LLM Analyst (`research-task`)

[![PyPI version](https://img.shields.io/pypi/v/research-task.svg?color=blue)](https://pypi.org/project/research-task/)
[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An autonomous multi-agent research analyst and report generation framework. **LLM Analyst** conducts in-depth automated research across public web engines, targeted URLs, and local document repositories (including biomedical literature and scientific PDFs). It decompresses, analyzes, and synthesizes source material into publication-ready, APA-cited reports in Markdown, PDF, and Word DOCX formats.

---

## Table of Contents

- [Key Capabilities](#key-capabilities)
- [Architecture & Workflow](#architecture--workflow)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Quickstart Guide](#quickstart-guide)
  - [1. Simple Web Research](#1-simple-web-research)
  - [2. Hierarchical Detailed Report (Multi-Agent)](#2-hierarchical-detailed-report-multi-agent)
  - [3. Local Document & Paper Research](#3-local-document--paper-research)
  - [4. Multi-Format Publishing (PDF, DOCX, MD)](#4-multi-format-publishing-pdf-docx-md)
- [Configuration Reference](#configuration-reference)
  - [Configuration File & Variables](#configuration-file--variables)
  - [Search Engines](#search-engines)
  - [LLM & Embedding Providers](#llm--embedding-providers)
- [Data Ingestion & Academic Intelligence](#data-ingestion--academic-intelligence)
- [Project Structure](#project-structure)
- [Testing & Validation](#testing--validation)
- [License](#license)

---

## Key Capabilities

- **Autonomous Agent Personas**: Dynamically assigns domain-specialized agent personas (Finance, Business Analyst, Academic Researcher, etc.) with custom system prompts tailored to the specific query.
- **Hierarchical Multi-Agent Coordination**: `LLMEditor` orchestrates multiple `LLMAnalyst` sub-agents, recursively partitioning broad subjects into targeted subtopics and consolidating the findings into a unified document.
- **Multi-Source Ingestion**:
  - **Web Search**: Integrates with DuckDuckGo (free, default), Tavily, Serper, SerpAPI, Google Custom Search, and Bing.
  - **Local Knowledge Store**: Ingests collections of local files (`.pdf`, `.docx`, `.pptx`, `.csv`, `.xlsx`, `.md`, `.txt`) into ChromaDB with SHA-256 directory hashing for instant incremental caching.
  - **Curated URLs**: Deep-dives into specific lists of user-provided URLs.
- **Domain-Specific & Academic Scrapers**:
  - `arxiv_scraper`: Direct abstract and paper extraction from arXiv.
  - `pdf_scraper`: PyMuPDF document extraction.
  - `cell_selenium_scraper`: Headless browser automation handling cookie consent and publisher portals (e.g., Cell Press).
  - High-throughput parallel scraping via `ThreadPoolExecutor`.
- **Contextual Compression**: Combines chunking, recursive text splitting, and vector similarity filtering (`ContextCompressor`) to isolate high-signal excerpts and eliminate token bloat.
- **Automated Document Synthesis**: `LLMWriter` automatically extracts headings, generates nested hierarchical Tables of Contents, drafts structured introductions, and compiles clean reference bibliographies.
- **Multi-Format Export**: Generates `.md`, professionally styled `.pdf` (via CSS-styled `md2pdf`), and editable `.docx` files.

---

## Architecture & Workflow

```mermaid
flowchart TD
    User([User Request / Topic]) --> Config[Config & DataSource Selection]
    Config --> Mode{Data Source}

    %% Ingestion Paths
    Mode -->|DataSource.WEB| Search[Multi-Engine Search: DDG / Tavily / Serper]
    Mode -->|DataSource.LOCAL_STORE| Chroma[ChromaDB Local Vector Store & SHA-256 Cache]
    Mode -->|DataSource.SELECT_URLS| DirectURLs[Custom URL List]

    Search --> ScraperPool[Parallel Scraper Pool\nArXiv | PDF | Cell Selenium | Web]
    DirectURLs --> ScraperPool

    %% Context Processing
    ScraperPool --> Compressor[ContextCompressor: Embeddings Filter & Text Splitter]
    Chroma --> Compressor

    %% Agent Core
    Compressor --> Analyst[LLMAnalyst: Persona Selection & Sub-Query Generation]
    Analyst --> Editor{Report Level}

    Editor -->|Standard Report| Writer[LLMWriter: APA Citations & Formatting]
    Editor -->|Detailed Multi-Agent Report| Subtopics[LLMEditor: Subtopic Assistants Dispatch]
    Subtopics --> Analyst
    Subtopics --> Writer

    %% Publication
    Writer --> State[ResearchState Snapshot]
    State --> Publisher[LLMPublisher]
    Publisher --> OutMD[Markdown .md]
    Publisher --> OutPDF[Styled PDF .pdf]
    Publisher --> OutDOCX[Word Document .docx]
```

---

## Installation

### From PyPI

```bash
pip install research-task
```

### From Source

Clone the repository and install dependencies in your virtual environment:

```bash
git clone https://github.com/DanHUMassMed/llm_analyst.git
cd llm_analyst
pip install -r requirements.txt
pip install -e .
```

*Note: For headless browser scraping (e.g. `cell.com` via Selenium), ensure Firefox and geckodriver are installed, or install `pyvirtualdisplay` / `Xvfb` on Linux/macOS.*

---

## Environment Setup

Configure your preferred API keys via environment variables or a `.env` file:

```bash
# Core LLM Providers (OpenAI default)
export OPENAI_API_KEY="your-openai-api-key"
export GROQ_API_KEY="your-groq-api-key"

# Search Providers (DuckDuckGo requires no API key)
export TAVILY_API_KEY="your-tavily-api-key"
export SERPER_API_KEY="your-serper-api-key"
export SERP_API_KEY="your-serpapi-key"
export GOOGLE_API_KEY="your-google-api-key"
export GOOGLE_CX_KEY="your-google-cx-key"
export BING_API_KEY="your-bing-api-key"

# User-Agent header (recommended for web scraping)
export USER_AGENT="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
```

---

## Quickstart Guide

### 1. Simple Web Research

Generate an objective, APA-referenced research report from the live web:

```python
import asyncio
from llm_analyst.core.config import Config, DataSource
from llm_analyst.core.research_analyst import LLMAnalyst

async def main():
    topic = "Recent breakthroughs in synthetic biology and metabolic engineering"
    
    # Initialize analyst with default web search (DuckDuckGo) and OpenAI GPT-4o
    analyst = LLMAnalyst(
        active_research_topic=topic,
        data_source=DataSource.WEB
    )
    
    # Conduct research and generate report
    await analyst.conduct_research()
    state = await analyst.write_report()
    
    print(state.report_md)

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Hierarchical Detailed Report (Multi-Agent)

For deep, multi-section investigations, `LLMEditor` decomposes the main subject into subtopics, delegates each subtopic to an `LLMAnalyst` instance, and merges the findings:

```python
import asyncio
from llm_analyst.core.research_editor import LLMEditor
from llm_analyst.core.research_publisher import LLMPublisher
from llm_analyst.core.config import DataSource

async def main():
    topic = "CRISPR-Cas9 off-target mitigation strategies in clinical gene therapy"
    
    editor = LLMEditor(
        active_research_topic=topic,
        data_source=DataSource.WEB
    )
    
    # Spawns sub-agents, conducts research across subtopics, builds TOC & references
    research_state = await editor.create_detailed_report()
    
    # Publish to Markdown, PDF, and Word
    publisher = LLMPublisher(**research_state.dump())
    await publisher.publish_to_md_file()
    await publisher.publish_to_pdf_file()
    await publisher.publish_to_word_file()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Local Document & Paper Research

Research against an existing folder of PDFs, Word documents, presentations, or data tables:

```python
import asyncio
from llm_analyst.core.config import Config, DataSource
from llm_analyst.core.research_analyst import LLMAnalyst

async def main():
    config = Config()
    config.set_values_for_config({
        "local_store_dir": "/path/to/research_papers",
        "cache_dir": "./data/vector_cache"
    })
    
    query = "What mechanisms link S-adenosylmethionine to lipid metabolism?"
    
    analyst = LLMAnalyst(
        active_research_topic=query,
        data_source=DataSource.LOCAL_STORE,
        config=config
    )
    
    await analyst.conduct_research()
    state = await analyst.write_report()
    print(state.report_md)

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Multi-Format Publishing (PDF, DOCX, MD)

Export any research state snapshot to styled PDF, Word DOCX, or Markdown:

```python
from llm_analyst.core.research_publisher import LLMPublisher

publisher = LLMPublisher(**research_state.dump(), config=config)

# Export options
md_path = await publisher.publish_to_md_file()     # -> ~/llm_analyst_out/Research-*.md
pdf_path = await publisher.publish_to_pdf_file()   # -> ~/llm_analyst_out/Research-*.pdf
docx_path = await publisher.publish_to_word_file() # -> ~/llm_analyst_out/Research-*.docx
```

---

## Configuration Reference

Configuration can be customized via:
1. Environment variables.
2. Custom config file set via `LLM_ANALYST_CONFIG=/path/to/custom.config`.
3. Direct dictionary overrides via `config.set_values_for_config({...})`.

### Configuration File & Variables

| Config Key | Environment Variable | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `internet_search` | `INTERNET_SEARCH` | `ddg_search` | Search engine function name (`ddg_search`, `tavily_search`, etc.) |
| `embedding_provider` | `EMBEDDING_PROVIDER` | `openai` | Embeddings provider (`openai`, `ollama`, `huggingface`) |
| `llm_provider` | `LLM_PROVIDER` | `openai` | LLM module under `chat_models` (`openai`, `groq`) |
| `llm_model` | `LLM_MODEL` | `gpt-4o-2024-05-13` | Specific LLM model string |
| `llm_token_limit` | `LLM_TOKEN_LIMIT` | `4000` | Max tokens for generation |
| `llm_temperature` | `LLM_TEMPERATURE` | `0.25` | Model temperature (lower for deterministic factual output) |
| `max_search_results_per_query` | `MAX_SEARCH_RESULTS_PER_QUERY` | `5` | Maximum search results retrieved per sub-query |
| `total_words` | `TOTAL_WORDS` | `1000` | Minimum target word count for generated reports |
| `max_subsections` | `MAX_SUBSECTIONS` | `5` | Maximum subsections per subtopic report |
| `max_iterations` | `MAX_ITERATIONS` | `3` | Number of sub-queries generated per research task |
| `max_subtopics` | `MAX_SUBTOPICS` | `3` | Maximum subtopics generated for detailed reports |
| `report_out_dir` | `REPORT_OUT_DIR` | `~/llm_analyst_out` | Output directory for rendered reports |
| `local_store_dir` | `LOCAL_STORE_DIR` | `""` | Directory containing local documents for ingestion |
| `cache_dir` | `CACHE_DIR` | `~/.cache/llm_analyst`| Vector database persistence directory |

### Search Engines

- `ddg_search`: DuckDuckGo text search (**default, free, no API key required**).
- `tavily_search`: AI-optimized search engine (`TAVILY_API_KEY`).
- `serper_search`: Google Serper API (`SERPER_API_KEY`).
- `serp_api_search`: SerpAPI Google Search (`SERP_API_KEY`).
- `google_search`: Google Custom Search API (`GOOGLE_API_KEY`, `GOOGLE_CX_KEY`).
- `bing_search`: Microsoft Bing Web Search API (`BING_API_KEY`).

### LLM & Embedding Providers

- **LLM Models**:
  - `openai`: `OPENAI_Model` (GPT-4o, GPT-4-turbo, GPT-3.5-turbo).
  - `groq`: `GROQ_Model` (Llama 3, Mixtral 8x7B, Gemma).
- **Embedding Models**:
  - `openai`: `OpenAIEmbeddings`.
  - `ollama`: `OllamaEmbeddings(model="llama3")`.
  - `huggingface`: `HuggingFaceEmbeddings()`.
  - Chroma local embeddings: `SentenceTransformerEmbeddings("all-MiniLM-L6-v2")`.

---

## Data Ingestion & Academic Intelligence

`llm_analyst` includes specialized utilities built for academic, scientific, and biomedical workflows:

1. **PubMed & PMC Canonical Linking**:
   When indexing text files adhering to PubMed or PMC naming conventions (`PM12345.txt` or `PMC12345.txt`), the system automatically resolves them to canonical web URLs (`https://pubmed.ncbi.nlm.nih.gov/12345/` and `https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12345/`) for clean inline citations.
2. **Directory Hashing & Incremental Cache**:
   `VectorStore` computes a cumulative SHA-256 hash across all files in your `local_store_dir`. If the local files have not changed, it skips re-indexing and utilizes the cached ChromaDB vectors immediately.
3. **Multi-Format Ingestion**:
   Supports recursive directory ingestion for:
   - PDF (`.pdf`) via `PyMuPDFLoader`
   - Plain Text (`.txt`)
   - Word Documents (`.doc`, `.docx`)
   - PowerPoint (`.pptx`)
   - Spreadsheets (`.csv`, `.xls`, `.xlsx`)
   - Markdown (`.md`)
4. **Targeted Scrapers**:
   - `arxiv_scraper`: Automatically retrieves paper abstracts directly from arXiv.
   - `cell_selenium_scraper`: Automates cookie acceptance dialogs and extracts structured full-text from scientific journal portals.

---

## Project Structure

```
llm_analyst/
├── llm_analyst/
│   ├── chat_models/              # LLM interfaces
│   │   ├── groq.py               # Groq provider (ChatGroq)
│   │   └── openai.py             # OpenAI provider (ChatOpenAI)
│   ├── core/                     # Core research framework
│   │   ├── config.py             # Config, ReportType, DataSource
│   │   ├── exceptions.py         # Custom exceptions
│   │   ├── prompts.py            # Singleton prompt manager
│   │   ├── research_analyst.py   # LLMAnalyst core agent
│   │   ├── research_editor.py    # LLMEditor hierarchical coordinator
│   │   ├── research_publisher.py # Multi-format export (PDF/DOCX/MD)
│   │   ├── research_state.py     # State management & serialization
│   │   └── research_writer.py    # TOC, intro, and reference generation
│   ├── documents/                # Ingestion & storage
│   │   ├── document.py           # DocumentLoader for multi-format files
│   │   └── vector_store.py       # ChromaDB vector store with SHA caching
│   ├── embedding_methods/        # Context compression
│   │   └── compressor.py         # ContextCompressor with embeddings filter
│   ├── resources/                # Assets & templates
│   │   ├── llm_analyst.config    # Default config schema
│   │   ├── pdf_styles.css        # CSS stylesheet for PDF reports
│   │   └── prompts.json          # System & task prompts
│   ├── scrapers/                 # Specialized web scraping
│   │   └── scraper_methods.py    # arXiv, PyMuPDF, Selenium, WebBaseLoader
│   ├── search_methods/           # Search providers
│   │   └── internet_search.py    # DuckDuckGo, Tavily, Google, Serper, Bing
│   └── utils/                    # Common utilities & logging
│       ├── app_logging.py
│       └── utilities.py
├── notebooks/                    # Interactive walkthroughs
│   ├── example_runs.ipynb
│   ├── example_slack_channel.ipynb
│   └── reference.ipynb
├── tests/                        # Comprehensive pytest suite
├── setup.py                      # Package setup (research-task)
├── requirements.txt              # Dependency specifications
└── LICENSE                       # MIT License
```

---

## Testing & Validation

The test suite covers unit and integration tests across core agents, scrapers, search methods, vector stores, and publishing pipelines:

```bash
# Run the complete test suite
pytest

# Run tests with output logging
pytest -v -s

# Run core analyst tests
pytest tests/llm_analyst/core/test_research_analyst.py
```

*Note: Some tests require external API credentials (e.g. `OPENAI_API_KEY`). Ensure your environment variables are set before executing end-to-end LLM tests.*

---

## License

This project is licensed under the [MIT License](LICENSE).
Copyright (c) 2024 Daniel Higgins / Assaf Elovic.
