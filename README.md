# 🛡️ Insurance Lead Qualifier Bot (FastAPI)

A conversational chatbot built with **FastAPI** that qualifies insurance leads in real time.  
It extracts customer info (age, state, insurance type, budget, provider, urgency),  
scores the lead, and returns structured JSON ready for a CRM.

---

## 🚀 Features
- Conversational chatbot endpoint (`/chat`)
- Information extraction endpoint (`/extract`)
- Lead scoring heuristic (urgency + budget + coverage)
- Outputs CRM-friendly JSON
- Example CRM webhook integration (HubSpot, Salesforce, etc.)

---

## 🛠 Tech Stack
- Python 3.10+
- FastAPI + Uvicorn
- Pydantic for validation
- OpenAI Chat Completions API

---

## 📂 Project Structure
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


---

## ⚙️ Setup & Run
```bash
# 1. Clone repo
git clone https://github.com/colbybarkee01/insurance-lead-qualifier.git
cd insurance-lead-qualifier

# 2. Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env   # then add your OpenAI key

# 5. Run server
uvicorn app.main:app --reload

👉 Docs available at: http://127.0.0.1:8000/docs

'''
---

## 🔑 Environment Variables
Create a .env file (copy from .env.example) and set:

OPENAI_API_KEY=sk-...

MODEL=gpt-3.5-turbo

---

## 📡 API Endpoints Tech Stack
- Python 3.10+
- FastAPI + Uvicorn
- Pydantic for validation
- OpenAI Chat Completions API

---

## 📂 Project Structure




## 📡 API Endpoints

/chat

Qualify conversation input with fallback rules.



- Request:

{

  "messages": [
  
    {"role": "user", "content": "Hi, I need life insurance in CA. My budget is $120."}
    
   ]
  
}



- Response:

{"reply": "Got it — you're looking for life insurance in CA with a $120 budget."}

/extract

Extract customer data + score + CRM JSON.



- Request:

{"transcript": "I need life insurance. I'm 29, in CA. Budget is $120. Urgency 4. Provider is Acme."}



- Response:

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




## 📊 Roadmap

 - Add authentication (API key or JWT)

 - Improve lead scoring with ML

 - Add real CRM integration (HubSpot, Salesforce)

 - Deploy to Render/Fly.io with Docker



## 💼 About / Portfolio Notes

This project demonstrates practical AI-assisted automation in insurance sales:

- Problem: Agents waste time on unqualified leads.

- Solution: A lightweight chatbot that gathers structured customer info (age, state, coverage type, budget), applies a scoring heuristic, and pushes qualified leads to a CRM.

- Outcome: Sales teams can focus on high-value prospects instead of manually filtering leads.

- Next Steps: Connect to real CRMs (HubSpot, Salesforce), add retrieval-augmented generation (RAG) for plan-specific FAQs, and enhance lead scoring with machine learning.

This repo serves as a portfolio-ready demo showcasing:

- API design with FastAPI

- Real-world AI integrations with OpenAI

- CRM-friendly JSON workflows

- Deployment-ready structure



## 📜 License

MIT License – free to use, modify, and share.



## Portfolio Notes
- Problem: agents waste time on unqualified leads.
- Solution: bot gathers info (age, state, coverage type, budget), scores lead, and posts JSON to CRM webhook (stubbed).
- Next: plug into real CRM (HubSpot, Salesforce), add RAG over plan docs.
