# DeskFlow

AI-powered IT Helpdesk assistant built with Chainlit, a local ONNX LLM (LFM2.5-350M), and a form-driven intake system using formora.

## Overview

DeskFlow uses natural language understanding to:
1. Detect the intent of an IT support request
2. Render a structured intake form tailored to that intent
3. Retrieve relevant runbook context via TF-IDF RAG
4. Generate a step-by-step resolution using a local LLM

## Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd deskflow

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your model path and knowledge directory

# 5. Download LFM2.5-350M-ONNX model
# Place model files in the directory specified by MODEL_PATH in .env
```

## Run

```bash
chainlit run main.py
```

## Project Structure

```
deskflow/
├── main.py                  # Chainlit entry point
├── requirements.txt
├── .env.example
├── intent/
│   └── classifier.py        # Keyword-based intent detection
├── forms/
│   ├── dispatcher.py        # Maps intents to forms
│   ├── vpn.py               # VPN issue form
│   ├── account.py           # Account issue form
│   ├── hardware.py          # Hardware issue form
│   ├── software.py          # Software issue form
│   ├── network.py           # Network issue form
│   ├── email_comms.py       # Email/comms issue form
│   ├── access.py            # Access request form
│   ├── procurement.py       # Procurement request form
│   ├── onboarding.py        # Onboarding setup form
│   └── generic_incident.py  # Generic incident form
├── rag/
│   └── retriever.py         # TF-IDF knowledge base retrieval
├── llm/
│   └── responder.py         # ONNX LLM response generation
├── adapters/
│   └── chainlit_adapter.py  # Chainlit event handlers
└── knowledge/
    └── runbooks/            # Markdown runbook files
```

## How to Add New Forms

1. Create `forms/<name>.py` with a `build() -> str` function using formora
2. Add the intent keyword list to `intent/classifier.py` under `INTENT_KEYWORDS`
3. Register the form in `forms/dispatcher.py` under `FORM_MAP`

## How to Add New Runbooks

1. Add a `.md` or `.txt` file to `knowledge/runbooks/`
2. The RAG retriever will automatically index it on next startup

## How to Swap the LLM Model

1. Update `MODEL_PATH` in your `.env` file
2. In `llm/responder.py`, adjust `load_model()` if the new model uses a different architecture
3. The fallback template responder will be used if the model fails to load

## Architecture

```
User Message
     │
     ▼
Intent Classifier (keyword scoring)
     │
     ├──► Form Dispatcher → formora HTML Form → User fills form
     │                                               │
     │                                               ▼
     │                                     formora Parse Result
     │                                               │
     ├──────────────────────────────────────────────►│
     │                                               ▼
     │                                     RAG Retriever (TF-IDF)
     │                                               │
     │                                               ▼
     └──────────────────────────────────────► LLM Responder (ONNX)
                                                      │
                                                      ▼
                                              Markdown Response
```
