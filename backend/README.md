# Backend – AI Travel Planning Agent

Python FastAPI + LangGraph backend. Use the virtual environment for all commands.

## Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Add OPENAI_API_KEY if using LLM-based agents
```

## Run

```bash
# From backend/ with venv activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or without activating venv
./venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`
