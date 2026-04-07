# DeskFlow

> **Experimental example project for [barq-chat-form](https://github.com/YASSERRMD/barq-chat-form)**

DeskFlow demonstrates what you can build with barq-chat-form in a real-world scenario — an AI-powered IT helpdesk assistant that runs entirely in the browser, with no data ever leaving the user's machine.

It is not intended for production use. It exists to showcase barq-chat-form's form engine integrated with intent classification, runbook-based RAG, and on-device LLM inference via WebGPU.

Two deployment modes are included to cover both Python and pure-frontend usage of barq-chat-form:

| Mode | Path | Description |
|------|------|-------------|
| **FastAPI Backend** | `public/` | Python backend using `barq_chat_form` — intent detection, RAG, and prompt building server-side. Browser runs LLM inference via WebGPU. |
| **Standalone Frontend** | `deskflow-web/` | Pure browser implementation using `barq-chat-form.js` — zero backend, everything runs client-side. |

---

## Features

- **On-device LLM inference** via WebGPU — two models available, switchable at runtime:
  - [HuggingFaceTB/SmolLM2-360M-Instruct](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) — fast, lightweight
  - [LiquidAI/LFM2.5-350M](https://huggingface.co/onnx-community/LFM2.5-350M-ONNX) — hybrid convolutional-attention architecture from Liquid AI, optimised for edge inference
- **Structured intake forms** powered by [barq-chat-form](https://github.com/YASSERRMD/barq-chat-form) — 10 IT support form types
- **Intent classification** — keyword scoring across 10 IT categories with greeting detection
- **Runbook-backed RAG** — TF-IDF retrieval (server-side) or inline JS (client-side) from 10 markdown runbooks
- **Ticket generation** — auto-assigned `INC-XXXX` reference numbers with streamed LLM resolution responses
- **Graceful fallback** — rule-based template responses when WebGPU is unavailable
- **Privacy-first** — all processing is local; no telemetry, no server calls for inference

---

## How It Works

```
  User types a message
         │
         ▼
┌─────────────────────┐
│  Intent Classifier  │  keyword scoring — 10 IT intents + greeting detection
└──────────┬──────────┘
           │ intent label
           ▼
┌─────────────────────┐
│  Chat Response      │  LLM replies conversationally (WebGPU or template fallback)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Form Dispatcher    │  maps intent → barq-chat-form HTML form
└──────────┬──────────┘
           │ form injected into chat bubble
           ▼
      User fills form
           │
           ▼
┌─────────────────────┐
│  RAG Retrieval      │  TF-IDF over runbook knowledge base
└──────────┬──────────┘
           │ INC-XXXX ticket number + retrieved context
           ▼
┌─────────────────────┐
│  LLM Resolution     │  SmolLM2-360M or LFM2.5-350M via WebGPU
└──────────┬──────────┘
           │ streamed markdown response
           ▼
      Chat bubble rendered
```

---

## On-Device Models

DeskFlow runs inference entirely in the browser using the [Hugging Face Transformers.js](https://huggingface.co/docs/transformers.js) library with WebGPU acceleration. Models are downloaded once and cached by the browser.

### SmolLM2-360M-Instruct

A compact, instruction-tuned language model from Hugging Face. Ideal for low-latency responses on consumer hardware.

- **Model:** `HuggingFaceTB/SmolLM2-360M-Instruct`
- **Parameters:** 360M
- **Quantisation:** INT4 (q4) via ONNX

### LFM2.5-350M (Liquid AI)

A next-generation hybrid architecture from [Liquid AI](https://www.liquid.ai/) combining convolutional layers with full-attention layers. Purpose-built for efficient on-device inference with a 128K context window.

- **Model:** `onnx-community/LFM2.5-350M-ONNX`
- **Architecture:** LFM2 — 16 hybrid layers (conv + full-attention), SwiGLU activation, RoPE
- **Parameters:** 350M
- **Context window:** 128,000 tokens
- **Quantisation:** INT4 (q4) via ONNX

Both models stream tokens directly into chat bubbles and fall back to template responses if WebGPU is unavailable.

---

## Option 1 — FastAPI Backend (`public/`)

The Python backend handles intent classification, form dispatch, and RAG retrieval. The frontend fetches structured prompts from the API and runs LLM inference locally via WebGPU.

### Project Structure

```
├── main.py                    # FastAPI entry point + COOP/COEP headers
├── requirements.txt
├── .env.example
├── adapters/
│   └── fastapi_adapter.py     # /api/message, /api/submit, /api/resolve routes
├── intent/
│   └── classifier.py          # Keyword scoring — 10 IT intents + greeting detection
├── forms/
│   ├── dispatcher.py          # FORM_MAP: intent → build function
│   ├── vpn.py                 # VPN connectivity form
│   ├── account.py             # Account / MFA form
│   ├── hardware.py            # Hardware fault form
│   ├── software.py            # Software issue form
│   ├── network.py             # Network issue form
│   ├── email_comms.py         # Email / Teams form
│   ├── access.py              # Access request form
│   ├── procurement.py         # Procurement request form
│   ├── onboarding.py          # New joiner setup form (multi-step)
│   └── generic_incident.py    # Generic IT incident form
├── rag/
│   └── retriever.py           # TF-IDF index over knowledge/runbooks/
├── llm/
│   └── responder.py           # Prompt builders + template fallback
├── knowledge/
│   └── runbooks/              # 10 markdown runbooks (one per intent)
├── public/
│   └── index.html             # Chat UI — served at /
└── tests/
    ├── test_intent.py
    ├── test_forms.py
    └── test_pipeline.py
```

### Setup

```bash
git clone https://github.com/YASSERRMD/DeskFlow.git
cd DeskFlow

python -m venv venv
source venv/bin/activate       # macOS / Linux
# venv\Scripts\activate        # Windows

pip install -r requirements.txt
cp .env.example .env
```

### Run

```bash
python3 main.py
# http://localhost:8000
```

The FastAPI server serves the full chat UI at `/` and the standalone frontend at `/web/`.

### API Routes

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/message` | Detect intent, return chat prompts + form HTML |
| `POST` | `/api/submit` | RAG retrieval + resolution prompts + INC-XXXX ticket |
| `POST` | `/api/resolve` | Log a browser-generated LLM response |
| `GET`  | `/api/resolutions` | List all resolved tickets |

---

## Option 2 — Standalone Frontend (`deskflow-web/`)

Zero backend required. Intent detection, form building, runbook lookup, and LLM inference all run in the browser.

### Project Structure

```
deskflow-web/
├── index.html            # Chat UI — self-contained, no build step
├── barq-chat-form.js     # JS port of the barq-chat-form form engine
├── barq-chat-form.css    # Dark-theme form styles
├── forms.js              # 10 IT support forms built with barq-chat-form.js
└── intent.js             # Intent classifier, prompt builders, inline runbooks, template responses
```

### Run

Served automatically at `/web/` by the FastAPI server, or with any static file server:

```bash
cd deskflow-web
python3 -m http.server 8080
# http://localhost:8080
```

> **Requirements:** Chrome 113+ or any browser with WebGPU support. Falls back to template responses when WebGPU is unavailable.

---

## Self-Contained Build (`publish/index.html`)

`publish/index.html` is a single-file build with all JavaScript and CSS inlined — no external dependencies except CDN references for Tailwind, marked.js, and Transformers.js. Drop it anywhere and it works.

---

## Model Switcher

Both `public/index.html` and `deskflow-web/index.html` include a runtime model switcher in the header. Click **SmolLM2** or **LFM2.5** to hot-swap the active model. The previous model is disposed and the new one loads with a live progress bar. Pill buttons are disabled during the load and re-enabled on completion.

---

## Tests

```bash
python3 -m pytest tests/ -v
```

```
72 passing tests:
  36 intent tests    — all 10 intents, greeting detection, fallback, case insensitivity
  21 form tests      — all 10 form builds, field content, dispatcher
  15 pipeline tests  — load_knowledge_base, build_index, retrieve_context
```

---

## Extending DeskFlow

### Add a new IT form — FastAPI version

1. Create `forms/<name>.py` with a `build() -> str` function using `barq_chat_form`
2. Add intent keywords in `intent/classifier.py` → `INTENT_KEYWORDS`
3. Register the builder in `forms/dispatcher.py` → `FORM_MAP`
4. Add a template response in `llm/responder.py` → `_TEMPLATE_RESPONSES`

### Add a new IT form — standalone frontend

1. Add a builder function in `deskflow-web/forms.js` using `barq-chat-form.js`
2. Register it in `FORM_MAP` in `forms.js`
3. Add intent keywords in `deskflow-web/intent.js` → `INTENT_KEYWORDS`
4. Add a template response in `intent.js` → `TEMPLATES`

### Add a runbook — FastAPI version

Drop a `.md` or `.txt` file into `knowledge/runbooks/`. The TF-IDF index rebuilds automatically on next startup.

### Add a runbook — standalone frontend

Add an entry to `RUNBOOKS` in `deskflow-web/intent.js`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM inference | [Transformers.js](https://huggingface.co/docs/transformers.js) `@4.0.0` · WebGPU |
| Models | SmolLM2-360M-Instruct · LFM2.5-350M (Liquid AI) |
| Forms | [barq-chat-form](https://github.com/YASSERRMD/barq-chat-form) |
| Backend (optional) | FastAPI · Python 3.9+ |
| RAG | TF-IDF (scikit-learn server-side · custom JS client-side) |
| Styling | Tailwind CSS · Custom dark theme |
| Markdown rendering | marked.js |
