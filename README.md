# DeskFlow

AI-powered IT Helpdesk assistant built with Chainlit, a local ONNX LLM (LFM2.5-350M), and a form-driven intake system using [formora](https://github.com/YASSERRMD/formora).

## Overview

DeskFlow uses natural language understanding to:
1. Detect the intent of an IT support request (10 categories)
2. Render a structured Tailwind-styled intake form tailored to that intent
3. Retrieve relevant runbook context via TF-IDF RAG over the knowledge base
4. Generate a step-by-step resolution using a local LFM2.5-350M ONNX model (or a rule-based template fallback)

## Architecture

```
  User types a message
         │
         ▼
┌─────────────────────┐
│  Intent Classifier  │  keyword scoring over 10 intent categories
│  (intent/classifier)│
└──────────┬──────────┘
           │ intent label
           ▼
┌─────────────────────┐
│  Form Dispatcher    │  maps intent → formora HTML form
│  (forms/dispatcher) │
└──────────┬──────────┘
           │ HTML form rendered in Chainlit
           ▼
      User fills form
           │
           ▼  formora submit (__formora__JSON)
┌─────────────────────┐
│  formora parse()    │  extracts typed_data from submission
└──────────┬──────────┘
           │ FormResult
           ▼
┌─────────────────────┐
│  RAG Retriever      │  TF-IDF search over knowledge/runbooks/
│  (rag/retriever)    │  returns top-5 relevant runbook chunks
└──────────┬──────────┘
           │ context string
           ▼
┌─────────────────────┐
│  LLM Responder      │  LFM2.5-350M-ONNX via optimum/onnxruntime
│  (llm/responder)    │  or rule-based template fallback
└──────────┬──────────┘
           │ markdown response
           ▼
    Chainlit chat message
```

## Project Structure

```
deskflow/
├── main.py                  # Chainlit entry point
├── demo.py                  # Terminal demo (no Chainlit required)
├── requirements.txt
├── .env.example
├── intent/
│   └── classifier.py        # Keyword scoring for 10 IT intents
├── forms/
│   ├── dispatcher.py        # FORM_MAP: intent → build function
│   ├── vpn.py               # VPN issue form
│   ├── account.py           # Account/MFA issue form
│   ├── hardware.py          # Hardware fault form
│   ├── software.py          # Software issue form
│   ├── network.py           # Network issue form
│   ├── email_comms.py       # Email/Teams issue form
│   ├── access.py            # Access request form (multi-step approval)
│   ├── procurement.py       # Procurement/purchase request form
│   ├── onboarding.py        # New joiner setup form (3 steps)
│   └── generic_incident.py  # Generic IT incident form
├── rag/
│   └── retriever.py         # TF-IDF index + retrieval with memory caching
├── llm/
│   └── responder.py         # ONNX model loading + template fallback
├── adapters/
│   └── chainlit_adapter.py  # on_chat_start + on_message handlers
├── knowledge/
│   └── runbooks/            # 10 markdown runbooks (one per intent)
└── tests/
    ├── test_intent.py        # 36 intent tests
    ├── test_forms.py         # 21 form tests
    └── test_pipeline.py      # 15 RAG pipeline tests
```

## Setup

### Prerequisites

- Python 3.9+
- Rust toolchain (for building formora from source)
- `maturin` build tool: `pip install maturin`

```bash
# 1. Clone the repo
git clone https://github.com/YASSERRMD/DeskFlow.git
cd DeskFlow

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows

# 3. Install dependencies (builds formora from source)
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — set MODEL_PATH to your LFM2.5-350M-ONNX directory
# The app works without a model using the built-in template fallback
```

### (Optional) Download LFM2.5-350M-ONNX

```bash
# Using Hugging Face CLI
pip install huggingface_hub
huggingface-cli download LiquidAI/LFM2.5-350M-ONNX --local-dir ./model/LFM2.5-350M-ONNX
```

Then set `MODEL_PATH=./model/LFM2.5-350M-ONNX` in `.env`.

## Run

```bash
# Interactive chat (Chainlit)
chainlit run main.py

# Terminal demo (no Chainlit)
python3 demo.py

# Tests
python3 -m pytest tests/ -v
```

## How to Add New Forms

1. Create `forms/<name>.py` with a `build() -> str` function using formora:
   ```python
   from formora import Form, CssFramework

   def build() -> str:
       return (
           Form("my_form_id")
           .css(CssFramework.tailwind())
           .text("field_name", "Field Label", required=True)
           .submit_label("Submit My Form")
           .build()
       )
   ```
2. Add keywords to `intent/classifier.py` → `INTENT_KEYWORDS` and an intro to `_INTRO_MESSAGES`
3. Register in `forms/dispatcher.py` → `FORM_MAP`
4. Add a template response in `llm/responder.py` → `_TEMPLATE_RESPONSES`

## How to Add New Runbooks

1. Add a `.md`, `.txt`, or `.pdf` file to `knowledge/runbooks/`
2. The RAG retriever automatically indexes new files on next startup (or `invalidate_index()`)
3. Structure runbooks with sections: Overview, Common Causes, Resolution Steps, Escalation

## How to Swap the LLM Model

1. Set `MODEL_PATH` in `.env` to the new model directory
2. If the model uses a different architecture than `ORTModelForCausalLM`, update `load_model()` in `llm/responder.py`
3. Adjust `max_new_tokens` and `do_sample` in the pipeline call as needed
4. The template fallback activates automatically if model loading fails

## Tests

```
72 passing tests:
  36 intent tests  — all 10 intents, fallback, case insensitivity
  21 form tests    — all 10 form builds, field content, dispatcher
  15 pipeline tests — load_knowledge_base, build_index, retrieve_context
```
