# Insurance Lead Qualifier Bot (FastAPI)

Conversational form that qualifies prospects, extracts key fields, and writes
structured JSON suitable for a CRM. Includes a simple scoring heuristic.

## Tech
- Python 3.10+
- FastAPI, Uvicorn
- OpenAI Chat Completions
- Pydantic models

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API key
uvicorn app.main:app --reload
```

## Environment
```
OPENAI_API_KEY=sk-...
MODEL=gpt-4o-mini
```

## Portfolio Notes
- Problem: agents waste time on unqualified leads.
- Solution: bot gathers info (age, state, coverage type, budget), scores lead, and posts JSON to CRM webhook (stubbed).
- Next: plug into real CRM (HubSpot, Salesforce), add RAG over plan docs.
