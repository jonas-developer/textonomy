# Textonomy AI

👉 **Live Demo:** https://textonomy.xyz

Textonomy is a multi-LLM AI detection platform that analyzes text and surfaces the highest-likelihood AI signal with transparent reasoning.

It evaluates submissions using multiple large language models — including OpenAI, DeepSeek, and IBM watsonx — to estimate the probability that a text was AI-generated.

The React frontend displays **only the highest-scoring model result**, including:

- AI-likelihood percentage  
- Red / Yellow / Green classification  
- Model explanation

## Tech Stack

**Backend**
- Django (Python)
- Django REST Framework
- LangChain

**Frontend**
- React (JavaScript)
- Vite

**LLM Providers**
- OpenAI  
- DeepSeek  
- IBM watsonx

**Database**
- PostgreSQL


# Repository Structure

```
textonomy-ai/
├── backend/        # Django + DRF + LangChain API
├── frontend/       # React (Vite)
├── .env.example
├── requirements.txt
└── README.md
```



# Backend (Django + LangChain)

The backend:

- Exposes `POST /api/analyze/`
- Calls 3 LLM providers:
  - OpenAI
  - DeepSeek
  - IBM watsonx
- Aggregates responses
- Returns structured JSON

---

## Requirements

- Python 3.11+
- PostgreSQL (optional — SQLite works for local development)
- Node.js 18+ (for frontend)

---

## Setup Python Environment

### From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Alternatively in repo directory

Python 3.11 is recommended (see `.python-version`).

```bash
pyenv install 3.11.8
pyenv local 3.11.8
python -m venv .venv
source .venv/bin/activate
python --version
```

## 2. Create LLM accounts of your choice and associated API keys.
- Example: Deepseek, Watsonx (IBM) and OpenAI
- Pick model. For example: gpt-4.1-mini, deepseek-chat, mistralai/mistral-small-3-1-24b-instruct-2503
- Fill in the associated API keys, urls, project ids etc as environmental variables (.env file)

## 2.1. Create .env file on the root directory
```bash
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

DATABASE_URL=postgresql://USERNAME:PASSWORD@localhost:5432/textonomy_ai

OPENAI_API_KEY=your_openai_key
DEEPSEEK_API_KEY=your_deepseek_key

WATSONX_CREDENTIALS={"apikey":"...","url":"...","project_id":"..."}

OPENAI_MODEL=gpt-4.1-mini
DEEPSEEK_MODEL=deepseek-chat
WATSONX_MODEL=meta-llama/llama-3-8b-instruct

MAX_GENERATIONS=1000
LLM_TIMEOUT=45

```

## 3. Run Backend Locally

```bash
cd backend
python manage.py migrate
python manage.py runserver

```
Backend runs at:
http://127.0.0.1:8000

## Test the API manually:

```bash
curl -X POST http://127.0.0.1:8000/api/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"text":"This is a test message."}'
```

## Frontend (React + Vite)

## The frontend:

- Mobile-friendly
- Displays only the highest scoring LLM result
- Shows score, color indicator, and reasoning

## 1. Install dependencies

```bash
cd frontend
npm install

```

## 2. Configure dev proxy. Ensure frontend/vite.config.js contains:

```javascript
server: {
  proxy: {
    "/api": "http://127.0.0.1:8000",
  },
}

```

## 3. Run the Frontend

```bash
npm run dev

```

## 3.1 Open: http://localhost:5173 in your web browser.

######


## Local Development Workflow - use two terminals

### Terminal 1 (Backend)

```bash
cd backend
python manage.py runserver


```

### Terminal 2 (Frontend)

```bash
cd frontend
npm run dev

```

## Production uses same-origin routing:

https://yourdomain.xyz/    → React
https://yourdomain/api/    → Django


# Live Demo

Try the live version:

👉 https://textonomy.xyz

## Steps

1. Paste text into the input field
2. Click **Analyze**

## How It Works

The system:

- Queries multiple LLMs
- Selects the highest scoring model
- Displays:
  - AI-likelihood percentage
  - Red / Yellow / Green classification
  - Explanation from that model


## 📌 Important Notes

- **This tool provides a likelihood indicator** — not proof of AI authorship.
- Results are **heuristic-based and model-dependent**.
- 🔐 **Do not submit confidential or sensitive data.**


## Contributing

Contributions, ideas, and issue reports are welcome.

If you'd like to improve Textonomy, please open an issue first to discuss proposed changes.

## Issues

If you encounter a bug or have a feature request, please open an issue.


## Copyright

© 2025 L.J. Bergman. All rights reserved.

Licensed under the [MIT License](LICENSE).