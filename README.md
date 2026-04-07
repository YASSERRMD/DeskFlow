# DeskFlow

AI-powered IT Helpdesk assistant with two implementations:

- **`public/`** — FastAPI backend + browser WebGPU inference (Python-powered)
- **`deskflow-web/`** — Fully standalone frontend (no backend, everything runs in the browser)

Both use [barq-chat-form](https://github.com/YASSERRMD/barq-chat-form) for structured intake forms and [SmolLM2-360M](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) via WebGPU for local LLM inference.

---

## How It Works

```
  User types a message
         │
         ▼
┌─────────────────────┐
│  Intent Classifier  │  keyword scoring over 10 intent categories
└──────────┬──────────┘
           │ intent label
           ▼
┌─────────────────────┐
│  Chat Response      │  LLM replies conversationally first
│  (WebGPU / template)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Form Dispatcher    │  maps intent → barq-chat-form HTML form
└──────────┬──────────┘
           │ HTML form injected into chat
           ▼
      User fills form
           │
           ▼
┌─────────────────────┐
│  RAG Context        │  runbook knowledge (TF-IDF server-side
│                     │  or inline JS client-side)
└──────────┬──────────┘
           │ INC-XXXX ticket + context
           ▼
┌─────────────────────┐
│  LLM Resolution     │  SmolLM2-360M via WebGPU in the browser
│  (WebGPU / template)│  or rule-based template fallback
└──────────┬──────────┘
           │ markdown response
           ▼
      Chat bubble rendered
```

---

## Option 1 — FastAPI Backend (`public/`)

Python FastAPI backend handles intent detection, RAG retrieval, and prompt building. The browser runs LLM inference via WebGPU.

### Project Structure

```
├── main.py                    # FastAPI entry point + COOP/COEP middleware
├── requirements.txt
├── .env.example
├── adapters/
│   └── fastapi_adapter.py     # /api/message, /api/submit, /api/resolve routes
├── intent/
│   └── classifier.py          # Keyword scoring — 10 IT intents + greeting detection
├── forms/
│   ├── dispatcher.py          # FORM_MAP: intent → build function
│   ├── vpn.py                 # VPN issue form
│   ├── account.py             # Account/MFA issue form
│   ├── hardware.py            # Hardware fault form
│   ├── software.py            # Software issue form
│   ├── network.py             # Network issue form
│   ├── email_comms.py         # Email/Teams issue form
│   ├── access.py              # Access request form
│   ├── procurement.py         # Procurement request form
│   ├── onboarding.py          # New joiner setup form (3 steps)
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
source venv/bin/activate       # macOS/Linux
# venv\Scripts\activate        # Windows

pip install -r requirements.txt
cp .env.example .env
```

### Run

```bash
python3 main.py
# open http://localhost:8000
```

The FastAPI server serves the chat UI at `/` and the frontend-only app at `/web/`.

### API Routes

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/message` | Detect intent, return chat prompts + form HTML |
| `POST` | `/api/submit` | RAG retrieval + resolution prompts + INC-XXXX ticket |
| `POST` | `/api/resolve` | Log browser-generated LLM response |
| `GET`  | `/api/resolutions` | List all resolved tickets |

---

## Option 2 — Standalone Frontend (`deskflow-web/`)

Zero backend. Everything — intent detection, form building, runbook lookup, and LLM inference — runs in the browser.

### Project Structure

```
deskflow-web/
├── index.html     # Full chat UI
├── barq-chat-form.js     # JS port of the barq-chat-form builder
├── barq-chat-form.css    # Dark-theme form styles
├── forms.js       # All 10 IT support forms built with barq-chat-form.js
└── intent.js      # Intent classifier, prompt builders, inline runbooks, template responses
```

### Run

Served automatically at `/web/` by the FastAPI server. Or run standalone with any static file server:

```bash
cd deskflow-web
python3 -m http.server 8080
# open http://localhost:8080
```

> **Note:** Requires a browser with WebGPU support (Chrome 113+). Falls back to template responses when WebGPU is unavailable.

---

## WebGPU LLM

Both versions use `HuggingFaceTB/SmolLM2-360M-Instruct` loaded via `@huggingface/transformers@3.5.0` directly in the browser. The model is downloaded once and cached by the browser. No data leaves the device.

- Model loads in the background — the app is fully usable via templates while loading
- Streams tokens into chat bubbles as they are generated
- Falls back to rule-based template responses if WebGPU is unavailable

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

### Add a new form (FastAPI version)

1. Create `forms/<name>.py` with a `build() -> str` function using barq-chat-form
2. Add keywords to `intent/classifier.py` → `INTENT_KEYWORDS`
3. Register in `forms/dispatcher.py` → `FORM_MAP`
4. Add a template response in `llm/responder.py` → `_TEMPLATE_RESPONSES`

### Add a new form (frontend-only version)

1. Add a builder function in `deskflow-web/forms.js` using `barq-chat-form.js`
2. Register it in `FORM_MAP` in `forms.js`
3. Add intent keywords in `deskflow-web/intent.js` → `INTENT_KEYWORDS`
4. Add a template response in `intent.js` → `TEMPLATES`

### Add a new runbook (FastAPI version)

Drop a `.md` or `.txt` file into `knowledge/runbooks/`. The TF-IDF index rebuilds automatically on next startup.

### Add runbook context (frontend version)

Add an entry to `RUNBOOKS` in `deskflow-web/intent.js`.
