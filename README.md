🛡️ Insurance Lead Qualifier Bot (FastAPI)

A conversational chatbot built with FastAPI that qualifies insurance leads in real time.
It extracts customer information (age, state, insurance type, budget, provider, urgency), scores the lead, and returns structured JSON ready for a CRM.

🚀 Features

- Conversational FastAPI chatbot endpoint (/chat)

- Information extraction endpoint (/extract)

- Lead scoring heuristic (urgency + budget + coverage)

- Outputs CRM-friendly JSON

- Example webhook integration for CRM systems (HubSpot, Salesforce, etc.)

🛠️ Tech Stack

- Python 3.10+

- FastAPI + Uvicorn

- Pydantic for validation

- OpenAI Chat Completions API


📂 Project Structure

insurance-lead-qualifier/
│
├── app/
│   ├── main.py          # FastAPI app (chat + extract endpoints)
│   ├── utils.py         # Helper functions (qualifier, scoring, CRM post)
│   └── models.py        # Pydantic models
│
├── requirements.txt     # Dependencies
├── README.md            # Project documentation
├── .gitignore           # Git ignore rules
└── .env.example         # Environment variable template

⚙️ Setup & Run

Clone the repository:

git clone https://github.com/colbybarkee01/insurance-lead-qualifier.git
cd insurance-lead-qualifier

Create and activate a virtual environment:

python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

Install dependencies:

pip install -r requirements.txt

Set up environment:

cp .env.example .env

Run the server:

uvicorn app.main:app --reload

Access interactive docs at:

👉 http://127.0.0.1:8000/docs

🔑 Environment Variables

Create a .env file (copy from .env.example) and set:

OPENAI_API_KEY=sk-...
MODEL=gpt-4o-mini

📡 API Endpoints
/chat

Qualify conversation input with fallback rules.

Request:

{
  "messages": [
    {"role": "user", "content": "Hi, I need life insurance in CA. My budget is $120."}
  ]
}

Response:

{"reply": "Got it — you're looking for life insurance in CA with a $120 budget."}

/extract

Extract customer data + score + CRM JSON.

Request:

{"transcript": "I need life insurance. I'm 29, in CA. Budget is $120. Urgency 4. Provider is Acme."}

Response:

{
  "customer_name": null,
  "customer_age": 29,
  "state_code": "CA",
  "insurance_type": "life",
  "current_provider": "Acme",
  "monthly_budget": 120,
  "priority_level": 4,
  "lead_score": 7,
  "crm_status": "sent",
  "crm_note": "200"
}

📊 Roadmap

 - Add authentication (API key or JWT)

 - Improve lead scoring with ML

 - Add real CRM integration (HubSpot, Salesforce)

 - Deploy to Render/Fly.io with Docker

📜 License

MIT License – free to use, modify, and share.







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
